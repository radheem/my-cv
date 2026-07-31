"""Tests for the scraper FastAPI server (engine/scraper_server.py).

Uses mock BrowserPool to avoid browser launch during testing.

Run inside the ingest container:
    docker exec -e PYTHONPATH=/app radr-cv-ingest-1 pytest -v tests/test_scraper_server.py
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
import engine.scraper_server as srv


@pytest.fixture
def mock_pool_no_launch():
    """Create a mock BrowserPool with async-returning methods (no browser launch)."""
    ctx = MagicMock()

    async def fake_new_page():
        page = MagicMock()
        async def fake_goto(*a, **k):
            return MagicMock()
        async def fake_inner_text(*a, **k):
            return "Example Domain\nThis domain is for use in ..."
        page.goto = fake_goto
        page.inner_text = fake_inner_text
        return page

    async def fake_close():
        pass

    ctx.new_page = fake_new_page
    ctx.close = fake_close

    async def fake_new_context():
        return ctx

    pool = MagicMock()
    pool.is_alive = MagicMock(return_value=True)
    pool.new_context = fake_new_context
    return pool


@pytest.fixture
def mock_pool_dead():
    """Create a mock BrowserPool with is_alive=False."""
    pool = MagicMock()
    pool.is_alive = MagicMock(return_value=False)

    async def fake_new_context():
        ctx = MagicMock()

        async def fake_close():
            pass

        ctx.close = fake_close
        return ctx

    pool.new_context = fake_new_context
    return pool


class TestHealthEndpoint:
    """GET /health should always return 200 regardless of browser state."""

    def test_health_returns_200(self, mock_pool_no_launch):
        """GET /health returns 200 with {"status": "ok"}."""
        with patch.object(srv, "_get_pool", return_value=mock_pool_no_launch):
            client = TestClient(srv.app, raise_server_exceptions=False)
            resp = client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"


class TestBrowserHealthEndpoint:
    """GET /browser-health should reflect the current browser state."""

    def test_browser_health_dead(self, mock_pool_dead):
        """Returns dead when pool.is_alive() is False."""
        with patch.object(srv, "_get_pool", return_value=mock_pool_dead):
            client = TestClient(srv.app, raise_server_exceptions=False)
            resp = client.get("/browser-health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert data["browser"] == "dead"
            assert data["connected"] is False

    def test_browser_health_alive(self, mock_pool_no_launch):
        """Returns alive when pool.is_alive() is True."""
        with patch.object(srv, "_get_pool", return_value=mock_pool_no_launch):
            client = TestClient(srv.app, raise_server_exceptions=False)
            resp = client.get("/browser-health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["browser"] == "alive"
            assert data["connected"] is True


class TestScrapeEndpoint:
    """GET /scrape/text should scrape a URL and return text."""

    def test_scrape_success(self, mock_pool_no_launch):
        """GET /scrape/text?url=valid returns page text."""

        ctx = MagicMock()

        async def fake_new_page():
            page = MagicMock()
            async def fake_goto(*a, **k):
                return MagicMock()
            async def fake_inner_text(*a, **k):
                return "Example Domain\nThis domain is for use in ..."
            page.goto = fake_goto
            page.inner_text = fake_inner_text
            return page

        async def fake_close():
            pass

        ctx.new_page = fake_new_page
        ctx.close = fake_close

        async def fake_new_context():
            return ctx

        mock_pool = MagicMock()
        mock_pool.is_alive = MagicMock(return_value=True)
        mock_pool.new_context = fake_new_context

        with patch.object(srv, "_get_pool", return_value=mock_pool):
            client = TestClient(srv.app, raise_server_exceptions=False)
            resp = client.get("/scrape/text?url=https://example.com")
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert "url" in data
            assert "text" in data
            assert "Example Domain" in data["text"]
            assert "elapsed" in data

    def test_scrape_timeout_returns_504(self, mock_pool_dead):
        """GET /scrape/text with unreachable URL returns error response."""
        from playwright.async_api import Error as PlaywrightError

        mock_ctx = MagicMock()

        async def fake_goto(url, timeout=None, wait_until=None):
            raise PlaywrightError("Navigation timeout of 30000ms exceeded")

        mock_page = MagicMock(goto=fake_goto)
        mock_ctx.new_page = MagicMock(return_value=mock_page)

        async def fake_close():
            pass

        mock_ctx.close = fake_close

        async def fake_new_context():
            return mock_ctx

        mock_pool = MagicMock(new_context=fake_new_context)

        with patch.object(srv, "_get_pool", return_value=mock_pool):
            client = TestClient(srv.app, raise_server_exceptions=False)
            resp = client.get("/scrape/text?url=http://127.0.0.1:19999")
            data = resp.json()
            assert data["success"] is False
            assert "error" in data

    def test_scrape_isolated_contexts(self, mock_pool_dead):
        """Multiple requests create separate browser contexts."""
        contexts = []

        async def fake_new_context():
            ctx = MagicMock()

            async def fake_new_page():
                page = MagicMock()
                async def fake_goto(*a, **k):
                    return MagicMock()
                async def fake_inner_text(*a, **k):
                    return "Page"
                page.goto = fake_goto
                page.inner_text = fake_inner_text
                return page

            async def fake_close():
                pass

            ctx.new_page = fake_new_page
            ctx.close = fake_close
            contexts.append(ctx)
            return ctx

        mock_pool = MagicMock(new_context=fake_new_context)

        with patch.object(srv, "_get_pool", return_value=mock_pool):
            client = TestClient(srv.app, raise_server_exceptions=False)

            r1 = client.get("/scrape/text?url=https://example.com")
            r2 = client.get("/scrape/text?url=https://example.com")

            assert r1.status_code == 200
            assert r2.status_code == 200
            assert len(contexts) == 2
            assert contexts[0] is not contexts[1]

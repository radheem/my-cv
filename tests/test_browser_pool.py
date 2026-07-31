"""Tests for the browser pool module (engine/scrapers.py).

Run inside the ingest container:
    docker exec -e PYTHONPATH=/app radr-cv-mcp-1 pytest -v tests/test_browser_pool.py
"""
from __future__ import annotations

import threading
import time

import pytest
from playwright.sync_api import sync_playwright

import engine.scrapers as m


@pytest.fixture(autouse=True)
def _clear_pool():
    """Reset the module-level singleton before each test."""
    m._pool = None
    m._pool_lock = threading.Lock()
    yield
    # Cleanup
    try:
        if m._pool is not None:
            m._pool.stop()
    except Exception:
        pass
    m._pool = None


def _make_pool() -> m._BrowserPool:
    """Helper to create a new BrowserPool with its own sync_playwright object."""
    pw = sync_playwright().start()
    return m._BrowserPool(pw_obj=pw)


def _teardown_pool(pool_obj: m._BrowserPool) -> None:
    """Teardown a BrowserPool: close browser and stop event loop."""
    try:
        if pool_obj._browser and pool_obj._browser.is_connected():
            pool_obj._browser.close()
    except Exception:
        pass
    try:
        pool_obj.stop()
    except Exception:
        pass


@pytest.fixture
def pool():
    """Return a new BrowserPool instance for a test.

    Each test gets its own BrowserPool so we can safely close
    browsers between tests.  The pool creates and owns its own
    sync_playwright event loop.
    """
    pool_obj = _make_pool()
    browser = pool_obj.get_browser()
    assert browser.is_connected()
    yield pool_obj
    # Teardown
    _teardown_pool(pool_obj)


def test_create_pool():
    """Pool can be instantiated with a sync_playwright object."""
    pool_obj = _make_pool()
    try:
        browser = pool_obj.get_browser()
        assert browser is not None
        assert browser.is_connected()
    finally:
        _teardown_pool(pool_obj)


class TestGetBrowser:
    def test_returns_connected_handle(self, pool):
        """get_browser() should return a connected Playwright Chromium browser."""
        browser = pool.get_browser()
        assert browser is not None
        assert browser.is_connected()

    def test_returns_same_browser_on_multiple_calls(self, pool):
        """Consecutive calls to get_browser() should return the same browser object."""
        b1 = pool.get_browser()
        b2 = pool.get_browser()
        assert b1 is b2


class TestAutoStart:
    def test_pool_starts_browser_on_get_browser_first_call(self, pool):
        """The pool should launch Chromium automatically on first access."""
        assert pool.is_alive()

    def test_get_browser_singleton_across_calls(self, pool):
        """Multiple calls to get_browser() should return the same instance after first launch."""
        first = pool.get_browser()
        second = pool.get_browser()
        assert first is second


class TestConnectionState:
    def test_is_alive_returns_true_when_connected(self, pool):
        assert pool.is_alive() is True

    def test_is_alive_returns_false_after_close(self):
        """After closing the browser, is_alive() should report False."""
        pool_obj = _make_pool()
        try:
            browser = pool_obj.get_browser()
            assert pool_obj.is_alive() is True
            browser.close()
            assert pool_obj.is_alive() is False
        finally:
            _teardown_pool(pool_obj)


class TestThreadSafety:
    def test_get_browser_is_thread_safe(self):
        """Multiple threads calling get_browser() simultaneously should not raise errors."""
        pool_obj = _make_pool()
        results: list[tuple[int, int, bool]] = []
        errors: list[tuple[int, str]] = []

        def worker(tid: int) -> None:
            try:
                for _ in range(3):
                    b = pool_obj.get_browser()
                    results.append((tid, id(b), b.is_connected()))
                    time.sleep(0.05)
            except Exception as exc:
                errors.append((tid, str(exc)))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        assert not errors, f"Thread errors: {errors}"
        assert len(results) == 15
        for tid, bid, connected in results:
            assert connected, f"Thread {tid} got disconnected"
        _teardown_pool(pool_obj)

    def test_concurrent_get_browser_returns_connected(self, pool):
        """Concurrent calls in the same pool must all return connected browsers."""
        results: list[bool] = []
        errors: list[str] = []

        def worker() -> None:
            try:
                b = pool.get_browser()
                results.append(b.is_connected())
            except Exception as e:
                errors.append(str(e))

        ts = [threading.Thread(target=worker) for _ in range(4)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(timeout=10)

        assert not errors
        assert all(results)


class TestSingleton:
    def test_get_browser_uses_singleton(self):
        """Module-level get_browser() should return the same pool handle each time."""
        m._pool = None
        m._pool_lock = threading.Lock()
        b1 = m.get_browser()
        b2 = m.get_browser()
        assert b1 is b2, "Singleton should return the same browser object"
        try:
            b1.close()
        except Exception:
            pass

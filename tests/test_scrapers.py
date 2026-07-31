"""Tests for the browser pool module (engine/scrapers.py).

Uses pytest-asyncio because the implementation uses Playwright async API.

Run inside the ingest container:
    docker exec -e PYTHONPATH=/app radr-cv-mcp-1 pytest -v tests/test_scrapers.py
"""
import pytest
import asyncio
import engine.scrapers as m


@pytest.fixture
def pool():
    """Create a fresh BrowserPool for each test."""
    pool_obj = m.BrowserPool()
    yield pool_obj
    # Cleanup - run in event loop
    async def _teardown():
        if pool_obj._browser and pool_obj._browser.is_connected():
            await pool_obj._browser.close()
        await pool_obj.stop()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_teardown())
        else:
            loop.run_until_complete(_teardown())
    except Exception:
        pass


@pytest.mark.asyncio
async def test_pool_creates_browser(pool):
    """BrowserPool creates a Chromium browser on first get_browser() call."""
    browser = await pool.get_browser()
    assert browser is not None
    assert browser.is_connected()


@pytest.mark.asyncio
async def test_pool_singleton_in_pool(pool):
    """Consecutive calls to pool.get_browser() return the same browser."""
    b1 = await pool.get_browser()
    b2 = await pool.get_browser()
    assert b1 is b2


@pytest.mark.asyncio
async def test_pool_alive_when_connected(pool):
    """is_alive() returns True when browser is connected."""
    await pool.get_browser()
    assert pool.is_alive() is True


@pytest.mark.asyncio
async def test_pool_not_alive_after_close():
    """is_alive() returns False after browser is closed."""
    pool_obj = m.BrowserPool()
    try:
        browser = await pool_obj.get_browser()
        assert pool_obj.is_alive() is True
        await browser.close()
        assert pool_obj.is_alive() is False
    finally:
        await pool_obj.stop()


@pytest.mark.asyncio
async def test_get_browser_singleton():
    """Module-level get_browser() should return the same browser handle."""
    m._pool = None
    b1 = await m.get_browser()
    b2 = await m.get_browser()
    assert b1 is b2
    await b1.close()


@pytest.mark.asyncio
async def test_new_context(pool):
    """new_context() creates a new isolated browser context."""
    ctx1 = await pool.new_context()
    assert ctx1 is not None
    await ctx1.close()


@pytest.mark.asyncio
async def test_is_alive_false_on_fresh_pool():
    """is_alive() returns False before any browser is created."""
    pool_obj = m.BrowserPool()
    assert pool_obj.is_alive() is False


@pytest.mark.asyncio
async def test_pool_detects_dead_browser():
    """When browser disconnects, get_browser() should relaunch."""
    pool_obj = m.BrowserPool()
    try:
        browser1 = await pool_obj.get_browser()
        assert pool_obj.is_alive() is True
        # Close the browser
        await browser1.close()
        assert pool_obj.is_alive() is False
        # Next get_browser() should create a new one
        browser2 = await pool_obj.get_browser()
        assert browser2 is not None
        assert browser2.is_connected()
        assert id(browser2) != id(browser1)
    finally:
        await pool_obj.stop()


@pytest.mark.asyncio
async def test_module_level_get_browser():
    """Module-level get_browser() should return a connected browser."""
    m._pool = None
    browser = await m.get_browser()
    assert browser is not None
    assert browser.is_connected()


@pytest.mark.asyncio
async def test_module_level_stop():
    """Module-level stop() should close the singleton browser."""
    m._pool = None
    browser = await m.get_browser()
    browser_id = id(browser)
    await m.stop()
    # After stop, should create a new pool
    new_browser = await m.get_browser()
    assert new_browser is not None
    assert id(new_browser) != browser_id


@pytest.mark.asyncio
async def test_pool_new_context_is_isolated():
    """Each new_context() should create a separate context."""
    pool_obj = m.BrowserPool()
    try:
        ctx1 = await pool_obj.new_context()
        ctx2 = await pool_obj.new_context()
        assert ctx1 is not ctx2
        await ctx1.close()
        await ctx2.close()
    finally:
        await pool_obj.stop()

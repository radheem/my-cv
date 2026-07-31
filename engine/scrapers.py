"""Persistent Playwright browser pool with auto-relaunch.

Uses Playwright's async API, which is compatible with any running
asyncio event loop (pytest, MCP server, etc.).

Usage
-----
    browser = await get_browser()
    text = await browser.version()

    ctx = await new_context()
    page = await ctx.new_page()
    await page.goto("https://example.com")
    text = await page.inner_text("body")
    await ctx.close()
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

import playwright.async_api as pw_api
from playwright.async_api import Browser, BrowserContext
from playwright.async_api import async_playwright

log = logging.getLogger("cv-tailor.scrapers")

# Re-export for convenience
__all__ = [
    "BrowserPool",
    "get_browser",
    "new_context",
    "stop",
    "Browser",
    "BrowserContext",
]

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-software-rasterizer",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-sync",
    "--disable-translate",
    "--no-first-run",
]

# Module-level singleton
_pool: Optional["BrowserPool"] = None
_pool_lock = asyncio.Lock()


class BrowserPool:
    """Manages a single persistent Chromium browser instance with auto-relaunch.

    The browser is launched lazily on the first ``get_browser()`` call.
    On subsequent calls we check ``is_connected()``; if the process has
    crashed, relaunches transparently.
    """

    def __init__(self) -> None:
        self._pw: Optional[async_playwright] = None
        self._browser: Optional[Browser] = None
        self._launch_lock = asyncio.Lock()

    async def _ensure_pw(self) -> pw_api.Playwright:
        """Ensure the Playwright async context is started."""
        if self._pw is None:
            self._pw = await async_playwright().start()
        return self._pw

    async def get_browser(self) -> Browser:
        """Return a connected Chromium browser handle."""
        if self._browser is not None and self._browser.is_connected():
            return self._browser

        async with self._launch_lock:
            if self._browser is not None and self._browser.is_connected():
                return self._browser

            if self._browser is not None:
                try:
                    await self._browser.close()
                except Exception:
                    pass
                self._browser = None

            log.info("Launching Chromium.")
            pw = await self._ensure_pw()
            self._browser = await pw.chromium.launch(
                headless=False,
                args=BROWSER_ARGS,
            )
        return self._browser

    async def new_context(self) -> BrowserContext:
        """Create a new isolated browser context."""
        browser = await self.get_browser()
        return await browser.new_context()

    def is_alive(self) -> bool:
        """Check whether the browser process is still connected."""
        try:
            return self._browser is not None and self._browser.is_connected()
        except Exception:
            return False

    async def stop(self) -> None:
        """Close the browser and release the Playwright event loop."""
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._pw is not None:
            try:
                await self._pw.stop()
            except Exception:
                pass
            self._pw = None


# ---------------------------------------------------------------------------
# Module-level async helpers
# ---------------------------------------------------------------------------


async def get_browser() -> Browser:
    """Get or create the singleton browser pool's browser."""
    global _pool
    if _pool is None:
        async with _pool_lock:
            if _pool is None:
                _pool = BrowserPool()
    return await _pool.get_browser()


async def stop() -> None:
    """Close the singleton browser."""
    global _pool
    if _pool is not None:
        await _pool.stop()
        _pool = None


async def new_context() -> BrowserContext:
    """Create an isolated context from the singleton pool."""
    pool = await get_browser()
    return await pool.new_context()

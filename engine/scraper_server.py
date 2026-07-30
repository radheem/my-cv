"""FastAPI scraper server — Playwright browser pool + HTTP endpoints.

Serves three endpoints:

  - GET /health              → 200 {"status": "ok"}
  - GET /browser-health      → 200 {"status": "ok", "browser": "alive|dead"}
  - GET /scrape/text?url=... → 200 {"success": true, "text": "...", "url": "..."}
                            or 504 (timeout) / 502 (error) {"success": false, "error": "..."}

Runs as an async server inside the ingest Docker container.
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import Error as PlaywrightError

from engine.scrapers import BrowserPool, new_context

log = logging.getLogger("cv-tailor.scraper-server")

# Module-level pool
_pool: Optional[BrowserPool] = None


async def _get_pool() -> BrowserPool:
    """Get or create the singleton browser pool."""
    global _pool
    if _pool is None:
        _pool = BrowserPool()
    return _pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks for the FastAPI app."""
    from engine.scrapers import get_browser
    pool = await _get_pool()
    browser = await pool.get_browser()
    version = browser.version
    log.info("Scraper server startup: browser connected, version=%s", version)
    yield
    # Shutdown: close browser and release event loop
    await pool.stop()
    log.info("Scraper server shutdown complete")


app = FastAPI(
    title="cv-tailor Scraper Service",
    description="Playwright-based browser pool with health and scrape endpoints",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Simple health check: container is alive and HTTP server accepts requests."""
    return {"status": "ok"}


@app.get("/browser-health")
async def browser_health():
    """Check if the Chromium browser process is alive."""
    pool = await _get_pool()
    alive = pool.is_alive()
    return {
        "status": "ok",
        "browser": "alive" if alive else "dead",
        "connected": alive,
    }


@app.get("/scrape/text")
async def scrape_text(url: str = Query(..., description="URL to scrape")):
    """Scrape a URL and return its inner text body.

    Creates a new isolated browser context per request (no cookie/session bleed).
    Applies stealth for anti-detection.
    Timeout: 30 seconds.
    """
    pool = await _get_pool()
    start = time.time()

    try:
        ctx = await pool.new_context()
        try:
            page = await ctx.new_page()

            # Apply stealth for anti-detection
            try:
                from playwright_stealth import stealth_async
                await stealth_async(page)
            except ImportError:
                log.warning("playwright-stealth not available, skipping stealth")

            # Navigate with timeout
            log.info("Navigating to %s", url)
            await page.goto(url, wait_until="load", timeout=30000)

            # Extract inner text of body
            text = await page.inner_text("body", timeout=10000)

            elapsed = round(time.time() - start, 3)
            return {
                "url": url,
                "text": text,
                "success": True,
                "elapsed": elapsed,
            }
        finally:
            await ctx.close()
    except PlaywrightError as e:
        elapsed = round(time.time() - start, 3)
        err_msg = str(e)
        if "Timeout" in err_msg or "navigation timeout" in err_msg.lower():
            status_code = 504
        else:
            status_code = 502
        return JSONResponse(
            status_code=status_code,
            content={
                "url": url,
                "error": f"Playwright: {err_msg}",
                "success": False,
                "elapsed": elapsed,
            },
        )
    except Exception as e:
        elapsed = round(time.time() - start, 3)
        return JSONResponse(
            status_code=502,
            content={
                "url": url,
                "error": f"Unexpected: {str(e)}",
                "success": False,
                "elapsed": elapsed,
            },
        )

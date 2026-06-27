"""Turn a job source (URL or local file) into clean text.

A local .md/.txt path needs no browser. A URL uses Playwright (optional dep) to
get past JS-rendered pages — install with `pip install -e '.[fetch]'` plus
`playwright install chromium`.
"""

from __future__ import annotations

import pathlib


def fetch_job_text(source: str) -> str:
    """Return clean job-posting text from a URL, a local file path, or database slug."""
    if source.startswith(("http://", "https://")):
        return _fetch_url(source)
    path = pathlib.Path(source)
    if not path.exists():
        # Fallback to database lookup if it matches a slug
        try:
            from .db import get_conn
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT description FROM jobs WHERE slug = %s AND description IS NOT NULL", (source,))
                    row = cur.fetchone()
                    if row and row["description"]:
                        return row["description"]
        except Exception:
            pass
        raise SystemExit(f"Job source not found: {source}")
    return path.read_text(encoding="utf-8")


def _fetch_url(url: str) -> str:
    import multiprocessing

    def worker(q, target_url):
        import sys
        import os
        # Redirect standard input/output to protect parent MCP Stdio channel, keeping stderr for tracebacks
        sys.stdin = open(os.devnull, "r")
        sys.stdout = open(os.devnull, "w")

        try:
            from playwright.sync_api import sync_playwright
            try:
                from playwright_stealth import stealth_sync
            except ImportError:
                stealth_sync = None

            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    page = browser.new_page()
                    if stealth_sync:
                        stealth_sync(page)
                    page.goto(target_url, wait_until="load", timeout=30000)
                    text = page.inner_text("body")
                    q.put((True, text))
                finally:
                    browser.close()
        except Exception as e:
            q.put((False, e))

    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=worker, args=(q, url))
    p.start()
    success, result = q.get()
    p.join()
    if success:
        return result
    raise result

"""Turn a job source (URL or local file) into clean text.

A local .md/.txt path needs no browser. A URL uses Playwright (optional dep) to
get past JS-rendered pages — install with `pip install -e '.[fetch]'` plus
`playwright install chromium`.
"""

from __future__ import annotations

import pathlib


def fetch_job_text(source: str) -> str:
    """Return clean job-posting text from a URL or a local file path."""
    if source.startswith(("http://", "https://")):
        return _fetch_url(source)
    path = pathlib.Path(source)
    if not path.exists():
        raise SystemExit(f"Job source not found: {source}")
    return path.read_text(encoding="utf-8")


def _fetch_url(url: str) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:  # pragma: no cover - optional dep
        raise SystemExit(
            "Fetching a URL needs Playwright. Install with: "
            "pip install -e '.[fetch]' && playwright install chromium\n"
            "Or paste the job description into a .txt/.md file and pass that path."
        ) from e

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            try:
                from playwright_stealth import stealth_sync
                stealth_sync(page)
            except ImportError:
                pass
            page.goto(url, wait_until="networkidle", timeout=30000)
            # innerText collapses to roughly what a human reads, dropping markup.
            text = page.inner_text("body")
        finally:
            browser.close()
    return text

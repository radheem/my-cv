"""Fraunhofer careers portal scraper — jobs.fraunhofer.de.

Public site; no login required. Uses Playwright (headless Chromium) to render
the JS-based search results and job detail pages.

Search URL:  https://jobs.fraunhofer.de/search/?q=<keywords>&locale=en_US
Job URL:     https://jobs.fraunhofer.de/job/<slug>/<job_id>/

Pure helpers (build_search_url, _extract_job_id) are unit-testable.
Browser-driving functions (search, capture_jd, hunt_and_capture) require Playwright.
"""
from __future__ import annotations

import datetime
import hashlib
import logging
import pathlib
import re
import sys
from urllib.parse import quote_plus

from ..linkedin.jobs import Job, clean_jd_text, load_seen, save_seen, slugify, write_jd

log = logging.getLogger("cv_tailor.fraunhofer.jobs")

BASE = "https://jobs.fraunhofer.de"
SEARCH_URL = f"{BASE}/search/"

_JOB_ID_RE = re.compile(r"/job/[^/]+/(\d+)/?")
_POSTAL_RE = re.compile(r"-\d{4,5}$")


# ── pure helpers ──────────────────────────────────────────────────────────────


def extract_job_id(url: str) -> str | None:
    m = _JOB_ID_RE.search(url)
    return m.group(1) if m else None


def _stable_id(url: str) -> str:
    """Numeric job id from path, or MD5-12 of URL as fallback."""
    jid = extract_job_id(url)
    return jid if jid else hashlib.md5(url.encode()).hexdigest()[:12]


def build_search_url(keywords: str, *, location: str | None = None) -> str:
    """Build a Fraunhofer jobs search URL. Pure (unit-testable)."""
    url = f"{SEARCH_URL}?q={quote_plus(keywords)}&locale=en_US"
    if location:
        url += f"&location={quote_plus(location)}"
    return url


def _title_from_url(url: str) -> str:
    """Derive a readable title from the URL slug as a last-resort fallback.

    /job/Berlin-Software-Engineer-Backend-10115/123456/
    → "Software Engineer Backend"
    """
    m = re.search(r"/job/([^/]+)/\d+", url)
    if not m:
        return ""
    slug = _POSTAL_RE.sub("", m.group(1))   # strip postal code
    parts = slug.split("-", 1)
    slug = parts[1] if len(parts) > 1 else slug   # drop leading city
    return slug.replace("-", " ").strip()


# ── browser-driving ───────────────────────────────────────────────────────────


def search(
    page,
    keywords: str,
    *,
    location: str | None = None,
    limit: int = 10,
) -> list[Job]:
    """Navigate Fraunhofer search results and return up to `limit` Job objects."""
    url = build_search_url(keywords, location=location)
    log.info("fraunhofer search: %r", keywords)
    page.goto(url, wait_until="domcontentloaded")

    # wait for at least one job link to appear
    try:
        page.wait_for_selector("a[href*='/job/']", timeout=15000)
    except Exception:
        log.warning("no job links on search page for %r", keywords)
        return []
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass

    jobs: list[Job] = []
    seen_ids: set[str] = set()
    links = page.locator("a[href*='/job/']")

    for i in range(links.count()):
        link = links.nth(i)
        try:
            href = link.get_attribute("href") or ""
        except Exception:
            continue

        if not re.search(r"/job/[^/]+/\d+", href):
            continue

        full_url = (BASE + href if not href.startswith("http") else href).split("?")[0]
        job_id = _stable_id(full_url)
        if job_id in seen_ids:
            continue
        seen_ids.add(job_id)

        # --- title ---
        try:
            raw = (link.inner_text(timeout=1500) or "").strip()
            title = raw.splitlines()[0].strip() if raw else ""
        except Exception:
            title = ""
        if not title:
            title = _title_from_url(full_url)
        if not title:
            continue

        # --- location from nearest list-item ancestor ---
        location_found = ""
        for anc in (
            "xpath=ancestor::li[1]",
            "xpath=ancestor::tr[1]",
            "xpath=ancestor::div[contains(@class,'card')][1]",
        ):
            try:
                card = link.locator(anc)
                if not card.count():
                    continue
                card_text = card.inner_text(timeout=1000) or ""
                lines = [ln.strip() for ln in card_text.splitlines()
                         if ln.strip() and ln.strip() != title]
                if lines:
                    location_found = lines[-1]
                break
            except Exception:
                continue

        jobs.append(Job(
            job_id=job_id,
            title=title,
            company="Fraunhofer",
            location=location_found,
            url=full_url,
        ))

        if len(jobs) >= limit:
            break

    log.info("found %d job(s)", len(jobs))
    return jobs


def capture_jd(page, job: Job) -> str:
    """Open a Fraunhofer job detail page and return its description text."""
    page.goto(job.url, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass

    # Try description-specific containers in preference order
    for sel in (
        ".job-description",
        "[class*='jobad-content']",
        "[class*='job-detail']",
        "#ctl00_plcMain_pnlLeft",
        "main article",
        "main",
        ".col-sm-8",
        ".col-md-8",
        "article",
    ):
        loc = page.locator(sel)
        if not loc.count():
            continue
        try:
            text = loc.first.inner_text(timeout=3000)
            if text and len(text.strip()) > 200:
                return text.strip()
        except Exception:
            continue

    # Fallback: full body
    return page.inner_text("body")


def hunt_and_capture(
    keywords: str,
    out_dir: pathlib.Path,
    *,
    location: str | None = None,
    limit: int = 10,
) -> dict:
    """Run one Fraunhofer search in a plain headless browser and capture JDs.

    No session required — Fraunhofer's portal is public. Opens its own Playwright
    Chromium context (headless, no profile persistence needed). Does NOT require Xvfb.
    """
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    seen_path = out_dir / ".seen.json"
    seen = load_seen(seen_path)
    counts = {"captured": 0, "skipped": 0, "errors": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = ctx.new_page()

        try:
            jobs = search(page, keywords, location=location, limit=limit)
            for job in jobs:
                if job.job_id in seen:
                    counts["skipped"] += 1
                    log.info("skip (seen): %s", job.url)
                    continue
                try:
                    text = capture_jd(page, job)
                except Exception as exc:
                    print(f"  error {job.url}: {exc}", file=sys.stderr)
                    counts["errors"] += 1
                    continue

                captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
                path = write_jd(
                    job, clean_jd_text(text), out_dir, captured_at, source="fraunhofer"
                )
                seen[job.job_id] = slugify(job.company, job.title, job.job_id)
                counts["captured"] += 1
                print(f"  captured {path}")
        finally:
            ctx.close()
            browser.close()

    save_seen(seen_path, seen)
    return counts

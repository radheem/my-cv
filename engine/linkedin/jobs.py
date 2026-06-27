"""Search LinkedIn jobs and capture clean JD text → vault/jds/<slug>.txt.

The pure helpers (slugify / extract_job_id / clean_jd_text / jd_frontmatter / dedup) are
unit-tested. The browser-driving functions (search / capture_jd) use Playwright locators and
are exercised by the e2e smoke. Output is the cross-sprint contract: Sprint 2's `cv-tailor
new` reads the front-matter + body verbatim.
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import re
from dataclasses import asdict, dataclass
from urllib.parse import quote_plus

from .humanize import human_click, human_pause, human_scroll, settle

log = logging.getLogger("cv_tailor.linkedin.jobs")

SEARCH_URL = "https://www.linkedin.com/jobs/search/"


@dataclass
class Job:
    job_id: str
    title: str
    company: str
    location: str
    url: str
    applicants: "int | None" = None


# ── pure helpers (unit-tested) ──────────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_APPLICANTS_RE = re.compile(
    r"(?:be among the first|first)\s+(\d+)\s+applicants?|"
    r"over\s+(\d[\d,]*)\s+applicants?|"
    r"(\d[\d,]*)\s+applicants?",
    re.IGNORECASE,
)


def parse_applicant_count(text: str) -> "int | None":
    """Parse an applicant count from card or JD text.

    Returns None if not found.
    - "Be among the first 25 applicants" → 24 (treat as fewer than 25)
    - "Over 200 applicants"              → 201
    - "1,234 applicants"                 → 1234
    """
    m = _APPLICANTS_RE.search(text or "")
    if not m:
        return None
    raw1, raw2, raw3 = m.group(1), m.group(2), m.group(3)
    if raw1:
        return int(raw1) - 1
    if raw2:
        return int(raw2.replace(",", "")) + 1
    if raw3:
        return int(raw3.replace(",", ""))
    return None
_JOBID_VIEW = re.compile(r"/jobs/view/(\d+)")
_JOBID_PARAM = re.compile(r"currentJobId=(\d+)")


def slugify(*parts: str) -> str:
    s = "-".join(p for p in parts if p)
    s = _SLUG_RE.sub("-", s.lower()).strip("-")
    return s[:80] or "job"


def extract_job_id(url: str) -> str | None:
    for rx in (_JOBID_VIEW, _JOBID_PARAM):
        m = rx.search(url or "")
        if m:
            return m.group(1)
    return None


def clean_jd_text(raw: str) -> str:
    """Strip per-line whitespace and collapse runs of blank lines."""
    out: list[str] = []
    for ln in (raw or "").splitlines():
        ln = ln.strip()
        if not ln:
            if out and out[-1] == "":
                continue
            out.append("")
        else:
            out.append(ln)
    return "\n".join(out).strip()


def _yaml_escape(v: str) -> str:
    return (v or "").replace("\\", "\\\\").replace('"', '\\"')


def jd_frontmatter(job: Job, captured_at: str, *, source: str = "linkedin") -> str:
    e = _yaml_escape
    applicants_line = f"applicants: {job.applicants}\n" if job.applicants is not None else ""
    return (
        "---\n"
        f"source: {source}\n"
        f'url: "{e(job.url)}"\n'
        f'company: "{e(job.company)}"\n'
        f'title: "{e(job.title)}"\n'
        f'location: "{e(job.location)}"\n'
        f'job_id: "{e(job.job_id)}"\n'
        f'captured_at: "{e(captured_at)}"\n'
        f"{applicants_line}"
        "---\n"
    )


def load_seen(path: pathlib.Path) -> dict:
    from ..db import get_conn
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT job_id, slug FROM jobs WHERE job_id IS NOT NULL")
                return {row["job_id"]: row["slug"] for row in cur.fetchall()}
    except Exception:
        # Fallback to local file if DB connection is unavailable (for offline tests)
        path = pathlib.Path(path)
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                return {}
        return {}


def save_seen(path: pathlib.Path, seen: dict) -> None:
    # Save local backup, but database is main truth
    try:
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(seen, indent=2, sort_keys=True))
    except Exception:
        pass


def already_seen(job_id: str, seen: dict) -> bool:
    return job_id in seen


def write_jd(job: Job, text: str, out_dir, captured_at: str, *, source: str = "linkedin") -> pathlib.Path:
    slug = slugify(job.company, job.title, job.job_id)
    
    # Upsert into PostgreSQL jobs table
    from ..db import get_conn
    import hashlib
    try:
        # Determine platform
        platform = "other"
        if "linkedin.com" in job.url:
            platform = "linkedin"
        elif "glassdoor" in job.url:
            platform = "glassdoor"
        elif "fraunhofer" in job.url:
            platform = "fraunhofer"
            
        # Compute new hash-based job_id for database representation
        if job.url and job.url.strip():
            clean_url = job.url.strip().rstrip("/")
            db_job_id = hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:12]
        else:
            clean_title = "".join(ch for ch in job.title.lower() if ch.isalnum() or ch.isspace()).strip()
            db_job_id = hashlib.md5(clean_title.encode("utf-8")).hexdigest()[:12]

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO jobs (job_id, slug, company, title, location, url, description, score, applicants, source, platform)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO UPDATE SET
                        slug = EXCLUDED.slug,
                        company = EXCLUDED.company,
                        title = EXCLUDED.title,
                        location = EXCLUDED.location,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description,
                        applicants = EXCLUDED.applicants,
                        source = EXCLUDED.source,
                        platform = EXCLUDED.platform
                """, (
                    db_job_id, slug, job.company, job.title, job.location, job.url, 
                    clean_jd_text(text), None, job.applicants, "url", platform
                ))
            conn.commit()
    except Exception as e:
        import logging
        logging.getLogger("cv-tailor").error(f"Failed to save captured job to DB: {e}")

    # Also write local backup text file
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    txt = out / f"{slug}.txt"
    txt.write_text(jd_frontmatter(job, captured_at, source=source) + "\n" + clean_jd_text(text) + "\n", "utf-8")
    (out / f"{slug}.json").write_text(
        json.dumps({**asdict(job), "captured_at": captured_at, "slug": slug}, indent=2)
    )
    return txt


# ── browser-driving (e2e-smoke-tested) ──────────────────────────────────────────────────


def _first_text(scope, selectors: list[str]) -> str:
    for sel in selectors:
        loc = scope.locator(sel)
        if loc.count():
            try:
                return (loc.first.inner_text(timeout=2000) or "").strip().splitlines()[0].strip()
            except Exception:
                continue
    return ""


def _abs_url(href: str) -> str:
    if href.startswith("http"):
        return href.split("?")[0]
    return "https://www.linkedin.com" + href.split("?")[0]


def build_search_url(
    keywords: str,
    *,
    location: "str | None" = None,
    geo_id: "str | None" = None,
    distance: "int | float | None" = None,
    days_back: int = 7,
    easy_apply: bool = False,
) -> str:
    """Build a LinkedIn jobs-search URL. Pure (unit-tested).

    `keywords` is passed through verbatim (URL-encoded), so LinkedIn boolean syntax
    works as typed: '"Go" OR "Golang" OR "Python"'. `geo_id` (the LinkedIn region id,
    `&geoId=`) is preferred over the free-text `location`; only one is emitted.
    `distance` → `&distance=`, `days_back` → `&f_TPR=r<seconds>`, `easy_apply` →
    `&f_EA=true`.
    """
    url = f"{SEARCH_URL}?keywords={quote_plus(keywords)}"
    if geo_id:
        url += f"&geoId={quote_plus(str(geo_id))}"
    elif location:
        url += f"&location={quote_plus(location)}"
    if distance is not None:
        url += f"&distance={distance}"
    if days_back:
        url += f"&f_TPR=r{days_back * 86400}"
    if easy_apply:
        url += "&f_EA=true"
    return url


def search(
    page,
    keywords: str,
    location: "str | None" = None,
    limit: int = 10,
    days_back: int = 7,
    max_applicants: "int | None" = None,
    *,
    geo_id: "str | None" = None,
    distance: "int | float | None" = None,
    easy_apply: bool = False,
) -> "list[Job]":
    """Run a jobs search and collect up to `limit` cards (human-paced scrolling).

    days_back: only surface jobs posted within this many days (LinkedIn f_TPR filter).
    max_applicants: discard cards whose displayed applicant count exceeds this value.
                    Cards with no count shown are kept and checked again after capture_jd.
    geo_id / location / distance / easy_apply: see build_search_url.
    """
    url = build_search_url(
        keywords,
        location=location,
        geo_id=geo_id,
        distance=distance,
        days_back=days_back,
        easy_apply=easy_apply,
    )
    log.info("searching: %s (last %d days)", keywords, days_back)
    page.goto(url, wait_until="domcontentloaded")
    settle(page)

    jobs: list[Job] = []
    ids: set[str] = set()
    card_sel = "div.job-card-container, li.jobs-search-results__list-item, div.base-card"
    for _ in range(10):
        cards = page.locator(card_sel)
        for i in range(cards.count()):
            if len(jobs) >= limit:
                break
            card = cards.nth(i)
            link = card.locator("a[href*='/jobs/view/']")
            if not link.count():
                continue
            href = link.first.get_attribute("href") or ""
            jid = extract_job_id(href)
            if not jid or jid in ids:
                continue

            # Try to read applicant count from card text for early rejection
            card_text = ""
            try:
                card_text = card.inner_text(timeout=1000) or ""
            except Exception:
                pass
            card_applicants = parse_applicant_count(card_text)
            if max_applicants is not None and card_applicants is not None:
                if card_applicants > max_applicants:
                    log.debug("skip %s: %d applicants (card)", jid, card_applicants)
                    ids.add(jid)
                    continue

            ids.add(jid)
            jobs.append(
                Job(
                    job_id=jid,
                    title=_first_text(card, ["a.job-card-list__title", "h3", "a"]),
                    company=_first_text(
                        card,
                        [
                            ".job-card-container__company-name",
                            ".artdeco-entity-lockup__subtitle",
                            ".base-search-card__subtitle",
                            "h4",
                        ],
                    ),
                    location=_first_text(
                        card,
                        [".job-card-container__metadata-item", ".job-search-card__location"],
                    ),
                    url=_abs_url(href),
                    applicants=card_applicants,
                )
            )
        if len(jobs) >= limit:
            break
        human_scroll(page, 2)
        settle(page, 0.8, 1.6)
    log.info("found %d job(s)", len(jobs))
    return jobs[:limit]


def _extract_applicant_count_from_page(page) -> "int | None":
    """Try to read the applicant count from an open job detail page."""
    for sel in (
        ".jobs-unified-top-card__applicant-count",
        ".jobs-unified-top-card__subtitle-secondary-grouping",
        ".num-applicants__caption",
        ".jobs-unified-top-card__bullet",
    ):
        loc = page.locator(sel)
        if loc.count():
            try:
                for i in range(loc.count()):
                    text = loc.nth(i).inner_text(timeout=1000) or ""
                    count = parse_applicant_count(text)
                    if count is not None:
                        return count
            except Exception:
                continue
    return None


def capture_jd(page, job: Job) -> str:
    """Open a job and return clean text from its description pane (never the whole body).

    Side-effect: sets job.applicants from the page header if not already known.
    """
    page.goto(job.url, wait_until="domcontentloaded")
    settle(page)

    if job.applicants is None:
        job.applicants = _extract_applicant_count_from_page(page)

    for sel in (
        '[data-testid="expandable-text-button"]',
        "button.show-more-less-html__button",
        "button[aria-label*='see more']",
        "button.jobs-description__footer-button",
    ):
        b = page.locator(sel)
        if b.count():
            try:
                human_click(page, b.first)
            except Exception:
                pass
            human_pause(0.3, 0.9)
            break

    for sel in (
        '[data-testid="expandable-text-box"]',
        ".jobs-description__content",
        ".jobs-box__html-content",
        ".show-more-less-html__markup",
        "div.description__text",
        "article",
    ):
        loc = page.locator(sel)
        if loc.count():
            text = loc.first.inner_text()
            if text and text.strip():
                return text
    try:  # diagnostic: dump the page so we can find the real description container
        dbg = pathlib.Path(os.environ.get("CV_TAILOR_VAULT", "vault")) / "challenges"
        dbg.mkdir(parents=True, exist_ok=True)
        (dbg / f"jobpage-{job.job_id}.html").write_text(page.content(), encoding="utf-8")
    except Exception:
        pass
    raise RuntimeError(f"description pane not found: {job.url}")

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


# ── pure helpers (unit-tested) ──────────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"[^a-z0-9]+")
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


def jd_frontmatter(job: Job, captured_at: str) -> str:
    e = _yaml_escape
    return (
        "---\n"
        "source: linkedin\n"
        f'url: "{e(job.url)}"\n'
        f'company: "{e(job.company)}"\n'
        f'title: "{e(job.title)}"\n'
        f'location: "{e(job.location)}"\n'
        f'job_id: "{e(job.job_id)}"\n'
        f'captured_at: "{e(captured_at)}"\n'
        "---\n"
    )


def load_seen(path: pathlib.Path) -> dict:
    path = pathlib.Path(path)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_seen(path: pathlib.Path, seen: dict) -> None:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(seen, indent=2, sort_keys=True))


def already_seen(job_id: str, seen: dict) -> bool:
    return job_id in seen


def write_jd(job: Job, text: str, out_dir, captured_at: str) -> pathlib.Path:
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = slugify(job.company, job.title, job.job_id)
    txt = out / f"{slug}.txt"
    txt.write_text(jd_frontmatter(job, captured_at) + "\n" + clean_jd_text(text) + "\n", "utf-8")
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


def search(page, keywords: str, location: str | None = None, limit: int = 10) -> list[Job]:
    """Run a jobs search and collect up to `limit` cards (human-paced scrolling)."""
    url = f"{SEARCH_URL}?keywords={quote_plus(keywords)}"
    if location:
        url += f"&location={quote_plus(location)}"
    log.info("searching: %s", keywords)
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
                )
            )
        if len(jobs) >= limit:
            break
        human_scroll(page, 2)
        settle(page, 0.8, 1.6)
    log.info("found %d job(s)", len(jobs))
    return jobs[:limit]


def capture_jd(page, job: Job) -> str:
    """Open a job and return clean text from its description pane (never the whole body)."""
    page.goto(job.url, wait_until="domcontentloaded")
    settle(page)
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

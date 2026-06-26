import argparse
import datetime
import logging
import pathlib
import re
from engine import cli, gmail
from engine.db import get_conn

log = logging.getLogger("cv-tailor-workflows")
_LINKEDIN_URL_RE = re.compile(
    r'https?://(?:www\.)?linkedin\.com/jobs/view/(?P<id>\d+)',
    re.IGNORECASE
)


def extract_urls_from_text(text: str) -> list[str]:
    urls = []
    for match in _LINKEDIN_URL_RE.finditer(text):
        url = f"https://www.linkedin.com/jobs/view/{match.group('id')}/"
        if url not in urls:
            urls.append(url)
    return urls


def run_gmail_hunt_workflow(filter_query: str = "subject:\"linkedin job alert\" is:unread", limit: int = 10, order: str = "top") -> str:
    """Pure Python implementation of the alert-to-application ingestion pipeline."""
    logs = ["=== Starting Gmail Ingest Pipeline ==="]
    
    # 1. Search Gmail Alerts
    try:
        threads = gmail.search_emails(filter_query, limit, include_bodies=True)
        logs.append(f"Found {len(threads)} alert threads matching query.")
    except Exception as e:
        log.exception("Gmail search failed")
        return f"ERROR: Gmail search failed: {str(e)}"
        
    urls = []
    for thread in threads:
        for msg in thread.get("messages", []):
            body = msg.get("body", "")
            for url in extract_urls_from_text(body):
                if url not in urls:
                    urls.append(url)
                    
    logs.append(f"Extracted {len(urls)} unique unseen job posting URLs.")
    if not urls:
        return "\n".join(logs) + "\nNo new job alerts to process. Exiting."

    # 2. Capture Job Descriptions via Playwright Session
    from engine.linkedin import jobs as J
    from engine.cli import _extract_title_company, _drive_session
    
    captured_slugs = []
    out_dir = pathlib.Path("vault/jds")
    
    for url in urls:
        logs.append(f"Capturing description: {url}")
        job_id = cli._job_id_from_source(url)
        view_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
        result_capture = {}
        
        try:
            def run(page) -> None:
                job = J.Job(job_id=job_id, title="role", company="company", location="", url=view_url)
                text = J.capture_jd(page, job)
                title, company = _extract_title_company(page)
                job.title = title or job.title
                job.company = company or job.company
                captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
                result_capture["path"] = J.write_jd(job, text, out_dir, captured_at)
                result_capture["slug"] = J.slugify(job.company, job.title, job.job_id)
                
            _drive_session(run)
            
            if "slug" in result_capture:
                captured_slugs.append(result_capture["slug"])
                logs.append(f"Successfully captured {result_capture["slug"]}")
        except Exception as e:
            logs.append(f"WARNING: Capture failed for {url}: {str(e)}")
            continue

    if not captured_slugs:
        return "\n".join(logs) + "\nNo jobs were successfully captured. Exiting."

    # 3. Score the captured JDs natively
    selected_slugs = []
    if order == "fifo":
        selected_slugs = captured_slugs[:limit]
    else:
        try:
            from scripts.score_jds import _load_config, _score
            scoring_cfg = _load_config().get("scoring", {})
            scored_jobs = []
            
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT slug, description FROM jobs WHERE slug = ANY(%s)", (captured_slugs,))
                    db_rows = cur.fetchall()
                    for r in db_rows:
                        score, _ = _score(r["description"] or "", scoring_cfg)
                        cur.execute("UPDATE jobs SET score = %s WHERE slug = %s", (score, r["slug"]))
                        scored_jobs.append((r["slug"], score))
                    conn.commit()
            scored_jobs.sort(key=lambda x: x[1], reverse=True)
            selected_slugs = [s[0] for s in scored_jobs[:limit]]
        except Exception as e:
            logs.append(f"WARNING: DB scoring failed: {str(e)}. Falling back to FIFO.")
            selected_slugs = captured_slugs[:limit]

    logs.append(f"Selected {len(selected_slugs)} top jobs to generate:")
    for s in selected_slugs:
        logs.append(f"  - {s}")

    # 4. Generate, Render, and Upload Applications
    for slug in selected_slugs:
        logs.append(f"Processing application: {slug}")
        args_new = argparse.Namespace(
            source=slug, slug=slug, provider="anthropic", model=None,
            ollama_url=None, no_translate=False, no_save_db=False, recipient=None
        )
        try:
            cli.cmd_new(args_new)
            logs.append(f"  -> Generated tailored cv.md and cover-letter.md")
            
            logs.append(f"  -> Rendering PDF for {slug}")
            args_pdf = argparse.Namespace(slug=slug)
            cli.cmd_pdf(args_pdf)
            
            logs.append(f"  -> Uploading to Google Drive")
            args_upload = argparse.Namespace(slug=slug)
            cli.cmd_upload(args_upload)
        except Exception as e:
            logs.append(f"ERROR: Generation failed for {slug}: {str(e)}")
            continue

    # 5. Push Updated Statuses to Google Sheets
    try:
        logs.append("Synchronizing statuses to Google Sheets...")
        args_push = argparse.Namespace(action="push", slug=None, status=None)
        cli.cmd_status(args_push)
        logs.append("Successfully synchronized application sheets!")
    except Exception as e:
        logs.append(f"WARNING: Sheets sync failed: {str(e)}")

    logs.append("=== Gmail Ingest Pipeline Complete ===")
    return "\n".join(logs)

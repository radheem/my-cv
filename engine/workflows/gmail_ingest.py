import argparse
import datetime
import logging
import pathlib
import re
from engine import cli, gmail
from engine.db import get_conn

log = logging.getLogger("cv-tailor-workflows")
import hashlib
from urllib.parse import urlparse

def parse_and_normalize_job_url(url: str) -> dict:
    """Parse any job URL and return a dict with:
    - job_id: stable unique identifier (numeric, alphanumeric, or MD5 hash fallback)
    - platform: 'linkedin', 'glassdoor', 'fraunhofer', 'indeed', or 'other'
    - normalized_url: standardized canonical URL format
    If the URL is identified as a non-job listing (e.g. settings, unsubscribe, general search, help, home page), returns None.
    """
    u = url.strip()
    u_lower = u.lower()
    
    # 1. Broadly filter out typical non-job-posting pages (unsubscribe, help, privacy, manage, premium, profile, etc.)
    discard_keywords = (
        "/unsubscribe", "unsubscribe", "/alerts", "/help/", "linkedin.com/help", 
        "linkedin.com/premium", "/manage/", "/settings", "privacy-policy", 
        "cookie-policy", "/about", "contact", "support", "linkedin.com/comm/premium",
        "linkedin.com/comm/premium/products", "/comm/premium/"
    )
    if any(k in u_lower for k in discard_keywords):
        return None
        
    # 2. LinkedIn
    # We only accept LinkedIn links that are actual individual job postings (jobs/view or currentJobId)
    is_linkedin = "linkedin.com" in u_lower
    m_li_view = re.search(r'linkedin\.com/(?:[a-z0-9-]+/)?jobs/view/(?P<id>\d+)', u, re.IGNORECASE)
    if m_li_view:
        jid = m_li_view.group('id')
        return {
            "job_id": jid,
            "platform": "linkedin",
            "normalized_url": f"https://www.linkedin.com/jobs/view/{jid}/"
        }
    m_li_param = re.search(r'linkedin\.com/.*[?&]currentJobId=(?P<id>\d+)', u, re.IGNORECASE)
    if m_li_param:
        jid = m_li_param.group('id')
        return {
            "job_id": jid,
            "platform": "linkedin",
            "normalized_url": f"https://www.linkedin.com/jobs/view/{jid}/"
        }
    if is_linkedin:
        # Ignore any other LinkedIn links that are not individual jobs (e.g., search lists, etc.)
        return None
        
    # 3. Fraunhofer
    m_fh = re.search(r'jobs\.fraunhofer\.de/job/(?P<slug>[^/]+)/(?P<id>\d+)', u, re.IGNORECASE)
    if m_fh:
        jid = m_fh.group('id')
        slug = m_fh.group('slug')
        return {
            "job_id": jid,
            "platform": "fraunhofer",
            "normalized_url": f"https://jobs.fraunhofer.de/job/{slug}/{jid}/"
        }
    if "fraunhofer.de" in u_lower and "/job/" not in u_lower:
        return None
        
    # 4. Glassdoor
    m_gd_jl = re.search(r'glassdoor\.com/.*[?&](?:jl|jobListingId)=(?P<id>\d+)', u, re.IGNORECASE)
    if m_gd_jl:
        jid = m_gd_jl.group('id')
        return {
            "job_id": jid,
            "platform": "glassdoor",
            "normalized_url": f"https://www.glassdoor.com/job-listing/detail.htm?jl={jid}"
        }
    m_gd_path = re.search(r'glassdoor\.com/.*jl_(?P<id>\d+)', u, re.IGNORECASE)
    if m_gd_path:
        jid = m_gd_path.group('id')
        return {
            "job_id": jid,
            "platform": "glassdoor",
            "normalized_url": f"https://www.glassdoor.com/job-listing/detail.htm?jl={jid}"
        }
    if "glassdoor.com" in u_lower:
        # Ignore any other Glassdoor links that don't have job listing IDs
        return None
        
    # 5. Indeed
    m_id_jk = re.search(r'indeed\.com/.*[?&]jk=(?P<id>[a-zA-Z0-9]+)', u, re.IGNORECASE)
    if m_id_jk:
        jid = m_id_jk.group('id')
        return {
            "job_id": jid,
            "platform": "indeed",
            "normalized_url": f"https://www.indeed.com/viewjob?jk={jid}"
        }
    if "indeed.com" in u_lower:
        # Ignore other indeed links without jk
        return None
        
    # 6. Fallback - generic URL
    # Keep only if it contains clear career/job indicators in its structure
    is_job_related_site = any(k in u_lower for k in ("/job/", "/jobs/", "/career/", "/careers/", "/stellenangebot/"))
    if not is_job_related_site:
        return None
        
    parsed = urlparse(u)
    domain_parts = parsed.netloc.split('.')
    platform = "other"
    if len(domain_parts) >= 2:
        potential_platform = domain_parts[-2].lower()
        if potential_platform in ("linkedin", "glassdoor", "fraunhofer", "indeed", "xing"):
            platform = potential_platform
            
    stable_id = hashlib.md5(u.encode('utf-8')).hexdigest()[:12]
    return {
        "job_id": stable_id,
        "platform": platform,
        "normalized_url": u
    }


def extract_urls_from_text(text: str) -> list[str]:
    urls = []
    # Match any raw HTTP/HTTPS links
    raw_urls_matches = re.findall(r'https?://[a-zA-Z0-9-._~:/?#\[\]@!$&\'()*+,;=%]+', text, re.IGNORECASE)
    for raw_url in raw_urls_matches:
        # Strip trailing punctuation commonly appended in plain text emails
        while raw_url and raw_url[-1] in ('.', ',', ';', ':', ')', '(', ']', '[', '"', "'", '*', '>'):
            raw_url = raw_url[:-1]
        if not raw_url:
            continue
            
        parsed_info = parse_and_normalize_job_url(raw_url)
        if parsed_info is None:
            continue
        norm_url = parsed_info["normalized_url"]
        if norm_url not in urls:
            urls.append(norm_url)
    return urls


def _capture_jobs_worker_func(urls: list[str]) -> tuple[list[str], list[str]]:
    import pathlib
    import re
    import datetime
    from playwright.sync_api import sync_playwright
    try:
        from playwright_stealth import stealth_sync
    except ImportError:
        stealth_sync = None
    from engine.linkedin import jobs as J
    from engine.cli import _extract_title_company
    
    captured_slugs = []
    worker_logs = []
    out_dir = pathlib.Path("vault/jds")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for url in urls:
                worker_logs.append(f"Capturing description: {url}")
                parsed_info = parse_and_normalize_job_url(url)
                if parsed_info is None:
                    continue
                job_id = parsed_info["job_id"]
                platform = parsed_info["platform"]
                view_url = parsed_info["normalized_url"]
                
                try:
                    page = browser.new_page()
                    if stealth_sync:
                        stealth_sync(page)
                        
                    if platform == "linkedin":
                        job = J.Job(job_id=job_id, title="role", company="company", location="", url=view_url)
                        text = J.capture_jd(page, job)
                        title, company = _extract_title_company(page)
                        job.title = title or job.title
                        job.company = company or job.company
                    elif platform == "fraunhofer":
                        from engine.fraunhofer import jobs as FJ
                        job = J.Job(job_id=job_id, title="role", company="company", location="", url=view_url)
                        text = FJ.capture_jd(page, job)
                        job.title = FJ._title_from_url(view_url) or job.title
                        job.company = "Fraunhofer"
                    else:
                        page.goto(view_url, wait_until="domcontentloaded")
                        try:
                            page.wait_for_load_state("networkidle", timeout=5000)
                        except Exception:
                            pass
                        text = page.inner_text("body")
                        
                        page_title = page.title() or ""
                        job_title = "role"
                        company_name = platform.capitalize()
                        
                        if page_title:
                            parts = re.split(r'\s+[-|]\s+', page_title)
                            if parts:
                                job_title = parts[0].strip()
                                if len(parts) > 1:
                                    company_name = parts[1].strip()
                                    
                        job = J.Job(job_id=job_id, title=job_title, company=company_name, location="", url=view_url)
                    
                    captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
                    slug = J.slugify(job.company, job.title, job.job_id)
                    write_path = J.write_jd(job, text, out_dir, captured_at, source=platform)
                    
                    captured_slugs.append(slug)
                    worker_logs.append(f"Successfully captured {slug}")
                    
                    page.close()
                except Exception as e:
                    worker_logs.append(f"WARNING: Capture failed for {url}: {str(e)}")
                    continue
        finally:
            browser.close()
    return captured_slugs, worker_logs


def _capture_jobs_process_worker(q, urls_to_capture):
    import sys
    import os
    # Redirect standard input/output to protect the parent MCP server's stdio channel, keeping stderr for tracebacks
    sys.stdin = open(os.devnull, "r")
    sys.stdout = open(os.devnull, "w")

    try:
        slugs, w_logs = _capture_jobs_worker_func(urls_to_capture)
        q.put((True, slugs, w_logs))
    except Exception as e:
        q.put((False, e, []))


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

    # Slice the URLs list to our limit so we don't try to crawl hundreds of postings sequentially
    active_urls = urls
    if len(active_urls) > limit:
        logs.append(f"Slicing to first {limit} URLs to respect limit.")
        active_urls = active_urls[:limit]

    # 2. Capture Job Descriptions via Playwright Session (Anonymous and Headless in isolated Process)
    import multiprocessing

    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_capture_jobs_process_worker, args=(q, active_urls))
    p.start()
    success, result_slugs, worker_logs = q.get()
    p.join()
    
    logs.extend(worker_logs)
    if not success:
        raise result_slugs  # Re-raise the exception
        
    captured_slugs = result_slugs

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
            source=slug, slug=slug, provider=None, model=None,
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
        args_push = argparse.Namespace(slug="push", state=None)
        cli.cmd_status(args_push)
        logs.append("Successfully synchronized application sheets!")
    except Exception as e:
        logs.append(f"WARNING: Sheets sync failed: {str(e)}")

    logs.append("=== Gmail Ingest Pipeline Complete ===")
    return "\n".join(logs)


def extract_job_metadata_from_body(body: str, url: str) -> dict:
    """Attempt to parse company, role, and a brief description for a job URL in the email body."""
    parsed_url = parse_and_normalize_job_url(url)
    platform = parsed_url["platform"] if parsed_url else "other"
    job_id = parsed_url["job_id"] if parsed_url else "unknown"
    
    company = "Unknown"
    role = "Unknown"
    brief_description = "Job found in alert email."
    
    idx = body.find(url)
    if idx != -1:
        # Get a window of text before the URL (e.g., 200 characters)
        start = max(0, idx - 200)
        window = body[start:idx]
        
        # Look for clean lines in this window
        lines = [line.strip() for line in window.split("\n") if line.strip()]
        if lines:
            rev = list(reversed(lines))
            if len(rev) >= 3:
                role = rev[2]
                company = rev[1]
                brief_description = f"{role} at {company} ({rev[0]})"
            elif len(rev) == 2:
                role = rev[1]
                company = rev[0]
                brief_description = f"{role} at {company}"
            elif len(rev) == 1:
                role = rev[0]
                brief_description = f"Job listing: {role}"
                
    # Clean up any HTML tags or weird characters from the extracted text
    def clean(text):
        t = re.sub(r'<[^>]+>', '', text)  # remove HTML tags
        t = re.sub(r'\s+', ' ', t).strip()  # normalize whitespace
        return t
        
    return {
        "job_id": job_id,
        "company": clean(company),
        "role": clean(role),
        "job_url": url,
        "brief_description": clean(brief_description)
    }


def list_gmail_jobs_workflow(provider: str, query: str = "is:unread", limit: int = 10) -> str:
    """Modular workflow to search Gmail alerts for a provider and return a lightweight list of discovered jobs."""
    import json
    from engine.config import resolve_search
    from engine import gmail
    
    try:
        cfg = resolve_search()
        email = cfg["gmail_alerts"][provider]
    except (KeyError, Exception):
        email = f"jobalerts-noreply@{provider}.com"
        
    full_query = f"from:{email}"
    if query:
        if "from:" in query:
            full_query = query
        else:
            full_query = f"from:{email} {query}"
            
    try:
        threads = gmail.search_emails(full_query, limit, include_bodies=True)
    except Exception as e:
        log.exception(f"Gmail search failed for provider {provider}")
        return json.dumps({"error": f"Gmail search failed: {str(e)}"})
        
    results = []
    seen_urls = set()
    
    for t in threads:
        for m in t.get("messages", []):
            body = m.get("body", "")
            for url in extract_urls_from_text(body):
                if url not in seen_urls:
                    seen_urls.add(url)
                    meta = extract_job_metadata_from_body(body, url)
                    results.append(meta)
                    if len(results) >= limit:
                        break
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break
            
    return json.dumps(results)


def extract_job_details_workflow(url: str) -> str:
    """Modular workflow to crawl a single job posting URL, extract details, and save to database."""
    import multiprocessing
    
    parsed_info = parse_and_normalize_job_url(url)
    if parsed_info is None:
        return f"ERROR: Invalid or non-job URL: {url}"
        
    norm_url = parsed_info["normalized_url"]
    
    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_capture_jobs_process_worker, args=(q, [norm_url]))
    p.start()
    success, result_slugs, worker_logs = q.get()
    p.join()
    
    if not success:
        if isinstance(result_slugs, Exception):
            return f"ERROR: Capture failed: {str(result_slugs)}"
        return f"ERROR: Capture failed: {result_slugs}"
        
    if not result_slugs:
        return "ERROR: Scraper failed to capture job details."
        
    slug = result_slugs[0]
    return f"SUCCESS: Captured job with slug '{slug}' and saved to database."


def create_application_from_job_workflow(slug: str) -> str:
    """Modular workflow to generate tailored application documents (CV/CL) for a specific job slug,
    compile them into PDFs, upload them to Google Drive, and sync tracking statuses."""
    import argparse
    from engine import cli
    
    logs = [f"=== Processing application tailoring for: {slug} ==="]
    
    # 1. Generate tailored markdown docs (cv.md, cover-letter.md, etc.)
    args_new = argparse.Namespace(
        source=slug, slug=slug, provider=None, model=None,
        ollama_url=None, no_translate=False, no_save_db=False, recipient=None
    )
    try:
        cli.cmd_new(args_new)
        logs.append("  -> Successfully generated tailored cv.md and cover-letter.md")
    except Exception as e:
        log.exception(f"Tailoring generation failed for slug {slug}")
        return f"ERROR: Tailoring generation failed: {str(e)}"
        
    # 2. Render Markdown docs to PDF via LaTeX
    try:
        args_pdf = argparse.Namespace(slug=slug)
        cli.cmd_pdf(args_pdf)
        logs.append("  -> Successfully rendered PDFs via LaTeX")
    except Exception as e:
        log.exception(f"LaTeX PDF rendering failed for slug {slug}")
        return f"ERROR: PDF rendering failed: {str(e)}"
        
    # 3. Upload compiled PDFs to Google Drive
    try:
        args_upload = argparse.Namespace(slug=slug)
        cli.cmd_upload(args_upload)
        logs.append("  -> Successfully uploaded compiled PDFs to Google Drive")
    except Exception as e:
        log.exception(f"Google Drive upload failed for slug {slug}")
        return f"ERROR: Google Drive upload failed: {str(e)}"
        
    # 4. Synchronize statuses to Google Sheets
    try:
        args_push = argparse.Namespace(slug="push", state=None)
        cli.cmd_status(args_push)
        logs.append("  -> Successfully synchronized application sheets!")
    except Exception as e:
        logs.append(f"WARNING: Sheets sync skipped or failed: {str(e)}")
        
    logs.append("=== Application Tailoring Pipeline Complete ===")
    return "\n".join(logs)

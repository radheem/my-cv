import argparse
import datetime
import logging
import pathlib
import re
from engine import cli
from . import client as gmail
from engine.shared.db import get_conn

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
    from engine.domains.linkedin import jobs as J
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
                        from engine.domains.fraunhofer import jobs as FJ
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
    from engine.shared.config import resolve_search
    from . import client as gmail
    
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


def verify_markdown_documents(slug: str) -> tuple[bool, list[str]]:
    """Verify generated Markdown files are complete, non-empty, and free of placeholder artifacts."""
    from engine.cli import _jobs_dir
    from engine import documents
    import re

    app_dir = _jobs_dir() / slug
    if not app_dir.is_dir():
        return False, [f"Application directory '{app_dir}' does not exist."]

    errors = []
    required_files = ["cv.md", "cover-letter.md"]
    
    # Check optional translation files if present
    if (app_dir / "cv.de.md").exists() or (app_dir / "cover-letter.de.md").exists():
        required_files.extend(["cv.de.md", "cover-letter.de.md"])

    placeholder_patterns = [
        r"\[[Yy]our\s+[Nn]ame\]",
        r"\[[Cc]ompany\s+[Nn]ame\]",
        r"\[[Rr]ecipient\s+[Nn]ame\]",
        r"\[[Dd]ate\]",
        r"\[[Aa]ddress\]",
        r"INSERT\s+HERE",
        r"TODO",
        # German equivalents
        r"\[[Ii]hr\s+[Nn]ame\]",
        r"\[[Dd]atum\]",
        r"\[[Aa]nschrift\]",
        r"\[[Nn]ame\s+des\s+[Ee]mpf[äa]ngers\]",
        # Strict bracket uppercase (but not a markdown link)
        r"\[[A-Z_]{2,}\](?!\()"
    ]

    for fname in required_files:
        file_path = app_dir / fname
        if not file_path.exists():
            errors.append(f"Required markdown file '{fname}' is missing.")
            continue
            
        content = file_path.read_text(encoding="utf-8")
        if len(content.strip()) < 100:
            errors.append(f"Markdown file '{fname}' is empty or too short.")
            continue

        # Front-matter validation
        try:
            meta, body = documents.split_front_matter(content)
        except Exception as e:
            errors.append(f"Failed to parse front-matter for '{fname}': {str(e)}")
            body = content

        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content)
            if matches:
                errors.append(f"File '{fname}' contains placeholder artifact: {', '.join(matches)}")

    if errors:
        return False, errors
    return True, []


def generate_markdown_workflow(
    slug: str,
    variant: str | None = None,
    custom_instructions: str | None = None,
) -> str:
    """Stage 1: Generate tailored Markdown documents (CV/CL in EN and DE)."""
    import argparse
    from engine import cli

    args_new = argparse.Namespace(
        source=slug, slug=slug, provider=None, model=None,
        ollama_url=None, no_translate=False, no_save_db=False, recipient=None,
        variant=variant, instructions=custom_instructions
    )
    try:
        cli.cmd_new(args_new)
        return f"SUCCESS: Tailored markdown cv.md and cover-letter.md generated for {slug}."
    except Exception as e:
        log.exception(f"Tailoring markdown generation failed for slug {slug}")
        return f"ERROR: Tailoring generation failed: {str(e)}"


def create_pdf_from_markdown_workflow(slug: str) -> str:
    """Stage 2: Verify Markdown files, compile them to PDFs, upload to Drive, and sync Sheet status."""
    import argparse
    from engine import cli

    logs = [f"=== Processing Stage 2 (PDF Compilation) for: {slug} ==="]

    # 1. Verification Step
    is_valid, verify_errors = verify_markdown_documents(slug)
    if not is_valid:
        return "ERROR: Markdown verification failed:\n" + "\n".join(f"- {err}" for err in verify_errors)

    # 2. Render Markdown to LaTeX and compile PDFs
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

    # 4. Synchronize status to Google Sheets
    try:
        args_push = argparse.Namespace(slug="push", state=None)
        cli.cmd_status(args_push)
        logs.append("  -> Successfully synchronized application sheets!")
    except Exception as e:
        logs.append(f"WARNING: Sheets sync skipped or failed: {str(e)}")

    logs.append("=== PDF Compilation Pipeline Complete ===")
    return "\n".join(logs)


def create_application_from_job_workflow(slug: str, variant: str | None = None) -> str:
    """Compose Stage 1 and Stage 2 sequentially for backward compatibility."""
    res1 = generate_markdown_workflow(slug, variant)
    if res1.startswith("ERROR"):
        return res1
    res2 = create_pdf_from_markdown_workflow(slug)
    return f"{res1}\n\n{res2}"


def generic_search_workflow(query: str, limit: int = 10, include_bodies: bool = True) -> str:
    """Modular workflow to search Gmail for any generic query terms."""
    import json
    from . import client as gmail

    try:
        threads = gmail.search_emails(query, limit, include_bodies=include_bodies)
    except Exception as e:
        log.exception(f"Gmail search failed for query '{query}'")
        return json.dumps({"error": f"Gmail search failed: {str(e)}"})

    results = []
    for t in threads:
        thread_id = t.get("id", "")
        for m in t.get("messages", []):
            msg_id = m.get("id", "")
            subject = m.get("subject", "")
            sender = m.get("from", "")
            date = m.get("date", "")
            snippet = m.get("snippet", "")
            body = m.get("body", "") if include_bodies else ""

            msg_entry = {
                "thread_id": thread_id,
                "message_id": msg_id,
                "from": sender,
                "date": date,
                "subject": subject,
                "snippet": snippet
            }
            if include_bodies:
                msg_entry["body"] = body

            results.append(msg_entry)
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    return json.dumps({"emails": results})


def check_application_updates_workflow(slug: str, limit: int = 5) -> str:
    """Lookup target application metadata from the database or filesystem, build a targeted search query, and return matching emails."""
    import json
    import datetime
    from engine.shared.db import get_conn, _get_applications_dir
    from engine import documents

    company = ""
    job_title = ""
    date_str = ""

    try:
        # 1. Try DB join first
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT j.company, j.title, j.created_at
                    FROM jobs j
                    JOIN applications a ON j.job_id = a.job_id
                    WHERE a.slug = ?
                """, (slug,))
                row = cur.fetchone()

        if row:
            company = row["company"] or ""
            created_at = row["created_at"]
            if isinstance(created_at, str):
                date_str = created_at[:10].replace("-", "/")
            elif isinstance(created_at, (datetime.datetime, datetime.date)):
                date_str = created_at.strftime("%Y/%m/%d")
            else:
                date_str = "2026/01/01"
        else:
            # 2. Fall back to filesystem markdown if DB job cache is missing
            app_dir = _get_applications_dir() / slug
            index_path = app_dir / "index.md"
            if index_path.exists():
                meta, _ = documents.split_front_matter(index_path.read_text(encoding="utf-8"))
                company = meta.get("company", "")
                job_title = meta.get("job_title", "")
                dt_found = meta.get("date_found", "")
                if dt_found:
                    # Parse YYYY-MM-DD to YYYY/MM/DD
                    date_str = str(dt_found).replace("-", "/")
                else:
                    date_str = "2026/01/01"

        if not company:
            return json.dumps({"error": f"No active application or filesystem metadata found matching slug '{slug}'."})

        company_escaped = company.replace('"', '\\"')
        query_str = f'"{company_escaped}" AND ("Application" OR "Interview" OR "Status" OR "Offer" OR "Resume" OR "CV") after:{date_str}'
        
        return generic_search_workflow(query_str, limit=limit, include_bodies=True)
    except Exception as e:
        log.exception(f"Failed to check application updates for slug: {slug}")
        return json.dumps({"error": f"Failed to check application updates: {str(e)}"})


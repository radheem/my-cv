import json
import logging
import decimal
from mcp.server.fastmcp import FastMCP
from ..shared.db import get_conn
from .sqlguard import guard_and_wrap
from ..workflows import (
    create_application_workflow,
    update_application_status_workflow,
    score_jobs_workflow,
    sync_status_to_sheets_workflow,
    list_gmail_jobs_workflow,
    extract_job_details_workflow,
    create_application_from_job_workflow,
)

log = logging.getLogger("cv-tailor-mcp")
mcp = FastMCP("cv-tailor", host="0.0.0.0", port=5000)


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder to gracefully handle PostgreSQL/psycopg data types.
    - Serializes decimal.Decimal (e.g. from AVG, SUM, numeric columns) to floats.
    - Serializes datetime/date/time objects to ISO format.
    """
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


@mcp.tool()
def cv_tailor_ontology() -> str:
    """The cv-tailor database decoder ring:
    - `jobs` table: Tracks crawled job postings, title, company, clean description, match score, source, and platform.
    - `applications` table: Tracks application status (draft, applied, interview, etc.), recipient name, Drive URLs, taxonomy classification clusters (array), and tailored English/German CV/cover letter Markdown texts.
    - FK Relationship: applications.job_id references jobs.job_id.
    Call this first to understand our tables, then compose read-only SELECT/WITH SQL queries with query()."""
    ontology = {
        "tables": {
            "jobs": {
                "description": "Tracks job descriptions, search metrics, scores, and crawling lineage.",
                "columns": {
                    "job_id": "VARCHAR(100) PRIMARY KEY (unique stable identifier; external job ID or MD5 hash fallback)",
                    "slug": "VARCHAR(255) NOT NULL (unique human-readable string, e.g. 'jobrad-platform-engineer-4426040429')",
                    "company": "VARCHAR(255) NOT NULL (company name)",
                    "title": "VARCHAR(255) NOT NULL (job title)",
                    "location": "VARCHAR(255) (job location, e.g. 'Remote')",
                    "url": "TEXT (original posting URL)",
                    "description": "TEXT (raw cleaned job description text used for scoring/tailoring)",
                    "score": "INTEGER (matching profile score calculated by score-jds.py)",
                    "applicants": "INTEGER (number of applicants if scraped)",
                    "source": "VARCHAR(50) NOT NULL ('file', 'gmail', or 'url')",
                    "platform": "VARCHAR(50) NOT NULL ('linkedin', 'glassdoor', 'fraunhofer', or 'other')",
                    "created_at": "TIMESTAMP WITH TIME ZONE (crawled timestamp)"
                }
            },
            "applications": {
                "description": "Tracks application status, drive links, taxonomy clusters, and tailored Markdown content.",
                "columns": {
                    "job_id": "VARCHAR(100) PRIMARY KEY REFERENCES jobs(job_id) ON DELETE CASCADE",
                    "slug": "VARCHAR(255) NOT NULL (human-readable string matching jobs.slug)",
                    "status": "VARCHAR(50) NOT NULL DEFAULT 'draft' ('draft', 'applied', 'interview', 'offer', 'rejected', 'withdrawn')",
                    "recipient": "VARCHAR(255) (salutation name used in cover letters)",
                    "cv_en": "TEXT (tailored English CV in markdown format)",
                    "cv_de": "TEXT (tailored German CV in markdown format)",
                    "cover_letter_en": "TEXT (tailored English cover letter in markdown format)",
                    "cover_letter_de": "TEXT (tailored German cover letter in markdown format)",
                    "drive_url": "TEXT (Google Drive directory link)",
                    "clusters": "TEXT[] (taxonomy classification clusters / tags)",
                    "updated_at": "TIMESTAMP WITH TIME ZONE (last update timestamp)"
                }
            }
        },
        "relationships": [
            {"from": "applications.job_id", "to": "jobs.job_id", "type": "foreign key (one-to-one)"}
        ]
    }
    return json.dumps(ontology)


@mcp.tool()
def query(sql: str) -> str:
    """Run a read-only SQL query (SELECT / WITH) over the cv-tailor PostgreSQL database and return the rows as JSON.
    Use this to inspect applications, search jobs, get matching scores, retrieve CVs/cover letters, etc.
    Results are capped at 1000 rows. Examples:
    - Get highest scoring unapplied jobs: SELECT slug, company, title, score FROM jobs WHERE slug NOT IN (SELECT slug FROM applications) ORDER BY score DESC LIMIT 5;
    - Count applications by status: SELECT status, COUNT(*) FROM applications GROUP BY status;
    - Retrieve tailored letters for a role: SELECT cover_letter_en, cv_en FROM applications WHERE slug = '...';"""
    try:
        wrapped = guard_and_wrap(sql)
        with get_conn() as conn:
            # Enforce read-only defense-in-depth on psycopg level
            conn.read_only = True
            with conn.cursor() as cur:
                cur.execute(wrapped)
                rows = cur.fetchall()
        return json.dumps({"rows": rows}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Query execution failed in FastMCP server")
        return json.dumps({"error": str(e)})


def _clean_html(html_content: str) -> str:
    """Helper to remove script, style, head, header, footer, nav tags, strip all HTML tags,
    unescape entities, and clean up redundant whitespace and empty lines."""
    import re
    import html

    # 1. Remove script, style, head, header, footer, nav tags and their content
    text = re.sub(r'<(script|style|head|header|footer|nav)\b[^>]*>([\s\S]*?)</\1>', '', html_content, flags=re.IGNORECASE)
    
    # 2. Replace block tags and list/table cells with line breaks or spaces
    text = re.sub(r'</?(p|div|br|h[1-6]|li|tr|th|td|blockquote)\b[^>]*>', '\n', text, flags=re.IGNORECASE)
    
    # 3. Strip all other HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # 4. Unescape HTML entities (e.g., &amp; -> &, &nbsp; -> space)
    text = html.unescape(text)
    
    # 5. Clean up redundant white spaces and empty lines
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = []
    for line in lines:
        if line:
            clean_lines.append(line)
        elif not clean_lines or clean_lines[-1] != "":
            clean_lines.append("")
    
    return "\n".join(clean_lines).strip()


@mcp.tool()
def fetch_public_job_url(url: str) -> str:
    """Step 1 (Direct Path - Generic). Download a public job description webpage's HTML and extract its clean, readable plain text.
    CRITICAL: Use this tool ONLY for generic, non-LinkedIn and non-Indeed public webpages. If you are dealing with a LinkedIn URL, you MUST extract the job ID and use the 'fetch_linkedin_job' tool instead. If you have an Indeed URL, you MUST extract the job ID and use 'fetch_indeed_job' instead. This tool bypasses heavy browser overhead and is extremely fast.
    """
    import urllib.request

    try:
        # Configure a realistic User-Agent to avoid basic bot blocks
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        # Open URL with standard 15s timeout
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")

        return _clean_html(html_content)
    except Exception as e:
        log.exception(f"Failed to fetch public URL: {url}")
        return f"ERROR: Failed to fetch public webpage: {str(e)}"


@mcp.tool()
def fetch_linkedin_job(job_id: str) -> str:
    """Step 1 (Direct Path - LinkedIn Preferred). Fetch a public LinkedIn job description's plain text by job_id.
    CRITICAL: If the user provides a LinkedIn job link (e.g. linkedin.com/jobs/view/... or linkedin.com/jobs-guest/...), DO NOT use 'fetch_public_job_url' or 'extract_job_details'. Instead, extract the 10-digit numeric job ID from the link and call this 'fetch_linkedin_job' tool immediately. It accesses the lightweight, public guest API directly and returns clean text in under 2 seconds without requiring browser automation or logging in.
    """
    import urllib.request

    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        # Configure a realistic User-Agent to avoid basic bot blocks
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        # Open URL with standard 15s timeout
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")

        return _clean_html(html_content)
    except Exception as e:
        log.exception(f"Failed to fetch LinkedIn job ID: {job_id}")
        return f"ERROR: Failed to fetch LinkedIn job: {str(e)}"


@mcp.tool()
def fetch_indeed_job(job_id: str) -> str:
    """Step 1 (Direct Path - Indeed Preferred). Fetch an Indeed job description by job_id (jk parameter).
    CRITICAL: If the user provides an Indeed job link, DO NOT use 'fetch_public_job_url'. Instead, extract the hexadecimal job ID (from the 'jk' URL parameter) and call this 'fetch_indeed_job' tool immediately. It requests Indeed's direct API view and returns pretty-printed JSON (or falls back cleanly to scraping and extracting plain text if the API is restricted). Bypasses browser CAPTCHAs.
    """
    import urllib.request
    import json

    url = f"https://de.indeed.com/viewjob?jk={job_id}"
    try:
        # Configure a realistic User-Agent to avoid basic bot blocks
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        # Open URL with standard 15s timeout
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode("utf-8", errors="ignore")

        # Try to parse response as JSON first
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # Fall back to cleaning HTML to support HTML rendering path
            return _clean_html(content)
            
    except Exception as e:
        log.exception(f"Failed to fetch Indeed job ID: {job_id}")
        return f"ERROR: Failed to fetch Indeed job: {str(e)}"


@mcp.tool()
def save_job_description(
    company: str,
    title: str,
    url: str,
    description: str,
    location: str = "Remote",
    applicants: int = None
) -> str:
    """Step 2 (Direct Path - Preferred). Save a job description directly to the database and filesystem.
    Use this tool as the primary/default way to save job postings after fetching their content 
    using fast, public tools (like fetch_public_job_url) or manual text extraction. This bypasses the browser 
    crawler completely, preventing timeouts and CAPTCHA blockages. Returns the generated job slug.
    """
    try:
        import datetime
        import hashlib
        from ..domains.linkedin.jobs import Job, write_jd, slugify

        # Compute stable hash-based job_id matching the system's URL hashing convention
        clean_url = url.strip().rstrip("/")
        job_id = hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:12]

        job = Job(
            job_id=job_id,
            title=title.strip(),
            company=company.strip(),
            location=location.strip() if location else "Remote",
            url=url.strip(),
            applicants=applicants
        )
        captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        
        # write_jd handles database upsert AND local backup file writing
        write_jd(job, description, "vault/jds", captured_at, source="manual")
        
        # Generate the slug
        slug = slugify(job.company, job.title, job.job_id)
        
        return f"SUCCESS: Job saved with slug '{slug}'."
    except Exception as e:
        log.exception("Failed to save job description directly")
        return f"ERROR: Failed to save job description: {str(e)}"


@mcp.tool()
def list_gmail_linkedin_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Step 1 (Gmail Alerts Discovery - LinkedIn). Scan unread Gmail search alerts from LinkedIn and return a lightweight list of newly discovered jobs.
    Use this to pull newly received opportunities into your processing pipeline. To extract the job description text afterward, extract the job_id from the return values and pass it directly to the 'fetch_linkedin_job' tool.
    """
    return list_gmail_jobs_workflow("linkedin", query, limit)


@mcp.tool()
def list_gmail_glassdoor_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Step 1 (Gmail Alerts Discovery - Glassdoor). Scan unread Gmail search alerts from Glassdoor and return a lightweight list of newly discovered jobs.
    Use this to pull newly received opportunities into your processing pipeline. To extract the job description text afterward, use the returned job_url with the 'fetch_public_job_url' tool.
    """
    return list_gmail_jobs_workflow("glassdoor", query, limit)


@mcp.tool()
def list_gmail_indeed_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Step 1 (Gmail Alerts Discovery - Indeed). Scan unread Gmail search alerts from Indeed and return a lightweight list of newly discovered jobs.
    Use this to pull newly received opportunities into your processing pipeline. To extract the job description text afterward, extract the 'jk' parameter (job_id) from the returned job_url and pass it directly to the 'fetch_indeed_job' tool.
    """
    return list_gmail_jobs_workflow("indeed", query, limit)


@mcp.tool()
def list_gmail_fraunhofer_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Step 1 (Gmail Alerts Discovery - Fraunhofer). Scan unread Gmail search alerts from Fraunhofer and return a lightweight list of newly discovered jobs.
    Use this to pull newly received opportunities into your processing pipeline. To extract the job description text afterward, use the returned job_url with the 'fetch_public_job_url' tool.
    """
    return list_gmail_jobs_workflow("fraunhofer", query, limit)


@mcp.tool()
def extract_job_details(url: str) -> str:
    """Step 2 (Scraper Path - Dynamic Crawl). Launch an isolated, headless browser (Playwright) to scrape and extract the job description from a given URL.
    CRITICAL: This tool is extremely slow (20-40 seconds) and highly prone to security gates or timeouts on public pages. It should ONLY be used for protected, authenticated LinkedIn views where guest APIs are completely restricted and an active, warmed browser session is required. For all public pages, ALWAYS prefer 'fetch_linkedin_job' (for LinkedIn), 'fetch_indeed_job' (for Indeed), or 'fetch_public_job_url' (for generic links) instead, followed by 'save_job_description'.
    """
    return extract_job_details_workflow(url)


import queue
import threading

# Global serial execution queue for tailoring applications
_tailor_queue = queue.Queue()
_tailor_worker_started = False
_tailor_lock = threading.Lock()


def _tailor_consumer_worker():
    global _tailor_worker_started
    while True:
        try:
            # Block indefinitely until a job is pushed to the queue
            slug = _tailor_queue.get()
            log.info(f"Serially processing queued tailoring job for slug: {slug}")
            
            # Transition the application row status to 'generating' in the database atomically
            is_valid_task = False
            try:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE applications 
                            SET status = 'generating', updated_at = CURRENT_TIMESTAMP 
                            WHERE slug = %s AND status IN ('queued', 'failed')
                            RETURNING status
                        """, (slug,))
                        row = cur.fetchone()
                        if row:
                            is_valid_task = True
                        conn.commit()
            except Exception as e:
                log.exception(f"Failed to update status to generating for slug: {slug}")

            if not is_valid_task:
                log.info(f"Discarding redundant or duplicate queued task for slug: {slug}")
                _tailor_queue.task_done()
                continue

            # Run the actual tailoring workflow
            try:
                res = create_application_from_job_workflow(slug)
                if res.startswith("ERROR"):
                    log.error(f"Queued tailoring failed for {slug}: {res}")
                    _mark_application_failed(slug)
            except Exception as bg_e:
                log.exception(f"Queued tailoring worker crashed for slug: {slug}")
                _mark_application_failed(slug)
            finally:
                _tailor_queue.task_done()
        except Exception as e:
            log.exception("Error in global tailor consumer worker loop")
            import time
            time.sleep(1)


def _mark_application_failed(slug: str):
    try:
        with get_conn() as conn_failed:
            with conn_failed.cursor() as cur_failed:
                cur_failed.execute("""
                    UPDATE applications 
                    SET status = 'failed', updated_at = CURRENT_TIMESTAMP 
                    WHERE slug = %s
                """, (slug,))
                conn_failed.commit()
    except Exception as db_err:
        log.exception(f"Failed to mark application as failed in DB: {db_err}")


def _ensure_tailor_worker():
    global _tailor_worker_started
    with _tailor_lock:
        if not _tailor_worker_started:
            worker_thread = threading.Thread(target=_tailor_consumer_worker, name="TailorConsumerWorker")
            worker_thread.daemon = True
            worker_thread.start()
            _tailor_worker_started = True
            log.info("Initialized global FIFO queue tailor consumer worker thread.")


@mcp.tool()
def create_application_from_job(slug: str) -> str:
    """Step 3 (Tailoring & PDF Rendering Path). Generate tailored job application documents (CV/CL in English and German) for a specific job slug.
    Use this tool to trigger the tailoring pipeline. It ranks your projects/skills, calls the LLM, compiles LaTeX PDFs bilingually, uploads them to Google Drive, and syncs status back to Google Sheets. Because LLM generation and PDF compilation are resource-intensive, requests are placed in an asynchronous in-memory background FIFO queue to process sequentially. You can monitor the application state (queued -> generating -> draft) on subsequent turns by calling 'get_application'.
    """
    try:
        # 1. Check if the job exists in the database
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT job_id FROM jobs WHERE slug = %s", (slug,))
                row = cur.fetchone()
                if not row:
                    return json.dumps({"error": f"Job with slug '{slug}' not found in database. Cannot create application."})
                job_id = row["job_id"]

                # Check if an application already exists and its current status
                cur.execute("SELECT status FROM applications WHERE job_id = %s", (job_id,))
                app_row = cur.fetchone()
                if app_row:
                    status = app_row["status"]
                    if status in ("draft", "applied", "interview", "offer", "rejected", "withdrawn"):
                        return json.dumps({
                            "error": f"An application for slug '{slug}' is already finished and finalized with status '{status}'. Cannot re-enqueue application tailoring."
                        })
                    if status == "generating":
                        return json.dumps({
                            "status": "generating",
                            "slug": slug,
                            "message": "Application tailoring is already actively generating. No new action taken."
                        })
                    if status == "queued":
                        return json.dumps({
                            "status": "queued",
                            "slug": slug,
                            "message": "Application tailoring is already enqueued and waiting in line. No new action taken."
                        })

                # 2. Insert or update the application row setting status to 'queued'
                cur.execute("""
                    INSERT INTO applications (job_id, slug, status)
                    VALUES (%s, %s, 'queued')
                    ON CONFLICT (job_id) DO UPDATE SET status = 'queued', updated_at = CURRENT_TIMESTAMP
                """, (job_id, slug))
                conn.commit()

        # 3. Ensure background worker is running and push to queue
        _ensure_tailor_worker()
        _tailor_queue.put(slug)

        return json.dumps({
            "status": "queued",
            "slug": slug,
            "message": "Application tailoring has been added to the sequential background queue. You can monitor its progress by calling get_application."
        })
    except Exception as e:
        log.exception(f"Failed to queue application creation for slug: {slug}")
        return json.dumps({"error": f"Failed to queue application tailoring: {str(e)}"})


@mcp.tool()
def list_applications(status: str = None, limit: int = 20) -> str:
    """List tracked job applications from the database, excluding large text fields (CVs, cover letters) to preserve context.
    Use this tool to get a lightweight overview of active/historical applications and their current lifecycle statuses (such as draft, applied, interview, offer, rejected).
    """
    try:
        query_sql = """
            SELECT a.slug, a.status, j.company, j.title, j.score, a.updated_at
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
        """
        params = []
        if status:
            query_sql += " WHERE a.status = %s"
            params.append(status)
        query_sql += " ORDER BY a.updated_at DESC LIMIT %s"
        params.append(limit)

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query_sql, params)
                rows = cur.fetchall()
        return json.dumps({"applications": rows}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to list applications")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_application(slug: str) -> str:
    """Retrieve full details of a specific application, including tailored CVs, cover letters, and Google Drive package directory links.
    Use this tool to read completed CVs and Cover Letter markdown drafts, extract Drive directories, or monitor the status (queued, generating, draft, applied) of a requested application.
    """
    try:
        query_sql = """
            SELECT a.slug, a.status, a.recipient, a.cv_en, a.cv_de, a.cover_letter_en, a.cover_letter_de, a.drive_url, a.clusters, a.updated_at,
                   j.company, j.title, j.location, j.url, j.score, j.created_at
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.slug = %s
        """
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query_sql, (slug,))
                row = cur.fetchone()
        if not row:
            return json.dumps({"error": f"Application with slug '{slug}' not found."})
        return json.dumps({"application": row}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to get application")
        return json.dumps({"error": str(e)})


@mcp.tool()
def list_jobs(unapplied_only: bool = True, limit: int = 20) -> str:
    """List crawled job postings from the database, excluding massive raw description text.
    Set unapplied_only to True to see jobs that do not have applications yet, sorted by match score."""
    try:
        if unapplied_only:
            query_sql = """
                SELECT slug, company, title, location, score, platform, created_at
                FROM jobs
                WHERE job_id NOT IN (SELECT job_id FROM applications)
                ORDER BY score DESC, created_at DESC LIMIT %s
            """
        else:
            query_sql = """
                SELECT slug, company, title, location, score, platform, created_at
                FROM jobs
                ORDER BY created_at DESC LIMIT %s
            """
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query_sql, (limit,))
                rows = cur.fetchall()
        return json.dumps({"jobs": rows}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to list jobs")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_job(slug: str) -> str:
    """Retrieve full details of a specific job posting, including the complete raw job description text."""
    try:
        query_sql = """
            SELECT slug, job_id, company, title, location, url, description, score, applicants, source, platform, created_at
            FROM jobs
            WHERE slug = %s
        """
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query_sql, (slug,))
                row = cur.fetchone()
        if not row:
            return json.dumps({"error": f"Job with slug '{slug}' not found."})
        return json.dumps({"job": row}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to get job")
        return json.dumps({"error": str(e)})


@mcp.tool()
def delete_job(slug: str) -> str:
    """Soft-delete a job posting from the database. Sets status to 'deleted' and releases unique constraints on the job's ID and slug, allowing identical future JDs to be re-captured successfully."""
    try:
        import time
        with get_conn() as conn:
            with conn.cursor() as cur:
                # 1. Fetch current job_id to ensure it exists and has not been deleted yet
                cur.execute("SELECT job_id, status FROM jobs WHERE slug = %s", (slug,))
                row = cur.fetchone()
                if not row:
                    return json.dumps({"error": f"Job with slug '{slug}' not found or already deleted."})
                
                job_id, current_status = row["job_id"], row["status"]
                if current_status == "deleted":
                    return json.dumps({"message": f"Job '{slug}' is already soft-deleted."})

                # 2. Append timestamped suffix to avoid primary key/unique constraint collisions on future crawls
                suffix = f"-deleted-{int(time.time())}"
                new_job_id = job_id + suffix
                new_slug = slug + suffix

                # 3. Clean up any associated application row first to satisfy FK dependencies
                cur.execute("DELETE FROM applications WHERE job_id = %s", (job_id,))

                # 4. Soft delete the job and apply suffixes to release unique constraints
                cur.execute("""
                    UPDATE jobs 
                    SET job_id = %s, slug = %s, status = 'deleted' 
                    WHERE job_id = %s
                """, (new_job_id, new_slug, job_id))
                conn.commit()

        return f"SUCCESS: Job '{slug}' has been soft-deleted. Suffix applied to release constraints."
    except Exception as e:
        log.exception(f"Failed to delete job: {slug}")
        return f"ERROR: Failed to delete job: {str(e)}"


@mcp.tool()
def search_jobs(keywords: str, limit: int = 10) -> str:
    """Search crawled job postings using keyword matching on job title, company name, or description."""
    try:
        query_sql = """
            SELECT slug, company, title, location, score, platform, created_at
            FROM jobs
            WHERE title ILIKE %s OR company ILIKE %s OR description ILIKE %s
            ORDER BY score DESC, created_at DESC LIMIT %s
        """
        pattern = f"%{keywords}%"
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query_sql, (pattern, pattern, pattern, limit))
                rows = cur.fetchall()
        return json.dumps({"results": rows}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to search jobs")
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_application(source: str) -> str:
    """Generate a tailored application (CV + Cover Letter in EN/DE) for a specific job source.
    `source` can be a URL, a local file path, or an existing job slug."""
    return create_application_workflow(source)


@mcp.tool()
def update_application_status(slug: str, status: str) -> str:
    """Update the lifecycle status of an application.
    Valid statuses: draft, applied, interview, offer, rejected, withdrawn."""
    return update_application_status_workflow(slug, status)


@mcp.tool()
def sync_status_to_sheets() -> str:
    """Push all database application statuses and metadata to Google Sheets."""
    return sync_status_to_sheets_workflow()


@mcp.tool()
def score_jobs(top: int = 10) -> str:
    """Score all unapplied job descriptions in the database against the user's profile and return the top matches."""
    return score_jobs_workflow(top)


@mcp.tool()
def initialize_agent_session() -> str:
    """Step 0 (Handshake & Core Context). Welcome, frame, and initialize the agent session.
    CRITICAL: This tool MUST be called on your very first turn in every session. It serves as the 'Init Handshake' and returns a unified context package containing:
    1. Operational Mental Model: The strict rules of the 'Ingestion Ingest Trilogy', fetching selection guidelines, and the asynchronous FIFO queue behavior.
    2. User Profile: Factual personal details loaded from 'data/profile.yml'.
    3. Master CV: Full written career history loaded from 'data/master-cv.md'.
    4. Operational Insights: Best practices regarding delays, rate limits, and troubleshooting.
    This collapses multiple rounds of context querying into exactly one call, saving significant API token usage and preventing operational mistakes.
    """
    try:
        import pathlib
        import yaml
        
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        
        # 1. Load User Profile
        profile_path = root / "data" / "profile.yml"
        profile_data = {}
        if profile_path.exists():
            profile_data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            
        # 2. Load Master CV
        cv_path = root / "data" / "master-cv.md"
        cv_data = ""
        if cv_path.exists():
            cv_data = cv_path.read_text(encoding="utf-8")
            
        # 3. Load Operational Insights
        insights_path = root / "data" / "guides" / "mcp-insights.md"
        insights_data = ""
        if insights_path.exists():
            insights_data = insights_path.read_text(encoding="utf-8")

        # 4. Construct unified payload
        payload = {
            "welcome_message": "Welcome to the cv-tailor workspace. Your operational instructions and the user's factual portfolio have been successfully loaded below.",
            
            "operational_mental_model": {
                "3step_ingestion_trilogy_workflow": {
                    "Step 1: Discover": "Use gmail alert searchers ('list_gmail_*_jobs') to pull unread alert emails and obtain raw links.",
                    "Step 2: Fetch & Save": "Extract job IDs and fetch postings with dedicated fast guest fetchers, then save with 'save_job_description' to obtain the job slug.",
                    "Step 3: Tailor": "Call 'create_application_from_job' with the job slug to enqueue asynchronous tailoring."
                },
                "strict_fetching_tool_selection_rules": {
                    "LinkedIn job URLs": "Identify the 10-digit job ID and call 'fetch_linkedin_job' immediately. DO NOT use generic or heavy scraper tools.",
                    "Indeed job URLs": "Identify the hexadecimal 'jk' parameter and call 'fetch_indeed_job' immediately. DO NOT use generic tools.",
                    "Other public URLs": "Call 'fetch_public_job_url' to download and clean the page text.",
                    "Protected/Authenticated LinkedIn pages": "Call 'extract_job_details' (Playwright headless crawler) ONLY as a last resort when public views are completely restricted."
                },
                "asynchronous_tailoring_sequential_queue": "Application generation (Step 3) is resource-intensive. It is enqueued asynchronously and processed serially, returning status 'queued' immediately. You MUST call 'get_application' on subsequent turns to monitor the status transition (queued -> generating -> draft) before presenting the results to the user."
            },
            
            "user_profile": profile_data,
            "master_cv": cv_data,
            "operational_insights": insights_data
        }
        return json.dumps(payload, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to initialize agent session")
        return json.dumps({"error": f"Failed to initialize agent session: {str(e)}"})


@mcp.tool()
def get_user_projects() -> str:
    """Retrieve the user's projects as parsed JSON (from data/projects.yml), detailing their technical portfolio."""
    try:
        import pathlib
        import yaml
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        projects_path = root / "data" / "projects.yml"
        if not projects_path.exists():
            return json.dumps({"error": "Projects file not found at data/projects.yml"})
        data = yaml.safe_load(projects_path.read_text(encoding="utf-8"))
        return json.dumps(data, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to load user projects")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_cv_guide() -> str:
    """Retrieve the comprehensive tactical CV writing guidelines in markdown format (from data/guides/how-to-write-a-cv.md) including bullet point formulation and layout rules."""
    try:
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        cv_guide_path = root / "data" / "guides" / "how-to-write-a-cv.md"
        if not cv_guide_path.exists():
            return "ERROR: CV writing guide not found at data/guides/how-to-write-a-cv.md"
        return cv_guide_path.read_text(encoding="utf-8")
    except Exception as e:
        log.exception("Failed to load CV guide")
        return f"ERROR: Failed to load CV guide: {str(e)}"


@mcp.tool()
def get_cover_letter_guide() -> str:
    """Retrieve tactical cover letter writing guidelines in markdown format (from data/guides/how-to-write-a-cover-letter.md) including structural paragraph and tone rules."""
    try:
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        cover_guide_path = root / "data" / "guides" / "how-to-write-a-cover-letter.md"
        if not cover_guide_path.exists():
            return "ERROR: Cover letter guide not found at data/guides/how-to-write-a-cover-letter.md"
        return cover_guide_path.read_text(encoding="utf-8")
    except Exception as e:
        log.exception("Failed to load cover letter guide")
        return f"ERROR: Failed to load cover letter guide: {str(e)}"


def main():
    import os
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()

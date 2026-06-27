import json
import logging
import decimal
from mcp.server.fastmcp import FastMCP
from ..db import get_conn
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


@mcp.tool()
def fetch_public_job_url(url: str) -> str:
    """Step 1 (Direct Path - Preferred). Download a public webpage's HTML and extract its clean, readable plain text.
    Use this tool on public job links to retrieve their description text without using heavy browser scrapers.
    """
    import re
    import html
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
    except Exception as e:
        log.exception(f"Failed to fetch public URL: {url}")
        return f"ERROR: Failed to fetch public webpage: {str(e)}"


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
        from ..linkedin.jobs import Job, write_jd, slugify

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
    """Step 1 of the job application workflow. Search Gmail alerts from LinkedIn and return a lightweight list of discovered jobs containing tentative job_id, company, role, job_url, and brief_description. Use the returned `job_url` with the `extract_job_details` tool."""
    return list_gmail_jobs_workflow("linkedin", query, limit)


@mcp.tool()
def list_gmail_glassdoor_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Step 1 of the job application workflow. Search Gmail alerts from Glassdoor and return a lightweight list of discovered jobs containing tentative job_id, company, role, job_url, and brief_description. Use the returned `job_url` with the `extract_job_details` tool."""
    return list_gmail_jobs_workflow("glassdoor", query, limit)


@mcp.tool()
def list_gmail_indeed_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Step 1 of the job application workflow. Search Gmail alerts from Indeed and return a lightweight list of discovered jobs containing tentative job_id, company, role, job_url, and brief_description. Use the returned `job_url` with the `extract_job_details` tool."""
    return list_gmail_jobs_workflow("indeed", query, limit)


@mcp.tool()
def extract_job_details(url: str) -> str:
    """Step 2 (Scraper Path). Execute Playwright scraper in an isolated process to extract the full job description from a given URL and save the completed record into the PostgreSQL database.
    WARNING: This tool launches a full headless browser and is only useful when there is an active, warm logged-in LinkedIn session to bypass login walls. It is prone to timeouts and CAPTCHAs on public/unauthenticated pages. For public links, prefer fetching content via 'fetch_public_job_url' and saving via 'save_job_description'.
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
            
            # Transition the application row status to 'generating' in the database
            try:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE applications 
                            SET status = 'generating', updated_at = CURRENT_TIMESTAMP 
                            WHERE slug = %s
                        """, (slug,))
                        conn.commit()
            except Exception as e:
                log.exception(f"Failed to update status to generating for slug: {slug}")

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
    """Step 3 of the job application workflow. Generate tailored job application documents (CV/CL in English and German) for a specific job slug (obtained from `extract_job_details`), render them to PDFs, upload them to Google Drive, and synchronize application status."""
    try:
        # 1. Check if the job exists in the database
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT job_id FROM jobs WHERE slug = %s", (slug,))
                row = cur.fetchone()
                if not row:
                    return json.dumps({"error": f"Job with slug '{slug}' not found in database. Cannot create application."})
                job_id = row["job_id"]

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
    """List tracked job applications from the database, excluding large text fields (CVs, cover letters).
    Use status (e.g. 'draft', 'applied', 'interview', 'rejected') to filter results."""
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
    """Retrieve full details of a specific application, including tailored CVs, cover letters, and Drive links."""
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
def get_user_profile() -> str:
    """Retrieve the user's complete profile as parsed JSON (from data/profile.yml), including contact info and narrative."""
    try:
        import pathlib
        import yaml
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        profile_path = root / "data" / "profile.yml"
        if not profile_path.exists():
            return json.dumps({"error": "Profile file not found at data/profile.yml"})
        data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
        return json.dumps(data, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to load user profile")
        return json.dumps({"error": str(e)})


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
def get_master_cv() -> str:
    """Retrieve the user's canonical Master CV in raw Markdown format (from data/master-cv.md) containing full career history."""
    try:
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        cv_path = root / "data" / "master-cv.md"
        if not cv_path.exists():
            return "ERROR: Master CV file not found at data/master-cv.md"
        return cv_path.read_text(encoding="utf-8")
    except Exception as e:
        log.exception("Failed to load master CV")
        return f"ERROR: Failed to load master CV: {str(e)}"


@mcp.tool()
def get_mcp_workflows() -> str:
    """Retrieve the supported system ingestion and application creation flowcharts and comparison matrix in markdown format (from docs/mcp-workflows.md)."""
    try:
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        workflows_path = root / "docs" / "mcp-workflows.md"
        if not workflows_path.exists():
            return "ERROR: Workflows documentation file not found at docs/mcp-workflows.md"
        return workflows_path.read_text(encoding="utf-8")
    except Exception as e:
        log.exception("Failed to load workflows documentation")
        return f"ERROR: Failed to load workflows documentation: {str(e)}"


@mcp.tool()
def get_mcp_insights() -> str:
    """Retrieve operational best practices and troubleshooting insights in markdown format (from data/guides/mcp-insights.md), such as pacing, delays, session warming, and timeout handling."""
    try:
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        insights_path = root / "data" / "guides" / "mcp-insights.md"
        if not insights_path.exists():
            return "ERROR: Operational insights guide not found at data/guides/mcp-insights.md"
        return insights_path.read_text(encoding="utf-8")
    except Exception as e:
        log.exception("Failed to load operational insights")
        return f"ERROR: Failed to load operational insights: {str(e)}"


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

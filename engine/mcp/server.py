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
def list_gmail_jobs(provider: str, query: str = "is:unread", limit: int = 10) -> str:
    """Search Gmail alerts from a specified provider (e.g. 'linkedin', 'glassdoor', 'indeed') and return a lightweight list of discovered jobs containing tentative job_id, company, role, job_url, and brief_description."""
    return list_gmail_jobs_workflow(provider, query, limit)


@mcp.tool()
def extract_job_details(url: str) -> str:
    """Execute Playwright scraper in an isolated process to extract the full job description from a given URL and save the completed record into the PostgreSQL database jobs table."""
    return extract_job_details_workflow(url)


@mcp.tool()
def create_application_from_job(slug: str) -> str:
    """Generate tailored job application documents (CV/CL in English and German) for a specific job slug, render them to PDFs, upload them to Google Drive, and synchronize application status."""
    return create_application_from_job_workflow(slug)


@mcp.tool()
def search_gmail_linkedin_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Search Gmail for LinkedIn job alerts from the configured email address and return a lightweight JSON list
    of matching message headers, subjects, and snippets without running crawlers or database mutations."""
    try:
        from ..config import resolve_search
        from .. import gmail
        cfg = resolve_search()
        email = cfg["gmail_alerts"]["linkedin"]
        full_query = f"from:{email}"
        if query:
            if "from:" in query:
                full_query = query
            else:
                full_query = f"from:{email} {query}"

        threads = gmail.search_emails(full_query, limit, include_bodies=True)
        results = []
        for t in threads:
            if not isinstance(t, dict):
                continue
            thread_id = t.get("id") or t.get("threadId") or ""
            messages = []
            for m in t.get("messages", []):
                if not isinstance(m, dict):
                    continue
                messages.append({
                    "id": m.get("id"),
                    "sender": m.get("sender"),
                    "subject": m.get("subject") or t.get("subject"),
                    "date": m.get("date"),
                    "snippet": m.get("snippet", m.get("body", ""))[:200]
                })
            results.append({
                "thread_id": thread_id,
                "messages": messages
            })
        return json.dumps({"threads": results}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to search LinkedIn Gmail alerts")
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_gmail_glassdoor_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Search Gmail for Glassdoor job alerts from the configured email address and return a lightweight JSON list
    of matching message headers, subjects, and snippets without running crawlers or database mutations."""
    try:
        from ..config import resolve_search
        from .. import gmail
        cfg = resolve_search()
        email = cfg["gmail_alerts"]["glassdoor"]
        full_query = f"from:{email}"
        if query:
            if "from:" in query:
                full_query = query
            else:
                full_query = f"from:{email} {query}"

        threads = gmail.search_emails(full_query, limit, include_bodies=True)
        results = []
        for t in threads:
            if not isinstance(t, dict):
                continue
            thread_id = t.get("id") or t.get("threadId") or ""
            messages = []
            for m in t.get("messages", []):
                if not isinstance(m, dict):
                    continue
                messages.append({
                    "id": m.get("id"),
                    "sender": m.get("sender"),
                    "subject": m.get("subject") or t.get("subject"),
                    "date": m.get("date"),
                    "snippet": m.get("snippet", m.get("body", ""))[:200]
                })
            results.append({
                "thread_id": thread_id,
                "messages": messages
            })
        return json.dumps({"threads": results}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to search Glassdoor Gmail alerts")
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_gmail_indeed_jobs(query: str = "is:unread", limit: int = 10) -> str:
    """Search Gmail for Indeed job alerts from the configured email address and return a lightweight JSON list
    of matching message headers, subjects, and snippets without running crawlers or database mutations."""
    try:
        from ..config import resolve_search
        from .. import gmail
        cfg = resolve_search()
        email = cfg["gmail_alerts"]["indeed"]
        full_query = f"from:{email}"
        if query:
            if "from:" in query:
                full_query = query
            else:
                full_query = f"from:{email} {query}"

        threads = gmail.search_emails(full_query, limit, include_bodies=True)
        results = []
        for t in threads:
            if not isinstance(t, dict):
                continue
            thread_id = t.get("id") or t.get("threadId") or ""
            messages = []
            for m in t.get("messages", []):
                if not isinstance(m, dict):
                    continue
                messages.append({
                    "id": m.get("id"),
                    "sender": m.get("sender"),
                    "subject": m.get("subject") or t.get("subject"),
                    "date": m.get("date"),
                    "snippet": m.get("snippet", m.get("body", ""))[:200]
                })
            results.append({
                "thread_id": thread_id,
                "messages": messages
            })
        return json.dumps({"threads": results}, cls=CustomEncoder)
    except Exception as e:
        log.exception("Failed to search Indeed Gmail alerts")
        return json.dumps({"error": str(e)})


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


def main():
    import os
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()

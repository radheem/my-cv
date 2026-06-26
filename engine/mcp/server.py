import json
import logging
import decimal
from mcp.server.fastmcp import FastMCP
from ..db import get_conn
from .sqlguard import guard_and_wrap

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
    - FK Relationship: applications.slug references jobs.slug.
    Call this first to understand our tables, then compose read-only SELECT/WITH SQL queries with query()."""
    ontology = {
        "tables": {
            "jobs": {
                "description": "Tracks job descriptions, search metrics, scores, and crawling lineage.",
                "columns": {
                    "slug": "VARCHAR(255) PRIMARY KEY (unique identifier, e.g., 'jobrad-platform-engineer-4426040429')",
                    "job_id": "VARCHAR(100) UNIQUE (external job ID from LinkedIn, Fraunhofer, etc.)",
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
                    "slug": "VARCHAR(255) PRIMARY KEY REFERENCES jobs(slug) ON DELETE CASCADE",
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
            {"from": "applications.slug", "to": "jobs.slug", "type": "foreign key (one-to-one)"}
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


def main():
    import os
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()

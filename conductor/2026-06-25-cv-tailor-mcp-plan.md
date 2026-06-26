# cv-tailor PostgreSQL MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a secure, psycopg-native FastMCP server that exposes cv-tailor's PostgreSQL schema and open query surface.

**Architecture:** We will create `engine/mcp/sqlguard.py` (query safety checks) and `engine/mcp/server.py` (ontology and open query tools). We will define the console entrypoint `cv-tailor-mcp` in `pyproject.toml` and write automated tests verifying safety and execution.

**Tech Stack:** FastMCP (mcp[cli]), Python, psycopg, pytest.

---

### Task 1: Dependencies and Safety Guard (`engine/mcp/sqlguard.py`)

**Files:**
- Modify: `pyproject.toml`
- Create: `engine/mcp/__init__.py`
- Create: `engine/mcp/sqlguard.py`
- Create: `tests/test_mcp_sqlguard.py`

- [ ] **Step 1.1: Add dependencies to pyproject.toml**
  Open `pyproject.toml` and add the `mcp` extra group:
```toml
mcp = [
    "mcp[cli]>=1.2.0",
]
```
  Run: `uv sync --all-extras`

- [ ] **Step 1.2: Implement `sqlguard.py`**
  Create directory `engine/mcp` and create `engine/mcp/__init__.py` (empty) and `engine/mcp/sqlguard.py`:

```python
import re

_SELECT_RE = re.compile(r"(?is)^\s*(with|select)\b")
ROW_CAP = 1000

def guard_and_wrap(sql: str, row_cap: int = ROW_CAP) -> str:
    """Validate query and wrap it read-only + row-capped."""
    s = sql.strip().rstrip(";").strip()
    if not _SELECT_RE.match(s):
        raise ValueError("only SELECT / WITH queries are allowed")
    if ";" in s:
        raise ValueError("multiple statements are not allowed")
    return f"SELECT * FROM ({s}) _q LIMIT {row_cap}"
```

- [ ] **Step 1.3: Write `test_mcp_sqlguard.py` unit tests**
  Create `tests/test_mcp_sqlguard.py` to test that `sqlguard` enforces read-only whitelists, blocks injection, and wraps subqueries correctly:

```python
import pytest
from engine.mcp.sqlguard import guard_and_wrap

def test_sqlguard_valid_queries():
    assert guard_and_wrap("SELECT * FROM jobs") == "SELECT * FROM (SELECT * FROM jobs) _q LIMIT 1000"
    assert guard_and_wrap("WITH q AS (SELECT 1) SELECT * FROM q") == "SELECT * FROM (WITH q AS (SELECT 1) SELECT * FROM q) _q LIMIT 1000"

def test_sqlguard_rejects_mutations():
    with pytest.raises(ValueError, match="only SELECT / WITH queries"):
        guard_and_wrap("INSERT INTO jobs VALUES ('nope')")
    with pytest.raises(ValueError, match="only SELECT / WITH queries"):
        guard_and_wrap("UPDATE jobs SET score = 100")
    with pytest.raises(ValueError, match="only SELECT / WITH queries"):
        guard_and_wrap("DROP TABLE jobs")

def test_sqlguard_rejects_multi_statement():
    with pytest.raises(ValueError, match="multiple statements are not allowed"):
        guard_and_wrap("SELECT * FROM jobs; DROP TABLE jobs")
```

- [ ] **Step 1.4: Run tests**
  Run: `uv run pytest tests/test_mcp_sqlguard.py -v`
  Expected: All tests PASS.

- [ ] **Step 1.5: Commit Task 1**
  ```bash
  git add pyproject.toml uv.lock engine/mcp/__init__.py engine/mcp/sqlguard.py tests/test_mcp_sqlguard.py
  git commit -m "feat(mcp): add mcp dependency and query safety guard"
  ```

---

### Task 2: FastMCP Server implementation (`engine/mcp/server.py`)

**Files:**
- Create: `engine/mcp/server.py`
- Create: `tests/test_mcp_server.py`

- [ ] **Step 2.1: Write the FastMCP server**
  Create `engine/mcp/server.py` defining the tools `cv_tailor_ontology()` and `query(sql: str)`.

```python
import json
import logging
from mcp.server.fastmcp import FastMCP
from ..db import get_conn
from .sqlguard import guard_and_wrap

log = logging.getLogger("cv-tailor-mcp")
mcp = FastMCP("cv-tailor", host="0.0.0.0", port=5000)

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
            with conn.cursor() as cur:
                cur.execute(wrapped)
                rows = cur.fetchall()
        # Convert any timestamps/arrays to standard string formats for JSON serialization
        for r in rows:
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
        return json.dumps({"rows": rows})
    except Exception as e:
        return json.dumps({"error": str(e)})

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2.2: Write `tests/test_mcp_server.py` integration tests**
  Add mock DB tests verifying tools returned values:

```python
import json
import pytest
import psycopg
from engine.db import get_conn, init_db
from engine.mcp.server import cv_tailor_ontology, query

def test_mcp_ontology():
    ont = json.loads(cv_tailor_ontology())
    assert "tables" in ont
    assert "jobs" in ont["tables"]
    assert "applications" in ont["tables"]

def test_mcp_query():
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL offline. Skipping MCP server queries integration test.")

    init_db()
    
    # Test query tool
    res = json.loads(query("SELECT COUNT(*) FROM jobs"))
    assert "rows" in res
    assert len(res["rows"]) >= 1
```

- [ ] **Step 2.3: Run tests**
  Run: `uv run pytest tests/test_mcp_server.py -v`
  Expected: All tests PASS.

- [ ] **Step 2.4: Commit Task 2**
  ```bash
  git add engine/mcp/server.py tests/test_mcp_server.py
  git commit -m "feat(mcp): implement FastMCP server and schema integration tools"
  ```

---

### Task 3: Entrypoint Registration and Makefile Integration

**Files:**
- Modify: `pyproject.toml`
- Modify: `Makefile`

- [ ] **Step 3.1: Register console script inside `pyproject.toml`**
  Under `[project.scripts]`, append the new CLI entrypoint:
```toml
cv-tailor-mcp = "engine.mcp.server:main"
```
  Run: `uv sync --all-extras` to register the script.

- [ ] **Step 3.2: Add `make mcp` target inside `Makefile`**
  Open `Makefile` and append the new target:
```makefile
.PHONY: mcp
mcp: ## Start the cv-tailor PostgreSQL MCP server
	$(UV_RUN) cv-tailor-mcp
```

- [ ] **Step 3.3: Verify Makefile help output**
  Run: `make help | grep mcp`
  Expected: Displays the target help.

- [ ] **Step 3.4: Commit Task 3**
  ```bash
  git add pyproject.toml uv.lock Makefile
  git commit -m "feat(mcp): register console entrypoint and add make target to start the server"
  ```

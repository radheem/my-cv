# Secure Tested Python Workflows MCP Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement tested python workflows under a new `engine/workflows/` directory to replace the fragile bash scripts and `subprocess` CLI call hacks inside our MCP server, ensuring type-safety, robust error isolation, and secure execution.

**Architecture:**
*   Create a clean, tested python package `engine/workflows/` with submodules for macro pipelines.
*   **`engine/workflows/application_actions.py`**: Clean programmatic wrappers for creating an application, updating status, rendering PDFs, and uploading to Google Drive using CLI subcommand entrypoints internally.
*   **`engine/workflows/gmail_ingest.py`**: Fully pythonic rewrite of `gmail-hunt.sh` executing Gmail email searches, URL regex Extractions, Playwright Captures, Scoring/Ranking, Application Generation, Rendering, Upload, and Google Sheets status synchronization entirely in Python.
*   **FastMCP Server Update (`engine/mcp/server.py`)**: Imports and directly calls these clean Python workflow functions instead of calling shell tools via `subprocess.run()`.

**Tech Stack:** Python stdlib, FastMCP, psycopg3, pytest.

---

### Task 1: Building Programmatic Action Workflows (`engine/workflows/`)

**Files:**
- Create: `engine/workflows/__init__.py`
- Create: `engine/workflows/application_actions.py`
- Create: `engine/workflows/gmail_ingest.py`
- Create: `tests/test_workflows.py`

- [ ] **Step 1.1: Create `engine/workflows/__init__.py`**
  Make the workflows folder a clean python package:
```python
from .application_actions import (
    create_application_workflow,
    update_application_status_workflow,
    score_jobs_workflow,
    sync_status_to_sheets_workflow,
)
from .gmail_ingest import run_gmail_hunt_workflow

__all__ = [
    "create_application_workflow",
    "update_application_status_workflow",
    "score_jobs_workflow",
    "sync_status_to_sheets_workflow",
    "run_gmail_hunt_workflow",
]
```

- [ ] **Step 1.2: Implement `engine/workflows/application_actions.py`**
  Write secure programmatic workflows that feed argparse-like structures directly into `engine.cli` functions, avoiding `subprocess`:

```python
import argparse
import logging
from engine import cli

log = logging.getLogger("cv-tailor-workflows")

def create_application_workflow(source: str, provider: str = "anthropic") -> str:
    """Generate a tailored application draft programmatically."""
    args = argparse.Namespace(
        source=source,
        slug=None,
        provider=provider,
        model=None,
        ollama_url=None,
        no_translate=False,
        no_save_db=False,
        recipient=None
    )
    try:
        cli.cmd_new(args)
        return f"SUCCESS: Tailored application created for {source}."
    except Exception as e:
        log.exception("create_application_workflow failed")
        return f"ERROR: Failed to create application: {str(e)}"

def update_application_status_workflow(slug: str, status: str) -> str:
    """Update application lifecycle status."""
    # Since status command resolves slug, we can parse slug or numeric ID
    try:
        resolved_slug = cli._resolve_slug(slug)
    except SystemExit as e:
        return f"ERROR: {str(e)}"
        
    args = argparse.Namespace(
        slug=resolved_slug,
        status=status,
        action=None
    )
    try:
        cli.cmd_status(args)
        return f"SUCCESS: Status updated to '{status}' for {resolved_slug}."
    except Exception as e:
        log.exception("update_application_status_workflow failed")
        return f"ERROR: {str(e)}"

def sync_status_to_sheets_workflow() -> str:
    """Push database status changes to Google Sheets."""
    args = argparse.Namespace(action="push", slug=None, status=None)
    try:
        cli.cmd_status(args)
        return "SUCCESS: Application statuses synchronized to Google Sheets."
    except Exception as e:
        log.exception("sync_status_to_sheets_workflow failed")
        return f"ERROR: {str(e)}"

def score_jobs_workflow(top: int = 10) -> str:
    """Scans and scores all unapplied jobs in the database."""
    # We can run scripts/score-jds.py natively using Python's module load or import
    # But since it's a script with an argparse parser, we can run its inner main:
    import importlib.util
    import sys
    import pathlib
    
    script_path = pathlib.Path(__file__).resolve().parent.parent.parent / "scripts" / "score-jds.py"
    spec = importlib.util.spec_from_file_location("score_jds", script_path)
    score_jds = importlib.util.module_from_spec(spec)
    sys.modules["score_jds"] = score_jds
    spec.loader.exec_module(score_jds)
    
    # Run scoring main with mocked argv
    old_argv = sys.argv
    sys.argv = ["score-jds.py", "--top", str(top)]
    try:
        # We capture printed output
        from io import StringIO
        backup = sys.stdout
        sys.stdout = StringIO()
        score_jds.main()
        output = sys.stdout.getvalue()
        sys.stdout = backup
        return output
    except Exception as e:
        log.exception("score_jobs_workflow failed")
        return f"ERROR: Scoring failed: {str(e)}"
    finally:
        sys.argv = old_argv
```

- [ ] **Step 1.3: Implement `engine/workflows/gmail_ingest.py`**
  Convert the bash-based `gmail-hunt.sh` workflow into a pure, robust Python pipeline:

```python
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
                logs.append(f"Successfully captured {result_capture['slug']}")
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
```

- [ ] **Step 1.4: Write `tests/test_workflows.py`**
  Write tests verifying that actions and scoring work without exceptions:
```python
import pytest
from engine.workflows import create_application_workflow, update_application_status_workflow, score_jobs_workflow

def test_workflow_error_isolation():
    # Make sure we isolate errors and return clear exception strings instead of crashing
    res = create_application_workflow("invalid_nonexistent_file_path_xyz.txt")
    assert "ERROR" in res

def test_workflow_status_nonexistent():
    res = update_application_status_workflow("nonexistent-slug-123", "applied")
    assert "ERROR" in res
```

- [ ] **Step 1.5: Run tests**
  Run: `uv run pytest tests/test_workflows.py -v`
  Expected: Passes cleanly.

- [ ] **Step 1.6: Commit Task 1**
  ```bash
  git add engine/workflows/ tests/test_workflows.py
  git commit -m "feat(workflows): implement programmatic macro python workflows"
  ```

---

### Task 2: FastMCP Server Actions Integration (`engine/mcp/server.py`)

**Files:**
- Modify: `engine/mcp/server.py`

- [ ] **Step 2.1: Register mutating tools in FastMCP**
  Open `engine/mcp/server.py` and import the workflows, then register them cleanly.

```python
# ... existing imports ...
from ..workflows import (
    create_application_workflow,
    update_application_status_workflow,
    score_jobs_workflow,
    sync_status_to_sheets_workflow,
    run_gmail_hunt_workflow,
)

# ... existing tools ...

@mcp.tool()
def search_gmail_alerts(filter: str = "linkedin job alert", limit: int = 10, order: str = "top") -> str:
    """Search Gmail for job alerts, capture the job postings, rank them, and store them in the database.
    This triggers the full ingest pipeline (fetch -> score -> db)."""
    return run_gmail_hunt_workflow(filter, limit, order)

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
```

- [ ] **Step 2.2: Verify suite passes**
  Run: `uv run pytest -v`
  Expected: All tests pass.

- [ ] **Step 2.3: Commit Task 2**
  ```bash
  git add engine/mcp/server.py
  git commit -m "feat(mcp): expose robust native python workflows to fastmcp tools"
  ```

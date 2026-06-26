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
    except (Exception, SystemExit) as e:
        log.exception("create_application_workflow failed")
        return f"ERROR: Failed to create application: {str(e)}"


def update_application_status_workflow(slug: str, status: str) -> str:
    """Update application lifecycle status."""
    try:
        resolved_slug = cli._resolve_slug(slug)
    except (Exception, SystemExit) as e:
        return f"ERROR: {str(e)}"
        
    args = argparse.Namespace(
        slug=resolved_slug,
        status=status,
        action=None
    )
    try:
        cli.cmd_status(args)
        return f"SUCCESS: Status updated to '{status}' for {resolved_slug}."
    except (Exception, SystemExit) as e:
        log.exception("update_application_status_workflow failed")
        return f"ERROR: {str(e)}"


def sync_status_to_sheets_workflow() -> str:
    """Push database status changes to Google Sheets."""
    args = argparse.Namespace(action="push", slug=None, status=None)
    try:
        cli.cmd_status(args)
        return "SUCCESS: Application statuses synchronized to Google Sheets."
    except (Exception, SystemExit) as e:
        log.exception("sync_status_to_sheets_workflow failed")
        return f"ERROR: {str(e)}"


def score_jobs_workflow(top: int = 10) -> str:
    """Scans and scores all unapplied jobs in the database."""
    import importlib.util
    import sys
    import pathlib
    
    script_path = pathlib.Path(__file__).resolve().parent.parent.parent / "scripts" / "score-jds.py"
    spec = importlib.util.spec_from_file_location("score_jds", script_path)
    score_jds = importlib.util.module_from_spec(spec)
    sys.modules["score_jds"] = score_jds
    spec.loader.exec_module(score_jds)
    
    old_argv = sys.argv
    sys.argv = ["score-jds.py", "--top", str(top)]
    try:
        from io import StringIO
        backup = sys.stdout
        sys.stdout = StringIO()
        score_jds.main()
        output = sys.stdout.getvalue()
        sys.stdout = backup
        return output
    except (Exception, SystemExit) as e:
        log.exception("score_jobs_workflow failed")
        return f"ERROR: Scoring failed: {str(e)}"
    finally:
        sys.argv = old_argv

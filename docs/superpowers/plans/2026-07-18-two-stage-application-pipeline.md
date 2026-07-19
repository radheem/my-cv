# Two-Stage Job Application Pipeline and Custom Instructions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the resource-intensive job application creation pipeline into two distinct reviewable stages (Stage 1: Markdown Generation, Stage 2: PDF Compilation & Google Drive Upload) and add support for custom instructions when tailoring cover letters and CVs.

**Architecture:** 
1. **CLI Enhancements**: Add `--instructions` parameter to `cv-tailor new` command.
2. **Dynamic Tailoring**: Update `render_cover_letter` and `render_cv` to accept and append custom user instructions directly into the LLM user prompts.
3. **Workflow Decomposition**: Split `create_application_from_job_workflow` into `generate_markdown_workflow` (Stage 1) and `create_pdf_from_markdown_workflow` (Stage 2).
4. **Markdown Validation**: Build a robust validation function `verify_markdown_documents` to check for empty files, broken YAML front-matter, and remaining LLM-generated bracketed placeholders/TODOs before compiling.
5. **Queue & MCP Server Upgrades**: Refactor the global sequential background queue `_tailor_queue` to use dict payloads, supporting `slug`, `variant`, `custom_instructions`, and `stage` (e.g. `"generate"` vs. `"compile"`). Expose the Stage 2 compilation step as a new MCP tool `create_pdf_from_markdown` and update existing tools to support `custom_instructions`.

**Tech Stack:** Python 3.11, Pydantic, Jinja2, FastMCP (MCP), Pytest.

---

## File Structure & Responsibilities

- `radr-cv/engine/cli.py`: CLI command parser configuration and `cmd_new` handler. Updated to support and parse the `--instructions` flag and forward it to downstream render engines.
- `radr-cv/engine/domains/tailoring/render.py`: Custom prompting logic for LLM-based tailoring. Updated to accept and weave `custom_instructions` at high-priority within the prompts.
- `radr-cv/engine/domains/gmail/ingest.py`: Core workflow file. Split into `generate_markdown_workflow` and `create_pdf_from_markdown_workflow` containing markdown verification checks.
- `radr-cv/engine/mcp/server.py`: FastMCP server tools and sequential consumer background thread. Refactored to coordinate the new dual-stage tasks and support `custom_instructions` parameters across creation tools.
- `radr-cv/tests/test_gmail_workflows.py`: Unit and workflow tests. Refactored to cover decomposed workflow steps.
- `radr-cv/tests/test_mcp_server.py`: MCP tool tests. Updated to test dual-stage queue parameters and custom instructions.

---

## Tasks

### Task 1: CLI and Prompt Tailoring Support for Custom Instructions

**Files:**
- Modify: `radr-cv/engine/cli.py` (around line 1250 for argument parser and line 250 for `cmd_new`)
- Modify: `radr-cv/engine/domains/tailoring/render.py` (around line 160)

- [ ] **Step 1: Write a failing test for custom instructions prompt injection**
Create a new test file `radr-cv/tests/test_custom_instructions.py` to assert that custom instructions are correctly injected into the cover letter prompt.
Run: `pytest radr-cv/tests/test_custom_instructions.py -v` (Should fail/error because parameters are missing).

- [ ] **Step 2: Implement custom instructions parameter in render_cover_letter and render_cv**
Update `radr-cv/engine/domains/tailoring/render.py`:
```python
def render_cover_letter(
    jobspec: dict[str, Any],
    tailoring: dict[str, Any],
    profile_summary: str,
    job_text: str,
    guide: str,
    availability: str = "",
    relocation: str = "",
    custom_instructions: str = "",
) -> str:
    logistics = ""
    if availability or relocation:
        logistics = (
            "Logistics to weave naturally into the close (availability / relocation / work authorization):\n"
            f"{availability}\n{relocation}\n\n"
        )
    
    custom_instr_block = ""
    if custom_instructions:
        custom_instr_block = (
            f"## Custom Focus & Tailoring Instructions (High Priority - FOLLOW STRICTLY):\n"
            f"{custom_instructions}\n\n"
        )

    user = (
        f"## Target job\nTitle: {jobspec.get('title')}\n"
        f"Company: {jobspec.get('company')}\n\n"
        f"## Job posting\n{job_text.strip()}\n\n"
        f"## Candidate summary\n{profile_summary}\n\n"
        f"## Proof points (top projects — source facts; weave a couple in, do not list)\n"
        f"{_projects_block(tailoring['top_projects'], detailed=True)}\n\n"
        f"{logistics}"
        f"{custom_instr_block}"
        f"{_cover_exemplars()}"
        f"## House guide\n{guide}\n\n"
        "Write the tailored cover letter now."
    )
    # system, _ = prompts.load("cover", _COVER_SYSTEM)
    # ...
```

- [ ] **Step 3: Update `cmd_new` argument parsing and execution**
In `radr-cv/engine/cli.py`, add the optional `--instructions` parameter to `p_new` command:
```python
p_new.add_argument("--instructions", default=None, help="Custom instructions or guidance for tailoring.")
```
And in `cmd_new(args)` extract and pass `instructions`:
```python
    instructions = getattr(args, "instructions", None) or ""
    cl_body = render.render_cover_letter(
        spec, tailoring, profile.get("summary", ""), job_text, cl_guide,
        availability=profile.get("availability", ""),
        relocation=_student_relocation(spec.get("title", ""), profile.get("relocation", "")),
        custom_instructions=instructions
    )
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest radr-cv/tests/test_custom_instructions.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**
```bash
git add radr-cv/engine/cli.py radr-cv/engine/domains/tailoring/render.py radr-cv/tests/test_custom_instructions.py
git commit -m "feat: add support for custom instructions in tailoring cover letters"
```

---

### Task 2: Decompose Ingestion Workflows into Markdown Generation and PDF Compilation

**Files:**
- Modify: `radr-cv/engine/domains/gmail/ingest.py` (lines 367-420)
- Create: Markdown verification helper functions inside `ingest.py`.

- [ ] **Step 1: Write failing tests for decomposed workflows and markdown verification**
Add tests to `radr-cv/tests/test_gmail_workflows.py` checking that `verify_markdown_documents` flags empty files, missing files, and bracketed placeholders.
Run: `pytest radr-cv/tests/test_gmail_workflows.py -v` (Should fail due to missing functions).

- [ ] **Step 2: Implement `verify_markdown_documents` verification helper**
Add to `radr-cv/engine/domains/gmail/ingest.py`:
```python
def verify_markdown_documents(slug: str) -> tuple[bool, list[str]]:
    """Verify generated Markdown files are complete, non-empty, and free of placeholder artifacts."""
    from engine.cli import _jobs_dir, _load_data
    from engine import documents
    import re

    app_dir = _jobs_dir() / slug
    if not app_dir.is_dir():
        return False, [f"Application directory '{app_dir}' does not exist."]

    errors = []
    required_files = ["cv.md", "cover-letter.md"]
    
    # Check optional translation files if present or if translation is expected
    profile, *_ = _load_data()
    # If the user has a profile or configured bilingual settings, verify de files as well
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

        # Check for bracketed placeholders / LLM-style TODO artifacts
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, body)
            if matches:
                errors.append(f"File '{fname}' contains placeholder artifact matching pattern '{pattern}': {matches}")

    if errors:
        return False, errors
    return True, []
```

- [ ] **Step 3: Refactor workflows inside `ingest.py`**
Replace `create_application_from_job_workflow` with two distinct workflows:
```python
def generate_markdown_workflow(
    slug: str,
    variant: str | None = None,
    custom_instructions: str | None = None,
) -> str:
    """Stage 1: Generate tailored Markdown documents (CV/CL in EN and DE)."""
    import argparse
    from engine import cli

    # Translate is default unless bypassed or configured otherwise
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
    from engine import cli

    logs = [f"=== Processing Stage 2 (PDF Compilation) for: {slug} ==="]

    # 1. Verification Step
    is_valid, verify_errors = verify_markdown_documents(slug)
    if not is_valid:
        return f"ERROR: Markdown verification failed:\n" + "\n".join(f"- {err}" for verify_errors in verify_errors)

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
```
Ensure `create_application_from_job_workflow` is kept (or mapped back) for compatibility during refactoring if needed, or fully replaced by these two workflows. Let's export both in `engine/workflows/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest radr-cv/tests/test_gmail_workflows.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**
```bash
git add radr-cv/engine/domains/gmail/ingest.py radr-cv/engine/workflows/__init__.py
git commit -m "feat: split application workflow into generate_markdown and create_pdf_from_markdown"
```

---

### Task 3: Expose Workflows as MCP Tools & Refactor Sequential Queue

**Files:**
- Modify: `radr-cv/engine/mcp/server.py`
- Modify: `radr-cv/engine/workflows/application_actions.py`

- [ ] **Step 1: Write a failing test for MCP tool split**
In `radr-cv/tests/test_mcp_server.py`, adjust the tests to assert that `create_application_from_job` only triggers Markdown generation and that the new `create_pdf_from_markdown` enqueues and triggers the compile stage.
Run: `pytest radr-cv/tests/test_mcp_server.py -v` (Should fail/error).

- [ ] **Step 2: Update background queue consumer to support dict payloads**
Refactor the background queue worker thread `_tailor_consumer_worker` in `radr-cv/engine/mcp/server.py` to pop dict payloads:
```python
            item = _tailor_queue.get()
            if isinstance(item, dict):
                slug = item.get("slug")
                variant_override = item.get("variant")
                custom_instructions = item.get("custom_instructions")
                stage = item.get("stage", "generate")
            else:
                # Fallback for compatibility
                if isinstance(item, tuple):
                    slug, variant_override = item
                else:
                    slug, variant_override = item, None
                custom_instructions = None
                stage = "generate"

            log.info(f"Serially processing queued tailoring task for slug: {slug} (Stage: {stage})")
```
And dispatch the appropriate workflow:
```python
            # Transition the application row status to 'generating' in the database atomically
            # (Run same database check or adapt to compile check depending on stage)
            # ...
            try:
                if stage == "generate":
                    from engine.domains.gmail.ingest import generate_markdown_workflow
                    res = generate_markdown_workflow(slug, variant_override, custom_instructions)
                elif stage == "compile":
                    from engine.domains.gmail.ingest import create_pdf_from_markdown_workflow
                    res = create_pdf_from_markdown_workflow(slug)
                else:
                    res = f"ERROR: Unsupported stage '{stage}'"
```

- [ ] **Step 3: Expose Stage 2 Tool & Update Stage 1 Tools with Custom Instructions**
In `radr-cv/engine/mcp/server.py`:
- Update `create_application_from_job(slug: str, custom_instructions: str = None)`
- Update `create_application_with_variant(slug: str, variant_filename: str, custom_instructions: str = None)`
- Expose `create_pdf_from_markdown(slug: str)`
- Update `create_application` tool wrapper:
  ```python
  @mcp.tool()
  def create_application(source: str, custom_instructions: str = None) -> str:
      """Generate a tailored application markdown CV and Cover Letter for a specific job source.
      `source` can be a URL, a local file path, or an existing job slug."""
      # Wrap and pass custom_instructions to create_application_workflow
      return create_application_workflow(source, custom_instructions)
  ```

- [ ] **Step 4: Run tests to verify everything passes**
Run: `pytest -v` (to make sure all workspace tests pass).
Expected: PASS

- [ ] **Step 5: Commit changes**
```bash
git add radr-cv/engine/mcp/server.py radr-cv/engine/workflows/application_actions.py
git commit -m "feat: expose create_pdf_from_markdown MCP tool and refactor FIFO queue"
```

---

## Plan Handoff & Selection

This plan is fully formulated and saved under `radr-cv/docs/superpowers/plans/2026-07-18-two-stage-application-pipeline.md`.

Please choose one of the following execution options:
1. **Subagent-Driven (recommended)**: I dispatch specialized subagents to complete each task sequentially, validating and reviewing at each checkpoint to keep the main conversation lean and efficient.
2. **Inline Execution**: We execute tasks task-by-task within this current conversational session with checkpoints.

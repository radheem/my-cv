# Specification: Two-Stage Job Application Pipeline & Custom Instructions

## Overview
This track splits the resource-intensive job application creation pipeline into two distinct, reviewable stages:
- **Stage 1:** Markdown Generation (CV and Cover Letter text generation via LLMs).
- **Stage 2:** PDF Compilation & Cloud Sync (LaTeX compilation to PDF, Google Drive upload, and Sheets sync).
Additionally, it introduces a `--instructions` parameter to allow users to provide custom guidance during the tailoring process.

## Functional Requirements
1. **CLI Enhancements:**
   - Add an optional `--instructions` parameter to the `cv-tailor new` command.
   - Inject the custom instructions solely into the `render_cover_letter` prompt (CV generation uses static variants for now).

2. **Workflow Decomposition:**
   - Split `create_application_from_job_workflow` into `generate_markdown_workflow` (Stage 1) and `create_pdf_from_markdown_workflow` (Stage 2).
   - Implement `verify_markdown_documents` to validate generated files before compilation.
   - Verification must flag: English placeholders (e.g., `[Your Name]`), German placeholders (e.g., `[Ihr Name]`), standard `TODO` artifacts, and any strict un-rendered bracketed uppercase text.

3. **Background Queue & State Management:**
   - Refactor the global sequential background queue `_tailor_queue` to use dictionary payloads supporting `slug`, `variant`, `custom_instructions`, and `stage` (`"generate"` vs. `"compile"`).
   - At the end of Stage 1, the worker must read the generated Markdown files from disk and atomically save their contents into the `applications` table (`cv_en`, `cv_de`, `cover_letter_en`, `cover_letter_de`) so they are instantly accessible via MCP.
   - Enqueuing Stage 2 must set the application status to a distinct `'compiling'` state (rather than resetting to `'queued'`) to cleanly differentiate it from text generation. The background worker must be updated to select rows with status `'compiling'` when looking for Stage 2 tasks.

4. **MCP Server Integration:**
   - Expose Stage 2 compilation as a new MCP tool: `create_pdf_from_markdown`.
   - Update `create_application` tools to accept and pass the `custom_instructions` parameter to Stage 1.

## Non-Functional Requirements
- **Reliability:** The queue must remain strictly sequential to prevent CPU/memory exhaustion and rate-limiting issues.
- **Data Consistency:** Database records and on-disk Markdown files must remain synchronized after Stage 1.

## Acceptance Criteria
- `cv-tailor new --instructions "..."` correctly guides the LLM for cover letter generation.
- Stage 1 generates `.md` files on disk, updates the database status to `draft`, and saves the `.md` content to the `applications` table.
- Stage 2 correctly validates the `.md` files (failing if placeholders exist), sets status to `compiling`, generates PDFs, and updates Drive/Sheets.
- Unit and end-to-end tests pass, including the updated `test_mcp_e2e_client.py` using `--no-project` to bypass workspace constraints.

## Out of Scope
- Injecting custom instructions into dynamic CV generation (`render_cv`) — this feature applies to Cover Letters only at this time.
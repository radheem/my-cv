# Implementation Plan: Gmail Workflow Restructuring

This plan follows standard practices for Python script modifications with tests. 

---

## Phase 1: Implement Modular Workflows

- [x] Task: Create `list_gmail_jobs_workflow` (cc414ad)
    - [x] Write unit tests for the new workflow verifying email fetching and URL extraction returning a lightweight list.
    - [x] Implement `list_gmail_jobs_workflow` in `engine/workflows/gmail_ingest.py` reusing existing `extract_urls_from_text` and `search_emails` logic.
- [x] Task: Create `extract_job_details_workflow` (cffeed5)
    - [x] Write unit tests verifying single-URL extraction invokes the Playwright worker and saves to DB.
    - [x] Implement `extract_job_details_workflow` leveraging `_capture_jobs_process_worker`.
- [x] Task: Create `create_application_from_job_workflow` (b2d4d29)
    - [x] Write unit tests verifying the pipeline (generation, PDF rendering, upload, and status sync) triggers successfully for a given DB slug.
    - [x] Implement `create_application_from_job_workflow`.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) (b2d4d29)

## Phase 2: Retire Monolith and Wire MCP

- [x] Task: Remove old monolithic pipeline (527933f)
    - [x] Delete `run_gmail_hunt_workflow` from `engine/workflows/gmail_ingest.py`.
    - [x] Remove tests strictly tied to the monolithic pipeline.
- [x] Task: Update MCP tools in `engine/mcp/server.py` (0899cc0)
    - [x] Replace `search_gmail_alerts` with three new MCP tools mapping to the new workflows.
    - [x] Update `tests/test_mcp_server.py` to cover the new modular tool definitions.
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) (0899cc0)
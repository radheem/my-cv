# Implementation Plan: Gmail Workflow Restructuring

This plan follows standard practices for Python script modifications with tests. 

---

## Phase 1: Implement Modular Workflows

- [ ] Task: Create `list_gmail_jobs_workflow`
    - [ ] Write unit tests for the new workflow verifying email fetching and URL extraction returning a lightweight list.
    - [ ] Implement `list_gmail_jobs_workflow` in `engine/workflows/gmail_ingest.py` reusing existing `extract_urls_from_text` and `search_emails` logic.
- [ ] Task: Create `extract_job_details_workflow`
    - [ ] Write unit tests verifying single-URL extraction invokes the Playwright worker and saves to DB.
    - [ ] Implement `extract_job_details_workflow` leveraging `_capture_jobs_process_worker`.
- [ ] Task: Create `create_application_from_job_workflow`
    - [ ] Write unit tests verifying the pipeline (generation, PDF rendering, upload, and status sync) triggers successfully for a given DB slug.
    - [ ] Implement `create_application_from_job_workflow`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Retire Monolith and Wire MCP

- [ ] Task: Remove old monolithic pipeline
    - [ ] Delete `run_gmail_hunt_workflow` from `engine/workflows/gmail_ingest.py`.
    - [ ] Remove tests strictly tied to the monolithic pipeline.
- [ ] Task: Update MCP tools in `engine/mcp/server.py`
    - [ ] Replace `search_gmail_alerts` with three new MCP tools mapping to the new workflows.
    - [ ] Update `tests/test_mcp_server.py` to cover the new modular tool definitions.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
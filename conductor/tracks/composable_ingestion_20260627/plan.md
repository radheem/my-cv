# Implementation Plan: Composable Ingestion and Application Flow

## Phase 1: Setup and Test Restructure
- [x] Task: Create isolated unit tests for new composable tools (fc0ff63)
    - [x] Write failing test `test_mcp_fetch_public_job_url` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_save_job_description` in `tests/test_mcp_server.py` verifying DB upsert and slug return.
    - [x] Update E2E test `test_mcp_3step_pipeline_e2e` to also simulate the new direct pipeline (Fetch -> Save -> Create).
    - [x] Run tests and verify they fail (Red Phase).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Test Restructure' (Protocol in workflow.md)

## Phase 2: Implement Composable MCP Tools
- [x] Task: Implement `fetch_public_job_url`
    - [x] Add `fetch_public_job_url` to `engine/mcp/server.py` using `urllib` or `requests` (with appropriate headers to avoid basic blocks).
    - [x] Ensure it strips HTML and returns clean readable text.
- [x] Task: Implement `save_job_description` (6e51490)
    - [x] Add `save_job_description` to `engine/mcp/server.py`.
    - [x] Import `write_jd` and `slugify` from `engine.linkedin.jobs`.
    - [x] Hash the URL to create a `job_id`, instantiate the `Job` object, and call `write_jd`.
    - [x] Return the generated slug.
    - [x] Run unit tests to verify they pass (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implement Composable MCP Tools' (Protocol in workflow.md)

## Phase 3: Documentation and E2E Integration
- [ ] Task: Update Tool Descriptions and Architecture Docs
    - [ ] Update `engine/mcp/server.py` docstrings to clearly contrast the "Authenticated Browser Flow" (`extract_job_details`) vs "Direct/Public Flow" (`fetch` + `save`).
    - [ ] Write the proposed Mermaid-based workflows documentation to `docs/mcp-workflows.md` detailing the composable architecture.
- [ ] Task: Final Test Verification
    - [ ] Run the full test suite (`pytest`) to guarantee no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Documentation and E2E Integration' (Protocol in workflow.md)
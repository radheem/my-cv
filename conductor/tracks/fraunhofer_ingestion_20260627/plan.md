# Implementation Plan: Fraunhofer Job Alerts MCP Tool

## Phase 1: Configuration Update
- [x] Task: Add Fraunhofer email to configuration (253f649)
    - [ ] Update `config/search.yml` to include `fraunhofer: "fraunhofer-jobnotification@noreply12.jobs2web.com"` under `gmail_alerts`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Configuration Update' (Protocol in workflow.md)

## Phase 2: MCP Tool Implementation (TDD)
- [ ] Task: Write failing test for `list_gmail_fraunhofer_jobs`
    - [ ] Add a unit test in `tests/test_mcp_server.py` that verifies the `list_gmail_fraunhofer_jobs` tool exists and calls the underlying workflow correctly.
- [ ] Task: Implement `list_gmail_fraunhofer_jobs` tool
    - [ ] Add the `@mcp.tool()` function `list_gmail_fraunhofer_jobs` to `engine/mcp/server.py`.
    - [ ] Ensure the function correctly delegates to `list_gmail_jobs_workflow("fraunhofer", query, limit)`.
- [ ] Task: Refactor and verify tests
    - [ ] Run the test suite to ensure all tests pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: MCP Tool Implementation (TDD)' (Protocol in workflow.md)
# Implementation Plan: MCP Guides and Workflows Tools

## Phase 1: Setup and Testing
- [x] Task: Create unit tests for the 4 new tools (1bdc481)
    - [x] Write failing test `test_mcp_get_mcp_workflows` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_mcp_insights` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_cv_guide` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_cover_letter_guide` in `tests/test_mcp_server.py`.
    - [x] Run tests and verify they fail (Red Phase).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Testing' (Protocol in workflow.md)

## Phase 2: Implementation
- [x] Task: Create `data/guides/mcp-insights.md`
    - [x] Write a detailed markdown guide documenting delays, scraping pacing, session warming, and timeout handling.
- [x] Task: Implement the 4 tools (253546b)
    - [x] Add `get_mcp_workflows` tool to `engine/mcp/server.py`.
    - [x] Add `get_mcp_insights` tool to `engine/mcp/server.py`.
    - [x] Add `get_cv_guide` tool to `engine/mcp/server.py`.
    - [x] Add `get_cover_letter_guide` tool to `engine/mcp/server.py`.
- [x] Task: Test Verification
    - [x] Run test suite and ensure all tests pass (Green Phase).
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Documentation and Finalization
- [x] Task: Update Runbooks (039b536)
    - [x] Update `docs/runbooks/mcp-server.md` to list the 4 new read-only tools under a new "Guides & Workflows" section.
- [x] Task: Final Test Verification
    - [x] Run the full test suite (`pytest`) to guarantee no regressions.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Documentation and Finalization' (Protocol in workflow.md)
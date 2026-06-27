# Implementation Plan: MCP Guides and Workflows Tools

## Phase 1: Setup and Testing
- [x] Task: Create unit tests for the 4 new tools (1bdc481)
    - [x] Write failing test `test_mcp_get_mcp_workflows` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_mcp_insights` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_cv_guide` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_cover_letter_guide` in `tests/test_mcp_server.py`.
    - [x] Run tests and verify they fail (Red Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Testing' (Protocol in workflow.md)

## Phase 2: Implementation
- [ ] Task: Create `data/guides/mcp-insights.md`
    - [ ] Write a detailed markdown guide documenting delays, scraping pacing, session warming, and timeout handling.
- [ ] Task: Implement the 4 tools
    - [ ] Add `get_mcp_workflows` tool to `engine/mcp/server.py`.
    - [ ] Add `get_mcp_insights` tool to `engine/mcp/server.py`.
    - [ ] Add `get_cv_guide` tool to `engine/mcp/server.py`.
    - [ ] Add `get_cover_letter_guide` tool to `engine/mcp/server.py`.
- [ ] Task: Test Verification
    - [ ] Run test suite and ensure all tests pass (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Documentation and Finalization
- [ ] Task: Update Runbooks
    - [ ] Update `docs/runbooks/mcp-server.md` to list the 4 new read-only tools under a new "Guides & Workflows" section.
- [ ] Task: Final Test Verification
    - [ ] Run the full test suite (`pytest`) to guarantee no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Documentation and Finalization' (Protocol in workflow.md)
# Implementation Plan: Profile MCP Tools

## Phase 1: Setup and Testing
- [x] Task: Create unit tests for the new profile tools (2b4be34)
    - [x] Write failing test `test_mcp_get_user_profile` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_user_projects` in `tests/test_mcp_server.py`.
    - [x] Write failing test `test_mcp_get_master_cv` in `tests/test_mcp_server.py`.
    - [x] Run tests and verify they fail (Red Phase).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Testing' (Protocol in workflow.md)

## Phase 2: Implementation
- [x] Task: Implement `get_user_profile` (8cff009)
    - [x] Add `get_user_profile` tool to `engine/mcp/server.py` that reads and returns `data/profile.yml` as JSON.
- [x] Task: Implement `get_user_projects`
    - [x] Add `get_user_projects` tool to `engine/mcp/server.py` that reads and returns `data/projects.yml` as JSON.
- [x] Task: Implement `get_master_cv`
    - [x] Add `get_master_cv` tool to `engine/mcp/server.py` that reads and returns `data/master-cv.md` as text.
- [x] Task: Test Verification
    - [x] Run test suite and ensure all tests pass (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Documentation and Finalization
- [ ] Task: Update Runbooks
    - [ ] Update `docs/runbooks/mcp-server.md` to list the three new read-only tools under the "Read-Only Database Queries" or a new "Read-Only Profile Data" section.
- [ ] Task: Final Test Verification
    - [ ] Run the full test suite (`pytest`) to guarantee no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Documentation and Finalization' (Protocol in workflow.md)
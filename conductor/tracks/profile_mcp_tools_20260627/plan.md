# Implementation Plan: Profile MCP Tools

## Phase 1: Setup and Testing
- [ ] Task: Create unit tests for the new profile tools
    - [ ] Write failing test `test_mcp_get_user_profile` in `tests/test_mcp_server.py`.
    - [ ] Write failing test `test_mcp_get_user_projects` in `tests/test_mcp_server.py`.
    - [ ] Write failing test `test_mcp_get_master_cv` in `tests/test_mcp_server.py`.
    - [ ] Run tests and verify they fail (Red Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Testing' (Protocol in workflow.md)

## Phase 2: Implementation
- [ ] Task: Implement `get_user_profile`
    - [ ] Add `get_user_profile` tool to `engine/mcp/server.py` that reads and returns `data/profile.yml` as JSON.
- [ ] Task: Implement `get_user_projects`
    - [ ] Add `get_user_projects` tool to `engine/mcp/server.py` that reads and returns `data/projects.yml` as JSON.
- [ ] Task: Implement `get_master_cv`
    - [ ] Add `get_master_cv` tool to `engine/mcp/server.py` that reads and returns `data/master-cv.md` as text.
- [ ] Task: Test Verification
    - [ ] Run test suite and ensure all tests pass (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Documentation and Finalization
- [ ] Task: Update Runbooks
    - [ ] Update `docs/runbooks/mcp-server.md` to list the three new read-only tools under the "Read-Only Database Queries" or a new "Read-Only Profile Data" section.
- [ ] Task: Final Test Verification
    - [ ] Run the full test suite (`pytest`) to guarantee no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Documentation and Finalization' (Protocol in workflow.md)
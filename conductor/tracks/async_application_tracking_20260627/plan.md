# Implementation Plan: Async Application Tracking

## Phase 1: Setup and Testing
- [ ] Task: Create unit tests for async lifecycle
    - [ ] Update `tests/test_mcp_server.py` to assert that `create_application_from_job` returns immediately with `generating` status.
    - [ ] Add unit tests verifying that the background thread successfully updates the DB to `failed` upon a simulated workflow failure.
    - [ ] Run test suite and verify failing tests (Red Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Testing' (Protocol in workflow.md)

## Phase 2: Implementation
- [ ] Task: Implement Async `create_application_from_job`
    - [ ] Refactor `create_application_from_job` in `engine/mcp/server.py` to upsert status as `'generating'`.
    - [ ] Implement the background thread worker that catches errors and updates status to `'failed'` on failure.
- [ ] Task: Test Verification
    - [ ] Run test suite and ensure all tests pass (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Finalization
- [ ] Task: Final Test Verification
    - [ ] Run the full test suite (`pytest`) to guarantee no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Finalization' (Protocol in workflow.md)
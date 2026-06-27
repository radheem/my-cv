# Implementation Plan: Global Sequential Ingestion FIFO Queue

## Phase 1: Setup and Testing
- [~] Task: Update unit tests for queue lifecycle
    - [ ] Update `tests/test_mcp_server.py` to assert that `create_application_from_job` returns immediately with `'queued'` status.
    - [ ] Update unit tests verifying that the background worker correctly transitions status from `'queued'` to `'generating'`, and then either `'draft'` (success) or `'failed'` (failure).
    - [ ] Run test suite and verify failing tests (Red Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Testing' (Protocol in workflow.md)

## Phase 2: Implementation
- [x] Task: Implement Global FIFO Queue and Worker (8f305e1)
    - [x] Add `queue.Queue`, `TailorConsumerWorker`, and path locking/checks to `engine/mcp/server.py`.
    - [x] Refactor `create_application_from_job` to upsert application status as `'queued'` and push to the queue.
- [x] Task: Test Verification
    - [x] Run test suite and ensure all tests pass (Green Phase).
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Finalization
- [x] Task: Final Test Verification
    - [x] Run the full test suite (`pytest`) to guarantee no regressions.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Finalization' (Protocol in workflow.md)
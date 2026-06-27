# Implementation Plan: Async Application Tracking & Job Soft-Delete

## Phase 1: Setup and Testing
- [x] Task: Create unit tests for async lifecycle and job soft-delete (90ec1c4)
    - [x] Update `tests/test_mcp_server.py` to assert that `create_application_from_job` returns immediately with `'generating'` status.
    - [x] Add unit tests verifying that the background thread successfully updates the DB to `'failed'` upon a simulated workflow failure.
    - [x] Add unit tests for the new `delete_job` tool, verifying that deleting a job changes its status, suffixes its `job_id` and `slug`, and allows a subsequent identical URL save to insert a brand-new active record.
    - [x] Run tests and verify they fail (Red Phase).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Testing' (Protocol in workflow.md)

## Phase 2: Implementation
- [x] Task: Implement database schema update
    - [x] In `engine/db.py`, update `init_db` to include `status VARCHAR(50) NOT NULL DEFAULT 'active'` in the `jobs` table.
    - [x] Add an `ALTER TABLE jobs ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'active';` execution step during database initialization to safely migrate existing databases.
- [x] Task: Implement Async `create_application_from_job`
    - [x] Refactor `create_application_from_job` in `engine/mcp/server.py` to upsert application status as `'generating'`.
    - [x] Implement the background thread worker that catches errors and updates the application status to `'failed'` on failure.
- [x] Task: Implement `delete_job` tool and suffix freeing pattern (ef00143)
    - [x] Implement the `delete_job(slug)` tool in `engine/mcp/server.py`.
    - [x] In the tool, update `status = 'deleted'`, append `-deleted-<epoch>` suffix to the `job_id` and `slug`, and commit.
- [x] Task: Test Verification
    - [x] Run test suite and ensure all tests pass (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Finalization
- [ ] Task: Final Test Verification
    - [ ] Run the full test suite (`pytest`) to guarantee no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Finalization' (Protocol in workflow.md)
# Implementation Plan: Create Application Queue Idempotency

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement strict idempotency for finished jobs and worker-side duplicate filtering for in-progress jobs to protect the `create_application_from_job` workflow from redundant resource exhaustion.

**Architecture:** We will modify `engine/mcp/server.py`. The `create_application_from_job` tool will query the DB and reject post-processing states outright. The background worker `_tailor_consumer_worker` will check the DB state of a popped task to ensure it hasn't been picked up by a duplicate queued event.

---

## Phase 1: Tool-Level Strict Idempotency

- [x] Task: Reject finished application generation requests 86eb197
    - [x] Step 1.1: Add a new unit test in `tests/test_mcp_server.py` (`test_mcp_create_application_idempotency`) that creates a mock job and an application with status `'draft'`, then asserts that `create_application_from_job` returns a rejection error.
    - [x] Step 1.2: Run the test and verify it fails (Red phase).
    - [x] Step 1.3: Update `create_application_from_job` in `engine/mcp/server.py`. After fetching the job, query the `applications` table. If the status is one of `'draft', 'applied', 'interview', 'offer', 'rejected', 'withdrawn'`, return an error JSON explicitly stating it is already finished. Allow `'queued'`, `'generating'`, or `'failed'`.
    - [x] Step 1.4: Run the test and verify it passes (Green phase).
    - [x] Step 1.5: Commit changes: `feat(mcp): block redundant application generation for finished statuses`

- [x] Task: Conductor - User Manual Verification 'Phase 1: Tool-Level Strict Idempotency' (Protocol in workflow.md)

## Phase 2: Worker-Side Duplicate Filtering

- [x] Task: Ignore redundant queue tasks in the background worker a0657b3
    - [x] Step 2.1: Write a unit test `test_mcp_stress_duplicate_queue_filtering` that mocks the `create_application_from_job_workflow`. Submit the same slug to the queue 3 times. Verify the background worker calls the workflow exactly 1 time instead of 3.
    - [x] Step 2.2: Run the test and verify it fails (Red phase).
    - [x] Step 2.3: Modify `_tailor_consumer_worker` in `engine/mcp/server.py`. After popping a `slug` from the queue, query its current status. If the status is `'generating'`, skip processing and `continue`. To avoid race conditions, use an atomic `UPDATE applications SET status = 'generating' WHERE slug = %s AND status IN ('queued', 'failed') RETURNING status` to grab the lock. If no row is returned, `continue`.
    - [x] Step 2.4: Run the test and verify it passes (Green phase).
    - [x] Step 2.5: Commit changes: `feat(mcp): implement worker-side duplicate filtering for queued tasks`

- [x] Task: Conductor - User Manual Verification 'Phase 2: Worker-Side Duplicate Filtering' (Protocol in workflow.md)

## Phase 3: End-to-End Testing

- [x] Task: Run E2E Deployment Tests inside Docker Compose a0657b3
    - [x] Step 3.1: Build and start the PostgreSQL database and MCP server containers: `docker compose up -d db mcp`.
    - [x] Step 3.2: Execute the full `pytest` suite inside the `ingest` container: `docker compose run --rm ingest uv run pytest -v`.
    - [x] Step 3.3: Verify that 100% of the unit and integration tests pass successfully in the container environment.

- [x] Task: Conductor - User Manual Verification 'Phase 3: End-to-End Testing' (Protocol in workflow.md)
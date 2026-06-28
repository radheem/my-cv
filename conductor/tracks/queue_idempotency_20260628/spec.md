# Specification: Create Application Queue Idempotency

## Overview
The `create_application_from_job` MCP tool enqueues computationally heavy application-tailoring workloads asynchronously into an in-memory queue. Currently, if a user or agent submits multiple requests for the same job slug, the job gets enqueued multiple times. This track introduces robust idempotency and lifecycle safeguards to prevent redundant processing.

## Functional Requirements

1. **Worker-Side Duplicate Filtering**:
   - Instead of rejecting incoming requests immediately, the `create_application_from_job` tool will continue to enqueue requests.
   - However, the background `TailorConsumerWorker` must implement an idempotency check right before starting processing: if a job is popped from the in-memory queue but its PostgreSQL status is already `'generating'`, `'draft'`, or any other post-queued state, the worker must safely discard the duplicate task and continue to the next item.

2. **Strict Idempotency for Finished Jobs**:
   - If an agent attempts to call `create_application_from_job` on a slug whose application status is already complete (e.g., `'draft'`, `'applied'`, `'interview'`, `'offer'`, `'rejected'`, `'withdrawn'`), the MCP tool should **block the request** immediately.
   - It will return an error string specifying that the application is already generated or finalized and must be manually deleted or modified rather than re-enqueued.
   - Exception: if the status is `'failed'`, it should allow re-queuing so the user/agent can retry the workflow.

## Non-Functional Requirements
- Maintain thread safety between the background consumer and the MCP request handler.
- Ensure the database constraints prevent race conditions if multiple workers attempt to process simultaneously in a multi-threaded context.

## Acceptance Criteria
- [ ] Attempting to enqueue an already finished (e.g., `'draft'`) application returns an immediate rejection.
- [ ] Attempting to enqueue a `'failed'` application successfully resets its status to `'queued'` and enqueues it.
- [ ] Pushing the same valid slug 5 times back-to-back results in the worker skipping the 4 redundant tasks and generating the application only once.
- [ ] All updated logic is covered by unit tests mimicking parallel or consecutive duplicate submissions.

## Out of Scope
- Creating new application lifecycle statuses.
- Distributing the queue externally to Redis/RabbitMQ.
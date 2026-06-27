# Specification: Async Application Generation and Lifecycle Tracking

## Overview
Currently, the `create_application_from_job` MCP tool runs synchronously, making it prone to HTTP disconnections and timeouts during long-running LLM generation and LaTeX rendering phases. We will refactor this tool to run asynchronously using a background worker thread. We will use the existing `applications` table to manage and track the task's lifecycle (`generating`, `draft`, `failed`), allowing agents to spawn creations in batch and safely poll progress via `get_application`.

## Functional Requirements
1. **Asynchronous Generation Tool (`create_application_from_job`)**:
   - Checks if the job exists in the database. If not, returns a clean error message.
   - Inserts or updates the `applications` row with status set to `'generating'`.
   - Spawns a background thread (`threading.Thread`) to execute `create_application_from_job_workflow(slug)` in isolation.
   - Immediately returns a JSON response:
     ```json
     {
       "status": "generating",
       "slug": "<slug>",
       "message": "Application tailoring started in the background. Monitor progress using get_application."
     }
     ```
2. **Background Thread Lifecycle Rules**:
   - The worker executes the synchronous generation pipeline.
   - If successful, the existing push workflow (`cmd_db_push`) automatically parses the generated markdown files and updates the status to `'draft'` in the DB.
   - If an error occurs (the workflow returns an `"ERROR"` string or raises an exception), the background thread catches it, logs it, and updates the database row status to `'failed'` in the `applications` table.
3. **Robust Error Messages**:
   - Avoid raising raw exceptions that crash the ASGI process.
   - Safely return structured JSON strings with `{"error": "message"}` on tool invocation failures.

## Non-Functional Requirements
- **No Database Migrations Required**: The `applications` table stores status as `VARCHAR(50)` with no check constraints, allowing us to store custom intermediate statuses like `'generating'` and `'failed'` natively.
- **Resource Protection**: Runs tasks sequentially in thread pools if necessary, though lightweight threads are standard.

## Acceptance Criteria
1. Invoking `create_application_from_job` returns in under 50 milliseconds.
2. The `applications` table status is immediately set to `'generating'`.
3. Polling `get_application` during compilation returns `{"status": "generating"}`.
4. On successful completion, the status changes to `'draft'`.
5. On failure, the status changes to `'failed'`.
6. Unit tests are added to verify the async lifecycle behavior.

## Out of Scope
- Implementing external persistent broker queues (like Celery/Redis). Lightweight Python memory threads are sufficient and robust for a single-user VM setup.
# Specification: Global Sequential Ingestion FIFO Queue

## Overview
Currently, the `create_application_from_job` MCP tool runs asynchronous background threads concurrently. When multiple requests are submitted (such as in a batch), multiple local LLM (Ollama) generation and LaTeX compiling pipelines run at the same time, leading to heavy resource contention, massive compilation delays, and potential crashes. We will introduce a global, thread-safe, first-in-first-out (FIFO) sequential Queue. All tailoring tasks will be queued and processed **one at a time, serially**, by a single dedicated background consumer thread.

## Functional Requirements
1. **Global Queue Architecture**:
   - Define a global `queue.Queue()` in `engine/mcp/server.py` to hold pending tailoring slugs.
   - Start a single background consumer thread (`TailorConsumerWorker`) that runs indefinitely.
   - The consumer thread pops a slug, updates the database application status to `'generating'`, runs the tailoring workflow, and updates the status to `'draft'` (on success) or `'failed'` (on failure).
2. **Asynchronous Queueing Tool (`create_application_from_job`)**:
   - Immediately verifies if the job exists. If not, returns a clean JSON error.
   - Inserts or updates the `applications` row with status set to `'queued'`.
   - Pushes the slug to the global queue.
   - Returns a success response immediately indicating the job is queued:
     ```json
     {
       "status": "queued",
       "slug": "<slug>",
       "message": "Application tailoring has been added to the sequential background queue. Monitor progress using get_application."
     }
     ```

## Non-Functional Requirements
- **Thread Safety**: Use `queue.Queue` (which is natively thread-safe) and `threading.Lock` to ensure safe consumer initialization.
- **Resource Conservation**: Restricts execution to exactly **1 active compilation** at any time.

## Acceptance Criteria
1. Submitting an application creation request returns in under 50ms with status `'queued'`.
2. The `applications` table shows status as `'queued'` immediately after submission.
3. Once the background consumer pops the job, it transitions its status in the DB to `'generating'`.
4. The jobs are processed sequentially (FIFO).
5. All 150+ unit and integration tests are modified to match this queue lifecycle and pass successfully.
# Specification: Async Application Tracking & Job Soft-Delete

## Overview
Currently, the `create_application_from_job` MCP tool runs synchronously, making it prone to HTTP disconnections and timeouts. We will refactor it to run asynchronously via background thread workers and track its lifecycle states (`generating`, `draft`, `failed`) inside the `applications` table. 

Additionally, we will add support for soft-deleting jobs. If a job is deleted, it is marked as `'deleted'`. If the system crawls/scrapes that same job again later, it must create a brand-new record with active status, bypassing previous unique key conflicts.

## Functional Requirements

### 1. Asynchronous Application Creation
- **`create_application_from_job`**:
  - Immediately verifies if the job exists. If not, returns a clean JSON error.
  - Inserts or updates the `applications` row with status set to `'generating'`.
  - Spawns a background thread (`threading.Thread`) to execute `create_application_from_job_workflow(slug)` in isolation.
  - Returns a success response immediately:
    ```json
    {
      "status": "generating",
      "slug": "<slug>",
      "message": "Application tailoring started in the background. Monitor progress using get_application."
    }
    ```
  - If the background task fails, the thread catches the error, logs it, and sets the DB row status to `'failed'`. On success, the existing push workflow automatically sets the status to `'draft'`.

### 2. Job Table Status & Reinstatement
- **Schema Modification**:
  - Add a `status` column to the `jobs` table: `status VARCHAR(50) NOT NULL DEFAULT 'active'`.
  - Automatically execute `ALTER TABLE jobs ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'active';` during database initialization.
- **Delete Action & Suffix-Freeing Pattern**:
  - Introduce or update the delete logic (e.g., in a tool or helper):
    - When a job is marked as `'deleted'`, update its `status = 'deleted'`.
    - To free up its unique primary key `job_id` and unique `slug`, append a timestamped suffix:
      - `job_id = job_id || '-deleted-' || timestamp`
      - `slug = slug || '-deleted-' || timestamp`
  - When the same job URL is fetched again:
    - The computed clean `job_id` hash is free.
    - It inserts successfully as a fresh, brand-new `'active'` record!

## Non-Functional Requirements
- **Thread Safety**: Use standard, lightweight Python thread pools or threads.
- **Robust Error Messages**: Catch exceptions gracefully inside MCP tools and return formatted JSON error strings instead of raw process crashes.

## Acceptance Criteria
1. `create_application_from_job` returns in under 50ms with status `'generating'`.
2. Polling `get_application` during tailoring returns status `'generating'`.
3. If tailoring fails, the status in `get_application` changes to `'failed'`.
4. Marking a job as deleted updates its status, suffixes its ID/slug, and allows a subsequent identical URL scrape to insert a brand-new active record.
5. All 146+ unit and E2E tests pass cleanly.
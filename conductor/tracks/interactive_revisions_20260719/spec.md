# Specification: Interactive Revision, Smart Regeneration, Queue Control, & Independent Translation

## Overview
This track addresses the functional gaps identified in our two-stage pipeline by adding four interactive capabilities to the MCP server:
1.  **Iterative Revision Tools** (`revise_cover_letter`, `revise_cv`): Allows natural-language refinement of generated CVs and cover letters, preserving previous draft context.
2.  **Smart Regeneration** (`regenerate_application`): Performs complete deletion of on-disk applications and DB records, then triggers a fresh generation run.
3.  **Queue Control** (`cancel_queued_task`): Dequeues pending tasks from the sequential in-memory queue.
4.  **Independent Translation Tool** (`translate_application`): Allows separately triggering German translation for the English drafts on demand.

---

## Functional Requirements

### 1. Iterative Revision Engine (`revise_cover_letter` and `revise_cv`)
*   **Input**: `slug` (application identifier), `revision_instructions` (natural language feedback, e.g. *"make the introduction shorter and warmer"*).
*   **Behavior**:
    1.  Read the existing markdown content (`cover-letter.md` or `cv.md`) from `applications/<slug>/` on disk. If the files are missing or empty, return an error.
    2.  Read the parent job description from the database to maintain context.
    3.  Call the LLM with a specialized **Revision Prompt**:
        *   Provide the target job description.
        *   Provide the current draft.
        *   Provide the user's specific feedback/revision instructions.
        *   Instruct the LLM to output the revised Markdown text cleanly.
    4.  Save the newly revised text back to the corresponding file on disk.
    5.  Atomically update the database row (`cv_en` or `cover_letter_en` column in the `applications` table) so the changes are instantly synchronized.
*   **Output**: Return the newly revised Markdown text to the caller.

### 2. Independent Translation Tool (`translate_application`)
*   **Input**: `slug` (application identifier), `kind` (string, either `"cv"`, `"cover-letter"`, or `"both"`, default is `"both"`).
*   **Behavior**:
    1.  Verify the specified English draft exists on disk.
    2.  For each target draft (CV, Cover Letter, or both):
        *   Call `translate_markdown` from `engine/domains/tailoring/render.py` to generate the German translation.
        *   Save the translated `.de.md` file on disk.
        *   Atomically update the corresponding database column (`cv_de`, `cover_letter_de` or both in the `applications` table).
*   **Output**: Return the translated German markdown text(s).

### 3. Smart Regeneration Tool (`regenerate_application`)
*   **Input**: `slug` (application identifier).
*   **Behavior**:
    1.  Delete the corresponding application row from the `applications` table in DuckDB.
    2.  Recursively delete the `applications/<slug>/` directory on disk.
    3.  Call `create_application_from_job(slug)` to enqueue a fresh, complete Stage 1 generation task.
*   **Output**: Return a JSON string confirming deletion and enqueuing status.

### 4. Queue Control Tool (`cancel_queued_task`)
*   **Input**: `slug` (application identifier).
*   **Behavior**:
    1.  Verify if there is a pending task for the given slug in `_tailor_queue` (which hasn't started running yet).
    2.  Safely remove the task from the queue in-memory.
    3.  If the task was a fresh generation, delete the newly created application row from the DB. If it was a compile task, reset the status from `'compiling'` back to `'draft'`.
*   **Output**: Return a JSON string indicating if the task was successfully cancelled.

---

## Non-Functional Requirements
*   **Thread Safety**: Ensure queue manipulations and database status transitions are fully synchronized and thread-safe.
*   **Graceful Recovery**: Return descriptive JSON errors to the client if files are missing or a task is already executing and cannot be cancelled.

---

## Acceptance Criteria
*   Calling `revise_cover_letter` correctly updates `cover-letter.md`, updates the database, and returns the modified draft.
*   Calling `revise_cv` correctly updates `cv.md`, updates the database, and returns the modified draft.
*   Calling `translate_application` with `kind="cover-letter"` translates the cover letter and updates the database, leaving the CV untouched.
*   Calling `regenerate_application` purges files, DB, and starts a fresh queue job.
*   Calling `cancel_queued_task` successfully dequeues a pending task.
*   Unit and integration tests pass cleanly.

# Implementation Plan: Interactive Revision, Smart Regeneration, Queue Control, & Translation

## Phase 1: Iterative Revision Engine & Independent Translation
- [x] Task: Implement revision logic (1fcf435)
    - [ ] Write failing tests in `tests/test_mcp_revisions.py` for `revise_cover_letter` and `revise_cv` checking LLM prompt injection, file writing, and DB updates.
    - [ ] Implement revision helper functions in `engine/domains/tailoring/render.py` to read previous drafts, combine them with feedback, and call the LLM.
    - [ ] Expose `revise_cover_letter` and `revise_cv` as MCP tools in `engine/mcp/server.py`.
    - [ ] Ensure the database is atomically updated with revised copy, and status remains `'draft'`.
    - [ ] Ensure tests pass (Green phase).
- [x] Task: Implement Independent Translation Tool (a0e0c35)
    - [ ] Write failing tests in `tests/test_mcp_revisions.py` for `translate_application` verifying CV, cover letter, or joint translation flows.
    - [ ] Expose `translate_application(slug, kind)` as an MCP tool in `engine/mcp/server.py`.
    - [ ] Ensure it loads the current draft, calls `translate_markdown` bilingually, writes translated `.de.md` files to disk, and updates database columns (`cv_de`/`cover_letter_de`).
    - [ ] Ensure tests pass (Green phase).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Iterative Revision Engine & Independent Translation' (Protocol in workflow.md) (8a657c0)

## Phase 2: Smart Regeneration & Queue Control Tools
- [x] Task: Implement Smart Regeneration (28fba91)
    - [ ] Write failing tests in `tests/test_mcp_revisions.py` for `regenerate_application`.
    - [ ] Expose `regenerate_application` as an MCP tool in `engine/mcp/server.py`.
    - [ ] Ensure it purges local directories, deletes DuckDB application rows, and enqueues a fresh Stage 1 tailoring task.
    - [ ] Ensure tests pass (Green phase).
- [ ] Task: Implement Queue Control
    - [ ] Write failing tests in `tests/test_mcp_revisions.py` for `cancel_queued_task`.
    - [ ] Expose `cancel_queued_task` as an MCP tool in `engine/mcp/server.py`.
    - [ ] Ensure it safely removes pending tasks from `_tailor_queue` in-memory and resets their DB states.
    - [ ] Ensure tests pass (Green phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Smart Regeneration & Queue Control Tools' (Protocol in workflow.md)

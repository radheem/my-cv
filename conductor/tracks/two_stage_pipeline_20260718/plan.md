# Implementation Plan: Two-Stage Job Application Pipeline & Custom Instructions

## Phase 1: CLI & Prompt Tailoring (Custom Instructions)
- [ ] Task: Update cover letter rendering prompt
    - [ ] Write failing test in `tests/test_custom_instructions.py` for `render_cover_letter` checking instruction injection.
    - [ ] Update `render_cover_letter` in `engine/domains/tailoring/render.py` to accept and prioritize `custom_instructions`.
    - [ ] Ensure tests pass (Green phase) and refactor if needed.
- [ ] Task: Update CLI command `cmd_new`
    - [ ] Add optional `--instructions` parameter to the `new` subparser in `engine/cli.py`.
    - [ ] Extract and pass the `instructions` flag to `render_cover_letter` in `cmd_new`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: CLI & Prompt Tailoring (Custom Instructions)' (Protocol in workflow.md)

## Phase 2: Workflow Decomposition & Markdown Verification
- [ ] Task: Implement Markdown Verification
    - [ ] Write failing tests in `tests/test_gmail_workflows.py` for `verify_markdown_documents` covering English/German placeholders and strict bracket regex.
    - [ ] Implement `verify_markdown_documents` in `engine/domains/gmail/ingest.py`.
    - [ ] Ensure tests pass (Green phase).
- [ ] Task: Split Ingestion Workflows
    - [ ] Decompose `create_application_from_job_workflow` in `engine/domains/gmail/ingest.py` into `generate_markdown_workflow` (Stage 1) and `create_pdf_from_markdown_workflow` (Stage 2).
    - [ ] Integrate `verify_markdown_documents` at the start of Stage 2.
    - [ ] Update tests in `tests/test_gmail_workflows.py` to reflect the decomposed workflows.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Workflow Decomposition & Markdown Verification' (Protocol in workflow.md)

## Phase 3: MCP Server, Global Queue Refactoring & E2E Fixes
- [ ] Task: Refactor Background Queue and Worker
    - [ ] Write failing tests for dictionary payloads and DB state handling in `tests/test_mcp_server.py`.
    - [ ] Refactor `_tailor_consumer_worker` and `_tailor_queue` in `engine/mcp/server.py` to use dictionary payloads (`slug`, `variant`, `custom_instructions`, `stage`).
    - [ ] Update worker to atomically save generated `.md` contents (cv_en, cv_de, etc.) to the `applications` table at the end of Stage 1.
    - [ ] Update worker to support the `compiling` state for Stage 2 tasks and dispatch `create_pdf_from_markdown_workflow`.
    - [ ] Ensure tests pass.
- [ ] Task: Update MCP Tools
    - [ ] Update `create_application_from_job` and `create_application_with_variant` in `engine/mcp/server.py` to accept `custom_instructions` and pass them to the queue.
    - [ ] Create new MCP tool `create_pdf_from_markdown` that enqueues a Stage 2 task with state `compiling`.
    - [ ] Expose `create_pdf_from_markdown` in the server tool registry.
- [ ] Task: Fix E2E Client Tests
    - [ ] Modify `server_params` fixture in `tests/test_mcp_e2e_client.py` to use `args=["run", "--no-project", "cv-tailor-mcp"]` to bypass uv workspace resolution issues.
    - [ ] Run full test suite and verify 100% pass rate.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: MCP Server, Global Queue Refactoring & E2E Fixes' (Protocol in workflow.md)
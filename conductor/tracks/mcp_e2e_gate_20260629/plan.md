# Implementation Plan: Fix DDD Import Regression & Establish MCP E2E Quality Gate

## Phase 1: Fix Domain Import Regression

- [ ] Task: Fix Domain Relative Imports
    - [ ] Step 1.1: Fix the inline relative `latex` import in `engine/cli.py` (L212 in `_render_tex`).
    - [ ] Step 1.2: Fix the inline relative `linkedin` imports in `engine/cli.py` (L871 in `_build_linkedin_session`, L955 and L956 in `_do_ingest`, and L1078 in `cmd_capture`).
    - [ ] Step 1.3: Fix the inline relative `fraunhofer` import in `engine/cli.py` (L1056 in `cmd_hunt`).
    - [ ] Step 1.4: Fix the inline relative `linkedin` imports in `engine/pixel_capture.py` (L100 in `_derive_source_and_job_id` and L160 in `capture_screenshot`).
- [ ] Task: Verify Relative Imports Fixed
    - [ ] Step 1.5: Run unit tests to confirm no regressions: `uv run pytest`.
    - [ ] Step 1.6: Manually test compiling a bilingual PDF for an existing application (e.g. `flix-middle-software-engineer-m-f-d-670a0995e3fe`) via CLI: `uv run engine/cli.py pdf flix-middle-software-engineer-m-f-d-670a0995e3fe`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Fix Domain Import Regression' (Protocol in workflow.md)

## Phase 2: Implement MCP E2E Test Suite

- [ ] Task: Implement Automated E2E Test Suite
    - [ ] Step 2.1: Create a new test file `tests/test_mcp_e2e_client.py` and import the FastMCP server, pytest, and DB connections.
    - [ ] Step 2.2: Add an E2E test verifying server capabilities: checking that calling the MCP server's `list_tools`, `list_prompts`, and `list_resources` lists all expected options.
    - [ ] Step 2.3: Add an E2E test verifying the read-only SQL queries (`mcp_query`) tool and confirming safety policies (blocked write-access / restricted query requests via SQL Guard).
    - [ ] Step 2.4: Add an E2E test verifying async queueing/tailoring (`create_application_from_job`) using mock inputs.
- [ ] Task: Verify E2E Tests Executing Successfully
    - [ ] Step 2.5: Run the new E2E test suite locally: `uv run pytest -v tests/test_mcp_e2e_client.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implement MCP E2E Test Suite' (Protocol in workflow.md)

## Phase 3: Acceptance Gate Integration

- [ ] Task: Update Quality Gates & Workflow
    - [ ] Step 3.1: Add a new mandate to `conductor/workflow.md` under **Testing Requirements > End-to-End (E2E) Testing** to require running the MCP E2E tests before marking any track complete.
    - [ ] Step 3.2: Update the "Definition of Done" checklist in `conductor/workflow.md` to explicitly include running the MCP E2E tests.
- [ ] Task: E2E Verification & Complete Integration Checks
    - [ ] Step 3.3: Restart a clean containerized PostgreSQL DB: `docker compose down -v && docker compose up -d db mcp`.
    - [ ] Step 3.4: Run the entire test suite locally (which connects to the containerized DB) to verify absolute coverage and correctness: `uv run pytest`.
    - [ ] Step 3.5: Run the E2E live pipeline validation script: `uv run test-live-pipeline.py` and verify it runs cleanly without errors.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Acceptance Gate Integration' (Protocol in workflow.md)

# Specification: Fix DDD Import Regression & Establish MCP E2E Quality Gate

## Overview
Following a successful Domain-Driven Design (DDD) refactoring (`ddd_refactoring_20260628`), some inline imports inside `engine/cli.py` and `engine/pixel_capture.py` were left pointing to legacy paths, causing runtime `ImportError` regressions (such as the failure of LaTeX rendering in the background queue). 

This track aims to:
1. Fix all 8 identified broken inline imports in `engine/cli.py` and `engine/pixel_capture.py` to restore full system functionality.
2. Develop a comprehensive, robust End-to-End (E2E) testing suite for the MCP server that verifies server capabilities, read-only SQL queries, SQL guards, and asynchronous tailoring.
3. Make the execution of this MCP E2E test suite a mandatory quality gate for all future tracks by updating the project's core workflow instructions.

## Functional Requirements

### Part 1: Fix Domain Import Regression
Update all broken relative/inline imports to reference the correct post-refactoring domain paths:
- **`engine/cli.py`:**
  - `_render_tex` (L212): Update `from . import latex` to `from .domains.tailoring import latex`
  - `_build_linkedin_session` (L871): Update `from .linkedin.session ...` to `from .domains.linkedin.session ...`
  - `_do_ingest` (L955): Update `from .linkedin ...` to `from .domains.linkedin ...`
  - `_do_ingest` (L956): Update `from .linkedin.humanize ...` to `from .domains.linkedin.humanize ...`
  - `cmd_hunt` (L1056): Update `from .fraunhofer ...` to `from .domains.fraunhofer ...`
  - `cmd_capture` (L1078): Update `from .linkedin ...` to `from .domains.linkedin ...`
- **`engine/pixel_capture.py`:**
  - `_derive_source_and_job_id` (L100): Update `from .linkedin.jobs ...` to `from .domains.linkedin.jobs ...`
  - `capture_screenshot` (L160): Update `from .linkedin.jobs ...` to `from .domains.linkedin.jobs ...`

### Part 2: Comprehensive MCP E2E Testing Suite
Create a dedicated automated test file `tests/test_mcp_e2e_client.py` (or extend an existing one) that performs E2E integration testing against a live, running MCP server:
- **Server Capabilities Verification:** Run `ListTools`, `ListPrompts`, and `ListResources` requests and verify they return correct structures and descriptions.
- **SQL Query & SQL Guard Verification:** Run queries through the `mcp_query` tool to confirm expected results, and test the `sqlguard` safety policies to ensure restricted/write-access queries are correctly blocked.
- **Async Queueing & Tailoring Verification:** Verify calling `create_application_from_job` with mock inputs successfully enqueues tailoring jobs, manages states, and runs asynchronous workers cleanly.

### Part 3: Acceptance Gate Integration
- Update `conductor/workflow.md` under **Testing Requirements > End-to-End (E2E) Testing** to add a new requirement making the execution of the MCP E2E tests a mandatory verification step for all current and future tracks.
- Add the MCP E2E test suite step to the "Definition of Done" checklist in `conductor/workflow.md`.

## Non-Functional Requirements
- **Execution Environment:** Tests must run cleanly inside a Docker-compose environment (where database is containerized and mapped locally) as well as locally using `uv run pytest`.
- **Cleanups:** Tests must not pollute the PostgreSQL database; any test applications/jobs must be cleanly deleted or isolated inside transaction playgrounds.

## Acceptance Criteria
- [ ] All 8 inline imports are corrected, and `cv-tailor pdf <slug>` runs without `ImportError`.
- [ ] Run `uv run pytest` executes and passes 100% of all unit/integration tests including the new E2E tests.
- [ ] Run `uv run test-live-pipeline.py` or the new E2E verification test suite executes successfully.
- [ ] `conductor/workflow.md` is updated to include the MCP E2E test as an explicit quality gate.

## Out of Scope
- Changing database table schemas or altering column names.
- Adding new feature tools to the MCP server.

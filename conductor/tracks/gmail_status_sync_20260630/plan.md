# Implementation Plan: Closed-Loop Application Status Sync

## Phase 1: Core Gmail Search Workflows
- [ ] Task: In `engine/workflows/__init__.py`, update `__all__` to expose new workflows.
- [ ] Task: In `engine/domains/gmail/ingest.py` (or create `engine/domains/gmail/search.py` if cleaner), implement `generic_search_workflow(query, limit, include_bodies)`. It should call `client.search_emails` and cleanly format the output for the LLM.
- [ ] Task: In `engine/domains/gmail/ingest.py`, implement `check_application_updates_workflow(slug)`. It should query DuckDB for the application metadata, construct the targeted boolean query, and call `generic_search_workflow` under the hood.
- [ ] Task: Write tests in `tests/test_gmail_workflows.py` to mock `client.search_emails` and verify that both workflows format outputs correctly and construct the proper boolean string.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core Gmail Search Workflows' (Protocol in workflow.md)

## Phase 2: MCP Tool Registration & E2E Testing
- [ ] Task: In `engine/mcp/server.py`, register the `@mcp.tool()` `search_gmail` bridging to the generic workflow.
- [ ] Task: In `engine/mcp/server.py`, register the `@mcp.tool()` `check_application_updates` bridging to the application context workflow.
- [ ] Task: Update the `operational_mental_model` inside `mcp_initialize_agent_session` to instruct the LLM on how to use `check_application_updates` to close the loop on application status.
- [ ] Task: In `tests/test_mcp_e2e_client.py`, verify that `search_gmail` and `check_application_updates` are exposed in the server capabilities.
- [ ] Task: In `tests/test_mcp_server.py`, mock `client.search_emails` and write E2E tests for the new MCP tool endpoints.
- [ ] Task: Execute the full `make test` suite.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: MCP Tool Registration & E2E Testing' (Protocol in workflow.md)
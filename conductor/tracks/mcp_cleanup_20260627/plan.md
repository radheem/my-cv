# Implementation Plan: MCP Tool Cleanup

## Phase 1: Setup and Refactor Tests
- [ ] Task: Update test cases to target new specialized tools
    - [ ] Write failing test for `list_gmail_linkedin_jobs` in `tests/test_mcp_server.py` and `tests/test_gmail_workflows.py`.
    - [ ] Write failing test for `list_gmail_glassdoor_jobs` in `tests/test_mcp_server.py`.
    - [ ] Write failing test for `list_gmail_indeed_jobs` in `tests/test_mcp_server.py`.
    - [ ] Update any test asserting against the presence or functionality of `list_gmail_jobs` to instead assert on the new specialized tools.
    - [ ] Run the tests and confirm they fail.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Refactor Tests' (Protocol in workflow.md)

## Phase 2: Refactor MCP Server Tools
- [ ] Task: Remove deprecated and generic tools
    - [ ] Remove `search_gmail_linkedin_jobs` from `engine/mcp/server.py`.
    - [ ] Remove `search_gmail_glassdoor_jobs` from `engine/mcp/server.py`.
    - [ ] Remove `search_gmail_indeed_jobs` from `engine/mcp/server.py`.
    - [ ] Remove `list_gmail_jobs` from `engine/mcp/server.py`.
- [ ] Task: Implement specialized tools
    - [ ] Add `list_gmail_linkedin_jobs` function in `engine/mcp/server.py` that delegates to `list_gmail_jobs_workflow`.
    - [ ] Add `list_gmail_glassdoor_jobs` function in `engine/mcp/server.py` that delegates to `list_gmail_jobs_workflow`.
    - [ ] Add `list_gmail_indeed_jobs` function in `engine/mcp/server.py` that delegates to `list_gmail_jobs_workflow`.
    - [ ] Run test suite and ensure all tests pass (Green Phase).
- [ ] Task: Update Tool Descriptions and Imports
    - [ ] Update docstring for `extract_job_details` to indicate it is Step 2.
    - [ ] Update docstring for `create_application_from_job` to indicate it is Step 3.
    - [ ] Remove any unused imports in `engine/mcp/server.py`.
    - [ ] Rerun test suite to verify no breakage from import cleanup.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Refactor MCP Server Tools' (Protocol in workflow.md)
# Implementation Plan: MCP Tool Cleanup

## Phase 1: Setup and Refactor Tests
- [x] Task: Update test cases to target new specialized tools (addebd3)
    - [x] Write failing test for `list_gmail_linkedin_jobs` in `tests/test_mcp_server.py` and `tests/test_gmail_workflows.py`.
    - [x] Write failing test for `list_gmail_glassdoor_jobs` in `tests/test_mcp_server.py`.
    - [x] Write failing test for `list_gmail_indeed_jobs` in `tests/test_mcp_server.py`.
    - [x] Update any test asserting against the presence or functionality of `list_gmail_jobs` to instead assert on the new specialized tools.
    - [x] Run the tests and confirm they fail.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Refactor Tests' (Protocol in workflow.md)

## Phase 2: Refactor MCP Server Tools
- [x] Task: Remove deprecated and generic tools (84ca7db)
    - [x] Remove `search_gmail_linkedin_jobs` from `engine/mcp/server.py`.
    - [x] Remove `search_gmail_glassdoor_jobs` from `engine/mcp/server.py`.
    - [x] Remove `search_gmail_indeed_jobs` from `engine/mcp/server.py`.
    - [x] Remove `list_gmail_jobs` from `engine/mcp/server.py`.
- [x] Task: Implement specialized tools (9252bad)
    - [x] Add `list_gmail_linkedin_jobs` function in `engine/mcp/server.py` that delegates to `list_gmail_jobs_workflow`.
    - [x] Add `list_gmail_glassdoor_jobs` function in `engine/mcp/server.py` that delegates to `list_gmail_jobs_workflow`.
    - [x] Add `list_gmail_indeed_jobs` function in `engine/mcp/server.py` that delegates to `list_gmail_jobs_workflow`.
    - [x] Run test suite and ensure all tests pass (Green Phase).
- [x] Task: Update Tool Descriptions and Imports (fba3fa7)
    - [x] Update docstring for `extract_job_details` to indicate it is Step 2.
    - [x] Update docstring for `create_application_from_job` to indicate it is Step 3.
    - [x] Remove any unused imports in `engine/mcp/server.py`.
    - [x] Rerun test suite to verify no breakage from import cleanup.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Refactor MCP Server Tools' (Protocol in workflow.md)

## Phase 3: End-to-End Testing
- [ ] Task: Create E2E test for the 3-step pipeline
    - [ ] Create mock email with a job listing in `tests/test_mcp_server.py`.
    - [ ] Query Gmail using `list_gmail_linkedin_jobs` and verify the `job_url` is parsed and returned.
    - [ ] Fetch the job using `extract_job_details` with the returned URL and verify the record is saved.
    - [ ] Create an application using `create_application_from_job` with the saved job slug and verify application files are mocked/generated.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: End-to-End Testing' (Protocol in workflow.md)
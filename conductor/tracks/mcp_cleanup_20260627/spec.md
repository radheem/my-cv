# Specification: MCP Tool Cleanup

## Overview
The goal of this track is to clean up and refactor the MCP server's Gmail job search tools to prevent agents from mistakenly using deprecated or generic endpoints. We will remove the legacy `search_gmail_*_jobs` tools and replace the generic `list_gmail_jobs` tool with three specialized, hardcoded tools for LinkedIn, Glassdoor, and Indeed. This will enforce a strict, unbroken 3-step pipeline: `list_gmail_[provider]_jobs` -> `extract_job_details` -> `create_application_from_job`.

## Functional Requirements
1. Remove deprecated tools from `engine/mcp/server.py`: `search_gmail_linkedin_jobs`, `search_gmail_glassdoor_jobs`, `search_gmail_indeed_jobs`.
2. Remove the generic `list_gmail_jobs` tool from `engine/mcp/server.py`.
3. Implement three new specialized tools in `engine/mcp/server.py` that wrap the existing `list_gmail_jobs_workflow`:
   - `list_gmail_linkedin_jobs(query: str = "is:unread", limit: int = 10)`
   - `list_gmail_glassdoor_jobs(query: str = "is:unread", limit: int = 10)`
   - `list_gmail_indeed_jobs(query: str = "is:unread", limit: int = 10)`
4. Update the docstrings for `extract_job_details` and `create_application_from_job` to clearly indicate their step number in the workflow (Step 2 and Step 3).
5. Clean up any unused imports in `engine/mcp/server.py` as a result of the changes.

## Non-Functional Requirements
1. The underlying workflow logic in `engine/workflows/gmail_ingest.py` must remain generic; only the MCP exposed tools should be specialized.

## Acceptance Criteria
1. The MCP server successfully exposes the updated tools and no longer exposes the deprecated ones.
2. The agent has restricted choices for listing jobs (LinkedIn, Glassdoor, Indeed) and the tool descriptions clearly guide the 3-step process.
3. Existing tests in `tests/test_mcp_server.py` and `tests/test_gmail_workflows.py` are refactored to explicitly test the new specialized tools instead of the deprecated generic ones.
4. All tests pass successfully.

## Out of Scope
- Modifying the underlying job extraction or application creation logic.
- Adding new supported job providers.
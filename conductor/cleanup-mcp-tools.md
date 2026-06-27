# Refactor Gmail Job Search Tools

## Objective
Remove the deprecated, broken `search_gmail_*_jobs` tools from the MCP server. Replace the generic `list_gmail_jobs` tool with three specialized, hardcoded tools (`list_gmail_linkedin_jobs`, `list_gmail_glassdoor_jobs`, `list_gmail_indeed_jobs`) to restrict agent choices and prevent errors. Update the descriptions of the remaining workflow tools to clearly document the supported three-step job processing pipeline.

## Key Files & Context
- `engine/mcp/server.py`: Contains the MCP tool definitions. We need to remove the deprecated tools, remove the generic `list_gmail_jobs`, add the new specialized list tools, and update the docstrings for the remaining tools.
- `tests/test_mcp_server.py`: Ensure any tests covering the removed tools are also removed or updated to use the new specialized tools.

## Implementation Steps

1. **Remove Deprecated & Generic Tools**:
   - In `engine/mcp/server.py`, remove the definitions and `@mcp.tool()` decorators for:
     - `search_gmail_linkedin_jobs`
     - `search_gmail_glassdoor_jobs`
     - `search_gmail_indeed_jobs`
     - `list_gmail_jobs`

2. **Add Specialized List Tools**:
   - In `engine/mcp/server.py`, add three new tools that wrap the underlying `list_gmail_jobs_workflow`:
     - `list_gmail_linkedin_jobs(query: str = "is:unread", limit: int = 10)`
     - `list_gmail_glassdoor_jobs(query: str = "is:unread", limit: int = 10)`
     - `list_gmail_indeed_jobs(query: str = "is:unread", limit: int = 10)`
   - *Draft Description for these tools:* "Step 1 of the job application workflow. Search Gmail alerts from [Provider] and return a lightweight list of discovered jobs containing tentative job_id, company, role, job_url, and brief_description. Use the returned `job_url` with the `extract_job_details` tool."

3. **Update Remaining Tool Descriptions**:
   - Update the docstring for `extract_job_details` to state it is Step 2.
     - *Draft Description:* "Step 2 of the job application workflow. Execute Playwright scraper in an isolated process to extract the full job description from a given URL (obtained from a `list_gmail_*_jobs` tool) and save the completed record into the PostgreSQL database. Returns the database record including the job slug."
   - Update the docstring for `create_application_from_job` to state it is Step 3.
     - *Draft Description:* "Step 3 of the job application workflow. Generate tailored job application documents (CV/CL in English and German) for a specific job slug (obtained from `extract_job_details`), render them to PDFs, upload them to Google Drive, and synchronize application status."

4. **Update Tests**:
   - In `tests/test_mcp_server.py`, remove any tests specifically testing `search_gmail_*_jobs`.
   - Update any tests using `list_gmail_jobs` to use one of the new specialized tools (e.g., `list_gmail_linkedin_jobs`).

## Verification & Testing
- Run `pytest tests/test_mcp_server.py` to ensure the test suite passes with the new specialized tools.
- Start the MCP server locally (if applicable) and verify via the MCP client/inspector that only the correct tools (`list_gmail_linkedin_jobs`, `list_gmail_glassdoor_jobs`, `list_gmail_indeed_jobs`, `extract_job_details`, `create_application_from_job`) are exposed and that their descriptions reflect the updated pipeline.
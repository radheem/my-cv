# Specification: LinkedIn and Indeed MCP Tools

## Overview
This track introduces two dedicated, highly specialized MCP tools: `fetch_linkedin_job` and `fetch_indeed_job`. These tools allow the agent to fetch job postings directly by extracting the unique platform Job ID (or indeed JK parameter) from a URL and retrieving details using clean, lightweight API or direct view endpoints. This bypasses dynamic, heavy browser crawling overhead.

## Functional Requirements
1. **HTML Clean Refactoring (`_clean_html`)**:
   - Extract the regex-based HTML-cleaning logic from `fetch_public_job_url` into a shared, private helper `_clean_html(html_content: str) -> str`.
   - Update `fetch_public_job_url` to leverage `_clean_html`.

2. **LinkedIn Job Fetch Tool (`fetch_linkedin_job`)**:
   - Name: `fetch_linkedin_job`
   - Parameters: `job_id: str`
   - URL Construction: `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}`
   - Behavior: Fetch the URL via standard HTTP requests with a realistic `User-Agent`. Run the HTML response through the `_clean_html` helper to extract and return plain text.

3. **Indeed Job Fetch Tool (`fetch_indeed_job`)**:
   - Name: `fetch_indeed_job`
   - Parameters: `job_id: str`
   - URL Construction: `https://de.indeed.com/viewjob?jk={job_id}`
   - Behavior: Fetch the URL via standard HTTP requests with a realistic `User-Agent`. Attempt to parse the response as JSON (returning a pretty-printed or formatted JSON string). If JSON parsing fails (or if Indeed returns HTML), fall back to cleaning the HTML with `_clean_html` and return the resulting text.

4. **Robust Error Handling**:
   - Catch all HTTP/URL exception errors (such as 403 Forbidden, 404 Not Found, etc.). Return a clean, readable error string (e.g. `ERROR: Failed to fetch...`) rather than raising raw Python exceptions so the calling agent can handle it gracefully.

## Non-Functional Requirements
- **Performance**: Fetches must complete under a standard timeout of 15 seconds.
- **Maintainability**: Share the text extraction logic between `fetch_public_job_url`, `fetch_linkedin_job`, and the fallback in `fetch_indeed_job` via `_clean_html()`.

## Acceptance Criteria
- [ ] Refactored `_clean_html` helper works seamlessly and all existing tests pass.
- [ ] `fetch_linkedin_job` fetches and extracts readable plain text from a mock LinkedIn guest job posting HTML response.
- [ ] `fetch_indeed_job` handles a JSON response successfully, returning pretty-printed JSON.
- [ ] `fetch_indeed_job` falls back to cleaning HTML successfully if the response is HTML.
- [ ] Request errors are caught and returned as clean descriptive strings.
- [ ] Both new tools are registered and successfully exposed on the cv-tailor FastMCP server.

## Out of Scope
- This track does not implement dynamic session login warming or Playwright-based crawling for LinkedIn/Indeed guest fetching.
- Full E2E database storage flows (like `save_job_description`) are not modified.

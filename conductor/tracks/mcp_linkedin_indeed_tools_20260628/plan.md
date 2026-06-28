# LinkedIn and Indeed MCP Tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement two specialized MCP tools (`fetch_linkedin_job` and `fetch_indeed_job`) in the FastMCP server, optimizing platform-specific fetching and avoiding dynamic browser crawling overhead.

**Architecture:** Create a shared private helper `_clean_html(html_content: str) -> str` to centralize HTML text extraction. Build tool decorators exposing `fetch_linkedin_job` and `fetch_indeed_job` which accept `job_id`, build the canonical URL, fetch using `urllib.request`, parse according to their content type (HTML/JSON), and return clean output or clean error strings.

**Tech Stack:** Python 3, FastMCP, `urllib.request`.

---

## Phase 1: Shared Helper Refactoring

- [x] Task: Extract HTML text cleaning logic to `_clean_html` f3f4de2
    - [x] Step 1.1: Identify the regex cleaning logic in `fetch_public_job_url` inside `engine/mcp/server.py`.
    - [x] Step 1.2: Implement `_clean_html(html_content: str) -> str` directly before `fetch_public_job_url`.
    - [x] Step 1.3: Modify `fetch_public_job_url` to call `_clean_html(html_content)`.
    - [x] Step 1.4: Run the test suite using `pytest tests/test_mcp_server.py::test_mcp_fetch_public_job_url` to ensure no regression.
    - [x] Step 1.5: Commit changes with message: `refactor(mcp): extract _clean_html helper`

- [x] Task: Conductor - User Manual Verification 'Phase 1: Shared Helper Refactoring' (Protocol in workflow.md)


## Phase 2: LinkedIn Job Fetcher

- [x] Task: Implement `fetch_linkedin_job` using TDD c3775ed
    - [x] Step 2.1: Write a failing unit test `test_mcp_fetch_linkedin_job` in `tests/test_mcp_server.py`.
    - [x] Step 2.2: Mock `urllib.request.urlopen` in the test to return mock LinkedIn guest job posting HTML.
    - [x] Step 2.3: Run the test and verify it fails with an `AttributeError` (tool not defined).
    - [x] Step 2.4: Implement `@mcp.tool()` and `fetch_linkedin_job(job_id: str) -> str` in `engine/mcp/server.py`.
    - [x] Step 2.5: Implement URL construction to `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}`.
    - [x] Step 2.6: Use `urllib.request` to fetch HTML and run it through `_clean_html()`.
    - [x] Step 2.7: Add robust error handling to return clean error strings.
    - [x] Step 2.8: Run the test and verify that it passes.
    - [x] Step 2.9: Commit changes with message: `feat(mcp): add fetch_linkedin_job tool`

- [x] Task: Conductor - User Manual Verification 'Phase 2: LinkedIn Job Fetcher' (Protocol in workflow.md)


## Phase 3: Indeed Job Fetcher

- [ ] Task: Implement `fetch_indeed_job` using TDD
    - [ ] Step 3.1: Write a failing unit test `test_mcp_fetch_indeed_job` in `tests/test_mcp_server.py`.
    - [ ] Step 3.2: Mock `urllib.request.urlopen` in the test to support both JSON and HTML responses for testing fallback.
    - [ ] Step 3.3: Run the test and verify it fails with an `AttributeError` (tool not defined).
    - [ ] Step 3.4: Implement `@mcp.tool()` and `fetch_indeed_job(job_id: str) -> str` in `engine/mcp/server.py`.
    - [ ] Step 3.5: Implement URL construction to `https://de.indeed.com/viewjob?jk={job_id}`.
    - [ ] Step 3.6: Fetch response via `urllib.request`.
    - [ ] Step 3.7: Attempt `json.loads` parsing. If successful, pretty-print with indentation.
    - [ ] Step 3.8: On parsing failure, fall back to cleaning HTML with `_clean_html()`.
    - [ ] Step 3.9: Add robust error handling to return clean error strings.
    - [ ] Step 3.10: Run the test and verify that both HTML fallback and JSON paths pass.
    - [ ] Step 3.11: Commit changes with message: `feat(mcp): add fetch_indeed_job tool`

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Indeed Job Fetcher' (Protocol in workflow.md)

# Specification: Add 4 Read-Only MCP Tools for Workflows, Insights, and Writing Guides

## Overview
To empower external AI agents to operate the `cv-tailor` system safely and generate outstanding applications, we will expose 4 read-only MCP tools. These tools provide on-demand documentation regarding system workflows, operational best practices (pacing, timeouts, delays), and tailored writing guidelines.

## Functional Requirements
1. **New MCP Tool `get_mcp_workflows`**:
   - Reads and returns `docs/mcp-workflows.md` containing the supported paths and comparison matrix.
2. **New MCP Tool `get_mcp_insights`**:
   - Reads and returns `data/guides/mcp-insights.md` (a new guide detailing operational guidelines, pacing, delays, and timeout recovery).
3. **New MCP Tool `get_cv_guide`**:
   - Reads and returns `data/guides/how-to-write-a-cv.md` containing tactical bullet-point and section rules.
4. **New MCP Tool `get_cover_letter_guide`**:
   - Reads and returns `data/guides/how-to-write-a-cover-letter.md` containing structure, salutation, and narrative guidelines.
5. **New Document `data/guides/mcp-insights.md`**:
   - Create this file to hold structured markdown on:
     - Scraping Delays & Pacing: Injecting 5-10s randomized sleep pauses between webpage fetching calls.
     - Timeout Recovery (Error -32001): Diagnosing browser bottlenecks and falling back securely to public web-fetching.
     - Warm Sessions: Managing Playwright LinkedIn login sessions.

## Non-Functional Requirements
- **Read-Only**: These tools must only read files from `docs/` and `data/` and return their content as plain text.
- **Safety**: Standard error-handling to prevent server crashes in case of missing files.

## Acceptance Criteria
1. The 4 new tools (`get_mcp_workflows`, `get_mcp_insights`, `get_cv_guide`, `get_cover_letter_guide`) are successfully exposed by the MCP server.
2. Unit tests are added to `tests/test_mcp_server.py` verifying that each tool correctly reads and returns the corresponding file.
3. All tests pass successfully.

## Out of Scope
- Modifying any of the underlying document generation engines.
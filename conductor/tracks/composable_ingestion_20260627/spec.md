# Specification: Design Composable Ingestion and Application Flow Refactor

## Overview
The goal of this track is to decompose the monolithic scraping workflows into composable pieces. Currently, the Playwright scrapers tightly couple fetching, parsing, and database persistence (`write_jd`). Since not all LLM clients natively possess a web fetcher, we will build a simple native Python fetch tool exposed via MCP. This allows agents to fetch public URLs lightweightly and then route the extracted data into a new standalone tool `save_job_description`. Both flows will ultimately funnel into the exact same standard persistence and application-creation pipeline.

## Functional Requirements
1. **New MCP Tool `fetch_public_job_url`** (or similar name):
   - Accepts a `url`.
   - Uses a lightweight HTTP library (e.g., `requests`, `urllib`, or `trafilatura` if available) to download and extract the readable text of a public webpage.
   - Returns the raw or mildly cleaned text content to the agent.
2. **New MCP Tool `save_job_description`**:
   - Accepts parameters: `company`, `title`, `url`, `description`, `location` (optional), and `applicants` (optional).
   - Internally instantiates a `Job` dataclass and delegates to the existing `write_jd` method for PostgreSQL upsert and file generation.
   - Returns the generated `slug` so agents can pass it directly to `create_application_from_job`.
3. **Update MCP Server Docstrings**:
   - Clearly document `extract_job_details` as the "Authenticated Browser Flow" specifically for complex login-walled pages (like LinkedIn).
   - Document `fetch_public_job_url` and `save_job_description` as the "Direct/Public Flow", directing agents to use them for public job links to bypass heavy browser overhead.

## Non-Functional Requirements
1. **Composability**: The design must treat persistence (`write_jd`) and document generation (`create_application_from_job`) as universal endpoints regardless of how the job data was fetched.
2. **Testing Restructure**: 
   - Add unit tests for `fetch_public_job_url` and `save_job_description` isolating them from complex browser logic.
   - Expand E2E tests to cover the "Direct Save Flow" (mocking `fetch_public_job_url` -> `save_job_description` -> `create_application_from_job`).

## Acceptance Criteria
1. The new tools `fetch_public_job_url` and `save_job_description` are successfully exposed via the MCP server.
2. Calling `save_job_description` successfully writes the data to the PostgreSQL database and `vault/jds/` directory.
3. The returned slug from `save_job_description` successfully triggers `create_application_from_job` without errors.
4. Unit and E2E tests validate the composable workflow explicitly.

## Out of Scope
- Removing the Playwright `extract_job_details` tool entirely (it will be kept as the authenticated fallback).
- Modifying the downstream `cv-tailor new` or `pdf` logic.
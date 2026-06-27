# Specification: Gmail Workflow Restructuring

## Overview
The goal of this track is to decompose the current monolithic Gmail ingest workflow (`run_gmail_hunt_workflow`) into three modular workflows. The core processing capabilities (Gmail search, URL extraction, job page scraping, LLM tailoring) already exist. The objective is to expose them independently so that agents or users can incrementally query for lists of jobs, extract the full details on demand, and generate applications when desired, retiring the old "one-click" pipeline.

## Architectural Changes

### 1. New Modular Workflows
We will define three separate workflows in `engine/workflows/gmail_ingest.py` (or related workflow modules):

1. **`list_gmail_jobs_workflow(provider: str, query: str = "is:unread", limit: int = 10)`**
   - *Purpose:* Searches the specified provider's Gmail alerts, extracts job links from the email bodies, performs basic URL normalization/deduplication, and returns a lightweight list of discovered jobs (tentative `job_id`, `job_url`, and basic contextual metadata like email `subject`).
   - *Returns:* JSON list of tentative job records.

2. **`extract_job_details_workflow(url: str)`**
   - *Purpose:* Given a specific job URL, executes the Playwright scraper in an isolated process to capture the full job description. Inserts the completed record into the PostgreSQL `jobs` table.
   - *Returns:* The fully captured job record (or its slug/DB confirmation).

3. **`create_application_from_job_workflow(slug: str)`**
   - *Purpose:* Executes the tailoring pipeline (`cv-tailor new <slug>`, renders PDF, uploads to Drive, and syncs status).
   - *Note:* This largely relies on the existing `create_application_workflow` and PDF/upload wrappers, but will be formalized as the final step of the new trilogy.

### 2. Retiring the Old Workflow
The legacy `run_gmail_hunt_workflow` function handles all steps (search -> parse -> scrape -> DB -> score -> tailor -> generate -> upload) iteratively. It must be marked as deprecated or removed entirely from `engine/workflows/gmail_ingest.py` and the MCP tool exports.

### 3. MCP Tool Mapping
The `engine/mcp/server.py` must be updated to expose these three distinct modular tools instead of the monolithic `search_gmail_alerts` pipeline.
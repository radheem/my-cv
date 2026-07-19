# Specification: Closed-Loop Application Status Sync & Generic Gmail Search

## Overview
Develop a dual-capability Gmail search system within the MCP server to close the loop on job application tracking. This track will expose two powerful tools: a generic Gmail search tool for ad-hoc agent queries (e.g., invoices, generic company terms) and an intelligent, context-aware application update scanner. The intelligent scanner queries the local DuckDB instance for a specific job application, automatically constructs a highly targeted Boolean search query (scoped by the application's timeline), and returns recruiter email bodies so the LLM agent can evaluate sentiment, classify the response (e.g., "interview", "rejected"), and sync the updated status to the database.

## Functional Requirements
### Tool 1: `search_gmail` (Generic Search)
- **Inputs:** `query` (str, standard Gmail search query), `limit` (int, max results, default 10), `include_bodies` (bool, default True).
- **Behavior:** Connects to the existing Gmail Apps Script API to execute the search.
- **Output:** Returns a JSON list of matching email threads/messages. When `include_bodies` is True, the full text of each email is included; otherwise, only basic metadata (sender, date, subject, snippet) is returned.

### Tool 2: `check_application_updates` (Intelligent Lookup)
- **Inputs:** `slug` (str, the application's unique identifier).
- **Behavior:** 
  1. Queries DuckDB to retrieve the `company` name, `job_title`, and `date_found` for the given slug.
  2. Constructs a dynamic Gmail Boolean query (e.g., `"Company Name" AND ("Application" OR "Interview" OR "Status" OR "Offer" OR "Resume") after:YYYY/MM/DD`).
  3. Executes the search, pulling full email bodies for any matches.
- **Output:** Returns a structured JSON payload containing the matched emails to allow the LLM to determine the application's current status.

## Non-Functional Requirements
- **Performance:** Gmail API calls via the Apps Script proxy should resolve in under 5 seconds.
- **Security:** Tools execute strictly in read-only mode regarding Gmail (no deletion or sending capabilities).
- **Decoupling:** Email search workflows must not directly modify the DuckDB application status; they simply supply the context for the agent to decide and then invoke the existing `update_application_status` tool.

## Acceptance Criteria
- The `search_gmail` tool successfully returns emails matching a generic query (e.g., "invoice"), correctly toggling full body fetching based on the `include_bodies` flag.
- The `check_application_updates` tool successfully constructs a date-scoped, company-specific query for an existing database slug and returns relevant email text.
- E2E tests verify the new MCP tools are correctly registered and invokable by LLM clients.
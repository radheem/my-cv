# Specification: Fraunhofer Job Alerts MCP Tool

## Overview
Expand the existing Model Context Protocol (MCP) server for `cv-tailor` to include an on-demand job link extraction tool for Fraunhofer email alerts. This builds upon the pattern established for LinkedIn, Glassdoor, and Indeed.

## Functional Requirements
- **Configuration Update:** Extend `config/search.yml` to map the `fraunhofer` key to the email address `fraunhofer-jobnotification@noreply12.jobs2web.com` under `gmail_alerts`.
- **MCP Tool Creation:** Add a new function `list_gmail_fraunhofer_jobs` to `engine/mcp/server.py`.
- **Workflow Integration:** The new MCP tool must delegate to the existing `list_gmail_jobs_workflow("fraunhofer", query, limit)` method to extract job metadata and links.

## Non-Functional Requirements
- Maintain consistency with existing `list_gmail_*_jobs` tools.
- Requires no UI/CLI changes, explicitly driven by the MCP server interface for on-demand execution.

## Acceptance Criteria
- [ ] `config/search.yml` contains the Fraunhofer sender email.
- [ ] `engine/mcp/server.py` exposes the `list_gmail_fraunhofer_jobs` tool.
- [ ] Testing the new tool via MCP successfully queries Gmail for `from:fraunhofer-jobnotification@noreply12.jobs2web.com` and parses Fraunhofer job links.

## Out of Scope
- Creating new backend URL scrapers/extractors.
- Adding cron jobs (Tool will run on-demand via MCP).
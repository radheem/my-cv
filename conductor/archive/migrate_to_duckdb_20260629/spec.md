# Specification: Migrate DB to DuckDB

## Overview
Migrate the `cv-tailor` project's state management from a local PostgreSQL database container to a purely local, file-based architecture using DuckDB as an in-memory query engine. This eliminates the dependency on Docker/PostgreSQL, resolves multi-source-of-truth conflicts, and establishes the local filesystem (`vault/jds/*.json` and `applications/<slug>/index.md`) as the absolute source of truth. 

## Functional Requirements
- **PostgreSQL Removal:** Remove all PostgreSQL/psycopg dependencies and setup instructions from the project.
- **In-Memory DuckDB Engine:** Implement a DuckDB connection factory that dynamically loads data from the filesystem (`vault/jds/` JSONs and `applications/` frontmatter) into in-memory SQL tables.
- **Query Compatibility:** The existing MCP `query` tool and internal metrics functions must continue to evaluate `SELECT` / `WITH` statements successfully using DuckDB.
- **Filesystem Source of Truth:** 
  - New job descriptions must write directly to `vault/jds/` (and create local backups).
  - Application state transitions must write directly to the frontmatter of `applications/<slug>/index.md`.
- **Auto-export CSVs:** Implementing automatic tracker CSV generation whenever application states change, ensuring the local `tracker.csv` is always up to date.
- **Preserve Integrations:** The Google Sheets synchronization (`cv-tailor status push/pull`) and Google Drive PDF upload workflows must continue to function by interfacing with the file-based source of truth or the DuckDB engine.

## Non-Functional Requirements
- **Performance:** Dynamic loading of local files into DuckDB must be fast enough to not noticeably degrade CLI or MCP tool responsiveness (e.g., sub-100ms loading).
- **Zero-Config Setup:** The application must run without requiring any database daemons or external service setup.

## Out of Scope
- Modifications to the LLM tailoring logic or RAG ranking algorithms.
- Changes to the Google Apps Script proxy code.
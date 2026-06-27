# Specification: Read-Only MCP Tools for User Profile Data

## Overview
To provide external AI agents with direct access to the user's core identity and career history, we will expose the three foundational "source of truth" files located in the `data/` directory as individual, read-only MCP tools. This allows agents to fetch exact context on demand without executing shell commands.

## Functional Requirements
1. **New MCP Tool `get_user_profile`**:
   - Reads `data/profile.yml`.
   - Parses the YAML and returns it as a JSON string for easy consumption by the agent.
2. **New MCP Tool `get_user_projects`**:
   - Reads `data/projects.yml`.
   - Parses the YAML and returns it as a JSON string.
3. **New MCP Tool `get_master_cv`**:
   - Reads `data/master-cv.md`.
   - Returns the raw Markdown text exactly as it exists on disk.
4. **Error Handling**:
   - Each tool must safely catch `FileNotFoundError` or parsing errors and return a clean `ERROR:` string instead of crashing the server process.

## Non-Functional Requirements
- **Read-Only**: These tools must only read data; they should not mutate any files.
- **Path Resolution**: The tools must resolve paths relative to the project root reliably (e.g., using a centralized `ROOT` path constant similar to `engine/config.py` or `pathlib`).

## Acceptance Criteria
1. The three new tools (`get_user_profile`, `get_user_projects`, `get_master_cv`) are successfully registered and exposed by the MCP server.
2. Unit tests are added to `tests/test_mcp_server.py` verifying that each tool correctly reads and returns the corresponding data file.
3. All tests pass successfully.

## Out of Scope
- Tools for modifying the profile data (mutation).
- Aggregating the data into a single tool (as explicitly rejected by the user).
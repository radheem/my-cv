# Implementation Plan: Migrate DB to DuckDB

## Phase 1: Infrastructure & Dependencies Update [checkpoint: 03d573a]
- [x] Task: Remove `psycopg` dependencies from `pyproject.toml`, `Makefile`, and `requirements.txt` (if applicable) and replace them with `duckdb`. 03d573a
- [x] Task: Update documentation (`docs/setup.md`, `docs/architecture.md`) to reflect the removal of PostgreSQL and Docker, emphasizing the zero-config DuckDB approach. 03d573a
- [x] Task: Update the `docker-compose.yml` to remove the `db` service. 03d573a
- [x] Task: Conductor - User Manual Verification 'Phase 1: Infrastructure & Dependencies Update' (Protocol in workflow.md) 03d573a

## Phase 2: DuckDB Engine Implementation [checkpoint: e600f81]
- [x] Task: Rewrite `engine/shared/db.py` to initialize an in-memory DuckDB connection. e600f81
    - [x] Sub-task: Implement a function to parse all `vault/jds/*.json` files into a `jobs` table. e600f81
    - [x] Sub-task: Implement a function to parse frontmatter from all `applications/*/index.md` files into an `applications` table. e600f81
- [x] Task: Refactor the MCP SQL guard (`engine/mcp/sqlguard.py` if applicable) or ensure DuckDB's execution of read-only queries remains secure. e600f81
- [x] Task: Update the `cv-tailor_query` MCP tool logic in `engine/mcp/server.py` to execute against the DuckDB connection. e600f81
- [x] Task: Conductor - User Manual Verification 'Phase 2: DuckDB Engine Implementation' (Protocol in workflow.md) e600f81

## Phase 3: Filesystem Write Operations [checkpoint: 06319f2]
- [x] Task: Refactor `engine/domains/linkedin/jobs.py` (`write_jd`) to eliminate Postgres `INSERT/UPDATE` operations, ensuring it exclusively manages `vault/jds/` JSON files and creates/updates `index.md` appropriately. 06319f2
- [x] Task: Refactor state transition logic in `engine/cli.py` (`cmd_status`) to modify `applications/<slug>/index.md` directly. 06319f2
- [x] Task: Implement the "Auto-export CSVs" logic to automatically regenerate `applications/tracker.csv` whenever a status is updated locally. 06319f2
- [x] Task: Conductor - User Manual Verification 'Phase 3: Filesystem Write Operations' (Protocol in workflow.md) 06319f2

## Phase 4: Integrations & Cleanup [checkpoint: 57e6bc7]
- [x] Task: Update Google Sheets sync logic (`_push_to_sheets`, `_pull_sheet_statuses`, `_sync_remote_statuses`) in `engine/cli.py` to seamlessly read/write from the file system and DuckDB engine. cb7d43a
- [x] Task: Audit and repair all unit tests in `tests/` that previously mocked or required PostgreSQL to now use DuckDB or mock the filesystem. 57e6bc7
- [x] Task: Conductor - User Manual Verification 'Phase 4: Integrations & Cleanup' (Protocol in workflow.md) 57e6bc7
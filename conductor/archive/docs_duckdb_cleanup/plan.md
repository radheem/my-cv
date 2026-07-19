# Docs and Code Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up legacy PostgreSQL references across the documentation and remove deprecated database synchronization commands from the codebase, accurately reflecting the current DuckDB serverless architecture.

**Architecture:** The update touches both the Python CLI/Database modules and the Markdown documentation. Code changes involve pruning dead/no-op functions related to PostgreSQL push/pull. Documentation changes involve surgical replacements of "PostgreSQL" with "DuckDB" (or filesystem) and documenting the previously undocumented `analyze` and `gmail` commands.

**Tech Stack:** Python (CLI), Markdown, Mermaid (Sequence Diagrams)

---

### Task 1: Clean up Legacy Code in Database Module

**Files:**
- Modify: `engine/shared/db.py`

- [ ] **Step 1: Write/Verify the failing test (if applicable)**
Since we are removing dead code, run existing tests to ensure we don't break anything.
Run: `make test`
Expected: PASS

- [ ] **Step 2: Remove legacy migration function**
Remove the `migrate_legacy_data(applications_dir: str = "applications") -> int` function definition from `engine/shared/db.py` since it is a no-op for DuckDB.

- [ ] **Step 3: Verify tests still pass**
Run: `make test`
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add engine/shared/db.py
git commit -m "refactor(db): remove dead legacy postgres migration function"
```

### Task 2: Remove Legacy CLI Database Commands

**Files:**
- Modify: `engine/cli.py`

- [ ] **Step 1: Remove dead command functions**
Remove `cmd_db_push`, `cmd_db_pull`, and `cmd_db_migrate_legacy` from `engine/cli.py`. Leave `cmd_db_export` intact.

- [ ] **Step 2: Remove argument parsers for dead commands**
In the `main` function of `engine/cli.py`, remove the subparser setups for `pdb_migrate`, `pdb_push`, and `pdb_pull`. Leave `pdb_export`.

- [ ] **Step 3: Test CLI parsing**
Run: `cv-tailor db --help`
Expected: Only the `export` command should be listed under the `db` subcommand.

- [ ] **Step 4: Commit**
```bash
git add engine/cli.py
git commit -m "refactor(cli): remove legacy db push, pull, and migrate commands"
```

### Task 3: Update Core Documentation (README, Setup, CLI)

**Files:**
- Modify: `README.md`
- Modify: `docs/setup.md`
- Modify: `docs/cli.md`

- [ ] **Step 1: Fix README runbook links**
In `README.md`, update the `docs/runbooks.md` link to point to `docs/runbooks/` or specific runbooks inside the directory. Ensure no stale PostgreSQL references exist.

- [ ] **Step 2: Update Setup docs**
In `docs/setup.md`, verify the statements about the file-based architecture and ensure no lingering PostgreSQL installation steps remain.

- [ ] **Step 3: Update CLI docs and document new commands**
In `docs/cli.md`:
  - Remove references to `cv-tailor db push`, `cv-tailor db pull`, etc.
  - Fix mentions of "PostgreSQL" in the `cv-tailor status` command description to say "DuckDB" or "filesystem".
  - Add a new section detailing the `cv-tailor analyze` command.
  - Add a new section detailing the `cv-tailor gmail` commands (`search`, `read`, `modify`, `send`).

- [ ] **Step 4: Commit**
```bash
git add README.md docs/setup.md docs/cli.md
git commit -m "docs: update core docs for duckdb and document new cli commands"
```

### Task 4: Update Architectural and Workflow Documentation

**Files:**
- Modify: `docs/architecture.md`
- Modify: `docs/mcp-workflows.md`

- [ ] **Step 1: Update Architecture Diagrams and Text**
In `docs/architecture.md`, replace all "PostgreSQL" mentions with "DuckDB" or "Filesystem". Update the Mermaid diagrams to reflect the serverless DB. Update the `Repository layout` descriptions for `engine/db.py`.

- [ ] **Step 2: Update MCP Workflows**
In `docs/mcp-workflows.md`, replace all references to PostgreSQL upserts and state syncs with the corresponding DuckDB terminology. Update Mermaid sequence diagrams.

- [ ] **Step 3: Commit**
```bash
git add docs/architecture.md docs/mcp-workflows.md
git commit -m "docs: update architecture and workflow docs to reflect duckdb migration"
```

### Task 5: Update Runbooks and Domains Documentation

**Files:**
- Modify: `docs/domains/fraunhofer.md`, `docs/domains/gmail.md`
- Modify: `docs/runbooks/create-application.md`, `docs/runbooks/mcp-server.md`, `docs/runbooks/search-fraunhofer.md`, `docs/runbooks/search-emails.md`, `docs/runbooks/search-linkedin.md`

- [ ] **Step 1: Update Domains Documentation**
Replace "PostgreSQL" with "DuckDB" in `docs/domains/*.md`.

- [ ] **Step 2: Update Runbooks**
Review all `docs/runbooks/*.md`. Change the title of the MCP Server runbook from "PostgreSQL MCP Server" to "DuckDB MCP Server". Replace any "PostgreSQL" text with "DuckDB" or "Filesystem" across all runbooks.

- [ ] **Step 3: Commit**
```bash
git add docs/domains/ docs/runbooks/
git commit -m "docs: scrub postgresql references from domains and runbooks"
```

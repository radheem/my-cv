# cv-tailor PostgreSQL MCP Server Design

- **Date:** 2026-06-25
- **Status:** Approved
- **Author:** Gemini CLI

---

## 1. Overview & Objectives

The goal is to introduce an MCP (Model Context Protocol) Server into the `cv-tailor` project based on the successful `iris-analytics` prototype. This server will securely expose the `cv-tailor` PostgreSQL database (`jobs` and `applications` tables) to any compatible AI agent (e.g. Claude Desktop or other MCP clients).

This empowers AI agents to seamlessly inspect job hunting metrics, retrieve top-scoring jobs, read tailored CVs and cover letters, and track application lifecycle statuses—all by running dynamic SQL queries over the primary source of truth!

---

## 2. Architecture & Security

### Secure Open-Query Surface
Unlike restrictive REST APIs with predefined endpoints, this MCP server provides "analytic supremacy" by offering an open-query surface. The agent learns the schema via an ontology tool, and then writes its own read-only PostgreSQL queries.

To guarantee system integrity, we will implement a rigorous `sqlguard` layer:
*   **Whitelist Filtering:** Queries must strictly begin with `SELECT` or `WITH`.
*   **No Multi-statement Execution:** Semicolons within the payload are strictly rejected.
*   **Subquery Wrapping:** Queries are wrapped as `SELECT * FROM (<sql>) _q LIMIT <row_cap>` to ensure pagination/row limits (capped at 1000) and prevent arbitrary mutations.
*   **Transaction Read-Only**: psycopg connections will be requested with read-only transaction parameters (if needed) or natively rely on the `SELECT` enforcement of the guard.

### Pure Python Integration
Rather than spawning `psql` shell subprocesses like the external prototype, our server will natively import and utilize `engine.db.get_conn()`. This provides robust psycopg3 connection pooling, dramatically reduces latency, and removes the need for system-level dependencies.

---

## 3. Server Implementation

### Dependencies
We will add `"mcp[cli]>=1.2.0"` to `pyproject.toml` under a new optional dependency group: `mcp`.

### Core Modules (`engine/mcp/`)

#### 1. `engine/mcp/sqlguard.py`
Contains the strict security parser:
```python
import re

_SELECT_RE = re.compile(r"(?is)^\s*(with|select)\b")
ROW_CAP = 1000

def guard_and_wrap(sql: str, row_cap: int = ROW_CAP) -> str:
    s = sql.strip().rstrip(";").strip()
    if not _SELECT_RE.match(s):
        raise ValueError("only SELECT / WITH queries are allowed")
    if ";" in s:
        raise ValueError("multiple statements are not allowed")
    return f"SELECT * FROM ({s}) _q LIMIT {row_cap}"
```

#### 2. `engine/mcp/server.py`
Contains the FastMCP server and tools:

**Tool 1: `cv_tailor_ontology()`**
Returns a structured JSON schema outlining the exact structures, data types, and primary/foreign keys of the `jobs` and `applications` tables. It acts as the "decoder ring" for the agent.

**Tool 2: `query(sql: str)`**
Receives raw SQL from the agent, passes it through `sqlguard.guard_and_wrap(sql)`, opens a connection via `engine.db.get_conn()`, executes the wrapped read-only query using `psycopg`, and returns the resultant rows as JSON!

### Entrypoint
We will define a new CLI console script in `pyproject.toml` so the MCP server can be started easily by MCP clients:
```toml
cv-tailor-mcp = "engine.mcp.server:main"
```
Or started locally via `uv run cv-tailor-mcp`.

---

## 4. Error Handling and Testing
*   **Unit tests** (`tests/test_mcp_sqlguard.py`): Will rigorously test `sqlguard` to verify it blocks `UPDATE`, `INSERT`, `DROP`, multi-statement attacks, and correctly wraps valid `SELECT` and `WITH` statements.
*   **Integration tests** (`tests/test_mcp_server.py`): Will test the ontology generation and database query execution.

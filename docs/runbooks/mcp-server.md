# Runbook — PostgreSQL MCP Server (SSE & STDIO)

This runbook covers how to launch, configure, connect, and operate the **cv-tailor PostgreSQL MCP (Model Context Protocol) Server**, allowing external AI agents (like Claude Desktop, Claude Code, or Gemini CLI) to securely query your database and execute pipeline actions.

---

## 1. Overview of Capabilities

The MCP server connects directly to your PostgreSQL database and exposes a unified, secure proxy for the entire job hunting pipeline. It provides two categories of tools:

### 🛡️ Read-Only Database Queries
*   `cv_tailor_ontology`: Exposes the database schema layouts, column types, and relationships (the perfect "decoder ring" for connecting agents).
*   `query`: Evaluates safe, read-only `SELECT` and `WITH` statements, preventing SQL injections or mutations, and capping return results to a hard **1,000-row limit**.

### 🚀 Programmatic Action Workflows (Safe, Non-Shell Python Actions)
*   `search_gmail_alerts`: Triggers the complete Gmail alert-to-application ingestion pipeline.
*   `create_application`: Programmatically generates tailored CVs and cover letter drafts on disk.
*   `score_jobs`: Scores and prioritizes unscored database job descriptions against your master profile terms.
*   `update_application_status`: Updates job tracking lifecycles.
*   `sync_status_to_sheets`: Synchronizes PostgreSQL application statuses directly with Google Sheets.

---

## 2. Option A: Containerized SSE Service (Recommended)

This runs the MCP server as a platform-agnostic, background Server-Sent Events (SSE) HTTP microservice. This is the recommended choice as it requires no local Python environment or path configurations on your host.

### Step 1: Boot the Background Service
Launch the PostgreSQL database and the MCP server service using Docker Compose:

```bash
# Start in the background:
make docker-build             # build unified image
docker compose up -d db mcp   # launch Postgres and MCP service
```

*The server will begin listening on host port **`5000`** with standard Xvfb virtual displays running in the container background (so Playwright runs launched by MCP have an X11 context).*

### Step 2: Verify Log Health
Check that the server process booted and initialized successfully:

```bash
docker compose logs mcp
```
*Expected Output:*
```text
INFO:     Started server process [7]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

### Step 3: Wire into Claude Desktop (or any SSE client)
Expose the server to Claude Desktop by adding this configuration to your local `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cv-tailor-mcp-sse": {
      "url": "http://localhost:5000/mcp"
    }
  }
}
```

---

## 3. Option B: Local STDIO Execution (Stdio Transport)

If you prefer to execute the MCP server locally via standard input/output (Stdio) directly through your shell, you can start the console script on your host.

### Step 1: Run the Server Command
Start the Stdio transport server using `uv`:

```bash
make mcp
# or: uv run cv-tailor-mcp
```

### Step 2: Wire into Claude Desktop / Claude Code
Configure your client to execute the CLI command directly:

```json
{
  "mcpServers": {
    "cv-tailor-mcp-stdio": {
      "command": "uv",
      "args": [
        "--project",
        "/home/radr/pers/radr-cv",
        "run",
        "cv-tailor-mcp"
      ],
      "env": {
        "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/cv_tailor"
      }
    }
  }
}
```

---

## 4. Operational Troubleshooting

### DB Connection Refused inside Container?
The MCP container is pre-configured with Docker-awareness. It checks if it is running inside Docker, and automatically replaces `localhost` inside your `.env` `DATABASE_URL` with the Docker Compose hostname `db`. No manual configuration is required.

### Playwright / Xvfb Errors?
Mutating tasks (like `search_gmail_alerts`) navigate through Playwright. Inside the container, these tasks run securely because the `mcp` service is bound to Xvfb on display `:99`. If you ever experience issues, inspect browser logs:
```bash
docker compose exec mcp ls -la /tmp
```

### How to use in natural language (Examples)
Once connected, try speaking to your model:
*   *“Check cv-tailor for high scoring unapplied jobs.”* (Triggers `query`)
*   *“Expose my applications tracking schema.”* (Triggers `cv_tailor_ontology`)
*   *“Update the status of my scouter-engineer application to 'applied'.”* (Triggers `update_application_status`)

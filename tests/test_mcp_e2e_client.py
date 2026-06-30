import asyncio
import json
import os
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from engine.shared.db import get_conn, init_db

@pytest.fixture(scope="module")
def server_params():
    """Returns the local stdio launch parameters for the cv-tailor MCP server."""
    return StdioServerParameters(
        command="uv",
        args=["run", "cv-tailor-mcp"],
        env=os.environ
    )

@pytest.mark.anyio
async def test_mcp_e2e_server_capabilities(server_params):
    """E2E Test: list tools and verify server capabilities."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            
            # Verify required tools are registered
            assert "cv_tailor_ontology" in tool_names
            assert "query" in tool_names
            assert "list_jobs" in tool_names
            assert "create_application_from_job" in tool_names
            assert "list_applications" in tool_names
            assert "analyze_cluster_keywords" in tool_names
            assert "suggest_taxonomy_updates" in tool_names
            assert "search_gmail" in tool_names
            assert "check_application_updates" in tool_names

@pytest.mark.anyio
async def test_mcp_e2e_sql_queries_and_guard(server_params):
    """E2E Test: run read-only SQL queries via 'query' tool and confirm SQL Guard restricts mutations."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Test a valid read-only query
            res = await session.call_tool("query", {"sql": "SELECT COUNT(*) FROM jobs"})
            assert res.content and len(res.content) > 0
            data = json.loads(res.content[0].text)
            assert "rows" in data
            assert len(data["rows"]) == 1
            assert "count" in data["rows"][0]
            
            # 2. Test SQL Guard rejection on mutations
            res_err = await session.call_tool("query", {"sql": "DROP TABLE jobs"})
            assert res_err.content and len(res_err.content) > 0
            data_err = json.loads(res_err.content[0].text)
            assert "error" in data_err
            assert "only select / with queries" in data_err["error"].lower()

@pytest.mark.anyio
async def test_mcp_e2e_async_tailoring(server_params):
    """E2E Test: trigger async tailoring and verify queued status."""
    # Ensure a mock job exists in the DB to test queueing
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform)
                VALUES ('e2e-mcp-test-job-999', 'e2e-mcp-test-slug-999', 'E2E Corp', 'E2E Engineer', 'file', 'other')
                ON CONFLICT (job_id) DO UPDATE SET slug = EXCLUDED.slug
            """)
            conn.commit()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Trigger async tailoring
            res = await session.call_tool("create_application_from_job", {"slug": "e2e-mcp-test-slug-999"})
            assert res.content and len(res.content) > 0
            data = json.loads(res.content[0].text)
            
            # Confirm status is queued or generating
            assert "status" in data
            assert data["status"] in ("queued", "generating")

async def run_standalone():
    """Standalone runner for direct script execution."""
    print("════════════════════════════════════════════════════════")
    print("  Standalone DuckDB MCP Server E2E Client Test")
    print("════════════════════════════════════════════════════════\n")
    
    params = StdioServerParameters(
        command="uv",
        args=["run", "cv-tailor-mcp"],
        env=os.environ
    )
    
    try:
        with get_conn():
            pass
    except Exception as e:
        print(f"  ERROR: DuckDB initialization failed: {e}")
        return

    print("── Connecting to MCP Server via Stdio...")
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("  Successfully connected.")
            
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            print(f"  Found {len(tool_names)} tools: {', '.join(tool_names)}")
            
            print("\n── Testing read-only query...")
            res = await session.call_tool("query", {"sql": "SELECT COUNT(*) FROM jobs"})
            print(f"  Result: {res.content[0].text}")
            
    print("\n════════════════════════════════════════════════════════")
    print("  Standalone E2E MCP Client Test Executed Successfully!")
    print("════════════════════════════════════════════════════════")

if __name__ == "__main__":
    asyncio.run(run_standalone())

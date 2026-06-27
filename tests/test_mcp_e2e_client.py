import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    print("════════════════════════════════════════════════════════")
    print("  PostgreSQL MCP Server E2E Client Test")
    print("════════════════════════════════════════════════════════\n")

    # Configure server parameters for local Stdio launch
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "cv-tailor-mcp"],
        env={
            **os.environ,
            "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/cv_tailor",
            "LINKEDIN_PACE": "1"
        }
    )

    print("── Step 1: Connecting to MCP Server via Stdio...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("  Successfully initialized client session.")

            # 1. List registered tools
            print("\n── Step 2: Listing Registered Tools...")
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            print(f"  Found {len(tool_names)} tools:")
            for name in sorted(tool_names):
                print(f"    - {name}")

            assert "search_gmail_alerts" in tool_names
            assert "create_application" in tool_names
            assert "list_jobs" in tool_names
            assert "query" in tool_names

            # 2. Call list_jobs to verify database query
            print("\n── Step 3: Verifying 'list_jobs' Database Tool...")
            jobs_res = await session.call_tool("list_jobs", {"unapplied_only": False, "limit": 2})
            jobs_data = json.loads(jobs_res.content[0].text)
            print(f"  Query result keys: {list(jobs_data.keys())}")
            if "jobs" in jobs_data:
                print(f"  Found {len(jobs_data['jobs'])} existing job records in database.")

            # 3. Call search_gmail_alerts to fetch, parse, and score top 1 job
            print("\n── Step 4: Executing 'search_gmail_alerts' (Limit 1)...")
            search_res = await session.call_tool(
                "search_gmail_alerts",
                {"filter_query": "linkedin job alert", "limit": 1}
            )
            print("  Ingestion logs:")
            print(search_res.content[0].text)

            # 4. Use list_jobs to find the highest-scoring unapplied job slug
            print("\n── Step 5: Finding Highest Scoring Unapplied Job Slug...")
            unapplied_res = await session.call_tool("list_jobs", {"unapplied_only": True, "limit": 1})
            unapplied_data = json.loads(unapplied_res.content[0].text)
            
            if not unapplied_data.get("jobs"):
                print("  No unapplied jobs found to tailor. Exiting.")
                return

            target_job = unapplied_data["jobs"][0]
            target_slug = target_job["slug"]
            print(f"  Target Job found: {target_job['company']} - {target_job['title']} (Slug: {target_slug})")

            # 5. Call create_application to generate CV/Cover Letter drafts
            print(f"\n── Step 6: Executing 'create_application' on slug: '{target_slug}'...")
            app_res = await session.call_tool("create_application", {"source": target_slug})
            print("  Application results:")
            print(app_res.content[0].text)

    print("\n════════════════════════════════════════════════════════")
    print("  E2E MCP Client Test Executed Successfully!")
    print("════════════════════════════════════════════════════════")

if __name__ == "__main__":
    asyncio.run(main())

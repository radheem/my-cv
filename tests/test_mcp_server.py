import json
import pytest
import psycopg
from engine.db import get_conn, init_db
from engine.mcp.server import cv_tailor_ontology, query


def test_mcp_ontology():
    ont = json.loads(cv_tailor_ontology())
    assert "tables" in ont
    assert "jobs" in ont["tables"]
    assert "applications" in ont["tables"]


def test_mcp_query():
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL offline. Skipping MCP server queries integration test.")

    init_db()
    
    # 1. Test basic COUNT (integer output)
    res = json.loads(query("SELECT COUNT(*) FROM jobs"))
    assert "rows" in res
    assert len(res["rows"]) >= 1
    assert "count" in res["rows"][0]

    # 2. Test aggregation queries (resulting in Decimal / numeric values)
    res_avg = json.loads(query("SELECT AVG(COALESCE(score, 0))::numeric as avg_score FROM jobs"))
    assert "rows" in res_avg
    assert "avg_score" in res_avg["rows"][0]
    # Check that decimal translates successfully into float or is serializable
    assert isinstance(res_avg["rows"][0]["avg_score"], (int, float))

    # 3. Test datetime representation serialization (should match ISO-8601)
    res_dates = json.loads(query("SELECT NOW() as current_time"))
    assert "rows" in res_dates
    assert "current_time" in res_dates["rows"][0]
    assert isinstance(res_dates["rows"][0]["current_time"], str)

    # 4. Test execution isolation & error packaging on syntax failure
    res_err = json.loads(query("SELECT invalid_column_name_xyz FROM jobs"))
    assert "error" in res_err
    assert "does not exist" in res_err["error"]


def test_mcp_list_and_get_tools():
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL offline. Skipping MCP server tools test.")

    from engine.mcp.server import list_applications, get_application, list_jobs, get_job, search_jobs
    
    # Run tests on the list tools
    res_jobs = json.loads(list_jobs(unapplied_only=False, limit=2))
    assert "jobs" in res_jobs
    
    res_apps = json.loads(list_applications(limit=2))
    assert "applications" in res_apps

    # Search jobs
    res_search = json.loads(search_jobs("engineer", limit=2))
    assert "results" in res_search


def test_mcp_search_gmail_platform_tools(monkeypatch):
    from engine import gmail
    from engine.mcp import server

    monkeypatch.setattr(gmail, "search_emails", lambda query, limit, include_bodies: [
        {"threadId": "123", "subject": "Mock Job Alert", "messages": [
            {"id": "msg1", "sender": "test@test.com", "subject": None, "snippet": "Job details"}
        ]}
    ])

    # Test LinkedIn Tool
    res_li = json.loads(server.search_gmail_linkedin_jobs(limit=2))
    assert "threads" in res_li
    assert len(res_li["threads"]) == 1
    assert res_li["threads"][0]["messages"][0]["subject"] == "Mock Job Alert"

    # Test Glassdoor Tool
    res_gd = json.loads(server.search_gmail_glassdoor_jobs(limit=2))
    assert "threads" in res_gd
    assert len(res_gd["threads"]) == 1

    # Test Indeed Tool
    res_ind = json.loads(server.search_gmail_indeed_jobs(limit=2))
    assert "threads" in res_ind
    assert len(res_ind["threads"]) == 1


def test_mcp_new_gmail_modular_tools(monkeypatch):
    from engine.mcp import server
    from engine import gmail
    import json
    
    # 1. Test list_gmail_jobs
    mock_body = """
    Software Engineer
    Acme Corp
    Munich
    https://www.linkedin.com/jobs/view/12345/
    """
    monkeypatch.setattr(gmail, "search_emails", lambda query, limit, include_bodies: [
        {"threadId": "123", "subject": "Mock Alert", "messages": [
            {"id": "msg1", "sender": "test@test.com", "subject": "Mock Alert", "body": mock_body}
        ]}
    ])
    
    res = json.loads(server.list_gmail_jobs(provider="linkedin", query="is:unread", limit=2))
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["job_id"] == "12345"
    assert res[0]["company"] == "Acme Corp"
    
    # 2. Test extract_job_details
    import engine.workflows.gmail_ingest as gi
    monkeypatch.setattr(gi, "_capture_jobs_worker_func", lambda urls: (["mock-acme-slug"], ["Successfully captured"]))
    
    # Mock Process and Queue to run inline (preserving monkeypatch!)
    class MockProcess:
        def __init__(self, target, args):
            self.target = target
            self.args = args
        def start(self):
            self.target(*self.args)
        def join(self):
            pass
            
    class MockQueue:
        def __init__(self):
            self.val = None
        def put(self, val):
            self.val = val
        def get(self):
            return self.val
            
    class MockContext:
        def Queue(self):
            return MockQueue()
        def Process(self, target, args):
            return MockProcess(target, args)
            
    import multiprocessing
    monkeypatch.setattr(multiprocessing, "get_context", lambda method: MockContext())
    
    res_extract = server.extract_job_details("https://www.linkedin.com/jobs/view/12345/")
    assert "SUCCESS" in res_extract
    assert "mock-acme-slug" in res_extract
    
    # 3. Test create_application_from_job
    from engine import cli
    calls = []
    monkeypatch.setattr(cli, "cmd_new", lambda args: calls.append("new"))
    monkeypatch.setattr(cli, "cmd_pdf", lambda args: calls.append("pdf"))
    monkeypatch.setattr(cli, "cmd_upload", lambda args: calls.append("upload"))
    monkeypatch.setattr(cli, "cmd_status", lambda args: calls.append("status"))
    
    res_create = server.create_application_from_job("mock-acme-slug")
    assert "Complete" in res_create
    assert calls == ["new", "pdf", "upload", "status"]

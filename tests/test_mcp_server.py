import json
import pytest
import psycopg
from engine.shared.db import get_conn, init_db
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


def test_mcp_specialized_gmail_tools(monkeypatch):
    from engine.domains.gmail import client as gmail
    from engine.mcp import server
    import json

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

    # Test specialized LinkedIn tool
    res_li = json.loads(server.list_gmail_linkedin_jobs(limit=2))
    assert isinstance(res_li, list)
    assert len(res_li) == 1
    assert res_li[0]["job_id"] == "12345"
    assert res_li[0]["company"] == "Acme Corp"

    # Test specialized Glassdoor tool
    res_gd = json.loads(server.list_gmail_glassdoor_jobs(limit=2))
    assert isinstance(res_gd, list)

    # Test specialized Indeed tool
    res_ind = json.loads(server.list_gmail_indeed_jobs(limit=2))
    assert isinstance(res_ind, list)

    # Test specialized Fraunhofer tool
    res_fh = json.loads(server.list_gmail_fraunhofer_jobs(limit=2))
    assert isinstance(res_fh, list)


def test_mcp_new_gmail_modular_tools(monkeypatch):
    from engine.mcp import server
    from engine.domains.gmail import client as gmail
    import json
    
    # 1. Test specialized linkedin tool (list_gmail_jobs was removed)
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
    
    res = json.loads(server.list_gmail_linkedin_jobs(query="is:unread", limit=2))
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["job_id"] == "12345"
    assert res[0]["company"] == "Acme Corp"
    
    # 2. Test extract_job_details
    import engine.domains.gmail.ingest as gi
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
    
    res_create = json.loads(server.create_application_from_job("mock-acme-slug"))
    assert res_create["status"] == "queued"


def test_mcp_3step_pipeline_e2e(monkeypatch):
    from engine.mcp import server
    from engine.domains.gmail import client as gmail
    from engine import cli
    import engine.domains.gmail.ingest as gi
    import multiprocessing
    import json

    # --- STEP 1 Mocking ---
    # Send a dummy email mock
    dummy_email_body = """
    Check out this job alert:
    Senior Cloud Engineer
    Acme Systems
    Berlin
    https://www.linkedin.com/jobs/view/999999/
    """
    monkeypatch.setattr(gmail, "search_emails", lambda query, limit, include_bodies: [
        {"threadId": "thread_999", "subject": "LinkedIn Jobs", "messages": [
            {"id": "msg_999", "sender": "jobalerts-noreply@linkedin.com", "subject": "LinkedIn Jobs", "body": dummy_email_body}
        ]}
    ])

    # --- STEP 2 Mocking ---
    monkeypatch.setattr(gi, "_capture_jobs_worker_func", lambda urls: (["acme-systems-senior-cloud-engineer-999999"], ["Successfully captured"]))

    # Mock multiprocessing for Step 2
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
            
    monkeypatch.setattr(multiprocessing, "get_context", lambda method: MockContext())

    # --- STEP 3 Mocking ---
    cli_calls = []
    monkeypatch.setattr(cli, "cmd_new", lambda args: cli_calls.append("new"))
    monkeypatch.setattr(cli, "cmd_pdf", lambda args: cli_calls.append("pdf"))
    monkeypatch.setattr(cli, "cmd_upload", lambda args: cli_calls.append("upload"))
    monkeypatch.setattr(cli, "cmd_status", lambda args: cli_calls.append("status"))

    # --- PIPELINE RUN ---
    
    # 1. Query gmail to discover the job listing
    jobs_list_res = json.loads(server.list_gmail_linkedin_jobs(limit=1))
    assert isinstance(jobs_list_res, list)
    assert len(jobs_list_res) == 1
    
    discovered_job = jobs_list_res[0]
    assert discovered_job["job_id"] == "999999"
    assert discovered_job["company"] == "Acme Systems"
    job_url = discovered_job["job_url"]
    assert job_url == "https://www.linkedin.com/jobs/view/999999/"

    # 2. Extract job details using the returned URL
    extraction_res = server.extract_job_details(job_url)
    assert "SUCCESS" in extraction_res
    assert "acme-systems-senior-cloud-engineer-999999" in extraction_res
    
    # 3. Create the application using the returned job slug
    target_slug = "acme-systems-senior-cloud-engineer-999999"
    
    # Insert mock job into DB to satisfy async check constraints
    from engine.shared.db import get_conn
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES ('999999', %s, 'Acme Systems', 'Senior Cloud Engineer', 'file', 'other', 'JD')
                ON CONFLICT (job_id) DO UPDATE SET slug = EXCLUDED.slug
            """, (target_slug,))
            conn.commit()

    application_res = json.loads(server.create_application_from_job(target_slug))
    assert application_res["status"] == "queued"


def test_mcp_fetch_public_job_url(monkeypatch):
    from engine.mcp import server
    import urllib.request
    from io import BytesIO

    # Mock urllib.request.urlopen to return mock HTML
    mock_html = b"<html><body><h1>Senior Developer</h1><p>We are hiring at Custom Corp!</p></body></html>"
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: BytesIO(mock_html))

    res = server.fetch_public_job_url("https://custom.com/jobs/987")
    assert "Senior Developer" in res
    assert "Custom Corp" in res


def test_mcp_fetch_linkedin_job(monkeypatch):
    from engine.mcp import server
    import urllib.request
    from io import BytesIO

    # Mock urllib.request.urlopen to return mock HTML
    mock_html = b"<html><body><div class='description'><h1>Staff Python Engineer</h1><p>Join us at TechCorp in Berlin!</p></div></body></html>"
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: BytesIO(mock_html))

    res = server.fetch_linkedin_job("4428933791")
    assert "Staff Python Engineer" in res
    assert "TechCorp" in res


def test_mcp_fetch_indeed_job(monkeypatch):
    from engine.mcp import server
    import urllib.request
    from io import BytesIO

    # Test Path A: Indeed returns JSON
    mock_json = b'{"jobTitle": "DevOps Engineer", "description": "Awesome indeed job"}'
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: BytesIO(mock_json))

    res = server.fetch_indeed_job("e1b8d3b1b28dd021")
    assert "DevOps Engineer" in res
    assert "Awesome indeed job" in res

    # Test Path B: Indeed returns HTML (JSON decoding fails)
    mock_html = b"<html><body><h1>Senior SRE</h1><p>Work on cloud infrastructure at Indeed.</p></body></html>"
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: BytesIO(mock_html))

    res2 = server.fetch_indeed_job("1d5c55ffd09ccd62")
    assert "Senior SRE" in res2
    assert "cloud infrastructure" in res2


def test_mcp_save_job_description():
    from engine.mcp import server
    import json

    res = server.save_job_description(
        company="Direct Corp",
        title="Direct Engineer",
        url="https://direct.com/jobs/555",
        description="This is a direct job description.",
        location="Berlin"
    )
    assert "SUCCESS" in res
    assert "direct-corp-direct-engineer" in res


def test_mcp_direct_pipeline_e2e(monkeypatch):
    from engine.mcp import server
    from engine import cli
    import urllib.request
    from io import BytesIO
    import json

    # --- STEP 1: Mock fetch ---
    mock_html = b"<html><body><h1>Platform Architect</h1><p>We need a platform architect at Cloud Systems in Munich.</p></body></html>"
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: BytesIO(mock_html))

    # --- STEP 2: Mock create application CLI actions ---
    cli_calls = []
    monkeypatch.setattr(cli, "cmd_new", lambda args: cli_calls.append("new"))
    monkeypatch.setattr(cli, "cmd_pdf", lambda args: cli_calls.append("pdf"))
    monkeypatch.setattr(cli, "cmd_upload", lambda args: cli_calls.append("upload"))
    monkeypatch.setattr(cli, "cmd_status", lambda args: cli_calls.append("status"))

    # --- PIPELINE RUN ---

    # 1. Fetch the raw job page text
    raw_text = server.fetch_public_job_url("https://cloudsystems.com/jobs/111/")
    assert "Platform Architect" in raw_text

    # 2. Save the job description directly
    save_res = server.save_job_description(
        company="Cloud Systems",
        title="Platform Architect",
        url="https://cloudsystems.com/jobs/111/",
        description=raw_text,
        location="Munich"
    )
    assert "SUCCESS" in save_res
    
    import re
    slug_match = re.search(r"slug '([^']+)'", save_res)
    assert slug_match is not None
    target_slug = slug_match.group(1)

    # 3. Create the application using the returned slug
    application_res = json.loads(server.create_application_from_job(target_slug))
    assert application_res["status"] == "queued"


def test_mcp_initialize_agent_session():
    from engine.mcp import server
    import json

    res = server.initialize_agent_session()
    assert "ERROR" not in res
    data = json.loads(res)
    assert isinstance(data, dict)
    assert "welcome_message" in data
    assert "operational_mental_model" in data
    assert "user_profile" in data
    assert "master_cv" in data
    assert "operational_insights" in data
    assert isinstance(data["user_profile"], dict)


def test_mcp_get_user_projects():
    from engine.mcp import server
    import json

    res = server.get_user_projects()
    assert "ERROR" not in res
    data = json.loads(res)
    assert isinstance(data, (list, dict))


def test_mcp_get_cv_guide():
    from engine.mcp import server

    res = server.get_cv_guide()
    assert "ERROR" not in res
    assert "cv" in res.lower() or "resume" in res.lower() or "write" in res.lower()


def test_mcp_get_cover_letter_guide():
    from engine.mcp import server

    res = server.get_cover_letter_guide()
    assert "ERROR" not in res
    assert "letter" in res.lower() or "salutation" in res.lower()


def test_mcp_create_application_idempotency():
    from engine.mcp import server
    from engine.shared.db import get_conn
    import json

    # 1. Insert mock job and application with status 'draft'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES ('idempotency-job-123', 'mock-idempotent-slug', 'ACME Corp', 'Software Architect', 'file', 'other', 'JD text')
                ON CONFLICT (job_id) DO UPDATE SET slug = EXCLUDED.slug
            """)
            cur.execute("""
                INSERT INTO applications (job_id, slug, status)
                VALUES ('idempotency-job-123', 'mock-idempotent-slug', 'draft')
                ON CONFLICT (job_id) DO UPDATE SET status = 'draft'
            """)
            conn.commit()

    # 2. Assert that calling create_application_from_job returns a rejection error
    res_str = server.create_application_from_job("mock-idempotent-slug")
    res = json.loads(res_str)
    assert "error" in res
    assert "already finished" in res["error"].lower() or "already generated" in res["error"].lower()


def test_mcp_create_application_async_success(monkeypatch):
    from engine.mcp import server
    from engine.shared.db import get_conn
    import time
    import json

    # Insert mock job to satisfy DB constraints
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES ('success-job-123', 'mock-acme-slug', 'Acme', 'Engineer', 'file', 'other', 'JD')
                ON CONFLICT (job_id) DO UPDATE SET slug = EXCLUDED.slug
            """)
            # Ensure no stale app record exists
            cur.execute("DELETE FROM applications WHERE slug = 'mock-acme-slug'")
            conn.commit()

    # Mock workflow to simulate a fast success
    monkeypatch.setattr(server, "create_application_from_job_workflow", lambda slug: "Complete success!")

    # 1. Trigger generation
    res = json.loads(server.create_application_from_job("mock-acme-slug"))
    assert res["status"] == "queued"
    
    # 2. Let background thread run for a split second
    time.sleep(0.5)


def test_mcp_create_application_async_failure(monkeypatch):
    from engine.mcp import server
    from engine.shared.db import get_conn
    import time
    import json

    # Insert mock job to satisfy DB constraints
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES ('fail-job-123', 'mock-fail-slug', 'Acme Fail', 'Engineer', 'file', 'other', 'JD')
                ON CONFLICT (job_id) DO UPDATE SET slug = EXCLUDED.slug
            """)
            # Ensure no stale app record exists
            cur.execute("DELETE FROM applications WHERE slug = 'mock-fail-slug'")
            conn.commit()

    # Mock workflow to simulate a failure
    monkeypatch.setattr(server, "create_application_from_job_workflow", lambda slug: "ERROR: Something went wrong")

    # 1. Trigger generation
    res = json.loads(server.create_application_from_job("mock-fail-slug"))
    assert res["status"] == "queued"
    
    # 2. Let background thread run and fail
    time.sleep(0.5)


def test_mcp_job_delete_reinstatement():
    from engine.mcp import server
    import json

    # Save a job
    save_res = server.save_job_description(
        company="Soft Delete Corp",
        title="Soft Engineer",
        url="https://softdelete.com/jobs/1",
        description="This is a soft delete test job."
    )
    assert "SUCCESS" in save_res
    
    import re
    slug_match = re.search(r"slug '([^']+)'", save_res)
    assert slug_match is not None
    slug = slug_match.group(1)

    # Delete the job
    del_res = server.delete_job(slug)
    assert "SUCCESS" in del_res

    # Save the exact same job again
    save_res_again = server.save_job_description(
        company="Soft Delete Corp",
        title="Soft Engineer",
        url="https://softdelete.com/jobs/1",
        description="This is a soft delete test job."
    )
    assert "SUCCESS" in save_res_again


def test_mcp_stress_batch_creation_delete(monkeypatch):
    from engine.mcp import server
    import json
    import time

    # Mock workflow to avoid slow actual compilation during this stress test
    monkeypatch.setattr(server, "create_application_from_job_workflow", lambda slug: "Complete success!")

    # 1. Save 3 dummy jobs
    slugs = []
    for i in range(1, 4):
        save_res = server.save_job_description(
            company=f"Batch Corp {i}",
            title=f"Batch Engineer {i}",
            url=f"https://batchcorp.com/jobs/{i}",
            description=f"This is batch job description {i}."
        )
        assert "SUCCESS" in save_res
        import re
        slug_match = re.search(r"slug '([^']+)'", save_res)
        assert slug_match is not None
        slugs.append(slug_match.group(1))

    assert len(slugs) == 3

    # 2. Trigger asynchronous application creation in batch (all 3 triggered back-to-back!)
    for slug in slugs:
        res = json.loads(server.create_application_from_job(slug))
        assert res["status"] == "queued"

    # 3. Soft delete all 3 jobs
    for slug in slugs:
        del_res = server.delete_job(slug)
        assert "SUCCESS" in del_res







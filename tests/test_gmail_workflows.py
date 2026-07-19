import json
import pytest
from engine.domains.gmail.ingest import list_gmail_jobs_workflow
from engine.domains.gmail import client as gmail

def test_list_gmail_jobs_workflow_success(monkeypatch):
    # Mock search_emails to return a mock thread with an email body containing job alert links
    mock_body = """
    We found some new jobs matching your alerts:
    
    Senior Software Engineer
    Acme Corp
    Munich, Germany
    https://www.linkedin.com/jobs/view/123456789/
    
    Data Engineer
    Beta Inc
    Remote
    https://www.linkedin.com/jobs/view/987654321/
    """
    
    monkeypatch.setattr(gmail, "search_emails", lambda query, limit, include_bodies: [
        {
            "threadId": "thread_abc123",
            "subject": "LinkedIn Job Alert",
            "messages": [
                {
                    "id": "msg_xyz",
                    "sender": "jobalerts-noreply@linkedin.com",
                    "subject": "LinkedIn Job Alert",
                    "body": mock_body
                }
            ]
        }
    ])

    # Run the workflow
    res_str = list_gmail_jobs_workflow(provider="linkedin", query="is:unread", limit=5)
    
    # Parse the returned JSON string
    res = json.loads(res_str)
    
    assert isinstance(res, list)
    assert len(res) == 2
    
    job1 = res[0]
    assert job1["job_id"] == "123456789"
    assert job1["company"] == "Acme Corp"
    assert job1["role"] == "Senior Software Engineer"
    assert job1["job_url"] == "https://www.linkedin.com/jobs/view/123456789/"
    assert "Munich" in job1["brief_description"]

    job2 = res[1]
    assert job2["job_id"] == "987654321"
    assert job2["company"] == "Beta Inc"
    assert job2["role"] == "Data Engineer"
    assert job2["job_url"] == "https://www.linkedin.com/jobs/view/987654321/"
    assert "Remote" in job2["brief_description"]


def test_list_gmail_jobs_workflow_no_jobs(monkeypatch):
    # Mock search_emails to return an empty list of emails
    monkeypatch.setattr(gmail, "search_emails", lambda query, limit, include_bodies: [])
    
    res_str = list_gmail_jobs_workflow(provider="linkedin", query="is:unread", limit=5)
    res = json.loads(res_str)
    assert isinstance(res, list)
    assert len(res) == 0


def test_extract_job_details_workflow_success(monkeypatch):
    import engine.domains.gmail.ingest as gi
    import multiprocessing
    
    # Mock the worker function to return a mock slug without launching Playwright
    monkeypatch.setattr(gi, "_capture_jobs_worker_func", lambda urls: (["mock-acme-engineer-123"], ["Successfully captured mock job"]))
    
    # Mock Process and Queue to run inline instead of spawning a new process (preserving monkeypatch!)
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
    
    # Run extract_job_details_workflow
    from engine.domains.gmail.ingest import extract_job_details_workflow
    res = extract_job_details_workflow("https://www.linkedin.com/jobs/view/1234567/")
    
    assert "SUCCESS" in res
    assert "mock-acme-engineer-123" in res


def test_extract_job_details_workflow_invalid_url():
    from engine.domains.gmail.ingest import extract_job_details_workflow
    res = extract_job_details_workflow("https://www.linkedin.com/settings/")
    assert "ERROR" in res
    assert "Invalid" in res


def test_create_application_from_job_workflow_success(monkeypatch):
    from engine import cli
    calls = []
    from engine.domains.gmail import ingest
    monkeypatch.setattr(ingest, "verify_markdown_documents", lambda slug: (True, []))
    
    # Mock core CLI execution actions
    monkeypatch.setattr(cli, "cmd_new", lambda args: calls.append("new"))
    monkeypatch.setattr(cli, "cmd_pdf", lambda args: calls.append("pdf"))
    monkeypatch.setattr(cli, "cmd_upload", lambda args: calls.append("upload"))
    monkeypatch.setattr(cli, "cmd_status", lambda args: calls.append("status"))
    
    from engine.domains.gmail.ingest import create_application_from_job_workflow
    res = create_application_from_job_workflow("test-slug-123")
    
    assert "Complete" in res
    assert "Successfully" in res
    assert calls == ["new", "pdf", "upload", "status"]


def test_generic_search_workflow(monkeypatch):
    from engine.domains.gmail.ingest import generic_search_workflow
    
    monkeypatch.setattr(gmail, "search_emails", lambda query, limit, include_bodies: [
        {
            "id": "thread_123",
            "messages": [
                {
                    "id": "msg_456",
                    "subject": "Test General Email",
                    "from": "sender@test.com",
                    "date": "2026-06-30",
                    "snippet": "Simple snippet text",
                    "body": "Rich full body content"
                }
            ]
        }
    ])

    res_str = generic_search_workflow("invoice", limit=5, include_bodies=True)
    res = json.loads(res_str)

    assert "emails" in res
    assert len(res["emails"]) == 1
    assert res["emails"][0]["subject"] == "Test General Email"
    assert res["emails"][0]["body"] == "Rich full body content"


def test_check_application_updates_workflow(monkeypatch):
    from engine.shared.db import get_conn, init_db
    from engine.domains.gmail.ingest import check_application_updates_workflow
    
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jobs")
            cur.execute("DELETE FROM applications")
            # Insert a job
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, created_at)
                VALUES ('e2e-job-id', 'polymodal-slug', 'Polymodal', 'Data Engineer', 'file', 'other', '2026-06-30 12:00:00')
            """)
            # Insert an application
            cur.execute("""
                INSERT INTO applications (job_id, slug, status, cv_en)
                VALUES ('e2e-job-id', 'polymodal-slug', 'applied', 'some cv')
            """)
        conn.commit()

    # Mock search_emails
    searches = []
    monkeypatch.setattr(gmail, "search_emails", lambda query, limit, include_bodies: (
        searches.append(query) or [
            {
                "id": "thread_abc123",
                "messages": [
                    {
                        "id": "msg_xyz",
                        "subject": "Interview Invite",
                        "from": "recruiter@polymodal.com",
                        "date": "2026-06-30",
                        "snippet": "Let's schedule an interview",
                        "body": "Hi Radheem, we loved your CV..."
                    }
                ]
            }
        ]
    ))

    res_str = check_application_updates_workflow("polymodal-slug")
    res = json.loads(res_str)

    assert "emails" in res
    assert len(res["emails"]) == 1
    assert res["emails"][0]["from"] == "recruiter@polymodal.com"
    assert res["emails"][0]["body"] == "Hi Radheem, we loved your CV..."
    
    # Verify the generated query string
    assert len(searches) == 1
    assert "Polymodal" in searches[0]
    assert "after:2026/06/30" in searches[0]



def test_verify_markdown_documents_exhaustive(tmp_path, monkeypatch):
    from engine.domains.gmail.ingest import verify_markdown_documents
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", str(tmp_path))
    
    # 1. Non-existent slug
    is_valid, errors = verify_markdown_documents("no-such-slug")
    assert not is_valid
    assert any("does not exist" in err for err in errors)
    
    # 2. Folder exists but missing files
    app_dir = tmp_path / "test-slug"
    app_dir.mkdir()
    is_valid, errors = verify_markdown_documents("test-slug")
    assert not is_valid
    assert any("missing" in err for err in errors)
    
    # 3. Files too short
    (app_dir / "cv.md").write_text("too short")
    (app_dir / "cover-letter.md").write_text("also too short")
    is_valid, errors = verify_markdown_documents("test-slug")
    assert not is_valid
    assert any("empty or too short" in err for err in errors)
    
    # 4. English placeholder
    (app_dir / "cv.md").write_text("A" * 150 + " [Your Name] " + "B" * 150)
    (app_dir / "cover-letter.md").write_text("C" * 150)
    is_valid, errors = verify_markdown_documents("test-slug")
    assert not is_valid
    assert any("placeholder" in err for err in errors)
    
    # 5. German placeholder
    (app_dir / "cv.md").write_text("A" * 150)
    (app_dir / "cover-letter.md").write_text("C" * 150 + " [Ihr Name] " + "D" * 150)
    is_valid, errors = verify_markdown_documents("test-slug")
    assert not is_valid
    assert any("placeholder" in err for err in errors)

    # 6. Strict bracket uppercase (but not a markdown link)
    (app_dir / "cover-letter.md").write_text("C" * 150 + " [ROLE_NAME] " + "D" * 150)
    is_valid, errors = verify_markdown_documents("test-slug")
    assert not is_valid
    assert any("placeholder" in err or "ROLE_NAME" in err for err in errors)

    # 7. Valid markdown link with brackets (should NOT be flagged)
    (app_dir / "cover-letter.md").write_text("C" * 150 + " [Polymodal](https://polymodal.com) " + "D" * 150)
    is_valid, errors = verify_markdown_documents("test-slug")
    assert is_valid
    assert not errors


def test_decomposed_workflows_exhaustive(monkeypatch):
    from engine import cli
    calls = []
    
    # Mock CLI actions
    monkeypatch.setattr(cli, "cmd_new", lambda args: calls.append("new"))
    monkeypatch.setattr(cli, "cmd_pdf", lambda args: calls.append("pdf"))
    monkeypatch.setattr(cli, "cmd_upload", lambda args: calls.append("upload"))
    monkeypatch.setattr(cli, "cmd_status", lambda args: calls.append("status"))
    
    # Mock verify_markdown_documents to bypass file existence checks
    from engine.domains.gmail import ingest
    monkeypatch.setattr(ingest, "verify_markdown_documents", lambda slug: (True, []))
    
    # Test generate_markdown_workflow (Stage 1)
    res1 = ingest.generate_markdown_workflow("test-slug")
    assert "SUCCESS" in res1
    assert "generated" in res1
    assert calls == ["new"]
    
    # Test create_pdf_from_markdown_workflow (Stage 2)
    res2 = ingest.create_pdf_from_markdown_workflow("test-slug")
    assert "Complete" in res2
    assert "Successfully" in res2
    assert "rendered PDFs" in res2
    assert "uploaded compiled" in res2
    assert "synchronized application" in res2
    assert calls == ["new", "pdf", "upload", "status"]

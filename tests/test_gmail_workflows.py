import json
import pytest
from engine.workflows.gmail_ingest import list_gmail_jobs_workflow
from engine import gmail

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
    import engine.workflows.gmail_ingest as gi
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
    from engine.workflows.gmail_ingest import extract_job_details_workflow
    res = extract_job_details_workflow("https://www.linkedin.com/jobs/view/1234567/")
    
    assert "SUCCESS" in res
    assert "mock-acme-engineer-123" in res


def test_extract_job_details_workflow_invalid_url():
    from engine.workflows.gmail_ingest import extract_job_details_workflow
    res = extract_job_details_workflow("https://www.linkedin.com/settings/")
    assert "ERROR" in res
    assert "Invalid" in res


def test_create_application_from_job_workflow_success(monkeypatch):
    from engine import cli
    calls = []
    
    # Mock core CLI execution actions
    monkeypatch.setattr(cli, "cmd_new", lambda args: calls.append("new"))
    monkeypatch.setattr(cli, "cmd_pdf", lambda args: calls.append("pdf"))
    monkeypatch.setattr(cli, "cmd_upload", lambda args: calls.append("upload"))
    monkeypatch.setattr(cli, "cmd_status", lambda args: calls.append("status"))
    
    from engine.workflows.gmail_ingest import create_application_from_job_workflow
    res = create_application_from_job_workflow("test-slug-123")
    
    assert "Complete" in res
    assert "Successfully" in res
    assert calls == ["new", "pdf", "upload", "status"]

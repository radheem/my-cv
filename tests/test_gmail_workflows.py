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

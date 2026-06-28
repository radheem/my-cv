import json
import urllib.request
from unittest.mock import MagicMock
import pytest
from engine.domains.gmail import client as gmail

def test_search_emails_success(monkeypatch):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    
    posted_req = None
    
    def mock_urlopen(req):
        nonlocal posted_req
        posted_req = req
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ok": True,
            "threads": [{"id": "thread123", "subject": "Test", "snippet": "...", "isUnread": True}]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    res = gmail.search_emails("is:unread", limit=5, include_bodies=True)
    
    assert len(res) == 1
    assert res[0]["id"] == "thread123"
    
    assert posted_req is not None
    assert posted_req.get_header("Content-type") == "text/plain"
    assert posted_req.full_url == "https://script.google.com/macros/s/test/exec"
    
    body = json.loads(posted_req.data.decode("utf-8"))
    assert body["token"] == "mock_token"
    assert body["action"] == "search_emails"
    assert body["query"] == "is:unread"
    assert body["limit"] == 5
    assert body["includeBodies"] is True

def test_batch_modify_threads_success(monkeypatch):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    
    posted_req = None
    
    def mock_urlopen(req):
        nonlocal posted_req
        posted_req = req
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ok": True,
            "modifiedCount": 3
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    res = gmail.batch_modify_threads(["id1", "id2"], mark_read=True, mark_starred=False, mark_important=None)
    assert res == 3
    
    assert posted_req is not None
    body = json.loads(posted_req.data.decode("utf-8"))
    assert body["token"] == "mock_token"
    assert body["action"] == "batch_modify_threads"
    assert body["threadIds"] == ["id1", "id2"]
    assert body["markRead"] is True
    assert body["markStarred"] is False
    assert body["markImportant"] is None

def test_batch_send_emails_success(monkeypatch):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    
    posted_req = None
    
    def mock_urlopen(req):
        nonlocal posted_req
        posted_req = req
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ok": True,
            "sentCount": 1,
            "details": [{"to": "test@example.com", "status": "success"}],
            "remainingQuota": 99
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    emails = [{"to": "test@example.com", "subject": "Sub", "body": "Body"}]
    res = gmail.batch_send_emails(emails)
    
    assert res["ok"] is True
    assert res["sentCount"] == 1
    assert res["remainingQuota"] == 99
    
    assert posted_req is not None
    body = json.loads(posted_req.data.decode("utf-8"))
    assert body["token"] == "mock_token"
    assert body["action"] == "batch_send_emails"
    assert body["emails"] == emails

def test_gmail_missing_url(monkeypatch):
    monkeypatch.delenv("APPS_SCRIPT_URL", raising=False)
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    
    with pytest.raises(SystemExit) as exc_info:
        gmail.search_emails("test")
    assert "APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN must be set" in str(exc_info.value)

def test_gmail_missing_token(monkeypatch):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.delenv("APPS_SCRIPT_TOKEN", raising=False)
    
    with pytest.raises(SystemExit) as exc_info:
        gmail.search_emails("test")
    assert "APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN must be set" in str(exc_info.value)

def test_gmail_error_response(monkeypatch):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    
    def mock_urlopen(req):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ok": False,
            "error": "some_error"
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    with pytest.raises(SystemExit) as exc_info:
        gmail.search_emails("test")
    assert "some_error" in str(exc_info.value)

def test_get_thread_success(monkeypatch):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    
    posted_req = None
    
    def mock_urlopen(req):
        nonlocal posted_req
        posted_req = req
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ok": True,
            "thread": {"id": "thread123", "subject": "Test", "snippet": "...", "messages": []}
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    res = gmail.get_thread("thread123")
    assert res["id"] == "thread123"
    assert res["subject"] == "Test"
    
    assert posted_req is not None
    body = json.loads(posted_req.data.decode("utf-8"))
    assert body["token"] == "mock_token"
    assert body["action"] == "get_thread"
    assert body["threadId"] == "thread123"

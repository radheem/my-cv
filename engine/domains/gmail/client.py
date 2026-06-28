import json
import os
import urllib.request

def _post_apps_script(payload: dict) -> dict:
    url = os.environ.get("APPS_SCRIPT_URL")
    token = os.environ.get("APPS_SCRIPT_TOKEN")
    if not url or not token:
        raise SystemExit("APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN must be set in the environment")
    
    payload["token"] = token
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "text/plain"})
    
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        if not res.get("ok"):
            raise SystemExit(f"Apps Script Error: {res.get('error')}")
        return res

def search_emails(query: str, limit: int = 20, include_bodies: bool = False) -> list[dict]:
    res = _post_apps_script({
        "action": "search_emails",
        "query": query,
        "limit": limit,
        "includeBodies": include_bodies
    })
    return res.get("threads", [])

def get_thread(thread_id: str) -> dict:
    res = _post_apps_script({
        "action": "get_thread",
        "threadId": thread_id
    })
    return res.get("thread", {})

def batch_modify_threads(
    thread_ids: list[str],
    mark_read: bool | None = None,
    mark_starred: bool | None = None,
    mark_important: bool | None = None
) -> int:
    res = _post_apps_script({
        "action": "batch_modify_threads",
        "threadIds": thread_ids,
        "markRead": mark_read,
        "markStarred": mark_starred,
        "markImportant": mark_important
    })
    return res.get("modifiedCount", 0)

def batch_send_emails(emails: list[dict]) -> dict:
    return _post_apps_script({
        "action": "batch_send_emails",
        "emails": emails
    })

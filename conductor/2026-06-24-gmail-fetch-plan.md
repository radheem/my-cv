# Gmail Fetch Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a robust, generic `gmail` CLI subcommand that interacts with a Google Apps Script proxy to search, read, modify (star/read/important), and send emails securely without storing complex local OAuth credentials.

**Architecture:** Python CLI (`engine/cli.py`) delegates arguments to a new client (`engine/gmail.py`). This client sends authorized HTTPS POST requests to the user's Apps Script Web App (`apps-script/Code.gs`), which executes the actual GmailApp API calls.

**Tech Stack:** Python 3 (standard library `urllib`, `argparse`, `json`), Google Apps Script (JavaScript).

---

## Phase 1: Apps Script Backend Extension

### Task 1: Add Gmail Actions to `Code.gs`

**Files:**
- Modify: `apps-script/Code.gs`

- [ ] **Step 1: Write implementation for Apps Script**

Replace the current `doPost(e)` block to route three new actions (`search_emails`, `batch_modify_threads`, `batch_send_emails`), and add their corresponding handler functions at the bottom of the file.

```javascript
// Add these routing blocks to doPost(e) before the generic return:
    if (body.action === 'search_emails') {
      return json(searchEmails(body.query || '', body.limit || 20, body.includeBodies));
    }
    if (body.action === 'batch_modify_threads') {
      return json(batchModifyThreads(body.threadIds || [], body.markRead, body.markStarred, body.markImportant));
    }
    if (body.action === 'batch_send_emails') {
      return json(batchSendEmails(body.emails || []));
    }

// Add these functions to the end of Code.gs:
function searchEmails(query, limit, includeBodies) {
  var threads = GmailApp.search(query || '', 0, limit || 20);
  var results = [];
  for (var i = 0; i < threads.length; i++) {
    var thread = threads[i];
    var threadData = {
      id: thread.getId(),
      subject: thread.getFirstMessageSubject(),
      date: thread.getLastMessageDate().getTime(),
      snippet: thread.getSnippet(),
      isUnread: thread.isUnread(),
      isStarred: thread.isStarred(),
      isImportant: thread.isImportant(),
      messages: []
    };
    if (includeBodies) {
      var messages = thread.getMessages();
      for (var j = 0; j < messages.length; j++) {
        var msg = messages[j];
        var plainBody = msg.getPlainBody() || '';
        if (plainBody.length > 32768) {
          plainBody = plainBody.substring(0, 32768) + "\n... [TRUNCATED BY PROXY] ...";
        }
        threadData.messages.push({
          id: msg.getId(),
          sender: msg.getFrom(),
          to: msg.getTo(),
          date: msg.getDate().getTime(),
          body: plainBody
        });
      }
    }
    results.push(threadData);
  }
  return { ok: true, threads: results };
}

function batchModifyThreads(threadIds, markRead, markStarred, markImportant) {
  if (!threadIds || threadIds.length === 0) return { ok: true, modifiedCount: 0 };
  var threads = [];
  for (var i = 0; i < threadIds.length; i++) {
    try {
      var t = GmailApp.getThreadById(threadIds[i]);
      if (t) threads.push(t);
    } catch (e) {}
  }
  if (threads.length === 0) return { ok: true, modifiedCount: 0 };
  
  if (markRead === true) GmailApp.markThreadsRead(threads);
  else if (markRead === false) GmailApp.markThreadsUnread(threads);
  
  if (markImportant === true) threads.forEach(function(t) { t.markImportant(); });
  else if (markImportant === false) threads.forEach(function(t) { t.markUnimportant(); });
  
  if (markStarred === true) {
    threads.forEach(function(t) {
      var msgs = t.getMessages();
      if (msgs.length > 0) msgs[0].star();
    });
  } else if (markStarred === false) {
    threads.forEach(function(t) {
      t.getMessages().forEach(function(m) { m.unstar(); });
    });
  }
  return { ok: true, modifiedCount: threads.length };
}

function batchSendEmails(emails) {
  var results = [];
  var successCount = 0;
  for (var i = 0; i < emails.length; i++) {
    var email = emails[i];
    try {
      var options = {};
      if (email.attachments && email.attachments.length > 0) {
        options.attachments = email.attachments.map(function(att) {
          return Utilities.newBlob(Utilities.base64Decode(att.b64), att.mimeType || 'application/octet-stream', att.name);
        });
      }
      MailApp.sendEmail({to: email.to, subject: email.subject, body: email.body, attachments: options.attachments});
      results.push({ to: email.to, status: 'success' });
      successCount++;
    } catch (e) {
      results.push({ to: email.to, status: 'failed', error: String(e) });
    }
  }
  return { ok: true, sentCount: successCount, details: results, remainingQuota: MailApp.getRemainingDailyQuota() };
}
```

- [ ] **Step 2: Commit**

```bash
git add apps-script/Code.gs
git commit -m "feat(apps-script): add gmail read, modify, and send endpoints"
```

*(Note: The user will need to manually copy-paste this file to their Google Apps Script project and redeploy as a new version.)*

---

## Phase 2: Python Client Logic

### Task 2: Create Python Gmail Service Client

**Files:**
- Create: `engine/gmail.py`
- Create: `tests/test_gmail.py`

- [ ] **Step 1: Write the failing tests**

```python
# In tests/test_gmail.py
import json
import urllib.request
from unittest.mock import MagicMock
from engine import gmail

def test_gmail_search_mocked(monkeypatch):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "ok": True,
        "threads": [{"id": "thread123", "subject": "Test", "snippet": "...", "isUnread": True}]
    }).encode("utf-8")
    
    mock_urlopen = MagicMock()
    mock_urlopen.__enter__.return_value = mock_response
    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    res = gmail.search_emails("is:unread", limit=1)
    assert len(res) == 1
    assert res[0]["id"] == "thread123"

def test_gmail_missing_env(monkeypatch):
    monkeypatch.delenv("APPS_SCRIPT_URL", raising=False)
    try:
        gmail.search_emails("test")
        assert False, "Should raise SystemExit"
    except SystemExit:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gmail.py -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Write minimal implementation**

```python
# In engine/gmail.py
import json
import os
import urllib.request

def _post_apps_script(payload: dict) -> dict:
    url = os.environ.get("APPS_SCRIPT_URL")
    token = os.environ.get("APPS_SCRIPT_TOKEN")
    if not url or not token:
        raise SystemExit("APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN must be set in .env")
    
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

def batch_modify_threads(
    thread_ids: list[str], mark_read: bool | None = None,
    mark_starred: bool | None = None, mark_important: bool | None = None
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_gmail.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add engine/gmail.py tests/test_gmail.py
git commit -m "feat(engine): add python client for apps script gmail proxy"
```

---

## Phase 3: CLI Integration

### Task 3: Add `gmail` command group to `engine/cli.py`

**Files:**
- Modify: `engine/cli.py`

- [ ] **Step 1: Write implementation**

Modify `engine/cli.py` to import `engine.gmail` and add the subcommand parsers.

```python
# Add to imports:
from . import gmail

# Add command functions:
def cmd_gmail_search(args: argparse.Namespace) -> int:
    threads = gmail.search_emails(args.query, args.limit, False)
    if args.json:
        print(json.dumps(threads, indent=2))
        return 0
    
    print(f"Found {len(threads)} threads:\n")
    for t in threads:
        status = []
        if t.get("isUnread"): status.append("UNREAD")
        if t.get("isStarred"): status.append("STARRED")
        if t.get("isImportant"): status.append("IMPORTANT")
        status_str = f"[{' '.join(status)}]" if status else ""
        print(f"ID: {t.get('id')} {status_str}")
        print(f"Sub: {t.get('subject')} | {t.get('snippet')}\n")
    return 0

def cmd_gmail_read(args: argparse.Namespace) -> int:
    threads = gmail.search_emails(f"rfc822msgid:{args.thread_id} OR {args.thread_id}", 1, True)
    if not threads:
        print(f"Thread {args.thread_id} not found.")
        return 1
    t = threads[0]
    print(f"Subject: {t.get('subject')}\n")
    for m in t.get("messages", []):
        print(f"--- From: {m.get('sender')} ---")
        print(m.get("body"))
        print("-" * 40 + "\n")
    return 0

def cmd_gmail_modify(args: argparse.Namespace) -> int:
    import sys
    ids = sys.stdin.read().split() if args.thread_ids == ["-"] else args.thread_ids
    
    read_flag = None
    if args.read: read_flag = True
    elif args.unread: read_flag = False
    
    star_flag = None
    if args.star: star_flag = True
    elif args.unstar: star_flag = False
    
    imp_flag = None
    if args.important: imp_flag = True
    elif args.unimportant: imp_flag = False
    
    count = gmail.batch_modify_threads(ids, read_flag, star_flag, imp_flag)
    print(f"Modified {count} threads.")
    return 0

def cmd_gmail_send(args: argparse.Namespace) -> int:
    if args.bulk_file:
        import pathlib
        emails = json.loads(pathlib.Path(args.bulk_file).read_text(encoding="utf-8"))
    else:
        if not args.to or not args.subject or not args.body:
            raise SystemExit("Missing --to, --subject, or --body")
        emails = [{"to": args.to, "subject": args.subject, "body": args.body}]
    
    res = gmail.batch_send_emails(emails)
    print(f"Sent {res.get('sentCount')} emails. Remaining quota: {res.get('remainingQuota')}")
    return 0

# Add parser bindings (in `main` before `args = parser.parse_args(argv)`):
    p_gmail = sub.add_parser("gmail", help="Gmail operations via Apps Script proxy")
    gmail_sub = p_gmail.add_subparsers(dest="gmail_cmd", required=True)
    
    pg_search = gmail_sub.add_parser("search", help="Search emails")
    pg_search.add_argument("--query", required=True, help="Gmail search query")
    pg_search.add_argument("--limit", type=int, default=20)
    pg_search.add_argument("--json", action="store_true")
    pg_search.set_defaults(func=cmd_gmail_search)
    
    pg_read = gmail_sub.add_parser("read", help="Read a full thread by ID")
    pg_read.add_argument("thread_id")
    pg_read.set_defaults(func=cmd_gmail_read)
    
    pg_mod = gmail_sub.add_parser("modify", help="Batch modify thread status")
    pg_mod.add_argument("--thread-ids", nargs="+", required=True, help="List of IDs or '-' for stdin")
    pg_mod.add_argument("--read", action="store_true")
    pg_mod.add_argument("--unread", action="store_true")
    pg_mod.add_argument("--star", action="store_true")
    pg_mod.add_argument("--unstar", action="store_true")
    pg_mod.add_argument("--important", action="store_true")
    pg_mod.add_argument("--unimportant", action="store_true")
    pg_mod.set_defaults(func=cmd_gmail_modify)
    
    pg_send = gmail_sub.add_parser("send", help="Send emails")
    pg_send.add_argument("--to")
    pg_send.add_argument("--subject")
    pg_send.add_argument("--body")
    pg_send.add_argument("--bulk-file", help="Path to JSON file with array of email objects")
    pg_send.set_defaults(func=cmd_gmail_send)
```

- [ ] **Step 2: Check manual test**
Test the parsing logic passes without syntax errors. `python engine/cli.py --help`

- [ ] **Step 3: Commit**

```bash
git add engine/cli.py
git commit -m "feat(cli): add gmail subcommands (search, read, modify, send)"
```

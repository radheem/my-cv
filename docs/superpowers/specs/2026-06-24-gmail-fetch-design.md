# Spec: Extensible Gmail Integration CLI

- **Date**: 2026-06-24
- **Feature**: Extensible Gmail CLI Interface (`gmail` subcommand)
- **Status**: Proposed

---

## 1. Context & Objectives

The goal is to provide a robust, safe, and highly extensible command-line interface to interact with Gmail (read/search, mark status, send emails, bulk processing) inside the `cv-tailor` workspace. 
This interface will eventually serve:
1. **Auto-ingesting Job Descriptions (JDs)** from job subscription emails (LinkedIn, Indeed).
2. **Auto-tracking Application Statuses** by reading confirmation and rejection emails.
3. **General CLI-based email manipulation** reusable for other tools.

To maintain maximum safety and structural simplicity, the feature uses the **Google Apps Script Proxy** architectural pattern. Python interacts with a Google Apps Script Web App deployed under the user's Google account. This bypasses the need for storing localized OAuth files or handling raw credentials.

---

## 2. Technical Architecture

### 2.1 Google Apps Script Gateway (`Code.gs`)
The web app is extended to handle three new actions: `search_emails`, `batch_modify_threads`, and `batch_send_emails`. It authenticates requests using the pre-existing, Git-ignored `APPS_SCRIPT_TOKEN` in the request body.

#### Flow Diagram
```
[Python CLI] ---> (HTTPS POST with APPS_SCRIPT_TOKEN) ---> [Google Apps Script Web App] ---> [GmailApp API]
```

### 2.2 Python Client Engine (`engine/gmail.py`)
A new service client is introduced to communicate with the Apps Script endpoint. This client provides raw programmatic wrappers for all 4 functions:
- `search_emails(query: str, limit: int = 20) -> list[dict]`
- `batch_modify_threads(thread_ids: list[str], mark_read: bool | None = None, mark_starred: bool | None = None, mark_important: bool | None = None) -> int`
- `batch_send_emails(emails: list[dict]) -> int`

### 2.3 CLI Command Suite (`engine/cli.py`)
A `gmail` subcommand is registered with `argparse`.

```bash
# Search and display emails in a table
cv-tailor gmail search --query "from:linkedin" [--limit 10] [--json]

# Bulk modify email threads (mark read, star, important)
cv-tailor gmail modify --thread-ids id1 id2 ... [--read/--unread] [--star/--unstar] [--important/--unimportant]

# Send a single or bulk emails
cv-tailor gmail send --to "recipient@example.com" --subject "Hello" --body "Message"
cv-tailor gmail send --bulk-file path/to/emails.json
```

---

## 3. Detailed Implementations

### 3.1 Apps Script Code Addition (`apps-script/Code.gs`)
The `doPost(e)` action block is updated to check and route the new actions:

```javascript
// Within doPost(e):
if (body.action === 'search_emails') {
  return json(searchEmails(body.query || '', body.limit || 20));
}
if (body.action === 'batch_modify_threads') {
  return json(batchModifyThreads(body.threadIds || [], body.markRead, body.markStarred, body.markImportant));
}
if (body.action === 'batch_send_emails') {
  return json(batchSendEmails(body.emails || []));
}
```

Implementation logic in `Code.gs`:
* **`searchEmails(query, limit)`**: Runs `GmailApp.search(query, 0, limit)`. For each thread, accesses its messages, parses body text/HTML, subject, date, sender, and flags (`isUnread`, `isStarred`, `isImportant`).
* **`batchModifyThreads(ids, markRead, markStarred, markImportant)`**: Iterates over thread IDs, loads threads via `GmailApp.getThreadById(id)`, and applies standard operations like `markRead()`, `markUnread()`, `star()`, `unstar()`, `addLabel()`, or `removeLabel()`.
* **`batchSendEmails(emailsList)`**: Sends multiple emails via `MailApp.sendEmail(to, subject, body)`.

### 3.2 Python Connection Handler (`engine/gmail.py`)
A standalone Python module to invoke the Apps Script POST endpoint, parsing errors, validating responses, and handling HTTP timeouts.

---

## 4. Security Considerations
- **Credential Storage**: Bearer security relies entirely on `APPS_SCRIPT_TOKEN` inside `.env`. No credentials or passwords are committed to Git.
- **Data Privacy**: No data is sent to third-party endpoints. The data travels directly from Google Apps Script (within your Google Account) to your local Python shell over secure HTTPS.
- **Rate Limits**: Governed by standard Google Apps Script daily quotas (e.g., 20,000 MailApp sends/day, and high-performance read limits).

---

## 5. Testing & Validation Plan
1. **Unit tests in `tests/test_gmail.py`**:
   - Mocking the HTTP call to the Apps Script endpoint.
   - Verifying parameter passing and error handling.
2. **Integration testing**:
   - Testing real connections against a sandbox Apps Script deployment with test emails.

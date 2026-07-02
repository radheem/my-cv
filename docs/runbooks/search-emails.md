# Runbook — Search & Summarize Emails

This runbook covers how to search emails using custom filters, summarize thread contents securely, and drive the automated **Gmail Job Hunt Pipeline** (`make gmail-hunt`).

---

## Prerequisites
Ensure that your `.env` contains the correct Apps Script configurations:
*   `APPS_SCRIPT_URL` — The deployment URL of your Apps Script Web App.
*   `APPS_SCRIPT_TOKEN` — The secure API token shared with your Apps Script instance.

---

## 1. Gmail Job Hunt Pipeline (`make gmail-hunt`)

The absolute best way to manage job alerts sent to your Gmail inbox is to run our end-to-end automated pipeline. This pipeline automatically queries Gmail, extracts unseen LinkedIn job URLs from alert emails, crawls and ingests them, ranks them, tailors cover letters and CVs on disk, compiles PDFs, and uploads them to Drive!

```bash
make gmail-hunt FILTER="subject:'linkedin job alert' is:unread" LIMIT=5 ORDER=top
```

### Overridable Parameters:
*   `FILTER`: The Gmail query used to search for alert emails (default: `"linkedin job alert"`).
*   `LIMIT`: Maximum number of applications to generate (default: `10`).
*   `ORDER`: Match ordering. `top` scores and selects the best matching roles; `fifo` selects the first N jobs chronologically.

---

## 2. Manual Search Emails with Filter

You can perform powerful structured searches on your Gmail inbox using standard Gmail search operators via the CLI:

```bash
make tailor CMD="gmail search --query '<query>' [--limit <num>]"
```

### Common Filter Examples:
*   **Unread emails from recruiters:**
    ```bash
    cv-tailor gmail search --query "from:recruiter is:unread" --limit 5
    ```
*   **Emails from Fraunhofer containing "interview":**
    ```bash
    cv-tailor gmail search --query "from:fraunhofer interview"
    ```
*   **Application-related threads received after a certain date:**
    ```bash
    cv-tailor gmail search --query "subject:'application' after:2026/06/01"
    ```

The output will list the matching threads, subjects, snippets, and status flags (e.g. `[UNREAD STARRED]`), along with their unique **Thread IDs**.

---

## 2. Read and Summarize an Email Thread

Once you have identified a Thread ID from the search results, you can fetch its complete body text.

### Step 1: Read the Thread
To print the full email thread to your console:
```bash
cv-tailor gmail read <thread_id>
```

### Step 2: Get a Summary of the Email Thread
You can pipe the thread directly into a local model (via Ollama) or save it to a file and summarize it with your configured LLM.

#### Option A: Local Ollama pipe (Recommended)
If you have Ollama running locally, pipe the output straight to a reasoning or summarization model:

```bash
cv-tailor gmail read <thread_id> | ollama run qwen3.5:35b "Summarize this email thread, extract the status, and list any action items or next steps required from me."
```

#### Option B: Clipboard / Text file
Save the output to a text file for manual review or to paste into another LLM window:
```bash
cv-tailor gmail read <thread_id> > email_thread.txt
```

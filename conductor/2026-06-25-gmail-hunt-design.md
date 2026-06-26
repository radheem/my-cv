# Gmail Job Hunt Pipeline Design

- **Date:** 2026-06-25
- **Status:** Approved
- **Author:** Gemini CLI

---

## 1. Overview & Objectives

The goal is to automate an end-to-end job application creation pipeline triggered directly by incoming Gmail alerts (e.g. LinkedIn job alert emails). The workflow must seamlessly extract job URLs from emails, capture their descriptions using the Playwright browser, rank the captured jobs against the user's profile, create tailored application packages (Markdown + PDFs), and sync them to Google Drive. 

The user requires a single command to drive this:
`make gmail-hunt FILTER="linkedin job alert" LIMIT=10 ORDER=[top|fifo]`

Where:
*   `FILTER`: The Gmail query string used to fetch alert emails (default: "linkedin job alert").
*   `LIMIT`: The maximum number of applications to generate.
*   `ORDER`: Controls whether we generate applications for the `top` N scoring jobs (matching user profile) or `fifo` (first N captured jobs chronologically).

## 2. Approach & Architecture

We will implement this workflow primarily as a bash script `scripts/gmail-hunt.sh`, adhering to the robust structure established in `scripts/job-hunt.sh`. The Makefile will provide the user-facing facade.

### Flow Diagram

1.  **Search Gmail**: Call `cv-tailor gmail search --query "$FILTER" --json`
2.  **Extract & Filter**: Parse the JSON threads, extract URLs via regex, and query `vault/jds/.seen.json` to filter out already-ingested URLs.
3.  **Capture**: Run `cv-tailor capture <url>` (via `xvfb-run`) for all unseen jobs.
4.  **Rank & Sort**: 
    *   If `ORDER=top`: Run `scripts/score-jds.py --top $LIMIT` to get the best-matching jobs.
    *   If `ORDER=fifo`: Simply slice the first `$LIMIT` files captured in Step 3.
5.  **Generate**: Run `cv-tailor new <file>` for the selected jobs.
6.  **Compile & Upload**: Run `cv-tailor pdf <slug>` and `cv-tailor upload <slug>`.
7.  **Status Sync**: Run `cv-tailor track` and optionally `cv-tailor sync-sheets`.

### Component 1: Python Extractor Helper
Extracting regex URLs from raw JSON email payloads inside bash is error-prone. We will write a lightweight python helper script `scripts/extract-email-urls.py` that reads the `cv-tailor gmail search` JSON output from stdin, parses message bodies, extracts LinkedIn job URLs (`/jobs/view/(\d+)`), checks against `vault/jds/.seen.json`, and outputs the raw unseen URLs to stdout.

### Component 2: `scripts/gmail-hunt.sh`
A bash script analogous to `job-hunt.sh` that orchestrates the workflow. It will:
- Accept `--filter`, `--limit`, and `--order`.
- Call `cv-tailor gmail search`.
- Pipe to the extractor helper.
- Loop over unseen URLs and call `xvfb-run cv-tailor capture`.
- Collect the generated slugs.
- Rank/Slice based on the `--order` parameter.
- Generate (`cv-tailor new`), compile (`pdf`), and sync (`upload`, `track`).

### Component 3: `Makefile` Target
We will register `gmail-hunt` in the Makefile, mapping `FILTER`, `LIMIT`, and `ORDER` variables to the script arguments.

---

## 3. Interfaces & Parameters

### Makefile Target
```makefile
FILTER ?= "linkedin job alert"
LIMIT  ?= 10
ORDER  ?= top

.PHONY: gmail-hunt
gmail-hunt: ## Search Gmail for alerts and generate applications: make gmail-hunt FILTER="..." LIMIT=10 ORDER=[top|fifo]
	bash scripts/gmail-hunt.sh --filter "$(FILTER)" --limit $(LIMIT) --order $(ORDER)
```

## 4. Error Handling and Edge Cases
- **No new jobs**: If the email extractor returns 0 URLs, the script exits cleanly early.
- **Capture failures**: If `cv-tailor capture` fails on a specific URL (e.g. dead link), the script must warn and continue, not crash the entire pipeline.
- **Idempotency**: Leveraging the existing `.seen.json` mechanism via the python extractor ensures we never double-ingest jobs.

# Specification & Guide: Composable Ingestion and Application Flow

This document outlines the architecture, supported flows, and execution pipelines of the `cv-tailor` Model Context Protocol (MCP) server. By segregating the browser-based scraping from direct HTTP fetching and persistence, the system achieves a highly composable and robust workflow.

---

## 1. Core Architecture
Regardless of *how* the job description text is obtained (via Gmail alerts, a Playwright browser crawler, manual text pasting, or direct HTTP fetching), all flows ultimately converge on a single, unified database persistence and application tailoring pipeline.

```mermaid
flowchart TD
    A[Discovered Job Text & Metadata] --> B(save_job_description / write_jd)
    
    subgraph Step 1: Database Ingestion & File Backup
        B --> C[Compute unique db_job_id from normalized URL]
        C --> D[Write Backup <slug>.txt with frontmatter to vault/jds/]
        C --> E[Write Backup <slug>.json metadata to vault/jds/]
        D & E --> F[DuckDB Serverless Cache auto-loads records]
    end

    F --> G[Generate Job Slug: company-title-job_id]
    
    subgraph Step 2: Application Tailoring & Output Generation
        G --> H(create_application_from_job slug)
        H --> I[LLM Revision: Generate tailored cv.md & cover-letter.md]
        I --> J[LaTeX Compiler: Render md to PDF via local/Docker TeX Live]
        J --> K[Google Apps Script Proxy: Upload PDFs to Google Drive]
        K --> L[Google Sheets Proxy: Push status tracking updates]
    end

    L --> M([Application Fully Tracked & Drafted!])
```

---

## 2. Supported Ingestion Flow Paths

### Path A: Direct Public Ingestion (Preferred & Standard Path)
*Highly recommended for public/unauthenticated links or platforms (like Glassdoor or Indeed) where browser crawlers hit anti-bot walls.*

```mermaid
sequenceDiagram
    autonumber
    participant Agent as AI Agent (Client)
    participant MCP as MCP Server
    participant FS as Local Filesystem & DuckDB

    Agent->>MCP: call_tool: fetch_public_job_url(url)
    MCP-->>Agent: Return stripped, clean plain-text job content
    Note over Agent: Extract company, title,<br/>location, and description
    Agent->>MCP: call_tool: save_job_description(company, title, url, description, ...)
    MCP->>FS: Save as .json and .txt under vault/jds/
    MCP-->>Agent: SUCCESS: Job saved with slug '<slug>'
```

### Path B: Authenticated Browser Crawler (Playwright Path)
*Specifically used for scraping complex pages (like LinkedIn) where public pages are heavily restricted and active logged-in cookies are required.*

```mermaid
sequenceDiagram
    autonumber
    participant Agent as AI Agent (Client)
    participant MCP as MCP Server
    participant Worker as Background Process (multiprocessing)
    participant Chrome as Playwright (Chromium)
    participant FS as Local Filesystem & DuckDB

    Agent->>MCP: call_tool: extract_job_details(url)
    MCP->>Worker: Spawn isolated worker process (with DISPLAY:99 Xvfb)
    Worker->>Chrome: Launch Headless Chromium & go to url
    
    alt If LinkedIn redirects to login/challenge
        Chrome-->>Worker: Classified as CHALLENGE_OTP / CHALLENGE_CAPTCHA
        Worker-->>MCP: Fail with session error
        MCP-->>Agent: Error (Action Required: Run warmup/login)
    else Warm Session / Public Access
        Worker->>Chrome: Wait for settle (networkidle / 8s max)
        Worker->>Chrome: Click "Expand Description" button
        Chrome-->>Worker: Extract page title & clean JD inner_text
        Worker->>FS: Save as .json and .txt under vault/jds/
        Worker-->>MCP: Return generated job slug
        MCP-->>Agent: SUCCESS: Captured job with slug '<slug>'
    end
```

---

## 3. Comparison Matrix

| Property | Path A (Direct Public Ingester) | Path B (Authenticated Scraper) |
| :--- | :--- | :--- |
| **Primary Use Case** | Public job links, Indeed/Glassdoor, custom websites, copy-pastes | Scraped LinkedIn pages requiring a logged-in session |
| **Speed** | 2–5 seconds (Extremely fast) | 20–40 seconds (Heavy browser overhead) |
| **Anti-Bot Resistance** | High (completely avoids driving a browser) | Prone to CAPTCHAs, requires session maintenance |
| **Failure Rate** | Low (Direct ingestion, highly reliable) | High on unauthenticated pages (timeouts) |
| **Requires Display/X11** | No (Pure Python & HTTP) | Yes (runs in virtual framebuffer Xvfb inside Docker) |

---

## 4. System Workflows Behind Each MCP Tool Call

This section documents the exact, backend system-level execution flows behind each Model Context Protocol (MCP) tool call.

### 0. Handshake & Core Context Loader
*Exposed as: `initialize_agent_session`*
* **Trigger:** Initializing an agent session on turn 1 to load instructions and facts.
* **Backend Flow:**
  1. Locates and parses the user's factual profile from `data/profile.yml`.
  2. Reads the full written career history from `data/master-cv.md`.
  3. Retrieves the troubleshooting, pacing, and rate limit rules from `data/guides/mcp-insights.md`.
  4. Combines the profile, CV, and insights with a strict, structured Operational Mental Model explaining how to correctly orchestrate the ingestion trilogy, tool selection guidelines, and queue mechanics.
  5. Serializes and returns this context package in under 1 second as a single structured JSON response.

### 1. Gmail Alert Ingestion Tools
*Exposed as: `list_gmail_linkedin_jobs`, `list_gmail_indeed_jobs`, `list_gmail_glassdoor_jobs`, `list_gmail_fraunhofer_jobs`*
* **Trigger:** Initiating Step 1 (Gmail Discovery Path) of the job application pipeline.
* **Backend Flow:**
  1. Connects securely to the Google Apps Script proxy API using credentials loaded from `.env`.
  2. Queries Gmail using provider-specific queries (e.g., `from:donotreply@jobalert.indeed.com is:unread`).
  3. Parses the raw email body text to locate potential job postings.
  4. Normalizes URLs to extract platform-specific job IDs using `parse_and_normalize_job_url`.
  5. Compiles and returns a lightweight JSON array of newly discovered jobs containing tentative `job_id`, `company`, `role`, `job_url`, and a brief description snippet without modifying any database state.

### 2. Specialized Platform Guest API Fetchers
*Exposed as: `fetch_linkedin_job`, `fetch_indeed_job`*
* **Trigger:** Direct fetching of job postings using known IDs (obtained via Gmail alerts or URL extraction) instead of heavy Playwright scraping.
* **Backend Flow:**
  1. Accepts a unique platform `job_id` (such as Indeed's `jk` or LinkedIn's guest ID).
  2. Constructs the canonical public API/direct view URL templates:
     * **LinkedIn:** `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}`
     * **Indeed:** `https://de.indeed.com/viewjob?jk={job_id}`
  3. Dispatches a standard HTTP request using `urllib.request` with a realistic desktop `User-Agent` string.
  4. Parses the response content based on the platform:
     * **LinkedIn (HTML):** Strips head, script, and style tags, formats blocks into structured line breaks, and returns clean plain text via `_clean_html()`.
     * **Indeed (JSON or HTML Fallback):** Attempts parsing as JSON first, returning a pretty-printed JSON string if successful. If JSON decoding fails, falls back gracefully to treating it as HTML and parsing text via `_clean_html()`.
  5. Gracefully handles network/HTTP errors (e.g., 403 Forbidden) and returns clean error strings to prevent calling agent failures.

### 3. Generic Guest Fetcher
*Exposed as: `fetch_public_job_url`*
* **Trigger:** Reading unstructured job descriptions directly from general public websites.
* **Backend Flow:**
  1. Opens a standard HTTP stream with `urllib.request` using custom headers.
  2. Retrieves and decodes HTML content to UTF-8.
  3. Feeds the HTML string into a central `_clean_html()` parser:
     * Strips structural boilerplate: `<script>`, `<style>`, `<head>`, `<header>`, `<footer`, `<nav>`.
     * Replaces layout tags (e.g. `<p>`, `<div>`, `<br>`, `<li>`) with structured line breaks.
     * Strips remaining HTML tags, unescapes characters (`&amp;` to `&`), and collapses redundant whitespace.
  4. Returns the clean, readable plain text of the job description.

### 4. Direct Database Ingest & File Backup
*Exposed as: `save_job_description`*
* **Trigger:** Persisting discovered job metadata and description to system storage before starting application tailoring.
* **Backend Flow:**
  1. Accepts `company`, `title`, `url`, `description`, `location`, and optional metadata.
  2. Hashes the URL using MD5 to compute a stable, unique 12-character `job_id`.
  3. Resolves/generates a unique human-readable `slug` (e.g., `company-title-job_id`).
  4. Writes local files (`<slug>.txt` with frontmatter and `<slug>.json` metadata) to the filesystem in `vault/jds/`.
  5. The local files are automatically registered by the serverless DuckDB cache for scoring and querying.
  6. Returns the generated unique job `slug` to the caller.

### 5. Asynchronous Tailoring Engine
*Exposed as: `create_application_from_job`*
* **Trigger:** Initiating application creation (CV/Cover Letter rendering) for an ingested job.
* **Backend Flow:**
  1. Accepts a unique job `slug`.
  2. Verifies that the corresponding job description files exist under `vault/jds/`.
  3. Updates the job state directly in the local `index.md` frontmatter, setting status to `'queued'`.
  4. Pushes the job slug to a global, thread-safe in-memory FIFO Queue (`_tailor_queue`).
  5. A dedicated serial consumer background thread pops the job, advances the state in the local frontmatter to `'generating'`, and runs the LLM tailoring engine to produce tailored CV + Cover Letter Markdown files.
  6. Compiles LaTeX documents locally (using standard `latexmk` or inside a TeX Live container) to generate high-quality English/German PDFs.
  7. Uploads the finalized packages to Google Drive via an Apps Script proxy.
  8. Synchronizes the application status back to the Google Sheets tracker.
  9. Marks the application state in `index.md` as `'draft'` (or `'failed'` on crash).



## 5. End-to-End User Story Walkthroughs

### Story 1: Create Application (Standard Path)
* **Step 1 (Ingestion & Scoring):** The user provides a job URL or Gmail text. The guest fetcher scrapers (`fetch_linkedin_job`, `fetch_indeed_job`, `fetch_public_job_url`) parse the details and save them via `save_job_description`. The job is scored.
* **Step 2 (Stage 1 - Markdown Generation):** The user triggers the tailoring pipeline via `create_application_from_job`. The LLM runs in the background, crafts tailored markdown drafts bilingually, saves them on disk, and populates the `applications` database table with the text (`cv_en`, `cover_letter_en`, etc.). The status becomes `'draft'`.
* **Step 3 (Stage 2 - PDF Compilation):** The user reviews the generated markdown texts and is happy. They call `create_pdf_from_markdown`. The background worker validates the markdown to ensure no leftovers or brackets exist, compiles the LaTeX PDF, uploads it to Google Drive, and syncs status. The status remains `'draft'` and `drive_url` is saved.
* **Step 4 (Applied Sync):** The user applies to the company and calls `update_application_status` with `status="applied"`, which pushes the updated status to their central Google Sheet tracker.

### Story 2: Create Application with Manual Revision (Iterative Updates)
* **Step 1 (Generation):** The user generates an application via `create_application_from_job`.
* **Step 2 (Iterative Cover Letter Revision):** The user is not fully satisfied with the cover letter (e.g. they want it shorter or more casual). They call `revise_cover_letter(slug, revision_instructions)` with specific feedback. The LLM reads the previous draft and user instructions, generates the revised markdown, saves it to disk and the DB, and returns the result.
* **Step 3 (Iterative CV Revision):** The user wants to adjust a bullet point on their CV. They call `revise_cv(slug, revision_instructions)`. The LLM reads the previous `cv.md`, applies the adjustments, saves it to disk and the DB, and returns the result.
* **Step 4 (Compilation & Sync):** The user is now satisfied. They call `create_pdf_from_markdown` to compile their customized markdown drafts into high-quality PDFs and sync with Google Drive.
* **Step 5 (Applied Sync):** The user applies and updates status to `'applied'`.

### Story 3: Incorrect PDF Generation & Regeneration
* **Step 1 (Compilation Failure or Error):** The user compiles an application, but due to a rendering error, incorrect Markdown formatting, or a missing field, the compile fails or the PDF output contains formatting flaws.
* **Step 2 (Markdown Adjustment):** The user modifies the markdown draft (either directly on disk, or using revision tools to address the formatting flaw).
* **Step 3 (PDF Regeneration):** The user calls `create_pdf_from_markdown(slug)` again. Because the application status is `'draft'` or `'failed'`, the background queue picks it up, runs the LaTeX compiler to overwrite the existing PDFs on disk, uploads the corrected files to Google Drive, and updates the tracking state.

---

## 6. Implementation Gaps & Future Roadmap

To fully satisfy the end-to-end user stories (especially Story 2 and 3), we have identified the following gaps in our current implementation:

### Gap 1: Missing Revision/Editing Tools via MCP (Story 2)
* **Current Status:** Users currently have no way to dynamically update or refine generated drafts (`cv.md` or `cover-letter.md`) via natural language feedback instructions without opening a local text editor.
* **Roadmap Recommendation:** Expose two new MCP tools:
  1. `revise_cover_letter(slug: str, revision_instructions: str) -> str`: Loads the current cover letter from the DB/disk, calls the LLM with the user's instructions as a revision prompt, and updates the file on disk and the DB atomically.
  2. `revise_cv(slug: str, revision_instructions: str) -> str`: Loads the current CV markdown, uses the LLM to apply direct content revisions/updates based on user feedback, and saves/returns the updated CV draft.

### Gap 2: Missing Smart Regeneration/Clearance Tool via MCP (Story 4)
* **Current Status:** The CLI has a robust `scripts/regenerate_application.py` pipeline (which deletes local directories, purges the DB row, and starts a fresh new generation). However, this capability is not exposed via the MCP server interface.
* **Roadmap Recommendation:** Expose a new MCP tool:
  * `regenerate_application(slug: str) -> str`: Triggers the smart regeneration pipeline, purging local file caches and DB rows before enqueuing a fresh Stage 1 tailoring task automatically.

### Gap 3: Missing In-Memory Queue Deletion / Cancel Tool
* **Current Status:** If a user enqueues a Stage 1 or Stage 2 task by mistake (or if a compilation task hangs), there is currently no way to cancel or dequeue that item in-memory.
* **Roadmap Recommendation:** Expose a new MCP tool:
  * `cancel_queued_task(slug: str) -> str`: Removes any pending generation or compilation task for a given slug from the sequential queue.

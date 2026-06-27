# Operational Insights & Best Practices for Model Context Protocol (MCP)

This document outlines key strategies, guardrails, and recovery actions for agents using the `cv-tailor` MCP server. Follow these guidelines to prevent rate limits, resolve timeouts, and maximize system reliability.

---

## 1. Scraping Delays & Pacing
When fetching public job posting pages natively or crawling them, CDNs and Web Application Firewalls (like Cloudflare, Akamai, or AWS WAF) heavily monitor rapid sequential hits.
*   **Implement Randomized Delays**: Always inject a randomized **5 to 10-second pause** (e.g., `time.sleep` or task pauses) between consecutive `fetch_public_job_url` or `extract_job_details` calls.
*   **Anti-Bot Evision**: Rapid back-to-back requests will result in HTTP `429 Too Many Requests` or redirection to a CAPTCHA wall, breaking the automated pipeline.
*   **Batching Limits**: Do not attempt to ingest more than **3 to 5 jobs** in a single user session without clear spacing.

---

## 2. Timeout Recovery (MCP Error -32001)
The Model Context Protocol client has a strict timeout (usually 30 to 60 seconds). Because Playwright browser crawling (`extract_job_details`) spawns headless Chromium, manages displays, and waits for complex JavaScript to settle, it can easily cross this threshold.

### Fallback Protocol:
If a browser-crawling operation (`extract_job_details`) fails with a `-32001` timeout or is blocked by a CAPTCHA:
1.  **Switch to Direct Path (Preferred)**: Fetch the raw HTML content lightweightly using `fetch_public_job_url(url)`. This tool does not spin up a browser, uses standard HTTP, and returns cleanly in under 2 seconds.
2.  **Extract Details**: Read the returned text content, identify the `company`, `title`, and `description` fields.
3.  **Persist Directly**: Write the details using `save_job_description(company, title, url, description, location)`. This writes the record directly to your database and generates the conforming slug in milliseconds.
4.  **Tailor application**: Proceed directly to `create_application_from_job(slug)`.

---

## 3. Warm Sessions & Playwright Login
*   `extract_job_details` is specifically designed for complex, session-locked networks (like LinkedIn) where public unauthenticated page crawlers are heavily rate-limited or blocked.
*   It relies on a **pre-warmed LinkedIn session** (storing active authentication cookies). If the session expires or is invalidated, LinkedIn will force a login redirect, causing the scraper to hang and time out.
*   **Action Required**: If you repeatedly get timeouts on LinkedIn pages, notify the user to run the standard session warmup/login sequence to refresh the session cookies.

---

## 4. Concurrency Guardrails
The downstream document generation pipeline (`create_application_from_job`) is resource-intensive:
*   It invokes local LLMs (via Ollama or APIs) for deep tailoring.
*   It compiles complex TeX layouts via a localized Docker-based LaTeX processor.
*   It synchronizes file structures via Google Drive and Sheets proxies.
*   **CRITICAL**: Do **NOT** run multiple concurrent application-creation tasks. Run them strictly sequentially to prevent CPU/memory exhaustion, LaTeX compiler race conditions, or rate-limiting on Google API endpoints.

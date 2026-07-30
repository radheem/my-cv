# Playwright Scraper Endpoint

## Overview

Add a generic HTTP scraping endpoint to the `ingest` Docker container that accepts any URL, navigates to it using a **persistent Chromium browser pool** (launched once at container start via Playwright), and returns the page's raw inner text. Each request creates a new isolated page + browser context but reuses the same Chromium process — avoiding the ~2s launch penalty per scrape.

This allows the cv-tailor MCP tools (`fetch_indeed_job`, `extract_job_details`, any future scraper) to route their browser-based scraping through the container's Playwright instance instead of running headless Chromium on the host.

## Functional Requirements

### 1. Persistent Browser Pool (Startup)

- On container startup, a background process spawns Playwright and launches Chromium (`headless=True` via `p.chromium.launch()`).
- The browser process remains alive for the container's lifetime.
- If the browser crashes, the pool must detect the disconnection and automatically relaunch.
- The pool exposes a thread-safe `get_browser()` function returning the live browser handle.

### 2. Generic Scrape Endpoint

**Route:** `GET /scrape/text?url=<url>`
**Behavior:**
- Creates a new isolated browser context (no cookie/session bleed between requests).
- Applies `stealth_sync(page)` for anti-detection.
- Navigates to `<url>` with `wait_until="load"` and a 30-second timeout.
- Returns `{"url": "<url>", "text": "<page inner_text body>", "success": true}`.
- On failure: returns `{"url": "<url>", "error": "<reason>", "success": false}` with appropriate HTTP status (504 for timeout, 502 for other errors).
- If the browser pool is not yet ready, returns 503.

### 3. Health Endpoints

**`GET /health`:**
- Returns `{"status": "ok"}` if the container is running and the HTTP server is accepting requests.

**`GET /browser-health`:**
- Lightweight check: returns `{"status": "ok", "browser": "alive"}` if the Chromium process PID is alive.
- Returns `{"status": "error", "browser": "dead"}` if the process has exited.

### 4. Site-Specific Route (Future)

- The generic endpoint handles all URLs initially.
- When a site requires special handling (cookies, login, custom selectors), a dedicated route like `GET /scrape/indeed/{job_id}` can be added later without changing the generic path.

## Non-Functional Requirements

- **Performance:** Browser startup cost paid exactly once per container lifetime. Each subsequent request creates only a new page/context (~100ms vs ~2s for full launch).
- **Isolation:** Each request uses `browser.new_context()` to prevent cookie/localStorage/session bleed.
- **Testability:** The endpoints are standard FastAPI routes, testable via pytest with httpx.

## Acceptance Criteria

1. `GET /health` returns 200 `{"status": "ok"}` when container is up.
2. `GET /browser-health` returns 200 `{"status": "ok", "browser": "alive"}` when Chromium is running.
3. `GET /scrape/text?url=https://example.com` returns the page text within 30s.
4. `GET /scrape/text?url=https://invalid.nonexistent` returns a 502/504 error with `success: false`.
5. Consecutive requests do not share cookies (each gets a fresh context).
6. If Chromium crashes, `/browser-health` reports "dead" and the pool auto-restarts it.

## Out of Scope

- HTML or markdown output formats (raw text only).
- Batch scraping (single URL per request).
- Authentication/authorization for the scraper endpoint.
- Persistent authenticated sessions (LinkedIn login flows).

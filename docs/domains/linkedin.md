# Bounded Context: LinkedIn Ingestion Domain

## Overview
The `linkedin` domain manages all interactions with the LinkedIn platform. It covers two distinct scraping pathways: the **Direct Public Guest API** path (for rapid, unauthenticated text extraction under 2 seconds) and the **Authenticated Browser Crawler** path (for session-credentialed, Playwright-driven crawling of protected job postings).

## Domain Boundaries
*   **Included Concerns**:
    *   Warming and maintaining Playwright browser contexts.
    *   Paced human-like scrolling, clicking, and typing delays to resist bot detection.
    *   Surfacing OTP challenge pages and CAPTCHA screens to a local virtual display (VNC) for human-in-the-loop hand-offs.
    *   Fetching public job postings via the guest API (`jobs-guest`).
    *   Parsing and cleaning HTML job description bodies into readable plain text.
    *   Writing job descriptions to local `.txt` frontmatter backups.
*   **Excluded Concerns**:
    *   Orchestrating search alert queues (handled by `gmail` domain).
    *   Evaluating or ranking job matches (handled by `tailoring` domain).

## Core Components
1.  **`session.py` (Playwright Engine)**:
    *   Configures headful or headless persistent browser profiles.
    *   Classifies page states (Login screen, OTP challenge, Security check, Feed).
    *   Handles state transitions and auto-relogins.
2.  **`jobs.py` (Parser & Scraper)**:
    *   Implements `capture_jd` which navigates directly to a job posting and extracts its content.
    *   Manages the local `.seen.json` deduplication database and write-back configurations.
3.  **`humanize.py` (Anti-Bot Helpers)**:
    *   Supplies humanized cursor/page scroll motions and variable sleep delays.

## Inputs & Outputs
*   **Inputs**:
    *   `job_id` (string): Standard 10-digit LinkedIn job posting identifier.
    *   `job_url` (string): LinkedIn URL link.
*   **Outputs**:
    *   Cleaned, unescaped job description plain text.

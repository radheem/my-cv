# Bounded Context: Gmail Alerts & Ingestion Domain

## Overview
The `gmail` domain is responsible for the **Discovery** phase of the job-hunting pipeline. It connects securely to the Gmail API via an external Google Apps Script web application proxy, retrieves unread alert emails from major job boards, extracts raw job URLs from email bodies, and normalizes them into platform-specific identifiers.

## Domain Boundaries
*   **Included Concerns**:
    *   Authenticating and establishing connections to Google Apps Script.
    *   Searching, retrieving, and modifying (marking read/starred) Gmail email threads.
    *   Parsing email bodies (HTML or plain text) to extract links.
    *   Normalizing job posting URLs and extracting platform-specific `job_id` keys.
*   **Excluded Concerns**:
    *   Scraping actual webpage contents (handled by platform-specific crawler domains).
    *   Writing job descriptions to the PostgreSQL database (handled by presentation orchestrators).

## Core Components
1.  **`client.py` (Gmail Connector)**:
    *   Handles the low-level OAuth-less HTTPS connection with the Google Apps Script proxy.
    *   Exposes `search_emails`, `get_thread`, `batch_modify_threads`, and `batch_send_emails`.
2.  **`ingest.py` (Workflow & Parser)**:
    *   Implements the high-level alert discovery workflow (`list_gmail_jobs_workflow`).
    *   Houses `parse_and_normalize_job_url()` which extracts platform-specific numeric or alphanumeric keys from unstructured URLs (LinkedIn, Indeed, Fraunhofer).

## Inputs & Outputs
*   **Inputs**:
    *   `query` (string): Standard Gmail search filter (e.g., `is:unread`).
    *   `provider` (string): The alert sender tag (e.g., `linkedin`, `indeed`).
*   **Outputs**:
    *   JSON array of discovered listings with `job_id`, `company`, `role`, `job_url`, and `brief_description` snippet.

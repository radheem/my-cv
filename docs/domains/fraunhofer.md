# Bounded Context: Fraunhofer Ingestion Domain

## Overview
The `fraunhofer` domain is a specialized scraper submodule designed to harvest job descriptions from the scientific research job portal of the **Fraunhofer-Gesellschaft** (`jobs.fraunhofer.de`). It parses their unique page templates to pull out role requirements and details.

## Domain Boundaries
*   **Included Concerns**:
    *   Loading and interacting with `jobs.fraunhofer.de` view links.
    *   Parsing the specific HTML structure of Fraunhofer listings.
    *   Extracting the title from Fraunhofer job URLs (`_title_from_url`).
*   **Excluded Concerns**:
    *   OAuth or email checking (handled by `gmail` domain).
    *   State updates and PostgreSQL database syncs.

## Core Components
1.  **`jobs.py` (Fraunhofer Scraper)**:
    *   Uses Playwright to navigate to a view link.
    *   Locates and extracts the text within Fraunhofer's specific content classes (e.g., extracting description text).
    *   Implements `_title_from_url` to parse clean titles out of URLs.

## Inputs & Outputs
*   **Inputs**:
    *   `url` (string): Active Fraunhofer job view link.
*   **Outputs**:
    *   Cleaned scientific job description text.

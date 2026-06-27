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
        C --> D[PostgreSQL Upsert: INSERT ... ON CONFLICT DO UPDATE]
        D --> E[Write Backup <slug>.txt with frontmatter to vault/jds/]
        D --> F[Write Backup <slug>.json metadata to vault/jds/]
    end

    E & F --> G[Generate Job Slug: company-title-job_id]
    
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
    participant DB as PostgreSQL Database

    Agent->>MCP: call_tool: fetch_public_job_url(url)
    MCP-->>Agent: Return stripped, clean plain-text job content
    Note over Agent: Extract company, title,<br/>location, and description
    Agent->>MCP: call_tool: save_job_description(company, title, url, description, ...)
    MCP->>DB: Upsert job via write_jd()
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
    participant DB as PostgreSQL Database

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
        Worker->>DB: Upsert job via write_jd()
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

# Architecture

A deliberate split: **content generation + rendering run locally** (they cost money, need
review, and need an LLM / LaTeX), while **CI only builds the public portfolio**. Tailored
documents never touch the public site — they go to Google Drive, and their status is tracked in
git.

```mermaid
flowchart TB
    subgraph Host ["Host Environment (User radr: 1016:1017)"]
        CLI[cv-tailor CLI]
        FILES[(Local Filesystem: applications/, vault/)]
    end

    subgraph Docker ["Docker Compose Stack"]
        subgraph mcp_container ["MCP Server Container (user 1016:1017)"]
            MCPS[FastMCP Server]
            ENGINE[Python Core Engine]
            PLAY[Playwright Scraper]
            LATEX[Local LaTeX / latexmk]
        end
    end

    subgraph External ["External Services"]
        LLM[Ollama qwen3.6:35b / Anthropic API]
        GMAIL[(Gmail Server)]
        DRIVE[(Google Drive)]
        SHEETS[(Google Sheets Tracker)]
    end

    %% Host connections
    CLI -->|Read/Write/Query| FILES

    %% MCP connections
    MCPS -->|Triggers Workflows| ENGINE
    ENGINE -->|Read/Write/Query| FILES
    ENGINE -->|Crawl Pages| PLAY
    ENGINE -->|Compile PDFs| LATEX

    %% External connections
    PLAY -->|Fetch Alerts/Postings| GMAIL
    PLAY -->|Scrape Description| External
    ENGINE -->|Tailor CV/CL| LLM
    ENGINE -->|Upload PDFs| DRIVE
    ENGINE -->|Sync Status| SHEETS
    ENGINE -->|Resolve host.docker.internal| LLM
```

## The two halves

| | Generation + rendering (`engine/`, `latex/`) | Publish (CI) |
|---|---|---|
| Runs | locally, on demand | GitHub Actions on push |
| Needs | LLM (Anthropic key or local Ollama) + LaTeX (latexmk / Docker) | nothing — no secrets |
| Output | bilingual PDFs → Drive; status in git | the public portfolio + the generic CV PDF |

The privacy guarantee is **structural**: `applications/` lives outside `docs/`, so `mkdocs build`
never sees it — no company name can appear in the site, sitemap, or search index. (This replaces
the old encrypted-gate design entirely.)

## Generation pipeline

`cv-tailor new <job-url-or-file>`:

1. **`fetch.py`** → clean job text (URL via Playwright, or a pasted `.txt`/`.md`).
2. **`jobspec.py`** → a structured **JobSpec** via `llm.structured_json` (json-schema constrained).
3. **`rank.py`** → the **top-3 projects** and the ordered **skills block**. Pure, no I/O, no LLM —
   unit-tested. Scores by token overlap (with tag aliasing `k8s→kubernetes`), **cluster affinity**,
   and per-project **weight**, steered by `data/taxonomy.yml` + `data/ranking.yml` (optional,
   default-inert). The same taxonomy writes the job's `clusters` into `index.md`.
4. **`render.py`** → tailored `cv.md` + `cover-letter.md` (prose around the chosen projects/skills;
   never picks them), then a German **translation pass** → `cv.de.md` / `cover-letter.de.md`.

## Markdown → LaTeX (the renderer)

`engine/latex.py` deterministically turns the LLM's Markdown into LaTeX for the
`resume` template — **the model never emits LaTeX**, so escaping and structure are always valid.

```mermaid
flowchart LR
    EN[cv.md / cover-letter.md] --> R[latex.py]
    DE[cv.de.md / cover-letter.de.md] --> R
    PROJ[(projects.yml — page URLs)] --> R
    R --> TEX[.tex\nEN page + \\clearpage\\selectlanguage{ngerman} + DE page]
    TEX --> MK[latexmk → 2-page PDF]
```

- Maps the known CV structure onto the class macros — `## Experience`→`\section`, `### Org — Role`
  + `*loc · dates*`→`\role`, bullets→`\bullets`, `## Projects`→`\project{name}{url}{desc}` (URLs
  resolved from `projects.yml`, reused positionally for the German page), `## Skills`→`\item`.
- Cover letter: `\senderblock` + `\recipient` + `\opening` + paragraphs + `\closing`, English then
  German (salutation `Dear …,` / `Sehr geehrte…,`).
- Compiled by `scripts/build-application.sh` (local `latexmk`, else the `texlive/texlive` Docker
  image). The shared classes live in `latex/` and are resolved via `TEXINPUTS`.

## Application records, status & database

The absolute source of truth for all application metadata, raw job descriptions, and tailored CV/letter text is the **local filesystem** under `applications/<slug>/` and `vault/jds/*.json`.

A local PostgreSQL database is no longer used. Instead, `cv-tailor` implements a zero-config, serverless setup:
- **Filesystem Source of Truth**: All status transitions, Drive links, and metadata are written directly to the frontmatter of `applications/<slug>/index.md`.
- **In-Memory DuckDB Cache**: For complex queries, analytical scoring, and MCP agent search capabilities, an in-memory **DuckDB engine** dynamically registers local JSON and Markdown files as SQL tables on the fly.
- **Google Sheets Sync**: Status changes are pulled from Google Sheets directly to `index.md` files on disk, and pushed back by compiling `applications/tracker.csv` directly from files.
- **Seen Jobs**: Scraped jobs are saved as JSON files in `vault/jds/` which serves as the discovery queue and Seen check.

## Repository layout

| Path | Role |
|---|---|
| `data/` | source of truth — `master-cv.md`, `profile.yml`, `projects.yml`, guides, prompts |
| `engine/rank.py` | **pure** ranking — unit-tested |
| `engine/jobspec.py`, `engine/render.py` | LLM calls (local only) incl. German translation |
| `engine/latex.py` | deterministic Markdown → LaTeX (bilingual) |
| `engine/cli.py`, `engine/fetch.py` | CLI entrypoint + job fetcher |
| `engine/shared/db.py` | DuckDB database connection wrapper and automatic file preloading |
| `engine/mcp/` | Model Context Protocol (MCP) server for secure database open-queries |
| `latex/` | `resume.cls`, `coverletter.cls`, `resume.tex` (public CV) |
| `scripts/build-application.sh` | compile an app's `.tex` → PDFs |
| `apps-script/Code.gs` | Google Drive uploader (`doPost`, owner-run) |
| `applications/<slug>/` | one dir per application (md + `.tex` + `index.md`); PDFs gitignored |
| `docs/` | the **public** portfolio (never holds applications) |
| `.github/workflows/deploy.yml` | compile public CV + `mkdocs build` → Pages |

## Model Context Protocol (MCP) Server

To enable fully autonomous, conversational job hunt metrics and application tracking, the project embeds a serverless **DuckDB Model Context Protocol (MCP) Server**. 

Using a strict, comment-aware `sqlguard` whitelisting query parser, the server exposes two powerful tools to AI agents:
1.  **`cv_tailor_ontology()`**: Exposes the table layouts, columns, types, and FK joins of our schema so agents understand the database layout out-of-the-box.
2.  **`query(sql)`**: Evaluates read-only `SELECT` / `WITH` statements, preventing SQL injection or mutations, and capping return records to a hard 1000-row limit.

Start the server locally or wire it into your desktop clients via:
```bash
make mcp
```

See [Setup](setup.md) to run it end to end.

---

## Workflow Sequence Diagrams

These sequence diagrams detail the end-to-end execution path for each of our core modular workflows, illustrating their specific purposes and interactions with external resources.

### 1. Gmail Alert Job Listing Workflow (`list_gmail_[provider]_jobs`)
*   **Purpose:** To securely query your Gmail inbox via the Apps Script API Proxy for unread job alert emails from a specified provider (LinkedIn, Glassdoor, or Indeed) using specialized tools (`list_gmail_linkedin_jobs`, `list_gmail_glassdoor_jobs`, `list_gmail_indeed_jobs`), parse their bodies to extract target links, normalize them, and compile a clean, lightweight list of newly discovered postings with tentative metadata (including `job_id`, `company`, `role`, and `brief_description`) without executing any heavy web-scraping or modifications.

```mermaid
sequenceDiagram
    autonumber
    actor Client as MCP Client (Agent/User)
    participant Server as FastMCP Server
    participant WF as list_gmail_jobs_workflow
    participant Config as config/search.yml
    participant Gmail as Gmail (via Proxy)

    Client->>Server: tools/call list_gmail_linkedin_jobs(query, limit)
    Server->>WF: Invoke list_gmail_jobs_workflow("linkedin", query, limit)
    WF->>Config: resolve_search() to get provider's alert email
    Config-->>WF: Return alert email address
    WF->>Gmail: search_emails(query, limit)
    Gmail-->>WF: Return unread alert thread bodies
    loop For each message body
        WF->>WF: extract_urls_from_text(body)
        WF->>WF: parse_and_normalize_job_url(url)
        WF->>WF: extract_job_metadata_from_body(surrounding_text)
    end
    WF-->>Server: Return JSON list of tentative job records
    Server-->>Client: 200 OK with job listing JSON
```

---

### 2. Ad-hoc Job Scraping Workflow (`extract_job_details`)
*   **Purpose:** To take a specific job posting URL, validate and normalize it, spawn a Chromium Playwright browser in a clean, isolated subprocess (to completely isolate standard input/output streams and prevent MCP console channel noise), bypass any anti-bot or session hurdles, scrape the full job description, and write a file-system backup under `vault/jds/` which serves as the source of truth for the local serverless DuckDB cache.

```mermaid
sequenceDiagram
    autonumber
    actor Client as MCP Client (Agent/User)
    participant Server as FastMCP Server
    participant WF as extract_job_details_workflow
    participant Sub as Playwright Subprocess
    participant Page as Job Posting Page

    Client->>Server: tools/call extract_job_details(url)
    Server->>WF: Invoke extract_job_details_workflow
    WF->>WF: parse_and_normalize_job_url(url)
    WF->>Sub: spawn process to run _capture_jobs_process_worker
    activate Sub
    Sub->>Page: Go to URL (anonymous headless Chromium)
    Page-->>Sub: Return page HTML / Text content
    Sub->>Sub: J.write_jd() saves to vault/jds/ (JSON + TXT)
    Sub-->>WF: Put success and slugs on Queue
    deactivate Sub
    WF-->>Server: Return success string with slug
    Server-->>Client: 200 OK with success slug
```

---

### 3. Bilingual Tailoring & Application Upload Workflow (`create_application_from_job`)
*   **Purpose:** To execute the downstream application compilation and tracking process for an ingested job slug. It triggers LLM queries to parse the JobSpec, adapts your master resume structure, and writes tailored English and German Markdown packages on disk (which serve as the source of truth for the serverless DuckDB cache). It then compiles them locally using the containerized LaTeX engine to create polished PDFs, uploads them to your secure Google Drive, and instantly pushes the tracking status to Google Sheets.

```mermaid
sequenceDiagram
    autonumber
    actor Client as MCP Client (Agent/User)
    participant Server as FastMCP Server
    participant WF as create_application_from_job_workflow
    participant CLI as cli.py (cmd_new / cmd_pdf / cmd_upload)
    participant LLM as Ollama / Anthropic
    participant LaTeX as Local pdflatex/latexmk
    participant Drive as Google Drive (via Proxy)
    participant Sheets as Google Sheets Tracker

    Client->>Server: tools/call create_application_from_job(slug)
    Server->>WF: Invoke create_application_from_job_workflow
    
    WF->>CLI: Call cmd_new(slug)
    CLI->>LLM: 1. query() to extract JobSpec
    LLM-->>CLI: Return JobSpec JSON
    CLI->>LLM: 2. query() to rank & tailor profile
    LLM-->>CLI: Return Tailoring JSON
    CLI->>LLM: 3. query() to render CV prose
    LLM-->>CLI: Return cv.md
    CLI->>LLM: 4. query() to render Cover Letter
    LLM-->>CLI: Return cover-letter.md
    CLI->>LLM: 5. query() to translate CV & CL to German
    LLM-->>CLI: Return cv.de.md & cover-letter.de.md
    CLI-->>WF: Success CV & CL generated on disk
    
    WF->>CLI: Call cmd_pdf(slug)
    CLI->>LaTeX: Run latexmk -pdf cv.tex / cover-letter.tex
    LaTeX-->>CLI: Return compiled cv.pdf / cover-letter.pdf
    CLI-->>WF: PDFs compiled locally
    
    WF->>CLI: Call cmd_upload(slug)
    CLI->>Drive: Upload PDFs (via doPost Apps Script)
    Drive-->>CLI: Return Google Drive Folder URL
    CLI-->>WF: PDFs uploaded & drive_url updated in index.md
    
    WF->>CLI: Call cmd_status(slug="push")
    CLI->>Sheets: Sync tracker.csv to Google Sheet (pushed rows)
    Sheets-->>CLI: Success sync
    CLI-->>WF: Sheets synchronization successful
    
    WF-->>Server: Return completion summary log
    Server-->>Client: 200 OK with tailoring summary report
```

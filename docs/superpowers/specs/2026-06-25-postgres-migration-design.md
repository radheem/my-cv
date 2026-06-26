# Postgres Application Tracking and Ingestion Pipeline Design

- **Date:** 2026-06-25
- **Status:** Approved (Revised)
- **Author:** Gemini CLI

---

## 1. Overview & Objectives

The goal is to transition the `cv-tailor` project's persistent state and application content from raw, unstructured flat files on the filesystem (`tracker.csv`, `vault/jds/*`, `.seen.json`) to a structured PostgreSQL 17 database. 

Final generated files (Markdown and compiled PDFs) will continue to reside in the `applications/` directory for local viewing and printing, but the database will become the single source of truth for the raw Markdown text, metadata, and ingestion history. 

This design will:
*   Eliminate filesystem clutter in the `vault/` directory.
*   Enforce structured relational schemas for job descriptions and application records.
*   Provide robust, explicit synchronization commands (`push` and `pull`) to transfer content between files and the DB, and statuses between the DB and Google Sheets.
*   Support a comprehensive data export function to dump database backups back to flat files.

---

## 2. System Architecture & Docker Integration

We will run PostgreSQL 17 locally within Docker Compose, exposing port `5432` for connection.

### `docker-compose.yml` Updates
A new `db` service running `postgres:17-alpine` will be added. A named volume `pgdata` will ensure local data persistence.

```yaml
services:
  ingest:
    # ...
    depends_on:
      - db
    environment:
      # ...
      DATABASE_URL: ${DATABASE_URL:-postgresql://postgres:postgres@db:5432/cv_tailor}

  db:
    image: postgres:17-alpine
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: cv_tailor
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

### Database Connection & Client
We will write a dedicated Python client module `engine/db.py` utilizing the `psycopg` (v3) binary driver. This client will dynamically read the database connection string from the `DATABASE_URL` environment variable, defaulting to local PostgreSQL if unset.

---

## 3. Database Schema

### Table: `jobs`
Tracks all crawled job descriptions, metadata, scores, and ingestion lineage.

To support legacy data ingestion where source job IDs or raw description texts may be missing, `job_id` and `description` are configured as **nullable** fields.

```sql
CREATE TABLE IF NOT EXISTS jobs (
    slug VARCHAR(255) PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE,        -- Nullable to support legacy folders
    company VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    url TEXT,
    description TEXT,                  -- Nullable to support legacy folders
    score INTEGER,
    applicants INTEGER,
    source VARCHAR(50) NOT NULL,       -- 'file', 'gmail', 'url'
    platform VARCHAR(50) NOT NULL,     -- 'linkedin', 'glassdoor', 'fraunhofer', 'other'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `applications`
Stores application lifecycle status, generated bilingual Markdown documents, and matching taxonomy clusters.

```sql
CREATE TABLE IF NOT EXISTS applications (
    slug VARCHAR(255) PRIMARY KEY REFERENCES jobs(slug) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- 'draft', 'applied', 'interview', 'offer', 'rejected', 'withdrawn'
    recipient VARCHAR(255),
    cv_en TEXT,
    cv_de TEXT,
    cover_letter_en TEXT,
    cover_letter_de TEXT,
    drive_url TEXT,
    clusters TEXT[],                   -- Postgres array to store taxonomy classifications
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. CLI Interfacing & Commands

We will introduce a set of unified commands under `cv-tailor` to drive the PostgreSQL workflow.

### A. Filesystem Sync (`cv-tailor db push | pull`)
*   `cv-tailor db pull [slug]`: Writes `cv_en`, `cv_de`, `cover_letter_en`, and `cover_letter_de` from the DB table directly into local files at `applications/<slug>/` (overwriting changes). If no slug is specified, it pulls all active applications.
*   `cv-tailor db push [slug]`: Reads local files in `applications/<slug>/` and overwrites the DB content. If no slug is specified, it pushes all local applications.

### B. Google Sheets Sync (`cv-tailor status push | pull`)
To prevent overwriting vital metadata inside Google Sheets, `cv-tailor status push` will automatically **join** `jobs` and `applications` to construct the full 9-column CSV matrix required by Google Sheets (`slug`, `company`, `job_title`, `status`, `recipient`, `date_found`, `drive_url`, `clusters`, `updated_at`).
*   `cv-tailor status push`: Pushes the fully reconstructed 9-column application records matrix from the DB to Google Sheets.
*   `cv-tailor status pull`: Pulls updated statuses, recipient names, or metadata from Google Sheets and writes them to the DB.

### C. Database Backup Export (`cv-tailor db export`)
Backs up and exports the entire database state into a single directory `application-data/`:
*   `application-data/applications.csv`: Raw applications table dump.
*   `application-data/jobs.csv`: Raw jobs table dump.
*   `application-data/jds/<slug>.txt`: Plain text of every captured job description (serving as the "seen" archive).
*   `application-data/applications/<slug>/`: Folder containing `cv.md`, `cv.de.md`, `cover-letter.md`, `cover-letter.de.md`, and `meta.json` (metadata like status, drive URL, source, etc.).

---

## 5. Migration Strategy & Backward Compatibility

1.  **Deduplication & Crawler Integration**: The database `jobs` table fully replaces `vault/jds/.seen.json`. 
    - `cv-tailor capture`, `cv-tailor hunt`, and `cv-tailor ingest` are refactored to read/write directly from/to the `jobs` database table instead of raw JSON seen files.
    - All shell pipelines (`job-hunt.sh`, `erfurt-hunt.sh`, `gmail-hunt.sh`) are updated to rely on PostgreSQL for duplication checks and scoring.
2.  **Legacy Ingestion Migration**: We will provide a one-off CLI tool `cv-tailor db migrate-legacy` that:
    - Reads existing `applications/` directories.
    - Matches them against the corresponding rows in `tracker.csv`.
    - Synthesizes dummy `job_id` and `description` payloads where missing.
    - Writes the results directly into the `jobs` and `applications` Postgres tables.
3.  **Removal of Local Seen Files**: Once the migration is successfully tested, `tracker.csv`, `vault/jds/*`, `.seen.json`, and `.ranked.json` can be completely deleted from git.

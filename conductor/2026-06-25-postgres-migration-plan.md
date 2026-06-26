# Postgres Application Tracking and Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition cv-tailor's application metadata and crawling seen files to PostgreSQL 17 in Docker Compose, providing robust `db push / pull`, `status push / pull`, and `db export` utilities.

**Architecture:** We will spin up a local PostgreSQL 17 service in Docker Compose. We will use the lightweight `psycopg[binary]` driver inside our Python CLI `cv-tailor` to execute schema definition SQL, perform sync commands, write ingestion records, and export snapshots.

**Tech Stack:** PostgreSQL 17, Docker Compose, Psycopg 3, Python.

---

### Phase 1: Database Setup and Connection Engine

**Files:**
- Modify: `docker-compose.yml`
- Modify: `pyproject.toml`
- Create: `engine/db.py`
- Create: `tests/test_db.py`

- [ ] **Step 1.1: Add postgres to docker-compose**
  Open `docker-compose.yml` and add the `db` service and `pgdata` volume:

```yaml
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

- [ ] **Step 1.2: Add psycopg to pyproject.toml**
  Add `"psycopg[binary]>=3.1.18"` to dependencies in `pyproject.toml` and sync the project dependencies:
  Run: `uv sync --all-extras`

- [ ] **Step 1.3: Implement the Database Client (`engine/db.py`)**
  Create a client module `engine/db.py` to handle database connections, connection pooling, and initial schema application.

```python
import os
import logging
import psycopg
from psycopg.rows import dict_row

log = logging.getLogger("cv-tailor")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cv_tailor")

def get_conn():
    """Retrieve a raw connection to the database."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    """Initialize the jobs and applications tables."""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS jobs (
        slug VARCHAR(255) PRIMARY KEY,
        job_id VARCHAR(100) UNIQUE,
        company VARCHAR(255) NOT NULL,
        title VARCHAR(255) NOT NULL,
        location VARCHAR(255),
        url TEXT,
        description TEXT,
        score INTEGER,
        applicants INTEGER,
        source VARCHAR(50) NOT NULL,
        platform VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS applications (
        slug VARCHAR(255) PRIMARY KEY REFERENCES jobs(slug) ON DELETE CASCADE,
        status VARCHAR(50) NOT NULL DEFAULT 'draft',
        recipient VARCHAR(255),
        cv_en TEXT,
        cv_de TEXT,
        cover_letter_en TEXT,
        cover_letter_de TEXT,
        drive_url TEXT,
        clusters TEXT[],
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            conn.commit()
    log.info("Database schema applied successfully.")
```

- [ ] **Step 1.4: Boot the database and verify**
  Run: `docker compose up -d db`
  Verify the service is running. Create initial basic tests in `tests/test_db.py` to verify schema generation and run:
  `uv run pytest tests/test_db.py -v`

- [ ] **Step 1.5: Commit Phase 1**
  ```bash
  git add docker-compose.yml pyproject.toml uv.lock engine/db.py tests/test_db.py
  git commit -m "feat(db): set up postgres 17 and database initialization layer"
  ```

---

### Phase 2: Legacy Migration CLI Tool & Initial Tests

**Files:**
- Modify: `engine/db.py`
- Modify: `engine/cli.py`
- Modify: `tests/test_db.py`

- [ ] **Step 2.1: Write the migration helper inside `engine/db.py`**
  Add a helper function `migrate_legacy_data()` in `engine/db.py` that reads directories under `applications/`, loads `index.md`, reads `tracker.csv`, and imports entries cleanly into `jobs` and `applications` tables.

- [ ] **Step 2.2: Add migrate CLI command inside `engine/cli.py`**
  Add `cv-tailor db migrate-legacy` command to parsing and execution logic in `engine/cli.py`.

- [ ] **Step 2.3: Write migration unit tests in `tests/test_db.py`**
  Add test cases to `tests/test_db.py` to test `migrate_legacy_data()` with temporary filesystem directories/CSV files and verify rows are written correctly in PostgreSQL.

- [ ] **Step 2.4: Execute the migration and verify**
  Run: `uv run cv-tailor db migrate-legacy`
  Verify migration logs. Run pytest:
  `uv run pytest tests/test_db.py -v`

- [ ] **Step 2.5: Commit Phase 2**
  ```bash
  git add engine/db.py engine/cli.py tests/test_db.py
  git commit -m "feat(db): implement legacy data migration CLI command"
  ```

---

### Phase 3: Filesystem, Sheets Synchronization, and Source Resolution

**Files:**
- Modify: `engine/cli.py`
- Modify: `engine/db.py`
- Modify: `engine/fetch.py`
- Modify: `tests/test_db.py`

- [ ] **Step 3.1: Refactor `fetch_job_text` in `engine/fetch.py`**
  Modify `fetch_job_text(source)` so that if the `source` is neither a URL nor an existing file path, but matches a `slug` in the database `jobs` table, it queries the database and returns the `description` text!

- [ ] **Step 3.2: Implement `db push` and `db pull`**
  Write CLI actions in `engine/cli.py` that read local Markdown files at `applications/<slug>/` and update the DB table (`push`), or conversely read text fields from PostgreSQL and overwrite filesystem Markdown files (`pull`).

- [ ] **Step 3.3: Implement `status push` and `status pull`**
  Refactor Google Sheets synchronization commands inside `engine/cli.py` (`cmd_sync_sheets` / `_pull_sheet_statuses` / `_push_to_sheets` etc.) to:
  - `status push`: Runs `SELECT j.slug, j.company, j.title, a.status, a.recipient, j.created_at, a.drive_url, a.clusters, a.updated_at FROM jobs j JOIN applications a ON j.slug = a.slug` to join the schemas, converts this matrix to CSV, and pushes it up to the Google Sheets Apps Script proxy.
  - `status pull`: Fetches CSV row status modifications from Google Sheets and writes them to PostgreSQL.

- [ ] **Step 3.4: Write unit tests for DB sync commands and source resolution**
  Add unit tests in `tests/test_db.py` to cover:
  - `fetch_job_text(slug)` with DB query fallback.
  - `db push` and `db pull` sync behavior with mock database transactions.

- [ ] **Step 3.5: Commit Phase 3**
  ```bash
  git add engine/cli.py engine/db.py engine/fetch.py tests/test_db.py
  git commit -m "feat(db): implement db push/pull, status push/pull, and db-backed job text resolution"
  ```

---

### Phase 4: Crawler, Search Pipeline, and Existing Tests Refactoring

**Files:**
- Modify: `engine/linkedin/jobs.py`
- Modify: `engine/fraunhofer/jobs.py`
- Modify: `engine/cli.py`
- Modify: `scripts/extract-email-urls.py`
- Modify: `scripts/score-jds.py`
- Modify: `scripts/job-hunt.sh`
- Modify: `scripts/erfurt-hunt.sh`
- Modify: `scripts/gmail-hunt.sh`
- Modify: `tests/test_extract_email_urls.py`
- Modify: `tests/test_linkedin_jobs.py`

- [ ] **Step 4.1: Refactor seen checks in Python Crawlers**
  Modify `load_seen` and `save_seen` in `engine/linkedin/jobs.py` and `engine/fraunhofer/jobs.py` to query PostgreSQL `SELECT 1 FROM jobs WHERE job_id = %s` instead of reading filesystem seen json files.
  Update crawler loops inside `engine/cli.py` (`_do_ingest`, `cmd_capture`) to write raw JDs, scores, and lineage (`source`, `platform`) directly to the PostgreSQL `jobs` table.

- [ ] **Step 4.2: Update `scripts/extract-email-urls.py`**
  Refactor `scripts/extract-email-urls.py` to connect directly to PostgreSQL via `get_conn()` and filter Gmail job URLs by checking if the numeric job ID exists in the `jobs` database table, fully bypassing `vault/jds/.seen.json`!

- [ ] **Step 4.3: Refactor `score-jds.py`**
  Modify `scripts/score-jds.py` to query raw postings from PostgreSQL `jobs` table, calculate match scores, write scores back to the DB `score` column, and print the ranked matches using database state!

- [ ] **Step 4.4: Refactor Shell Pipeline Scripts**
  Update `scripts/job-hunt.sh`, `scripts/erfurt-hunt.sh`, and `scripts/gmail-hunt.sh` to stop passing filesystem seen files, and call `cv-tailor new <slug>` (passing the database slug directly, resolved in Step 3.1) instead of `cv-tailor new vault/jds/<slug>.txt`.

- [ ] **Step 4.5: Refactor existing broken unit tests**
  Update `tests/test_extract_email_urls.py` and `tests/test_linkedin_jobs.py` (specifically `test_dedup_roundtrip`) which currently test or mock file-based seen-lists, refactoring them to use database mock connections or testing schemas cleanly.

- [ ] **Step 4.6: Commit Phase 4**
  ```bash
  git add engine/ scripts/ tests/
  git commit -m "refactor(db): integrate database seen-checks, crawling metrics, shell pipelines, and legacy tests into postgres"
  ```

---

### Phase 5: Database Flat Export and Legacy Clean-up

**Files:**
- Modify: `engine/cli.py`
- Modify: `engine/db.py`
- Modify: `.gitignore`

- [ ] **Step 5.1: Implement database export CLI command**
  Implement `cv-tailor db export` which creates `application-data/` on the filesystem, dumps table queries into CSV, and exports text logs of job descriptions and structured markdown files.

- [ ] **Step 5.2: Verify the exported backups**
  Run: `uv run cv-tailor db export`
  Ensure the files match the expected structured layout.

- [ ] **Step 5.3: Delete legacy tracking files from Git**
  Run: `git rm tracker.csv`
  Run: `git rm vault/jds/.seen.json` (and other legacy JDs files if present).
  Update `.gitignore` to ignore `application-data/` and `vault/jds/`.

- [ ] **Step 5.4: Final Verification and Commit**
  Run full unit test suite `uv run pytest` to ensure absolute stability.
  ```bash
  git add .
  git commit -m "feat(db): implement database export command and clean up filesystem files"
  ```

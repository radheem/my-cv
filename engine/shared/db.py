from __future__ import annotations

import os
import logging
import pathlib
import json
import hashlib
import datetime
import duckdb
from typing import Any
from engine import documents

log = logging.getLogger("cv-tailor")


def _get_vault_jds_dir() -> pathlib.Path:
    """Helper to get the vault/jds directory (facilitates mocking in tests)."""
    vault = os.getenv("CV_TAILOR_VAULT")
    if vault:
        return pathlib.Path(vault) / "jds"
    return pathlib.Path(__file__).resolve().parent.parent.parent / "vault" / "jds"


def _get_applications_dir() -> pathlib.Path:
    """Helper to get the applications directory (facilitates mocking in tests)."""
    return pathlib.Path(__file__).resolve().parent.parent.parent / "applications"


class DuckDBCursor:
    def __init__(self, con):
        self.con = con
        self.description = None
        self.rowcount = -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute(self, sql: str, params: Any = None):
        # Convert PostgreSQL %s parameter syntax to DuckDB ? syntax
        if "%s" in sql:
            # We replace %s with ? positional parameter placeholders
            sql = sql.replace("%s", "?")

        # Convert PostgreSQL CURRENT_TIMESTAMP to a VARCHAR-compatible strftime in DuckDB
        if "CURRENT_TIMESTAMP" in sql:
            sql = sql.replace("CURRENT_TIMESTAMP", "strftime(now(), '%Y-%m-%dT%H:%M:%SZ')")
            
        # Log/Print query for debugging
        if "applications" in sql or "CURRENT_TIMESTAMP" in sql:
            log.info(f"[DB DEBUG] Executing: {sql.strip()} with params: {params}")
            
        # Execute query
        if params is not None:
            # DuckDB expects a list or tuple of parameters.
            # If a single value is passed not in a tuple/list (e.g. list or string),
            # we make sure it's wrapped.
            if not isinstance(params, (tuple, list)):
                params = (params,)
            self.res = self.con.execute(sql, params)
        else:
            self.res = self.con.execute(sql)
            
        # Update rowcount
        try:
            self.rowcount = self.res.rowcount
        except Exception:
            self.rowcount = -1
            
        # Keep description updated for column access
        if self.res:
            self.description = self.res.description
            
        return self

    def fetchone(self):
        row = self.res.fetchone()
        if row is None:
            return None
        # Convert to dictionary using description keys, translating count_star() for Postgres compatibility
        cols = []
        for desc in self.description:
            name = desc[0]
            if name == "count_star()":
                name = "count"
            cols.append(name)
        return dict(zip(cols, row))

    def fetchall(self):
        rows = self.res.fetchall()
        if not rows:
            return []
        cols = []
        for desc in self.description:
            name = desc[0]
            if name == "count_star()":
                name = "count"
            cols.append(name)
        return [dict(zip(cols, r)) for r in rows]

    def close(self):
        pass


class DuckDBConnection:
    def __init__(self, con):
        self.con = con
        self._read_only = False

    @property
    def read_only(self) -> bool:
        return self._read_only

    @read_only.setter
    def read_only(self, value: bool):
        self._read_only = value

    def cursor(self, row_factory=None):
        return DuckDBCursor(self.con)

    def execute(self, sql: str, params: Any = None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        try:
            self.con.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _preload_jobs_table(con) -> None:
    """Parse all vault/jds/*.json files and metadata, and populate the jobs table in DuckDB."""
    # Create the jobs schema
    con.execute("""
        CREATE TABLE jobs (
            job_id VARCHAR PRIMARY KEY,
            slug VARCHAR,
            company VARCHAR,
            title VARCHAR,
            location VARCHAR,
            url VARCHAR,
            description VARCHAR,
            score INTEGER,
            applicants INTEGER,
            source VARCHAR,
            platform VARCHAR,
            status VARCHAR DEFAULT 'active',
            created_at VARCHAR
        )
    """)
    
    jds_dir = _get_vault_jds_dir()
    if not jds_dir.exists():
        return

    jobs_data = []
    # Search for all json files in vault/jds/
    for json_path in jds_dir.glob("*.json"):
        # Skip dotfiles
        if json_path.name.startswith("."):
            continue
        try:
            with open(json_path, encoding="utf-8") as f:
                job_json = json.load(f)
        except Exception as e:
            log.warning(f"Failed to read job json {json_path}: {e}")
            continue

        slug = job_json.get("slug") or json_path.stem
        txt_path = jds_dir / f"{slug}.txt"
        
        description = ""
        if txt_path.exists():
            try:
                txt_content = txt_path.read_text(encoding="utf-8")
                _, description = documents.split_front_matter(txt_content)
            except Exception as e:
                log.warning(f"Failed to read job description txt {txt_path}: {e}")

        # Platform deduction if not present
        url = job_json.get("url") or ""
        platform = job_json.get("platform")
        if not platform:
            platform = "other"
            if "linkedin.com" in url:
                platform = "linkedin"
            elif "glassdoor" in url:
                platform = "glassdoor"
            elif "fraunhofer" in url:
                platform = "fraunhofer"

        jobs_data.append({
            "job_id": job_json.get("job_id") or "",
            "slug": slug,
            "company": job_json.get("company") or "Unknown",
            "title": job_json.get("title") or "Unknown",
            "location": job_json.get("location") or "Remote",
            "url": url,
            "description": description,
            "score": job_json.get("score"),
            "applicants": job_json.get("applicants"),
            "source": job_json.get("source") or "manual",
            "platform": platform,
            "status": job_json.get("status") or "active",
            "created_at": job_json.get("captured_at") or job_json.get("created_at") or ""
        })

    if jobs_data:
        # Deduplicate by job_id in Python to prevent primary key constraint errors
        unique_jobs = {}
        for job in jobs_data:
            unique_jobs[job["job_id"]] = job
        jobs_data = list(unique_jobs.values())

        # We can insert multiple rows at once via parameterized query
        con.executemany("""
            INSERT INTO jobs (
                job_id, slug, company, title, location, url, description, 
                score, applicants, source, platform, status, created_at
            ) VALUES (
                $job_id, $slug, $company, $title, $location, $url, $description,
                $score, $applicants, $source, $platform, $status, $created_at
            )
        """, jobs_data)


def _preload_applications_table(con) -> None:
    """Parse frontmatter from applications/*/index.md and metadata, populating the applications table."""
    con.execute("""
        CREATE TABLE applications (
            job_id VARCHAR PRIMARY KEY,
            slug VARCHAR,
            status VARCHAR DEFAULT 'draft',
            recipient VARCHAR,
            cv_en VARCHAR,
            cv_de VARCHAR,
            cover_letter_en VARCHAR,
            cover_letter_de VARCHAR,
            drive_url VARCHAR,
            clusters VARCHAR[],
            updated_at VARCHAR
        )
    """)
    
    apps_dir = _get_applications_dir()
    if not apps_dir.exists():
        return

    apps_data = []
    for app_subdir in apps_dir.iterdir():
        if not app_subdir.is_dir() or app_subdir.name.startswith(".") or app_subdir.name == "__pycache__":
            continue

        slug = app_subdir.name
        index_path = app_subdir / "index.md"
        if not index_path.exists():
            continue

        try:
            content = index_path.read_text(encoding="utf-8")
            meta, _ = documents.split_front_matter(content)
        except Exception as e:
            log.warning(f"Failed to parse applications {slug}/index.md: {e}")
            meta = {}

        # Read helper
        def read_file_safe(filename):
            p = app_subdir / filename
            return p.read_text(encoding="utf-8") if p.exists() else ""

        cv_en = read_file_safe("cv.md")
        cv_de = read_file_safe("cv.de.md")
        cover_letter_en = read_file_safe("cover-letter.md")
        cover_letter_de = read_file_safe("cover-letter.de.md")

        # Parse recipient from cover letter frontmatter if not in index
        recipient = meta.get("recipient") or ""
        if not recipient and cover_letter_en:
            try:
                cl_meta, _ = documents.split_front_matter(cover_letter_en)
                recipient = cl_meta.get("recipient") or ""
            except Exception:
                pass

        # Compute stable job_id matching the systems hashing rules
        url = meta.get("job_url") or meta.get("url") or ""
        title = meta.get("job_title") or meta.get("title") or "Unknown"
        if url and url.strip():
            clean_url = url.strip().rstrip("/")
            job_id = hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:12]
        else:
            clean_title = "".join(ch for ch in title.lower() if ch.isalnum() or ch.isspace()).strip()
            job_id = hashlib.md5(clean_title.encode("utf-8")).hexdigest()[:12]

        clusters = meta.get("clusters") or []
        if isinstance(clusters, str):
            clusters = [c.strip() for c in clusters.split(";") if c.strip()]

        apps_data.append({
            "job_id": job_id,
            "slug": slug,
            "status": meta.get("status") or "draft",
            "recipient": recipient,
            "cv_en": cv_en,
            "cv_de": cv_de,
            "cover_letter_en": cover_letter_en,
            "cover_letter_de": cover_letter_de,
            "drive_url": meta.get("drive_url") or "",
            "clusters": clusters,
            "updated_at": meta.get("date_found") or ""
        })

    if apps_data:
        # Deduplicate by job_id in Python to prevent primary key constraint errors
        unique_apps = {}
        for app in apps_data:
            unique_apps[app["job_id"]] = app
        apps_data = list(unique_apps.values())

        con.executemany("""
            INSERT INTO applications (
                job_id, slug, status, recipient, cv_en, cv_de, 
                cover_letter_en, cover_letter_de, drive_url, clusters, updated_at
            ) VALUES (
                $job_id, $slug, $status, $recipient, $cv_en, $cv_de,
                $cover_letter_en, $cover_letter_de, $drive_url, $clusters, $updated_at
            )
        """, apps_data)


DB_FILE_PATH = str(pathlib.Path(__file__).resolve().parent.parent.parent / "vault" / "cv_tailor.db")


def get_conn() -> DuckDBConnection:
    """Retrieve a DuckDB connection to the local database file (thread-safe, self-healing)."""
    pathlib.Path(DB_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(database=DB_FILE_PATH)
    
    # Auto-initialize and preload tables if they don't exist
    try:
        con.execute("SELECT 1 FROM jobs LIMIT 1")
    except Exception:
        try:
            _preload_jobs_table(con)
            _preload_applications_table(con)
        except Exception as e:
            log.warning(f"Failed to auto-preload DuckDB tables: {e}")
            
    return DuckDBConnection(con)


def init_db():
    """Reset and reload the local file-based database with fresh data from disk."""
    if os.path.exists(DB_FILE_PATH):
        try:
            os.remove(DB_FILE_PATH)
        except Exception:
            # Fallback if file is locked or occupied by another connection
            try:
                con = duckdb.connect(database=DB_FILE_PATH)
                con.execute("DROP TABLE IF EXISTS jobs")
                con.execute("DROP TABLE IF EXISTS applications")
                con.close()
            except Exception:
                pass
                
    # Re-initialize by opening a connection which triggers preload
    get_conn()
    log.info("Filesystem-first database layer initialized successfully.")


def migrate_legacy_data(applications_dir: str = "applications") -> int:
    """No-op for DuckDB serverless mode."""
    return 0

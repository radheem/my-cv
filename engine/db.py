from __future__ import annotations

import os
import logging
import psycopg
from psycopg.rows import dict_row

log = logging.getLogger("cv-tailor")


def get_conn():
    """Retrieve a raw connection to the database."""
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cv_tailor")
    
    # If running inside Docker, replace localhost/127.0.0.1 with Compose db hostname
    if os.path.exists("/.dockerenv"):
        for local_host in ("localhost", "127.0.0.1"):
            if local_host in db_url:
                db_url = db_url.replace(local_host, "db")
        
    return psycopg.connect(db_url, row_factory=dict_row)


def init_db():
    """Initialize the jobs and applications tables."""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS jobs (
        job_id VARCHAR(100) PRIMARY KEY,
        slug VARCHAR(255) NOT NULL,
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
        job_id VARCHAR(100) PRIMARY KEY REFERENCES jobs(job_id) ON DELETE CASCADE,
        slug VARCHAR(255) NOT NULL,
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
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
                conn.commit()
        log.info("Database schema applied successfully.")
    except psycopg.OperationalError as e:
        log.error(f"Database connection failed: {e}\n-> Please ensure your PostgreSQL Docker container is running (docker compose up -d db) and DATABASE_URL is set correctly.")
        raise


def migrate_legacy_data(applications_dir: str = "applications") -> int:
    """Read existing folders in applications/ and legacy tracker.csv, and upsert them into the database."""
    import csv
    import pathlib
    import re
    from . import documents

    app_root = pathlib.Path(applications_dir)
    tracker_path = app_root / "tracker.csv"
    
    tracker_rows = {}
    if tracker_path.exists():
        with open(tracker_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tracker_rows[row["slug"]] = row

    if not app_root.exists():
        return 0

    count = 0
    with get_conn() as conn:
        for app_dir in app_root.iterdir():
            if not app_dir.is_dir() or app_dir.name == "__pycache__":
                continue
            
            slug = app_dir.name
            index_md = app_dir / "index.md"
            if not index_md.exists():
                continue

            # Read index.md frontmatter
            try:
                content = index_md.read_text(encoding="utf-8")
                meta, _ = documents.split_front_matter(content)
            except Exception as e:
                log.warning(f"Failed to parse index.md for {slug}: {e}")
                meta = {}

            # Fallback to tracker.csv data
            tracker_meta = tracker_rows.get(slug, {})
            
            company = meta.get("company") or tracker_meta.get("company") or "Unknown"
            title = meta.get("job_title") or tracker_meta.get("job_title") or "Unknown"
            url = meta.get("job_url") or tracker_meta.get("job_url") or ""
            status = meta.get("status") or tracker_meta.get("status") or "draft"
            drive_url = meta.get("drive_url") or tracker_meta.get("drive_url") or ""
            
            # Parse clusters (tags)
            clusters = meta.get("clusters")
            if not clusters and tracker_meta.get("clusters"):
                clusters = [c.strip() for c in tracker_meta["clusters"].split(";") if c.strip()]
            if not clusters:
                clusters = []

            # Platform & Source inference
            platform = "other"
            if "linkedin.com" in url:
                platform = "linkedin"
            elif "glassdoor" in url:
                platform = "glassdoor"
            elif "fraunhofer" in url:
                platform = "fraunhofer"

            # Generate stable job_id based on hashing rules
            import hashlib
            if url and url.strip():
                clean_url = url.strip().rstrip("/")
                job_id = hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:12]
            else:
                clean_title = "".join(ch for ch in title.lower() if ch.isalnum() or ch.isspace()).strip()
                job_id = hashlib.md5(clean_title.encode("utf-8")).hexdigest()[:12]

            # Read content files
            def read_file_safe(filename):
                p = app_dir / filename
                return p.read_text(encoding="utf-8") if p.exists() else ""

            cv_en = read_file_safe("cv.md")
            cv_de = read_file_safe("cv.de.md")
            cover_letter_en = read_file_safe("cover-letter.md")
            cover_letter_de = read_file_safe("cover-letter.de.md")
            description = read_file_safe("job-description.md")

            # Parse recipient from cover letter frontmatter
            recipient = ""
            if cover_letter_en:
                try:
                    cl_meta, _ = documents.split_front_matter(cover_letter_en)
                    recipient = cl_meta.get("recipient") or ""
                except Exception:
                    pass

            with conn.cursor() as cur:
                # Insert job first
                cur.execute("""
                    INSERT INTO jobs (job_id, slug, company, title, url, description, source, platform)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO UPDATE SET
                        slug = EXCLUDED.slug,
                        company = EXCLUDED.company,
                        title = EXCLUDED.title,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description
                """, (job_id, slug, company, title, url, description, "file", platform))

                # Insert application
                cur.execute("""
                    INSERT INTO applications (job_id, slug, status, recipient, cv_en, cv_de, cover_letter_en, cover_letter_de, drive_url, clusters)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO UPDATE SET
                        slug = EXCLUDED.slug,
                        status = EXCLUDED.status,
                        recipient = EXCLUDED.recipient,
                        cv_en = EXCLUDED.cv_en,
                        cv_de = EXCLUDED.cv_de,
                        cover_letter_en = EXCLUDED.cover_letter_en,
                        cover_letter_de = EXCLUDED.cover_letter_de,
                        drive_url = EXCLUDED.drive_url,
                        clusters = EXCLUDED.clusters
                """, (job_id, slug, status, recipient, cv_en, cv_de, cover_letter_en, cover_letter_de, drive_url, clusters))
            
            count += 1
        conn.commit()
    log.info(f"Successfully migrated {count} legacy applications from filesystem to database.")
    return count


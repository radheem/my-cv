from __future__ import annotations

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

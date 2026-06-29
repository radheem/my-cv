from __future__ import annotations

import os
import pytest
import pathlib
import json
from engine.shared.db import get_conn, init_db

def test_db_initialization():
    # Setup test schema
    init_db()
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Check tables exist
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main'")
            tables = [row["table_name"] for row in cur.fetchall()]
            assert "jobs" in tables
            assert "applications" in tables


def test_fetch_job_text_db_fallback():
    init_db()

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Delete any existing row to ensure isolation
            cur.execute("DELETE FROM jobs WHERE job_id='9999911111'")
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES ('9999911111', 'test-db-fallback-slug', 'Test Fallback Inc', 'Fallback Engineer', 'file', 'other', 'DB Fallback Description')
            """)
        conn.commit()

    from engine.fetch import fetch_job_text
    desc = fetch_job_text("test-db-fallback-slug")
    assert desc == "DB Fallback Description"


def test_db_export(tmp_path, monkeypatch):
    import json
    init_db()

    # Isolate paths
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("engine.cli._jobs_dir", lambda: tmp_path / "applications")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM applications WHERE job_id='88877711'")
            cur.execute("DELETE FROM jobs WHERE job_id='88877711'")
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES ('88877711', 'test-export-slug', 'Export Corp', 'Export Lead', 'file', 'other', 'JD Description Text')
            """)
            cur.execute("""
                INSERT INTO applications (job_id, slug, status, recipient, cv_en, cv_de, cover_letter_en, cover_letter_de, drive_url, clusters)
                VALUES ('88877711', 'test-export-slug', 'applied', 'Hiring Manager', 'CV EN', 'CV DE', 'CL EN', 'CL DE', 'http://drive/folder', ['web-api', 'distributed-systems'])
            """)
        conn.commit()

    from engine.cli import cmd_db_export
    import argparse

    cmd_db_export(argparse.Namespace())

    # Check files created in application-data/
    export_dir = tmp_path / "application-data"
    assert (export_dir / "jobs.csv").exists()
    assert (export_dir / "applications.csv").exists()
    assert (export_dir / "jds" / "test-export-slug.txt").exists()
    
    slug_dir = export_dir / "applications" / "test-export-slug"
    assert slug_dir.exists()
    assert (slug_dir / "cv.md").read_text(encoding="utf-8") == "CV EN"
    assert (slug_dir / "cv.de.md").read_text(encoding="utf-8") == "CV DE"
    assert (slug_dir / "cover-letter.md").read_text(encoding="utf-8") == "CL EN"
    assert (slug_dir / "cover-letter.de.md").read_text(encoding="utf-8") == "CL DE"
    
    meta = json.loads((slug_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["company"] == "Export Corp"
    assert meta["title"] == "Export Lead"
    assert meta["status"] == "applied"
    assert meta["recipient"] == "Hiring Manager"
    assert "web-api" in meta["clusters"]

from __future__ import annotations

import os
import pytest
import psycopg
from engine.db import get_conn, init_db

def test_db_initialization():
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL container is offline. Skipping database integration tests.")

    # Setup test schema
    init_db()
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Check tables exist
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [row["table_name"] for row in cur.fetchall()]
            assert "jobs" in tables
            assert "applications" in tables


def test_legacy_migration(tmp_path):
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL container is offline. Skipping database integration tests.")

    init_db()

    # Create dummy application structure on filesystem
    app_dir = tmp_path / "acme-engineering-123"
    app_dir.mkdir()
    
    (tmp_path / "tracker.csv").write_text(
        "slug,company,job_title,status,date_found,job_url,drive_url,drive_updated,clusters\n"
        "acme-engineering-123,ACME Inc,Engineer,draft,2026-06-25,https://linkedin.com/jobs/view/123,https://drive.google.com/drive/folders/abc,2026-06-25T12:00:00+00:00,distributed-systems;observability\n",
        encoding="utf-8"
    )

    (app_dir / "index.md").write_text(
        "---\n"
        "job_title: \"Engineer\"\n"
        "company: \"ACME Inc\"\n"
        "job_url: \"https://linkedin.com/jobs/view/123\"\n"
        "status: \"draft\"\n"
        "clusters: [\"distributed-systems\", \"observability\"]\n"
        "date_found: \"2026-06-25\"\n"
        "drive_url: \"https://drive.google.com/drive/folders/abc\"\n"
        "---\n\n"
        "# ACME Inc — Engineer\n",
        encoding="utf-8"
    )

    (app_dir / "cv.md").write_text("Gold CV EN", encoding="utf-8")
    (app_dir / "cv.de.md").write_text("Gold CV DE", encoding="utf-8")
    (app_dir / "cover-letter.md").write_text("---\nrecipient: \"Hiring Manager\"\n---\nCL Body EN", encoding="utf-8")
    (app_dir / "cover-letter.de.md").write_text("CL Body DE", encoding="utf-8")
    (app_dir / "job-description.md").write_text("Raw Description Text", encoding="utf-8")

    from engine.db import migrate_legacy_data
    count = migrate_legacy_data(str(tmp_path))
    assert count == 1

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM jobs WHERE slug='acme-engineering-123'")
            job = cur.fetchone()
            assert job is not None
            assert job["company"] == "ACME Inc"
            assert job["title"] == "Engineer"
            assert job["url"] == "https://linkedin.com/jobs/view/123"
            assert job["description"] == "Raw Description Text"
            assert job["platform"] == "linkedin"
            assert job["job_id"] == "123"

            cur.execute("SELECT * FROM applications WHERE slug='acme-engineering-123'")
            app = cur.fetchone()
            assert app is not None
            assert app["status"] == "draft"
            assert app["recipient"] == "Hiring Manager"
            assert app["cv_en"] == "Gold CV EN"
            assert app["cv_de"] == "Gold CV DE"
            assert app["cover_letter_en"] == "---\nrecipient: \"Hiring Manager\"\n---\nCL Body EN"
            assert app["cover_letter_de"] == "CL Body DE"
            assert "distributed-systems" in app["clusters"]
            assert "observability" in app["clusters"]


def test_fetch_job_text_db_fallback():
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL container is offline. Skipping database integration tests.")

    init_db()

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Delete any existing row to ensure isolation
            cur.execute("DELETE FROM jobs WHERE slug='test-db-fallback-slug'")
            cur.execute("""
                INSERT INTO jobs (slug, job_id, company, title, source, platform, description)
                VALUES ('test-db-fallback-slug', '9999911111', 'Test Fallback Inc', 'Fallback Engineer', 'file', 'other', 'DB Fallback Description')
            """)
        conn.commit()

    from engine.fetch import fetch_job_text
    desc = fetch_job_text("test-db-fallback-slug")
    assert desc == "DB Fallback Description"


def test_db_push_pull_sync(tmp_path, monkeypatch):
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL container is offline. Skipping database integration tests.")

    init_db()

    # Override jobs directory for local files isolation
    monkeypatch.setattr("engine.cli._jobs_dir", lambda: tmp_path)

    # 1. Test DB Push (Disk -> DB)
    app_slug = "test-sync-app-888"
    app_dir = tmp_path / app_slug
    app_dir.mkdir()

    (app_dir / "index.md").write_text(
        "---\n"
        "job_title: \"Cloud Engineer\"\n"
        "company: \"Sync Corp\"\n"
        "status: \"interview\"\n"
        "clusters: [\"ml-ai\"]\n"
        "---\n\n"
        "# Sync Corp\n",
        encoding="utf-8"
    )
    (app_dir / "cv.md").write_text("Local CV EN", encoding="utf-8")
    (app_dir / "cv.de.md").write_text("Local CV DE", encoding="utf-8")
    (app_dir / "cover-letter.md").write_text("---\nrecipient: \"Jane Doe\"\n---\nLocal CL EN", encoding="utf-8")
    (app_dir / "cover-letter.de.md").write_text("Local CL DE", encoding="utf-8")

    from engine.cli import cmd_db_push, cmd_db_pull
    import argparse

    # Push to DB
    args = argparse.Namespace(slug=app_slug)
    cmd_db_push(args)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM applications WHERE slug=%s", (app_slug,))
            row = cur.fetchone()
            assert row is not None
            assert row["status"] == "interview"
            assert row["recipient"] == "Jane Doe"
            assert row["cv_en"] == "Local CV EN"
            assert "ml-ai" in row["clusters"]

            # Update DB content to simulate external changes
            cur.execute("""
                UPDATE applications SET 
                    status = 'offer',
                    cv_en = 'Updated DB CV EN',
                    recipient = 'John Smith'
                WHERE slug = %s
            """, (app_slug,))
        conn.commit()

    # 2. Test DB Pull (DB -> Disk)
    cmd_db_pull(args)

    # Check local files were overwritten
    cv_txt = (app_dir / "cv.md").read_text(encoding="utf-8")
    assert cv_txt == "Updated DB CV EN"

    idx_txt = (app_dir / "index.md").read_text(encoding="utf-8")
    assert "status: \"offer\"" in idx_txt


def test_db_export(tmp_path, monkeypatch):
    import json
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL container is offline. Skipping database integration tests.")

    init_db()

    # Isolate paths
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("engine.cli._jobs_dir", lambda: tmp_path / "applications")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM applications WHERE slug='test-export-slug'")
            cur.execute("DELETE FROM jobs WHERE slug='test-export-slug'")
            cur.execute("""
                INSERT INTO jobs (slug, job_id, company, title, source, platform, description)
                VALUES ('test-export-slug', '88877711', 'Export Corp', 'Export Lead', 'file', 'other', 'JD Description Text')
            """)
            cur.execute("""
                INSERT INTO applications (slug, status, recipient, cv_en, cv_de, cover_letter_en, cover_letter_de, drive_url, clusters)
                VALUES ('test-export-slug', 'applied', 'Hiring Manager', 'CV EN', 'CV DE', 'CL EN', 'CL DE', 'http://drive/folder', ARRAY['web-api', 'distributed-systems'])
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





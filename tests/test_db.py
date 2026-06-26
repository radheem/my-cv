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



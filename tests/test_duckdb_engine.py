import os
import pathlib
import pytest
import json
from engine.shared.db import get_conn, init_db

def test_duckdb_get_conn_structure(tmp_path, monkeypatch):
    # Set up some dummy jobs and applications in our temp path
    jds_dir = tmp_path / "vault" / "jds"
    jds_dir.mkdir(parents=True, exist_ok=True)
    
    apps_dir = tmp_path / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Create a dummy scraped job in vault/jds/
    dummy_job = {
        "job_id": "dummyjob123",
        "title": "Data Platform Engineer",
        "company": "Lovable",
        "location": "Remote",
        "url": "https://linkedin.com/jobs/view/Lovable123",
        "applicants": 42,
        "source": "gmail",
        "platform": "linkedin",
        "score": 85,
        "status": "active"
    }
    (jds_dir / "lovable-data-platform-engineer.json").write_text(json.dumps(dummy_job))
    (jds_dir / "lovable-data-platform-engineer.txt").write_text("Dummy description text")

    # 2. Create a dummy application in applications/
    app_slug_dir = apps_dir / "lovable-data-platform-engineer"
    app_slug_dir.mkdir()
    
    (app_slug_dir / "index.md").write_text(
        "---\n"
        "company: Lovable\n"
        "job_title: Data Platform Engineer\n"
        "job_url: https://linkedin.com/jobs/view/Lovable123\n"
        "status: draft\n"
        "recipient: recruiter\n"
        "drive_url: https://drive.google.com/drive/folders/xyz\n"
        "clusters: [python, duckdb]\n"
        "date_found: \"2026-06-29\"\n"
        "---\n\n"
        "Dummy MD Content\n"
    )
    (app_slug_dir / "cv.md").write_text("Tailored CV Markdown")
    (app_slug_dir / "cover-letter.md").write_text("Tailored Cover Letter Markdown")

    # Mock the directory lookups to point to our tmp_path
    monkeypatch.setattr("engine.shared.db._get_vault_jds_dir", lambda: jds_dir)
    monkeypatch.setattr("engine.shared.db._get_applications_dir", lambda: apps_dir)
    monkeypatch.setattr("engine.shared.db.DB_FILE_PATH", str(tmp_path / "test_cv_tailor.db"))

    # Call get_conn
    conn = get_conn()
    
    # Check that we can query the jobs table
    res = conn.execute("SELECT * FROM jobs WHERE job_id = 'dummyjob123'").fetchone()
    assert res is not None
    # Result rows might be named tuples, dicts, or tuples depending on DuckDB. 
    # Let's query by name if possible, or index
    assert "Lovable" in str(res)
    
    # Check that we can query the applications table
    res_app = conn.execute("SELECT * FROM applications WHERE slug = 'lovable-data-platform-engineer'").fetchone()
    assert res_app is not None
    assert "draft" in str(res_app)
    
    # Check that init_db does not raise an error
    init_db()

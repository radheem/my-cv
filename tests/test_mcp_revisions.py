import json
import pytest
import shutil
import pathlib
from engine.shared.db import get_conn, init_db

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM applications WHERE slug = 'mock-test-slug'")
            cur.execute("DELETE FROM jobs WHERE slug = 'mock-test-slug'")
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, url, description, score, status, created_at)
                VALUES ('mocktestid12', 'mock-test-slug', 'TestCorp', 'Python Engineer', 'http://test.com', 'We need Python developers.', 85, 'new', '2026-07-19T10:00:00Z')
            """)
            cur.execute("""
                INSERT INTO applications (job_id, slug, status, cv_en, cover_letter_en, cv_de, cover_letter_de, drive_url, updated_at)
                VALUES ('mocktestid12', 'mock-test-slug', 'draft', 'Original CV', 'Original Cover Letter', 'Original CV DE', 'Original Cover Letter DE', 'http://drive.com', '2026-07-19T10:00:00Z')
            """)
        conn.commit()

    # Create dummy application files
    app_dir = pathlib.Path("applications/mock-test-slug")
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "cv.md").write_text("Original CV")
    (app_dir / "cover-letter.md").write_text("Original Cover Letter")
    (app_dir / "cv.de.md").write_text("Original CV DE")
    (app_dir / "cover-letter.de.md").write_text("Original Cover Letter DE")

    yield

    # Cleanup application files
    if app_dir.exists():
        shutil.rmtree(app_dir)


def test_mcp_revise_cover_letter(monkeypatch):
    from engine.mcp import server

    monkeypatch.setattr("engine.domains.tailoring.llm.stream_text", lambda sys, user, **kwargs: "Revised Cover Letter!")

    res_str = server.revise_cover_letter("mock-test-slug", "Make it warmer")
    res = json.loads(res_str)

    assert "cover_letter_en" in res
    assert res["cover_letter_en"] == "Revised Cover Letter!\n"
    assert res["status"] == "success"

    cover_letter_path = pathlib.Path("applications/mock-test-slug/cover-letter.md")
    assert cover_letter_path.read_text() == "Revised Cover Letter!\n"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT cover_letter_en FROM applications WHERE slug = 'mock-test-slug'")
            row = cur.fetchone()
            assert row["cover_letter_en"] == "Revised Cover Letter!\n"


def test_mcp_revise_cv(monkeypatch):
    from engine.mcp import server

    monkeypatch.setattr("engine.domains.tailoring.llm.stream_text", lambda sys, user, **kwargs: "Revised CV!")

    res_str = server.revise_cv("mock-test-slug", "Focus on React")
    res = json.loads(res_str)

    assert "cv_en" in res
    assert res["cv_en"] == "Revised CV!\n"
    assert res["status"] == "success"

    cv_path = pathlib.Path("applications/mock-test-slug/cv.md")
    assert cv_path.read_text() == "Revised CV!\n"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT cv_en FROM applications WHERE slug = 'mock-test-slug'")
            row = cur.fetchone()
            assert row["cv_en"] == "Revised CV!\n"


def test_mcp_translate_application(monkeypatch):
    from engine.mcp import server

    # Mock translate_markdown to translate input
    monkeypatch.setattr("engine.domains.tailoring.render.translate_markdown", lambda md, kind: f"Translated {md}!")

    res_str = server.translate_application("mock-test-slug", kind="cover-letter")
    res = json.loads(res_str)

    assert res["status"] == "success"
    assert "cover_letter_de" in res
    assert "Original Cover Letter" in res["cover_letter_de"]

    # Verify database
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT cover_letter_de FROM applications WHERE slug = 'mock-test-slug'")
            row = cur.fetchone()
            assert "Original Cover Letter" in row["cover_letter_de"]


def test_mcp_regenerate_application(monkeypatch):
    from engine.mcp import server

    # Mock create_application_from_job
    enqueued = []
    monkeypatch.setattr("engine.mcp.server.create_application_from_job", lambda slug: enqueued.append(slug))

    res_str = server.regenerate_application("mock-test-slug")
    res = json.loads(res_str)

    assert res["status"] == "success"
    assert "mock-test-slug" in enqueued

    # Files should have been wiped
    assert not pathlib.Path("applications/mock-test-slug").exists()

    # DB row should have been purged
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM applications WHERE slug = 'mock-test-slug'")
            row = cur.fetchone()
            assert row["cnt"] == 0


def test_mcp_cancel_queued_task():
    from engine.mcp import server

    # Clear queue
    while not server._tailor_queue.empty():
        server._tailor_queue.get_nowait()

    # Enqueue a dummy task
    server._tailor_queue.put({"slug": "mock-test-slug", "stage": "generate", "custom_instructions": None, "variant": None})

    res_str = server.cancel_queued_task("mock-test-slug")
    res = json.loads(res_str)

    assert res["status"] == "success"
    assert server._tailor_queue.empty()

    # DB application row should be removed for fresh enqueued tasks
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM applications WHERE slug = 'mock-test-slug'")
            row = cur.fetchone()
            assert row["cnt"] == 0

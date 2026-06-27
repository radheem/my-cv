import pytest
from engine.workflows import create_application_workflow, update_application_status_workflow, score_jobs_workflow


def test_workflow_error_isolation():
    # Make sure we isolate errors and return clear exception strings instead of crashing
    res = create_application_workflow("invalid_nonexistent_file_path_xyz.txt")
    assert "ERROR" in res


def test_workflow_status_nonexistent():
    res = update_application_status_workflow("nonexistent-slug-123", "applied")
    assert "ERROR" in res


def test_workflow_status_updates(monkeypatch, tmp_path):
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", str(tmp_path))
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://mock-apps-script.url")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock-token")

    app = tmp_path / "acme-platform-engineer-1"
    app.mkdir()
    (app / "index.md").write_text('---\nstatus: "draft"\ncompany: "Acme"\n---\n\nbody\n')

    import engine.cli as cli_mod
    monkeypatch.setattr(cli_mod, "_get_db_tracker_csv", lambda: "slug,company,status\nacme-platform-engineer-1,Acme,draft\n")
    monkeypatch.setattr(cli_mod, "_push_to_sheets", lambda url, token, path: 1)

    res = update_application_status_workflow("acme-platform-engineer-1", "applied")
    assert "SUCCESS" in res
    assert 'status: "applied"' in (app / "index.md").read_text()


def test_workflow_sync_status_to_sheets(monkeypatch, tmp_path):
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", str(tmp_path))
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://mock-apps-script.url")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock-token")

    import engine.cli as cli_mod
    monkeypatch.setattr(cli_mod, "_get_db_tracker_csv", lambda: "slug,company,status\nacme-platform-engineer-1,Acme,applied\n")
    monkeypatch.setattr(cli_mod, "_push_to_sheets", lambda url, token, path: 1)

    from engine.workflows import sync_status_to_sheets_workflow
    res = sync_status_to_sheets_workflow()
    assert "SUCCESS" in res

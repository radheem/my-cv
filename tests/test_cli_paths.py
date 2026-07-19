"""Sprint 2 wiring: configurable data/jobs dirs + the status subcommand. No LLM, no network."""

import argparse
import pathlib

import pytest

from engine import cli


def test_data_dir_default_and_override(monkeypatch):
    monkeypatch.delenv("CV_TAILOR_DATA_DIR", raising=False)
    assert cli._data_dir() == cli.DATA
    monkeypatch.setenv("CV_TAILOR_DATA_DIR", "/tmp/private-cv")
    assert cli._data_dir() == pathlib.Path("/tmp/private-cv")


def test_jobs_dir_default_and_override(monkeypatch):
    monkeypatch.delenv("CV_TAILOR_JOBS_DIR", raising=False)
    assert cli._jobs_dir() == cli.JOBS
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", "vault/applications")
    assert cli._jobs_dir() == pathlib.Path("vault/applications")


def test_status_flips_front_matter(monkeypatch, tmp_path):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", str(tmp_path))
    monkeypatch.setattr(cli, "_push_to_sheets", lambda url, token, path: 3)
    app = tmp_path / "acme-platform-engineer-1"
    app.mkdir()
    (app / "index.md").write_text('---\nstatus: "draft"\ncompany: "Acme"\n---\n\nbody\n')

    rc = cli.cmd_status(argparse.Namespace(slug="acme-platform-engineer-1", state="applied"))
    assert rc == 0
    assert 'status: "applied"' in (app / "index.md").read_text()


def test_status_missing_hub(monkeypatch, tmp_path):
    monkeypatch.setenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/test/exec")
    monkeypatch.setenv("APPS_SCRIPT_TOKEN", "mock_token")
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", str(tmp_path))
    with pytest.raises(SystemExit):
        cli.cmd_status(argparse.Namespace(slug="nope", state="applied"))


def test_build_app_collects_markdown_and_pdfs(monkeypatch, tmp_path):
    mock_app_dir = tmp_path / "mock-slug"
    mock_app_dir.mkdir()

    # Create mock target files
    (mock_app_dir / "cv.pdf").write_bytes(b"pdf cv")
    (mock_app_dir / "cover-letter.pdf").write_bytes(b"pdf letter")
    (mock_app_dir / "cv.md").write_text("markdown cv")
    (mock_app_dir / "cover-letter.md").write_text("markdown letter")
    (mock_app_dir / "cv.de.md").write_text("markdown cv de")
    (mock_app_dir / "index.md").write_text("index")
    (mock_app_dir / "other.json").write_text("{}")

    monkeypatch.setattr("engine.cli._render_tex", lambda slug: mock_app_dir)
    monkeypatch.setattr("engine.cli._compile", lambda app: None)

    results = cli._build_app("mock-slug")
    result_names = {p.name for p in results}

    assert "cv.pdf" in result_names
    assert "cover-letter.pdf" in result_names
    assert "cv.md" in result_names
    assert "cover-letter.md" in result_names
    assert "cv.de.md" in result_names

    assert "index.md" not in result_names
    assert "other.json" not in result_names
    assert len(results) == 5

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
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", str(tmp_path))
    app = tmp_path / "acme-platform-engineer-1"
    app.mkdir()
    (app / "index.md").write_text('---\nstatus: "draft"\ncompany: "Acme"\n---\n\nbody\n')

    rc = cli.cmd_status(argparse.Namespace(slug="acme-platform-engineer-1", state="applied"))
    assert rc == 0
    assert 'status: "applied"' in (app / "index.md").read_text()


def test_status_missing_hub(monkeypatch, tmp_path):
    monkeypatch.setenv("CV_TAILOR_JOBS_DIR", str(tmp_path))
    with pytest.raises(SystemExit):
        cli.cmd_status(argparse.Namespace(slug="nope", state="applied"))

"""Tests for engine.config.resolve_search — the runtime LinkedIn search config.

No network, no model. Covers defaults-into-entry merge, precedence, required-key
validation, and the CV_TAILOR_SEARCH_CONFIG path override.
"""

import pathlib

import pytest

from engine.shared import config


def _write(tmp_path: pathlib.Path, body: str) -> pathlib.Path:
    p = tmp_path / "search.yml"
    p.write_text(body, encoding="utf-8")
    return p


def test_defaults_fill_omitted_keys(tmp_path):
    p = _write(
        tmp_path,
        """
        defaults:
          days_back: 7
          max_applicants: 100
          limit: 5
        searches:
          - name: a
            keywords: "backend engineer"
            location: "Jena"
        """,
    )
    out = config.resolve_search(path=p)
    s = out["searches"][0]
    assert s["keywords"] == "backend engineer"
    assert s["location"] == "Jena"
    assert s["days_back"] == 7 and s["max_applicants"] == 100 and s["limit"] == 5
    assert s["easy_apply"] is False  # from _SEARCH_DEFAULTS
    assert s["geo_id"] is None


def test_entry_overrides_defaults(tmp_path):
    p = _write(
        tmp_path,
        """
        defaults:
          days_back: 7
          easy_apply: false
        searches:
          - name: go
            keywords: '"Go" OR "Python"'
            geo_id: "101768819"
            distance: 0
            easy_apply: true
            days_back: 3
        """,
    )
    s = config.resolve_search(path=p)["searches"][0]
    assert s["geo_id"] == "101768819"
    assert s["distance"] == 0
    assert s["easy_apply"] is True
    assert s["days_back"] == 3  # entry wins over defaults


def test_missing_keywords_raises(tmp_path):
    p = _write(tmp_path, "searches:\n  - name: bad\n    location: Berlin\n")
    with pytest.raises(ValueError):
        config.resolve_search(path=p)


def test_name_defaults_to_keywords(tmp_path):
    p = _write(tmp_path, 'searches:\n  - keywords: "data engineer"\n')
    s = config.resolve_search(path=p)["searches"][0]
    assert s["name"] == "data engineer"


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        config.resolve_search(path=tmp_path / "nope.yml")


def test_env_path_override(tmp_path, monkeypatch):
    p = _write(tmp_path, 'searches:\n  - keywords: "x"\n')
    monkeypatch.setenv("CV_TAILOR_SEARCH_CONFIG", str(p))
    assert config.search_config_path() == p
    assert config.resolve_search()["searches"][0]["keywords"] == "x"


def test_scoring_passed_through(tmp_path):
    p = _write(
        tmp_path,
        'searches:\n  - keywords: "x"\nscoring:\n  must_have: ["go", "python"]\n',
    )
    out = config.resolve_search(path=p)
    assert out["scoring"]["must_have"] == ["go", "python"]


def test_gmail_alerts_override_defaults(tmp_path):
    p = _write(
        tmp_path,
        """
        gmail_alerts:
          linkedin: "custom-linkedin@test.com"
        searches:
          - keywords: "x"
        """,
    )
    out = config.resolve_search(path=p)
    alerts = out["gmail_alerts"]
    assert alerts["linkedin"] == "custom-linkedin@test.com"
    assert alerts["glassdoor"] == "noreply@glassdoor.com"  # fallback from default
    assert alerts["indeed"] == "donotreply@jobalert.indeed.com"  # fallback from default


def test_repo_search_config_is_valid():
    """The committed config/search.yml must load and every search must have keywords."""
    out = config.resolve_search()
    assert out["searches"], "config/search.yml defines no searches"
    for s in out["searches"]:
        assert s["keywords"] and s["name"]
    assert out["gmail_alerts"]["linkedin"] == "jobalerts-noreply@linkedin.com"

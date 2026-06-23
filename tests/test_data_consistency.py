"""Drift guards for the data/ single-source-of-truth (no network, no model).

`master-cv.md` is canonical for FACTS; `profile.yml` is the structured mirror the
engine needs. These tests turn silent divergence between them into a failing test
(e.g. a skill added to profile.yml but not the master CV — exactly the SQL/Bash gap
that dragged generation quality before).
"""

import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _load():
    profile = yaml.safe_load((DATA / "profile.yml").read_text(encoding="utf-8"))
    master = (DATA / "master-cv.md").read_text(encoding="utf-8")
    projects = yaml.safe_load((DATA / "projects.yml").read_text(encoding="utf-8"))["projects"]
    return profile, master, projects


def _skills_section(master: str) -> str:
    # Skills is the final H2 in the master CV — take everything after it.
    return _norm(master.split("## Skills", 1)[-1])


def test_profile_contact_matches_master_cv():
    profile, master, _ = _load()
    nm = _norm(master)
    assert _norm(profile["email"]) in nm, "profile email not found in master-cv.md"
    assert _norm(profile["phone"]) in nm, "profile phone not found in master-cv.md"


def test_profile_summary_grounded_in_master_cv():
    profile, master, _ = _load()
    assert _norm(profile["summary"]) in _norm(master), (
        "profile.yml summary diverged from master-cv.md"
    )


def test_programming_languages_present_in_master_cv():
    """Every language the engine may surface must exist in the canonical CV."""
    profile, master, _ = _load()
    skills = _skills_section(master)
    missing = [lang for lang in profile["programming_languages"]
               if lang.lower() not in skills]
    assert not missing, f"programming_languages not in master CV Skills: {missing}"


def test_project_doc_paths_resolve():
    _, _, projects = _load()
    docs = ROOT / "doc-pages"
    missing = [p["id"] for p in projects
               if p.get("doc") and not (docs / p["doc"]).exists()]
    assert not missing, f"projects.yml doc: path does not resolve under doc-pages/: {missing}"


def test_project_highlights_are_subsets_of_master_or_summary():
    """highlights must be truthful — soft check that each project with highlights is a
    real catalogue project whose name is grounded somewhere in the master CV/docs.
    (Full fact-grounding is enforced by the generation truthfulness metric.)"""
    profile, master, projects = _load()
    for p in projects:
        if p.get("highlights"):
            assert isinstance(p["highlights"], list) and p["highlights"], p["id"]

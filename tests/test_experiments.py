"""Validate the cv-tailor benchmark scaffolding and its pure scoring core.

No network, no model, no generated outputs required — these tests exercise the
benchmark harness against the committed gold cases, so they run in CI alongside
the ranking tests. (Generation + the LLM judge are driven by run.py / evaluate.py.)
"""

import pathlib
import sys

import pytest
import yaml

EXP = pathlib.Path(__file__).resolve().parent / "experiments"
sys.path.insert(0, str(EXP))

import harness  # noqa: E402


# --------------------------------------------------------------------------- #
# Scaffolding                                                                  #
# --------------------------------------------------------------------------- #

def test_split_is_four_train_two_test():
    split = harness.load_split()
    assert len(split["train"]) == 4
    assert len(split["test"]) == 2
    slugs = split["train"] + split["test"]
    assert len(set(slugs)) == 6, "slugs must be unique across the split"


def test_every_case_is_complete_and_consistent():
    split = harness.load_split()
    for which in ("train", "test"):
        for slug in split[which]:
            d = harness.CASES / slug
            assert (d / "job-description.txt").is_file(), f"{slug}: missing JD"
            assert (d / "gold" / "cv.md").is_file(), f"{slug}: missing gold CV"
            assert (d / "gold" / "cover-letter.md").is_file(), f"{slug}: missing gold letter"
            meta = yaml.safe_load((d / "meta.yml").read_text(encoding="utf-8"))
            assert meta["split"] == which, f"{slug}: meta split != split.yml"
            assert meta["company"], f"{slug}: empty company"


@pytest.fixture(scope="module")
def cases():
    return [harness.load_case(s) for s in harness.all_slugs()]


# --------------------------------------------------------------------------- #
# Gold sanity (also exercises every pure metric)                               #
# --------------------------------------------------------------------------- #

def test_gold_cvs_have_all_sections(cases):
    for c in cases:
        assert harness.cv_structure_score(c.gold_cv) == 1.0, f"{c.slug}: gold CV missing a section"


def test_gold_cv_is_self_consistent(cases):
    """Gold scored against itself: full skill coverage and project match."""
    catalog = harness.load_projects_catalog()
    for c in cases:
        assert harness.skills_coverage(c.gold_cv, c.gold_cv) == 1.0
        assert harness.projects_match(c.gold_cv, c.gold_cv, catalog) == 1.0


def test_gold_cv_is_truthful_against_master(cases):
    """The truthfulness metric must clear the real, hand-written gold CVs."""
    master = harness.load_master_cv()
    for c in cases:
        t = harness.truthfulness(c.gold_cv, master)
        assert t["score"] == 1.0, f"{c.slug}: unexpected org flags {t['offenders']}"


def test_gold_cover_letters_are_body_only(cases):
    """Gold letters carry no salutation/sign-off and are 3-5 paragraphs.

    (company_mention is a soft signal, not asserted: a strong letter may name the
    company by identity — e.g. redcare's 'Europe's No.1 e-pharmacy' — not literally.)
    """
    for c in cases:
        m = harness.cover_metrics(c.gold_cover, c.company)
        assert m["no_salutation"] == 1.0, f"{c.slug}: salutation leaked into body"
        assert 3 <= m["paragraphs"] <= 5, f"{c.slug}: {m['paragraphs']} paragraphs"
        assert m["company_mention"] in (0.0, 1.0)


# --------------------------------------------------------------------------- #
# Metric behavior                                                              #
# --------------------------------------------------------------------------- #

def test_truthfulness_catches_fabricated_org():
    master = harness.load_master_cv()
    fake = "## Experience\n\n### Globex Corporation — Staff Engineer\n*Remote · 2019*\n\n- Did things.\n"
    t = harness.truthfulness(fake, master)
    assert t["score"] == 0.0
    assert "Globex Corporation" in t["offenders"]


def test_jd_keyword_coverage_partial():
    cv = "## Skills\n\n- Kubernetes, Go, PostgreSQL\n"
    cov = harness.jd_keyword_coverage(cv, ["Kubernetes", "Go", "Rust", "Elixir"])
    assert cov == pytest.approx(0.5)


def test_score_case_runs_and_is_bounded(cases):
    master = harness.load_master_cv()
    catalog = harness.load_projects_catalog()
    c = cases[0]
    # Gold-as-candidate is an upper-bound smoke test of the aggregate.
    row = harness.score_case(c.gold_cv, c.gold_cover, c, ["Go", "Kubernetes"], master, catalog)
    assert 0.0 <= row["heuristic"] <= 1.0
    assert set(row["parts"]) == set(harness._W)

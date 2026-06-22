"""Unit tests for engine.linkedin.jobs pure helpers — slug, job-id, JD cleaning,
front-matter, dedup, and the write_jd file contract. No browser, no network."""

import json

from engine.linkedin.jobs import (
    Job,
    already_seen,
    build_search_url,
    clean_jd_text,
    extract_job_id,
    jd_frontmatter,
    load_seen,
    parse_applicant_count,
    save_seen,
    slugify,
    write_jd,
)


def test_slugify():
    assert slugify("Acme Corp", "Senior Platform Engineer!", "12345") == (
        "acme-corp-senior-platform-engineer-12345"
    )
    assert slugify("", "", "") == "job"
    assert len(slugify("x" * 200, "y" * 200, "1")) <= 80


def test_extract_job_id():
    assert extract_job_id("https://www.linkedin.com/jobs/view/3899887766/") == "3899887766"
    assert extract_job_id("/jobs/search/?currentJobId=42&keywords=x") == "42"
    assert extract_job_id("https://example.com/none") is None


def test_clean_jd_text_collapses_blanks():
    raw = "  Title  \n\n\n  body line  \n\n\n\nend\n"
    assert clean_jd_text(raw) == "Title\n\nbody line\n\nend"


def test_parse_applicant_count():
    assert parse_applicant_count("Be among the first 25 applicants") == 24
    assert parse_applicant_count("Over 200 applicants") == 201
    assert parse_applicant_count("1,234 applicants") == 1234
    assert parse_applicant_count("42 applicants") == 42
    assert parse_applicant_count("No count here") is None
    assert parse_applicant_count("") is None


def test_jd_frontmatter_has_fields_and_escapes_quotes():
    job = Job("1", 'Eng "X"', "Acme", "Remote", "https://x/jobs/view/1")
    fm = jd_frontmatter(job, "2026-06-21T10:00:00+00:00")
    assert fm.startswith("---\n") and fm.rstrip().endswith("---")
    for key in ("source: linkedin", "company:", "title:", "job_id:", "captured_at:"):
        assert key in fm
    assert '\\"X\\"' in fm  # embedded quotes escaped
    assert "applicants:" not in fm  # not set, should be omitted


def test_jd_frontmatter_includes_applicants_when_set():
    job = Job("2", "Data Engineer", "Corp", "Berlin", "https://x/jobs/view/2", applicants=47)
    fm = jd_frontmatter(job, "2026-06-22T08:00:00+00:00")
    assert "applicants: 47" in fm


def test_build_search_url_minimal():
    url = build_search_url("platform engineer", days_back=7)
    assert url.startswith("https://www.linkedin.com/jobs/search/?keywords=")
    assert "platform+engineer" in url
    assert "f_TPR=r604800" in url  # 7 * 86400
    assert "geoId" not in url and "location" not in url and "f_EA" not in url


def test_build_search_url_boolean_keywords_passthrough():
    url = build_search_url('"Go" OR "Golang" OR "Python"')
    # quotes and the OR operator survive URL-encoding (LinkedIn parses the boolean)
    assert "%22Go%22" in url and "OR" in url and "%22Python%22" in url


def test_build_search_url_geo_id_preferred_over_location():
    url = build_search_url(
        "x", location="Berlin", geo_id="101768819", distance=0, easy_apply=True
    )
    assert "geoId=101768819" in url
    assert "location=" not in url  # geo_id wins
    assert "distance=0" in url
    assert "f_EA=true" in url


def test_build_search_url_location_when_no_geo_id():
    url = build_search_url("x", location="Berlin")
    assert "location=Berlin" in url


def test_build_search_url_reproduces_example():
    # The multi-keyword filter URL the user built, modulo tracking params.
    url = build_search_url(
        '"Go" OR "Golang" OR "Python"',
        geo_id="101768819",
        distance=0.0,
        days_back=7,
        easy_apply=True,
    )
    for frag in ("geoId=101768819", "distance=0.0", "f_TPR=r604800", "f_EA=true"):
        assert frag in url


def test_dedup_roundtrip(tmp_path):
    p = tmp_path / ".seen.json"
    assert load_seen(p) == {}
    seen = {"1": "acme-eng-1"}
    save_seen(p, seen)
    assert already_seen("1", load_seen(p))
    assert not already_seen("2", load_seen(p))


def test_write_jd_emits_txt_and_sidecar(tmp_path):
    job = Job("999", "Platform Engineer", "Acme Corp", "Remote", "https://x/jobs/view/999")
    path = write_jd(job, "Some\n\n\nJD text", tmp_path, "2026-06-21T10:00:00+00:00")
    assert path.name == "acme-corp-platform-engineer-999.txt"
    body = path.read_text()
    assert "source: linkedin" in body and "JD text" in body

    sidecar = tmp_path / "acme-corp-platform-engineer-999.json"
    meta = json.loads(sidecar.read_text())
    assert meta["job_id"] == "999" and meta["slug"] == "acme-corp-platform-engineer-999"

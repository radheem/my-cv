"""Tests for the pure document renderer (engine/documents.py).

No browser, no API key — just front-matter parsing, salutation logic, and
standalone-HTML composition.
"""

import datetime

from engine import documents

PROFILE = {
    "name": "John Doe",
    "tagline": "Distributed Systems Engineer",
    "location": "Ilmenau, Germany",
    "email": "john.doe@example.com",
    "links": {"portfolio": "https://johndoe.github.io/cv-tailor", "github": "https://github.com/johndoe"},
}


def test_split_front_matter():
    meta, body = documents.split_front_matter(
        "---\nrecipient: Jane Smith\ncompany: Acme\n---\n\nHello world.\n"
    )
    assert meta == {"recipient": "Jane Smith", "company": "Acme"}
    assert body.strip() == "Hello world."


def test_split_front_matter_absent():
    meta, body = documents.split_front_matter("# Title\n\nNo front matter.\n")
    assert meta == {}
    assert body.startswith("# Title")


def test_letter_default_salutation():
    html = documents.render_letter_html("Body paragraph.", {}, PROFILE)
    assert "Dear Hiring Team," in html
    assert "Dear Jane" not in html


def test_letter_named_recipient():
    html = documents.render_letter_html(
        "Body paragraph.", {"recipient": "Jane Smith"}, PROFILE
    )
    assert "Dear Jane Smith," in html


def test_letter_has_no_title_but_has_letterhead_and_signoff():
    html = documents.render_letter_html(
        "Body paragraph.", {}, PROFILE, today=datetime.date(2026, 6, 18)
    )
    assert 'class="letter"' in html
    assert "John Doe" in html          # letterhead name
    assert "Sincerely," in html        # sign-off
    assert "<h1" not in html           # a letter has no title
    assert "2026" in html              # date rendered


def test_cv_header_composed_from_profile_and_tagline():
    html = documents.render_cv_html(
        "## Experience\n\n### Acme — Engineer\n*Remote · 2020*\n\n- Did things.\n",
        "Platform Engineer",
        PROFILE,
    )
    assert 'class="cv"' in html
    assert "John Doe" in html                 # name from profile
    assert "Platform Engineer" in html        # tailored tagline
    assert "john.doe@example.com" in html      # contact from profile
    assert "<h2" in html                       # section heading present


def test_doc_html_inlines_css_no_external_assets():
    html = documents.render_cv_html("## Skills\n\n- Go\n", "Engineer", PROFILE)
    assert "<style>" in html                   # CSS inlined
    assert "stylesheets/extra.css" not in html  # no Material theme assets
    assert "<base" not in html                  # self-contained, no base href

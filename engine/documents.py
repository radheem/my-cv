"""Render generated Markdown into standalone, theme-independent HTML documents.

Pure (no API, no network). Produces self-contained HTML with the document
stylesheet inlined, so the SAME output drives both the WeasyPrint PDF and the
in-browser unlock view — no MkDocs Material chrome, no external assets.

Three document kinds:
  - CV     — classic one-column; header (name/tagline/contact) composed from
             profile.yml, body is the `## Experience …` sections.
  - Letter — minimal business letter; letterhead, date, salutation, body, sign-off.
             No title. Salutation uses a recipient name when given.
  - Plain  — job description (preformatted), same shell.
"""

from __future__ import annotations

import datetime
import html
import pathlib
from typing import Any

import markdown as _markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
_CSS_PATH = ROOT / "docs" / "assets" / "doc.css"

_MD_EXTENSIONS = ["tables", "attr_list", "sane_lists"]


def css() -> str:
    return _CSS_PATH.read_text(encoding="utf-8")


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split a leading `--- … ---` YAML block off the body. Returns ({}, text)
    when there is no front matter."""
    import yaml

    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            meta = yaml.safe_load(text[3:end]) or {}
            body = text[end + 4 :].lstrip("\n")
            return (meta if isinstance(meta, dict) else {}), body
    return {}, text


def _md(body_md: str) -> str:
    return _markdown.markdown(body_md, extensions=_MD_EXTENSIONS)


def _shell(body_html: str, doc_class: str) -> str:
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<style>{css()}</style></head>"
        f'<body><main class="{doc_class}">{body_html}</main></body></html>'
    )


def _contact_html(profile: dict[str, Any]) -> str:
    links = profile.get("links", {}) or {}
    parts: list[str] = []
    if profile.get("location"):
        parts.append(html.escape(str(profile["location"])))
    if profile.get("email"):
        e = html.escape(str(profile["email"]))
        parts.append(f'<a href="mailto:{e}">{e}</a>')
    for label in ("portfolio", "github", "linkedin"):
        if links.get(label):
            parts.append(f'<a href="{html.escape(str(links[label]))}">{label}</a>')
    return " &nbsp;|&nbsp; ".join(parts)


def render_cv_html(body_md: str, tagline: str, profile: dict[str, Any]) -> str:
    header = (
        f'<h1 class="cv-name">{html.escape(str(profile.get("name", "")))}</h1>'
        + (f'<p class="cv-tagline">{html.escape(tagline)}</p>' if tagline else "")
        + f'<p class="cv-contact">{_contact_html(profile)}</p>'
        + '<hr class="cv-rule">'
    )
    return _shell(header + _md(body_md), "cv")


def render_letter_html(
    body_md: str,
    meta: dict[str, Any],
    profile: dict[str, Any],
    today: datetime.date | None = None,
) -> str:
    name = html.escape(str(profile.get("name", "")))
    tagline = html.escape(str(profile.get("tagline", "")))
    recipient = (meta.get("recipient") or "").strip()
    salutation = f"Dear {recipient}," if recipient else "Dear Hiring Team,"
    date_str = meta.get("date") or (today or datetime.date.today()).strftime(
        "%-d %B %Y"
    )

    letterhead = (
        '<div class="letterhead">'
        f'<p class="lh-name">{name}</p>'
        + (f'<p class="lh-tagline">{tagline}</p>' if tagline else "")
        + f'<p class="lh-contact">{_contact_html(profile)}</p>'
        + '</div><hr class="lh-rule">'
    )
    body = (
        letterhead
        + f'<p class="date">{html.escape(str(date_str))}</p>'
        + f'<p class="salutation">{html.escape(salutation)}</p>'
        + f'<div class="body">{_md(body_md)}</div>'
        + '<div class="signoff">Sincerely,\n'
        + f'<span class="signer">{name}</span></div>'
    )
    return _shell(body, "letter")


def render_cv_raw(body_md: str) -> str:
    """Wrap an already-complete CV Markdown (its own name/contact header) in the
    classic .cv shell. Used for the public general CV (docs/cv.md)."""
    lines = [
        ln
        for ln in body_md.splitlines()
        if ".md-button" not in ln  # drop MkDocs download-button markup
    ]
    cleaned = "\n".join(lines).replace(":material-download: ", "")
    return _shell(_md(cleaned), "cv")


def render_plain_html(title: str, body_md: str) -> str:
    heading = f"<h1>{html.escape(title)}</h1>" if title else ""
    return _shell(heading + _md(body_md), "plain")

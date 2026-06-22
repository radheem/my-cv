"""Deterministic Markdown → LaTeX rendering for the resume.cls / coverletter.cls
templates (replicated from the `resume` project's LaTeX system).

The LLM produces structured Markdown — `cv.md` / `cover-letter.md` and their German
translations `cv.de.md` / `cover-letter.de.md`. This module fills the LaTeX template
from that Markdown: it handles LaTeX escaping, maps the known CV structure onto the
class macros (``\\role`` / ``\\edu`` / ``\\project`` / ``\\bullets``), and assembles the
bilingual (English-then-German) document. No LLM here — given the same Markdown it is
reproducible, and the model never has to emit valid LaTeX.

Expected `cv.md` body shape (after front matter is stripped)::

    ## Experience
    ### Bluefin Exchange — Senior Software Engineer
    *Pakistan · 06/2021 – 08/2023*
    - bullet
    ## Education
    ### Technical University of Ilmenau
    *Master of Research … · 04/2024 – Present*
    ## Projects
    - **IRS Platform (Stealth)** — one-line description
    ## Skills
    - **Languages** — English (fluent), Deutsch (A2)

The German body uses the same structure with translated headings
(Berufserfahrung / Ausbildung / Projekte / Kenntnisse) — parsing is structural, so it
is language-agnostic. Project hyperlinks are resolved once from the English project
list and reused positionally for the German block (same top-3, same order).
"""

from __future__ import annotations

import re
from typing import Any

# ---- LaTeX escaping ---------------------------------------------------------

_ESC = {
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}", "\\": r"\textbackslash{}",
}
_ESC_RE = re.compile(r"[&%$#_{}~^\\]")
_INLINE_RE = re.compile(r"\*\*(.+?)\*\*|`(.+?)`|\[(.+?)\]\((.+?)\)")


def escape_tex(s: str) -> str:
    """Escape LaTeX specials in literal text (single pass; no double-escaping)."""
    return _ESC_RE.sub(lambda m: _ESC[m.group()], s)


def _escape_url(url: str) -> str:
    return url.replace("\\", r"\\").replace("%", r"\%").replace("#", r"\#")


def inline(s: str) -> str:
    """Convert inline Markdown (**bold**, `code`, [text](url)) to LaTeX, escaping
    the literal text between markers."""
    out, i = [], 0
    for m in _INLINE_RE.finditer(s):
        out.append(escape_tex(s[i:m.start()]))
        if m.group(1) is not None:
            out.append(r"\textbf{" + escape_tex(m.group(1)) + "}")
        elif m.group(2) is not None:
            out.append(r"\texttt{" + escape_tex(m.group(2)) + "}")
        else:
            out.append(r"\href{" + _escape_url(m.group(4)) + "}{" + escape_tex(m.group(3)) + "}")
        i = m.end()
    out.append(escape_tex(s[i:]))
    return "".join(out)


# ---- Section parsing --------------------------------------------------------

_DASH = re.compile(r"\s+[—–-]\s+")  # em/en/hyphen dash with surrounding spaces
_MIDDOT = " · "

_KIND = {  # heading keyword (lowercased) → section kind
    "experience": "experience", "berufserfahrung": "experience",
    "education": "education", "ausbildung": "education",
    "projects": "projects", "projekte": "projects",
    "skills": "skills", "kenntnisse": "skills",
}


def _normalize_entry_headings(body: str) -> str:
    """Demote stray ``## Entry`` headings to ``### Entry`` inside a known section.

    The LLM sometimes writes an education/experience entry as an H2 (e.g.
    ``## Technical University of Ilmenau``) instead of an H3. Left alone, the
    section splitter would treat that as a new top-level section and the entry
    (degree, dates) would be dropped. We rewrite any ``## X`` whose heading is
    NOT a known section keyword to ``### X`` once we are inside a real section,
    so the per-section entry parsers see it correctly.
    """
    out, in_section = [], False
    for ln in body.splitlines():
        if ln.startswith("## "):
            heading = ln[3:].strip().lower()
            if heading in _KIND:
                in_section = True
                out.append(ln)
            elif in_section:
                out.append("#" + ln)  # ## X → ### X
            else:
                out.append(ln)
        else:
            out.append(ln)
    return "\n".join(out)


def _sections(body: str) -> list[tuple[str, str, list[str]]]:
    """Split a CV body into (kind, heading, lines) by ``## `` headings."""
    body = _normalize_entry_headings(body)
    out, heading, lines = [], None, []

    def flush():
        if heading is not None:
            kind = _KIND.get(heading.strip().lower(), "raw")
            out.append((kind, heading.strip(), lines.copy()))

    for ln in body.splitlines():
        if ln.startswith("## "):
            flush()
            heading, lines = ln[3:], []
        elif heading is not None:
            lines.append(ln)
    flush()
    return out


def _split_dates(italic: str) -> tuple[str, str]:
    """``*Pakistan · 06/2021 – 08/2023*`` → ('Pakistan', '06/2021 – 08/2023')."""
    text = italic.strip().strip("*").strip()
    if _MIDDOT in text:
        left, right = text.rsplit(_MIDDOT, 1)
        return left.strip(), right.strip()
    return "", text


def _skip_blank(lines: list[str], i: int) -> int:
    while i < len(lines) and not lines[i].strip():
        i += 1
    return i


def _experience(lines: list[str]) -> str:
    """### Org — Role / *loc · dates* / - bullets  →  \\role + \\bullets."""
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i].strip()
        if ln.startswith("### "):
            head = ln[4:].strip()
            i = _skip_blank(lines, i + 1)
            loc, dates = "", ""
            if i < n and lines[i].strip().startswith("*"):
                loc, dates = _split_dates(lines[i].strip())
                i = _skip_blank(lines, i + 1)
            bullets = []
            while i < n:
                s = lines[i].lstrip()
                if s.startswith(("- ", "* ")):
                    bullets.append(s[2:].strip())
                    i += 1
                elif not lines[i].strip():  # tolerate blank lines between bullets
                    i += 1
                else:
                    break
            out.append("\\role{%s}{%s}{%s}" % (inline(head), inline(loc), inline(dates)))
            if bullets:
                out.append("\\bullets")
                out += ["  \\item " + inline(b) for b in bullets]
                out.append("\\bulletsend")
            out.append("\\vspace{3pt}")
        else:
            i += 1
    return "\n".join(out)


def _edu_degree_dates(line: str) -> tuple[str, str]:
    """Parse degree and dates from various non-italic formats the LLM produces.

    Handles:
      - "Master of Research … · 04/2024 – Present"  (middot, no italic)
      - "Master of Research … | 04/2024 – Present"  (pipe)
      - "Master of Research … — 04/2024 – Present"  (em-dash)
      - "Master of Research …"                       (degree only, no dates found)
    """
    stripped = line.strip().strip("*").strip()
    for sep in (" · ", " | ", " — ", " – "):
        if sep in stripped:
            left, right = stripped.rsplit(sep, 1)
            # heuristic: the dates side looks like a year or "Present"
            if re.search(r"\d{4}|present", right, re.IGNORECASE):
                return left.strip(), right.strip()
    return stripped, ""


def _education(lines: list[str]) -> str:
    """Parse education entries in any of the formats the LLM produces.

    Canonical (what the prompt now asks for):
        ### Org
        *Degree · Dates*

    Also handles variants already in the wild:
        ### Org
        Degree | Dates           (plain line, pipe separator)

        ### Org
        Degree · Dates           (plain line, middot, no italic)

        ### Org — Degree
        *Dates*                  (degree embedded in heading, dates italic)

        ## Org                   (H2 instead of H3 — LLM slip)
        Degree | Dates
    """
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i].strip()
        # accept both ### and ## heading levels for education entries
        if ln.startswith("### ") or ln.startswith("## "):
            prefix_len = 4 if ln.startswith("### ") else 3
            org_raw = ln[prefix_len:].strip()
            # degree may be embedded in the heading after " — "
            heading_degree = ""
            if " — " in org_raw or " – " in org_raw:
                sep = " — " if " — " in org_raw else " – "
                parts = org_raw.split(sep, 1)
                org_raw = parts[0].strip()
                heading_degree = parts[1].strip()

            i = _skip_blank(lines, i + 1)
            degree, dates = heading_degree, ""

            if i < n:
                next_ln = lines[i].strip()
                if next_ln.startswith("*"):
                    # italic line → *Degree · Dates* or just *Dates*
                    d, dt = _split_dates(next_ln)
                    if heading_degree:
                        # degree already extracted from heading; this line is dates only
                        dates = dt or d
                    else:
                        degree, dates = d, dt
                    i = _skip_blank(lines, i + 1)
                elif next_ln and not next_ln.startswith(("#", "-", "*", ">")):
                    # plain text line — try to extract degree and dates
                    d, dt = _edu_degree_dates(next_ln)
                    if not heading_degree:
                        degree = d
                    dates = dt
                    i = _skip_blank(lines, i + 1)

            out.append("\\edu{%s}{%s}{%s}" % (inline(org_raw), inline(degree), inline(dates)))
            out.append("\\vspace{2pt}")
        else:
            i += 1
    return "\n".join(out[:-1] if out else out)  # drop trailing \vspace


def _project_items(lines: list[str]) -> list[tuple[str, str]]:
    """- **Name** — description  →  [(name, description)]."""
    items = []
    for ln in lines:
        s = ln.lstrip()
        if not s.startswith(("- ", "* ")):
            continue
        s = s[2:].strip()
        m = re.match(r"\*\*(.+?)\*\*\s*[—–-]\s*(.*)", s)
        if m:
            items.append((m.group(1).strip(), m.group(2).strip()))
        else:  # no bold name — best effort split on the first dash
            parts = _DASH.split(s, 1)
            items.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
    return items


def _projects(items: list[tuple[str, str]], urls: list[str]) -> str:
    out = ["\\begin{itemize}[leftmargin=1.4em,nosep,topsep=2pt]"]
    for (name, desc), url in zip(items, urls):
        out.append("  \\project{%s}{%s}{%s}" % (inline(name), _escape_url(url), inline(desc)))
    out.append("\\end{itemize}")
    return "\n".join(out)


def _skills(lines: list[str]) -> str:
    out = ["\\begin{itemize}[leftmargin=1.4em,nosep,topsep=2pt]"]
    for ln in lines:
        s = ln.lstrip()
        if not s.startswith(("- ", "* ")):
            continue
        s = s[2:].strip()
        m = re.match(r"\*\*(.+?)\*\*\s*[—–-]\s*(.*)", s)
        if m:
            out.append("  \\item \\textbf{%s:} %s" % (inline(m.group(1).strip()), inline(m.group(2).strip())))
        else:
            out.append("  \\item " + inline(s))
    out.append("\\end{itemize}")
    return "\n".join(out)


# ---- Project URL resolution -------------------------------------------------

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _resolve_urls(items: list[tuple[str, str]], projects: list[dict], portfolio: str) -> list[str]:
    """Map each project name to its portfolio page via projects.yml `doc:` path;
    fall back to the projects index. Resolved from the English list and reused for DE."""
    index = f"{portfolio}/projects/"
    table = []
    for p in projects:
        doc = str(p.get("doc", "")).strip()
        url = f"{portfolio}/{doc[:-3].rstrip('/')}/" if doc.endswith(".md") else index
        table.append((_norm(str(p.get("name", ""))), _norm(str(p.get("id", ""))), url))
    urls = []
    for name, _ in items:
        key = _norm(name)
        best = index
        for nname, nid, url in table:
            if key and (nname.startswith(key) or key.startswith(nname) or nid and nid in key):
                best = url
                break
        urls.append(best)
    return urls


# ---- Header -----------------------------------------------------------------

def _link_macros(profile: dict) -> str:
    links = profile.get("links", {}) or {}
    portfolio = links.get("portfolio", "https://radheem.github.io/my-cv")
    return "\n".join([
        "\\newcommand{\\Portfolio}{%s}" % portfolio,
        "\\newcommand{\\PortfolioText}{portfolio}",
        "\\newcommand{\\GitHub}{%s}" % links.get("github", ""),
        "\\newcommand{\\LinkedIn}{%s}" % links.get("linkedin", ""),
        "\\newcommand{\\Email}{%s}" % profile.get("email", ""),
    ])


def _header(name: str, tagline: str, location: str) -> str:
    return "\n".join([
        "\\begin{center}",
        "  {\\huge\\bfseries %s}\\\\[3pt]" % inline(name),
        "  {\\large %s}\\\\[6pt]" % inline(tagline),
        "  \\small",
        "  %s \\,\\textbar\\," % inline(location),
        "  \\href{mailto:\\Email}{\\Email} \\,\\textbar\\,",
        "  \\href{\\Portfolio}{\\PortfolioText} \\,\\textbar\\,",
        "  \\href{\\LinkedIn}{linkedin} \\,\\textbar\\,",
        "  \\href{\\GitHub}{github}",
        "\\end{center}",
        "\\vspace{2pt}",
    ])


def _render_cv_block(body: str, urls: list[str] | None, projects: list[dict], portfolio: str):
    """Render one language's CV sections; returns (latex, resolved_project_urls)."""
    parts, resolved = [], urls
    for kind, heading, lines in _sections(body):
        parts.append("\\section{%s}" % inline(heading))
        if kind == "experience":
            parts.append(_experience(lines))
        elif kind == "education":
            parts.append(_education(lines))
        elif kind == "projects":
            items = _project_items(lines)
            if resolved is None:
                resolved = _resolve_urls(items, projects, portfolio)
            parts.append(_projects(items, resolved + [f"{portfolio}/projects/"] * 5))
        elif kind == "skills":
            parts.append(_skills(lines))
        else:
            parts.append(inline("\n".join(lines)))
    return "\n\n".join(parts), resolved


def render_cv_tex(en_body: str, de_body: str, profile: dict, projects: list[dict],
                  tagline_en: str = "", tagline_de: str = "") -> str:
    """Bilingual tailored CV → a complete cv.tex using \\documentclass{resume}."""
    portfolio = (profile.get("links", {}) or {}).get("portfolio", "https://radheem.github.io/my-cv")
    name = profile.get("name", "")
    loc = profile.get("location", "")
    loc_de = loc.replace("Germany", "Deutschland")
    en_tex, urls = _render_cv_block(en_body, None, projects, portfolio)
    de_tex, _ = _render_cv_block(de_body, urls, projects, portfolio)
    return "\n".join([
        "\\documentclass[11pt,a4paper]{resume}",
        "",
        _link_macros(profile),
        "",
        "\\begin{document}",
        "",
        "%% ===== ENGLISH =====",
        _header(name, tagline_en, loc),
        "",
        en_tex,
        "",
        "\\clearpage",
        "\\selectlanguage{ngerman}",
        "",
        "%% ===== DEUTSCH =====",
        _header(name, tagline_de or tagline_en, loc_de),
        "",
        de_tex,
        "",
        "\\end{document}",
        "",
    ])


# ---- Cover letter -----------------------------------------------------------

def _paras(body: str) -> list[str]:
    """Split a cover-letter body into paragraphs (blank-line separated)."""
    return [p.strip() for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]


def _letter_block(body: str, company: str, attn: str, salutation: str,
                  signoff: str, name: str) -> str:
    paras = "\n\n".join(inline(" ".join(p.splitlines())) for p in _paras(body))
    return "\n".join([
        "\\recipient{%s}{%s}{}" % (inline(company), attn),
        "",
        "\\opening{%s}" % inline(salutation),
        "",
        paras,
        "",
        "\\closing{%s}{%s}" % (inline(signoff), inline(name)),
    ])


def render_cover_tex(en_body: str, de_body: str, meta: dict, profile: dict) -> str:
    """Bilingual cover letter → a complete cover-letter.tex using {coverletter}."""
    name = profile.get("name", "")
    tagline = profile.get("tagline", "")
    email = profile.get("email", "")
    portfolio = (profile.get("links", {}) or {}).get("portfolio", "")
    company = str(meta.get("company", ""))
    recipient = str(meta.get("recipient", "") or "").strip()
    sal_en = f"Dear {recipient}," if recipient else "Dear Hiring Team,"
    sal_de = f"Sehr geehrte/r {recipient}," if recipient else "Sehr geehrtes Hiring-Team,"
    contact = "%s \\textbar\\ \\href{mailto:%s}{%s} \\textbar\\ \\href{%s}{portfolio}" % (
        inline(profile.get("location", "")), email, inline(email), _escape_url(portfolio))
    return "\n".join([
        "\\documentclass[11pt,a4paper]{coverletter}",
        "",
        "\\senderblock",
        "  {%s}" % inline(name),
        "  {%s}" % inline(tagline),
        "  {%s}" % contact,
        "",
        "\\begin{document}",
        "",
        "%% ===== ENGLISH =====",
        _letter_block(en_body, company, "Hiring Team", sal_en, "Sincerely,", name),
        "",
        "\\clearpage",
        "\\selectlanguage{ngerman}",
        "",
        "%% ===== DEUTSCH =====",
        _letter_block(de_body, company, "Personalabteilung", sal_de,
                      "Mit freundlichen Grüßen,", name),
        "",
        "\\end{document}",
        "",
    ])

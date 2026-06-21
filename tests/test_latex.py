"""Tests for the deterministic Markdown → LaTeX renderer (engine/latex.py).

No LaTeX toolchain needed — these check escaping, macro mapping, and bilingual
assembly on the rendered .tex string."""

from engine import latex

PROFILE = {
    "name": "Radheem Bin Razi",
    "tagline": "Distributed Systems Engineer",
    "location": "Ilmenau, Germany",
    "email": "sheikh.radheem@gmail.com",
    "links": {
        "portfolio": "https://radheem.github.io/my-cv",
        "github": "https://github.com/radheem",
        "linkedin": "https://www.linkedin.com/in/radheem-razi",
    },
}
PROJECTS = [
    {"id": "irs", "name": "IRS Platform (Stealth)", "doc": "projects/irs.md"},
    {"id": "cv-tailor", "name": "cv-tailor (LLM Tailoring)", "doc": "projects/cv-tailor.md"},
]

CV = """## Experience

### Acme & Co — Senior Engineer
*Berlin · 06/2021 – 08/2023*

- Built 100% of the backend with C# and a_b_c.
- Led reviews.

## Education

### TU Ilmenau
*M.Sc. Research · 04/2024 – Present*

## Projects

- **IRS Platform (Stealth)** — Go microservices & gRPC.
- **cv-tailor (LLM Tailoring)** — pure ranker + LLM prose.

## Skills

- **Languages** — English (fluent), Deutsch (A2)
- **Programming Languages** — Go, Python
"""


def test_escape_specials():
    assert latex.escape_tex("a & b % c _ d # e") == r"a \& b \% c \_ d \# e"


def test_inline_bold_and_link():
    assert latex.inline("**bold** text") == r"\textbf{bold} text"
    assert latex.inline("[x](http://a.com)") == r"\href{http://a.com}{x}"


def test_render_cv_structure_and_escaping():
    tex = latex.render_cv_tex(CV, CV, PROFILE, PROJECTS, "Backend Engineer", "Backend-Ingenieur")
    assert tex.startswith("\\documentclass[11pt,a4paper]{resume}")
    assert "\\begin{document}" in tex and "\\end{document}" in tex
    # bilingual split
    assert "\\selectlanguage{ngerman}" in tex
    assert tex.count("\\section{Experience}") == 2  # EN body used for both here
    # macros + escaping
    assert "\\role{Acme \\& Co — Senior Engineer}{Berlin}{06/2021 – 08/2023}" in tex
    assert "\\bullets" in tex and "\\bulletsend" in tex
    assert "a\\_b\\_c" in tex
    assert "\\edu{TU Ilmenau}{M.Sc. Research}{04/2024 – Present}" in tex
    # project URL resolved from projects.yml doc path
    assert "\\project{IRS Platform (Stealth)}{https://radheem.github.io/my-cv/projects/irs/}" in tex
    assert "\\item \\textbf{Languages:} English (fluent), Deutsch (A2)" in tex


def test_render_cover_bilingual():
    tex = latex.render_cover_tex(
        "Para one.\n\nPara two.", "Absatz eins.\n\nAbsatz zwei.",
        {"company": "Acme & Co", "recipient": ""}, PROFILE,
    )
    assert "\\documentclass[11pt,a4paper]{coverletter}" in tex
    assert "\\opening{Dear Hiring Team,}" in tex
    assert "\\opening{Sehr geehrtes Hiring-Team,}" in tex
    assert "\\recipient{Acme \\& Co}" in tex
    assert "\\closing{Sincerely,}{Radheem Bin Razi}" in tex

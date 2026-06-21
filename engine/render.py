"""Render tailored CV + cover letter Markdown from a JobSpec (Claude API).

Consumes the pure ranking decisions from rank.tailor() so the LLM only writes
prose around already-chosen projects and skills — it never picks them.
"""

from __future__ import annotations

from typing import Any

import yaml

from . import config, llm, prompts


def _cover_exemplars() -> str:
    """Style-only opener exemplars from data/prompts/exemplars/cover.yml, as a
    prompt block. Empty when fewshot is off or the file is absent."""
    pcfg = config.load()["prompts"]
    if not pcfg.get("fewshot", True):
        return ""
    path = config.ROOT / pcfg.get("dir", "data/prompts") / "exemplars" / "cover.yml"
    if not path.exists():
        return ""
    items = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    lines = "\n".join(f"- {e['opening']}" for e in items if e.get("opening"))
    if not lines:
        return ""
    return (
        "## Example openings (style/tone ONLY — do not reuse their words or facts)\n"
        f"{lines}\n\n"
    )


def _skills_block(skills: list[dict[str, str]]) -> str:
    return "\n".join(f"- **{line['label']}** — {line['value']}" for line in skills)


def _projects_block(projects: list[dict[str, Any]], *, detailed: bool = False) -> str:
    """Render the featured projects for a prompt.

    detailed=True surfaces each project's `highlights` (role-neutral source facts)
    so the LLM can re-angle them to the job; falls back to `summary` when a project
    has no highlights. detailed=False keeps the one-line summary form."""
    out = []
    for p in projects:
        url = f" ({p['url']})" if p.get("url") else ""
        if detailed and p.get("highlights"):
            facts = "\n".join(f"    - {h}" for h in p["highlights"])
            out.append(f"- **{p['name']}**{url}\n{facts}")
        else:
            out.append(f"- **{p['name']}**{url} — {p['summary']}")
    return "\n".join(out)


_CV_SYSTEM = (
    "You write a tailored, one-page CV body in GitHub-flavored Markdown. Rules:\n"
    "- TRUTH ONLY: use only facts from the provided master CV. Never invent "
    "roles, employers, dates, skills, or metrics.\n"
    "- Reorder and reword experience bullets to foreground what the job needs.\n"
    "- Feature EXACTLY the provided top-3 projects (no more, no fewer) and use the "
    "provided skills block verbatim (do not add or drop skill lines).\n"
    "- Each project comes with a list of role-neutral source facts (highlights). "
    "In ## Projects, format each as a SINGLE Markdown bullet exactly like "
    "'- **<exact project name>** — <one re-angled sentence>' (a bold name, an em-dash, "
    "then prose). Do NOT use '###' headers for projects and do NOT rename, merge, or "
    "drop projects — keep each name verbatim. Re-frame each project's facts to "
    "foreground what THIS job needs — the data/ETL angle for a data role, the "
    "observability/Kubernetes angle for a platform/devops role, the API/microservice "
    "angle for a backend role. Use ONLY facts from that project's highlights and the "
    "master CV; never invent.\n"
    "- Do NOT include the candidate name or contact line — those are added by the "
    "template. The VERY FIRST line of your output must be exactly "
    "'tagline: <role tagline>' (a short role title retitled to fit the job, only "
    "if honest), then a blank line.\n"
    "- After that, the CV body with sections in this order, each an H2 "
    "(## Experience, ## Education, ## Projects, ## Skills). Use '### Org — Role' "
    "for each entry followed by an italic '*Location · dates*' line, then bullets.\n"
    "- Education entries are headers ONLY (org, degree, dates). Do NOT add coursework, "
    "GPA, focus areas, or bullet points under Education unless they appear verbatim in "
    "the master CV.\n"
    "- Write organization and institution names EXACTLY as they appear in the master CV "
    "(e.g. 'Technical University of Ilmenau', not 'TU Ilmenau'); do not abbreviate them.\n"
    "- Keep it tight (about one page). Output Markdown only — no code fences, no "
    "commentary."
)

_COVER_SYSTEM = (
    "You write the BODY of a tailored cover letter in GitHub-flavored Markdown — "
    "just the paragraphs, ~3-4 of them, 250-400 words, for a non-technical first "
    "reader. Rules:\n"
    "- TRUTH ONLY: no invented experience, skills, metrics, or dates.\n"
    "- Do NOT write a title/heading, a salutation ('Dear ...'), or a sign-off "
    "('Sincerely ...') — the template adds the letterhead, salutation, and "
    "signature. Output the body paragraphs ONLY.\n"
    "- OPENING: do NOT open with 'I am excited to apply' / 'I am writing to apply for "
    "the <role> position at <company>' or any variant of that cliché. Open with ONE "
    "genuine, specific idea that connects your motivation to THIS company's mission or "
    "problem, then name the role. Match the TONE of this example (style only, never "
    "reuse its words): \"A good monitoring system tells you what is wrong before a "
    "customer ever notices — building that quiet kind of reliability is the part of "
    "operations I enjoy most.\"\n"
    "- BODY (1-2 paragraphs): concrete, specific proof that COMPLEMENTS the CV (adds "
    "detail, never repeats its bullets verbatim). Prefer named systems and real numbers "
    "from the proof points over generic phrasing.\n"
    "- CLOSE: briefly restate fit, then state availability and relocation / "
    "work-authorization when they are provided.\n"
    "- One idea per sentence. Output Markdown only — no code fences, no commentary."
)


def _context(
    jobspec: dict[str, Any],
    tailoring: dict[str, Any],
    master_cv: str,
    guide: str,
) -> str:
    return (
        f"## Target job\n"
        f"Title: {jobspec.get('title')}\nCompany: {jobspec.get('company')}\n"
        f"Seniority: {jobspec.get('seniority')}\n"
        f"Must-haves: {', '.join(jobspec.get('must_haves', []))}\n"
        f"Nice-to-haves: {', '.join(jobspec.get('nice_to_haves', []))}\n"
        f"Stack: {', '.join(jobspec.get('stack', []))}\n\n"
        f"## Top-3 projects to feature (in this order) — re-angle each to the job\n"
        f"{_projects_block(tailoring['top_projects'], detailed=True)}\n\n"
        f"## Skills block to use verbatim\n{_skills_block(tailoring['skills'])}\n\n"
        f"## House guide\n{guide}\n\n"
        f"## Master CV (source of truth — facts only)\n{master_cv}"
    )


def render_cv(
    jobspec: dict[str, Any],
    tailoring: dict[str, Any],
    master_cv: str,
    guide: str,
) -> tuple[str, str]:
    """Return (tagline, cv_body_markdown). The body starts at '## Experience';
    the name/contact header is composed by the template from profile.yml."""
    user = _context(jobspec, tailoring, master_cv, guide) + (
        "\n\nWrite the tailored CV now."
    )
    system, _ = prompts.load("cv", _CV_SYSTEM)
    text = llm.stream_text(system, user, max_tokens=llm.resolve()["max_tokens"]["cv"]).strip()
    tagline = ""
    lines = text.splitlines()
    if lines and lines[0].lower().startswith("tagline:"):
        tagline = lines[0].split(":", 1)[1].strip()
        text = "\n".join(lines[1:]).lstrip("\n")
    return tagline, text + "\n"


def render_cover_letter(
    jobspec: dict[str, Any],
    tailoring: dict[str, Any],
    profile_summary: str,
    job_text: str,
    guide: str,
    availability: str = "",
    relocation: str = "",
) -> str:
    logistics = ""
    if availability or relocation:
        logistics = (
            "## Logistics for the close (weave in naturally; do not just list)\n"
            f"{availability}\n{relocation}\n\n"
        )
    user = (
        f"## Target job\nTitle: {jobspec.get('title')}\n"
        f"Company: {jobspec.get('company')}\n\n"
        f"## Job posting\n{job_text.strip()}\n\n"
        f"## Candidate summary\n{profile_summary}\n\n"
        f"## Proof points (top projects — source facts; weave a couple in, do not list)\n"
        f"{_projects_block(tailoring['top_projects'], detailed=True)}\n\n"
        f"{logistics}"
        f"{_cover_exemplars()}"
        f"## House guide\n{guide}\n\n"
        "Write the tailored cover letter now."
    )
    system, _ = prompts.load("cover", _COVER_SYSTEM)
    return llm.stream_text(
        system, user, max_tokens=llm.resolve()["max_tokens"]["cover"]
    ).strip() + "\n"

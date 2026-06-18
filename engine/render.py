"""Render tailored CV + cover letter Markdown from a JobSpec (Claude API).

Consumes the pure ranking decisions from rank.tailor() so the LLM only writes
prose around already-chosen projects and skills — it never picks them.
"""

from __future__ import annotations

from typing import Any

from . import llm


def _skills_block(skills: list[dict[str, str]]) -> str:
    return "\n".join(f"- **{line['label']}** — {line['value']}" for line in skills)


def _projects_block(projects: list[dict[str, Any]]) -> str:
    out = []
    for p in projects:
        url = f" ({p['url']})" if p.get("url") else ""
        out.append(f"- **{p['name']}**{url} — {p['summary']}")
    return "\n".join(out)


_CV_SYSTEM = (
    "You write a tailored, one-page CV body in GitHub-flavored Markdown. Rules:\n"
    "- TRUTH ONLY: use only facts from the provided master CV. Never invent "
    "roles, employers, dates, skills, or metrics.\n"
    "- Reorder and reword experience bullets to foreground what the job needs.\n"
    "- Use exactly the provided top-3 projects and the provided skills block "
    "(do not add or drop projects/skill lines).\n"
    "- Do NOT include the candidate name or contact line — those are added by the "
    "template. The VERY FIRST line of your output must be exactly "
    "'tagline: <role tagline>' (a short role title retitled to fit the job, only "
    "if honest), then a blank line.\n"
    "- After that, the CV body with sections in this order, each an H2 "
    "(## Experience, ## Education, ## Projects, ## Skills). Use '### Org — Role' "
    "for each entry followed by an italic '*Location · dates*' line, then bullets.\n"
    "- Keep it tight (about one page). Output Markdown only — no code fences, no "
    "commentary."
)

_COVER_SYSTEM = (
    "You write the BODY of a tailored cover letter in GitHub-flavored Markdown — "
    " just the paragraphs, ~3-4 of them, 250-400 words, for a non-technical first "
    "reader. Rules:\n"
    "- TRUTH ONLY: no invented experience, skills, metrics, or dates.\n"
    "- Do NOT write a title/heading, a salutation ('Dear ...'), or a sign-off "
    "('Sincerely ...') — the letter template adds the letterhead, salutation, and "
    "signature. Output the body paragraphs ONLY.\n"
    "- A light, genuine opening that names the role and a real 'why this company'; "
    "1-2 body paragraphs of concrete proof that complement (not repeat) the CV; a "
    "closing paragraph with availability.\n"
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
        f"## Top-3 projects to feature (in this order)\n"
        f"{_projects_block(tailoring['top_projects'])}\n\n"
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
    text = llm.stream_text(_CV_SYSTEM, user, max_tokens=16000).strip()
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
) -> str:
    user = (
        f"## Target job\nTitle: {jobspec.get('title')}\n"
        f"Company: {jobspec.get('company')}\n\n"
        f"## Job posting\n{job_text.strip()}\n\n"
        f"## Candidate summary\n{profile_summary}\n\n"
        f"## Proof points (top projects)\n{_projects_block(tailoring['top_projects'])}\n\n"
        f"## House guide\n{guide}\n\n"
        "Write the tailored cover letter now."
    )
    return llm.stream_text(_COVER_SYSTEM, user, max_tokens=8000).strip() + "\n"

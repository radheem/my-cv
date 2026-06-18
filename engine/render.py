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
    "You write a tailored, one-page CV in GitHub-flavored Markdown. Rules:\n"
    "- TRUTH ONLY: use only facts from the provided master CV. Never invent "
    "roles, employers, dates, skills, or metrics.\n"
    "- Reorder and reword experience bullets to foreground what the job needs.\n"
    "- Use exactly the provided top-3 projects and the provided skills block "
    "(do not add or drop projects/skill lines).\n"
    "- Start the page with an H1 of the candidate name, then a one-line role "
    "tagline retitled to fit the job (only if honest), then a one-line contact.\n"
    "- Sections in order: Experience, Education, Projects, Skills. Keep it tight "
    "(about one page). Output Markdown only — no code fences, no commentary."
)

_COVER_SYSTEM = (
    "You write a tailored cover letter in GitHub-flavored Markdown, ~4 paragraphs, "
    "250-400 words, for a non-technical first reader. Rules:\n"
    "- TRUTH ONLY: no invented experience, skills, metrics, or dates.\n"
    "- Structure: a light, genuine opening hook naming the role and a real 'why "
    "this company'; 2-3 body paragraphs with concrete proof that complement (not "
    "repeat) the CV; a closing with availability.\n"
    "- One idea per sentence; salutation 'Dear Hiring Team,'; never 'To Whom it "
    "May Concern'. Output Markdown only — no code fences, no commentary."
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
) -> str:
    user = _context(jobspec, tailoring, master_cv, guide) + (
        "\n\nWrite the tailored CV now."
    )
    return llm.stream_text(_CV_SYSTEM, user, max_tokens=16000).strip() + "\n"


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

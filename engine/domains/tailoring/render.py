"""Render tailored CV + cover letter Markdown from a JobSpec (Claude API).

Consumes the pure ranking decisions from rank.tailor() so the LLM only writes
prose around already-chosen projects and skills — it never picks them.
"""

from __future__ import annotations

from typing import Any

import yaml

from engine.shared import config
from . import llm, prompts


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


_CV_SYSTEM_FALLBACK = (
    "You write a tailored, one-page CV body in GitHub-flavored Markdown. Treat this CV as a high-signal \"landing page\" designed to encourage the viewer to visit the portfolio link for full details. You MUST be ruthless with your word count and focus purely on technical scale and impact.\n\n"
    "## RULES & CONSTRAINTS (MANDATORY)\n"
    "- TRUTH ONLY: Use only facts from the provided master CV. Never invent roles, employers, dates, skills, or metrics.\n"
    "- RUTHLESS BREVITY (EXPERIENCE): Reorder and reword experience bullets to foreground what the job needs. You MUST limit recent roles (last 2 jobs) to exactly 2 punchy, single-sentence bullet points. Limit older roles to exactly 1 bullet point. Add a final line 'Tech: ...' listing only relevant keywords.\n"
    "- RUTHLESS BREVITY (PROJECTS): Feature EXACTLY the provided top-2 projects (no more, no fewer). In ## Projects (which you can also title ## Selected Work), format each project with an H3 heading exactly like '### <exact project name>'. Underneath each heading, you MUST write exactly 2 concise, punchy bullet points (using '- ') highlighting the technical impact. Use ONLY facts from that project's highlights and the master CV; never invent.\n"
    "- RUTHLESS BREVITY (SKILLS): You MUST consolidate the skills list verbatim from the master CV into exactly 3 tight, high-signal categories/rows:\n"
    "  1. *Languages & Core*: Languages (spoken) first — always English (fluent), Deutsch (A2) — then Programming Languages, and core paradigms.\n"
    "  2. *Systems & Infrastructure*: Cloud/Infra, Systems, and Messaging keywords.\n"
    "  3. *Databases & Data Engineering*: Databases and Data/Persistence keywords.\n"
    "- Do NOT include the candidate name or contact line — those are added by the template. The VERY FIRST line of your output must be exactly 'tagline: <role tagline>' (a short role title retitled to fit the job, only if honest), then a blank line.\n"
    "- After that, the CV body with sections in this order, each an H2 (## Experience, ## Education, ## Projects, ## Skills). Use '### Org — Role' for each entry followed by an italic '*Location · dates*' line, then bullets.\n"
    "- Education entries use EXACTLY this two-line format — institution name as '### Org' (H3, no degree in the heading), then an italic line '*Degree · Dates*'. Example:\n"
    "  ### Technical University of Ilmenau\n"
    "  *Master of Research, Computer Systems and Engineering · 04/2024 – Present*\n"
    "  Do NOT add coursework, GPA, focus areas, or bullet points under Education unless they appear verbatim in the master CV.\n"
    "- Write organization and institution names EXACTLY as they appear in the master CV (e.g. 'Technical University of Ilmenau', not 'TU Ilmenau'); do not abbreviate them.\n"
    "- Keep it tight (STRICTLY one page). Output Markdown only — no code fences, no commentary."
)

_COVER_SYSTEM_FALLBACK = (
    "You write the BODY of a tailored cover letter in GitHub-flavored Markdown. It must strictly follow a two-question H2-based structure, ~150-250 words total, optimizing for a punchy, highly scannable reading experience.\n\n"
    "## RULES & CONSTRAINTS (MANDATORY)\n"
    "- LANGUAGE: Write the cover letter entirely in English, even if the target job description or company profile is written in German. NEVER output in German; German translation is handled separately by a downstream pipeline.\n"
    "- TRUTH ONLY: No invented experience, skills, metrics, or dates. Rely strictly and only on facts.\n"
    "- STRUCTURE: You must output exactly two Markdown H2 headings: `## 1. Why <Actual Company Name>?` and `## 2. Why me?` (where `<Actual Company Name>` is replaced by the actual company name). You MUST never leave literal brackets, placeholders, or \"[Company]\" in your headings; always use the actual company name provided.\n"
    "- SPACING: You MUST leave a double blank line (one empty line) between every heading and the paragraph below it.\n"
    "- NO EXTRA TEXT: Do NOT write a title, a salutation ('Dear ...'), or a sign-off ('Sincerely ...') — the template adds the letterhead, salutation, and signature. Output the headings and body paragraphs ONLY.\n"
    "- ONE IDEA PER SENTENCE: Keep sentences short, direct, and high-impact.\n\n"
    "## PROFESSIONAL TONE & SUBTLE ALIGNMENT\n"
    "- NO CLICHÉS: Do NOT open with 'I am excited to apply' or any variant of that cliché.\n"
    "- SUBTLE & MATURE ALIGNMENT: As a professional engineer, your aspiration comes from a combination of the company's long-term vision, tech stack, and goals. Connect your motivation to this company's mission or problem, then name the role.\n"
    "- AVOID EMOTIONAL HYPERBOLE: Avoid dramatic, desperate, or absolute destiny-like statements.\n"
    "  * NEVER say or imply phrases like \"exactly my goal in life\", \"precisely what I want to accomplish\", \"exactly where I want to focus my career\", \"the work I most want to do\", \"exactly the challenge I seek\", \"ultimate passion\", or \"perfectly aligned\".\n"
    "  * ALWAYS frame the connection in terms of alignment, interest, and professional contribution. Use realistic, collaborative alignment expressions such as:\n"
    "    - \"This aligns with my professional goals of...\"\n"
    "    - \"I would like to contribute my systems engineering background to help scale...\"\n"
    "    - \"This presents a compelling opportunity to apply my [tech/stack/domain] background to...\"\n"
    "    - \"I am eager to help your team solve/develop...\"\n"
    "- Match the TONE of this example (style/mood only): \"A good monitoring system tells you what is wrong before a customer ever notices — contributing to that quiet kind of reliability is the part of operations I find most satisfying.\"\n\n"
    "## WHY ME? SECTION (HIGHLIGHT BULLETS)\n"
    "- Do NOT write dense paragraphs. Instead, provide exactly 3 punchy bullet points (using '- ') highlighting your absolute strongest matching technical achievements from the CV.\n"
    "- Provide concrete, specific proof with named systems and real numbers.\n"
    "- First bullet: Focus on taking end-to-end ownership of a project and shipping it to production.\n"
    "- Second bullet: Focus on cross-functional team collaboration to achieve an outcome.\n"
    "- Third bullet: Focus on domain-related/technical deep work.\n"
    "- LOGISTICS: After the 3 bullets in the \"Why me?\" section, seamlessly weave your availability, relocation willingness, and work-authorization facts (if provided) into a single, natural close sentence immediately following the 3 bullets."
)


def _context(
    jobspec: dict[str, Any],
    tailoring: dict[str, Any],
    master_cv: str,
) -> str:
    return (
        f"## Target job\n"
        f"Title: {jobspec.get('title')}\nCompany: {jobspec.get('company')}\n"
        f"Seniority: {jobspec.get('seniority')}\n"
        f"Must-haves: {', '.join(jobspec.get('must_haves', []))}\n"
        f"Nice-to-haves: {', '.join(jobspec.get('nice_to_haves', []))}\n"
        f"Stack: {', '.join(jobspec.get('stack', []))}\n\n"
        f"## Top-2 projects to feature (in this order) — re-angle each to the job\n"
        f"{_projects_block(tailoring['top_projects'], detailed=True)}\n\n"
        f"## Technical Skills (Consolidate these into exactly 3-4 high-signal categories/rows under ## Skills)\n{_skills_block(tailoring['skills'])}\n\n"
        f"## Master CV (source of truth — facts only)\n{master_cv}"
    )


def render_cv(
    jobspec: dict[str, Any],
    tailoring: dict[str, Any],
    master_cv: str,
    guide: str = "",
) -> tuple[str, str]:
    """Return (tagline, cv_body_markdown). The body starts at '## Experience';
    the name/contact header is composed by the template from profile.yml."""
    user = _context(jobspec, tailoring, master_cv) + (
        "\n\nWrite the tailored CV now."
    )
    system, _ = prompts.load("cv", _CV_SYSTEM_FALLBACK)
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
    guide: str = "",
    availability: str = "",
    relocation: str = "",
    custom_instructions: str = "",
) -> str:
    logistics = ""
    if availability or relocation:
        logistics = (
            "Logistics to weave naturally into the close (availability / relocation / work authorization):\n"
            f"{availability}\n{relocation}\n\n"
        )
    custom_block = ""
    if custom_instructions.strip():
        custom_block = (
            "## Custom Focus & Tailoring Instructions (High Priority - FOLLOW STRICTLY):\n"
            f"{custom_instructions.strip()}\n\n"
        )
    user = (
        f"## Target job\nTitle: {jobspec.get('title')}\n"
        f"Company: {jobspec.get('company')}\n\n"
        f"## Job posting\n{job_text.strip()}\n\n"
        f"## Candidate summary\n{profile_summary}\n\n"
        f"## Proof points (top projects — source facts; weave a couple in, do not list)\n"
        f"{_projects_block(tailoring['top_projects'], detailed=True)}\n\n"
        f"{logistics}"
        f"{custom_block}"
        f"{_cover_exemplars()}"
        "Write the tailored cover letter now."
    )
    system, _ = prompts.load("cover", _COVER_SYSTEM_FALLBACK)
    return llm.stream_text(
        system, user, max_tokens=llm.resolve()["max_tokens"]["cover"]
    ).strip() + "\n"


_TRANSLATE_SYSTEM_FALLBACK = (
    "You are a professional German translator for job-application documents. Translate the "
    "given Markdown into natural, professional German (using the \"Sie\" form).\n\n"
    "STRICT RULES:\n"
    "- Preserve the Markdown structure EXACTLY: the same headings (##/###), bullet lines, "
    "bold (**...**), and blank lines, in the same order.\n"
    "- Translate the CV section headings: Experience→Berufserfahrung, Education→Ausbildung, "
    "Projects→Projekte, Skills→Kenntnisse. For skills: Languages→Sprachen, "
    "Programming Languages→Programmiersprachen.\n"
    "- Keep proper nouns, employer names, job titles, product/tech names, project names, URLs, "
    "dates, and metrics UNCHANGED (do not translate or invent).\n"
    "- Keep 'English (fluent), Deutsch (A2)' rendered as 'Englisch (fließend), Deutsch (A2)'.\n"
    "- Output ONLY the translated Markdown — no preamble, no code fences, no commentary."
)


def translate_markdown(markdown: str, kind: str = "cv") -> str:
    """Translate tailored CV/cover Markdown into German, preserving structure.

    A faithful translation of already-approved English (no new facts) — feeds the
    bilingual LaTeX renderer (engine/latex.py). `kind` is 'cv' or 'cover'."""
    budget = llm.resolve()["max_tokens"].get("cv" if kind == "cv" else "cover", 8000)
    user = f"Translate this {kind} Markdown into German:\n\n{markdown.strip()}\n"
    system, _ = prompts.load("translate", _TRANSLATE_SYSTEM_FALLBACK)
    return llm.stream_text(system, user, max_tokens=budget).strip() + "\n"


_REVISE_SYSTEM = (
    "You are an expert resume writer and editor. Your task is to edit and revise the provided job-application Markdown document (either a CV or a Cover Letter) "
    "according to the user's feedback/revision instructions while maintaining compatibility with the target Job Description.\n"
    "STRICT RULES:\n"
    "- Read the current draft and the feedback instructions carefully.\n"
    "- Apply the revision instructions precisely, editing the text where necessary.\n"
    "- Ensure the tone, style, and structure remain professional, cohesive, and perfectly aligned with the Job Description.\n"
    "- Preserve the original Markdown structure, headings, bold styling, and formatting as much as possible.\n"
    "- Output ONLY the revised Markdown text — absolutely no preamble, no explanations, and no markdown code block fences (e.g., do not wrap in \`\`\`markdown ... \`\`\`)."
)


def revise_document(
    draft: str,
    revision_instructions: str,
    job_text: str,
    job_title: str,
    company: str,
    kind: str = "cover"
) -> str:
    """Revise an existing CV or cover letter markdown using natural language feedback."""
    user_prompt = (
        f"## Target Job\n"
        f"Title: {job_title}\n"
        f"Company: {company}\n\n"
        f"## Job Description\n"
        f"{job_text.strip()}\n\n"
        f"## Current Draft\n"
        f"{draft.strip()}\n\n"
        f"## Revision Instructions\n"
        f"{revision_instructions.strip()}\n\n"
        f"Apply the revision instructions to the draft and return the final, fully revised Markdown text."
    )
    budget = llm.resolve()["max_tokens"].get("cv" if kind == "cv" else "cover", 8000)
    return llm.stream_text(_REVISE_SYSTEM, user_prompt, max_tokens=budget).strip() + "\n"

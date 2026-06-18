"""Pure relevance ranking — the testable core of the tailoring engine.

No I/O, no network, no LLM. Everything here is a deterministic function of its
arguments so it can be exercised with fixtures in tests/test_rank.py.

A `JobSpec` is a plain dict:
    {
        "title": str,
        "company": str,
        "must_haves": [str, ...],
        "nice_to_haves": [str, ...],
        "stack": [str, ...],
        "keywords": [str, ...],
        "seniority": str,
    }

`projects` and `profile` mirror data/projects.yml and data/profile.yml.
"""

from __future__ import annotations

import re
from typing import Any

# Weight applied to each JobSpec field when a project/skill term matches it.
_FIELD_WEIGHTS = {
    "must_haves": 3.0,
    "stack": 2.0,
    "nice_to_haves": 1.5,
    "keywords": 1.0,
    "title": 1.0,
}

_TOKEN_RE = re.compile(r"[a-z0-9+#.]+")


def _tokens(text: str) -> set[str]:
    """Lowercase a string into a set of comparable tokens.

    Keeps a few code-ish characters (+ # .) so things like 'c++', 'c#', and
    'node.js' survive, then also adds the de-dotted form ('nodejs')."""
    if not text:
        return set()
    toks: set[str] = set()
    for m in _TOKEN_RE.findall(text.lower()):
        t = m.strip(".")
        if not t:
            continue
        toks.add(t)
        if "." in t:
            toks.add(t.replace(".", ""))
    return toks


def _phrase_tokens(values: list[str]) -> set[str]:
    """Token set for a list of phrases — both the whole phrase (spaces removed)
    and the individual words, so 'vector search' matches 'vector' and 'search'
    and 'vectorsearch'."""
    toks: set[str] = set()
    for v in values or []:
        toks |= _tokens(v)
        compact = re.sub(r"[^a-z0-9+#]", "", v.lower())
        if compact:
            toks.add(compact)
    return toks


def _project_tokens(project: dict[str, Any]) -> set[str]:
    toks: set[str] = set()
    toks |= _phrase_tokens(project.get("tags", []))
    toks |= _phrase_tokens(project.get("stack", []))
    toks |= _phrase_tokens(project.get("domains", []))
    toks |= _tokens(project.get("summary", ""))
    toks |= _tokens(project.get("name", ""))
    return toks


def score_project(project: dict[str, Any], jobspec: dict[str, Any]) -> float:
    """Relevance score of one project against a JobSpec (higher = better)."""
    ptoks = _project_tokens(project)
    score = 0.0
    for field, weight in _FIELD_WEIGHTS.items():
        value = jobspec.get(field, [])
        terms = [value] if isinstance(value, str) else (value or [])
        for term in terms:
            if _phrase_tokens([term]) & ptoks:
                score += weight
    return score


def rank_projects(
    projects: list[dict[str, Any]], jobspec: dict[str, Any], top: int = 3
) -> list[dict[str, Any]]:
    """Return the `top` most relevant projects, highest first.

    Ties (and the all-zero case where nothing matches) fall back to the
    catalogue order, so the result is always deterministic."""
    indexed = list(enumerate(projects))
    ranked = sorted(
        indexed,
        key=lambda pair: (-score_project(pair[1], jobspec), pair[0]),
    )
    return [proj for _, proj in ranked[:top]]


def order_items_by_jobspec(items: list[str], jobspec: dict[str, Any]) -> list[str]:
    """Reorder a skill line's items so JD must-haves/stack lead, preserving the
    original relative order within each band."""
    leading = _phrase_tokens(jobspec.get("must_haves", [])) | _phrase_tokens(
        jobspec.get("stack", [])
    )
    front, back = [], []
    for item in items:
        (front if _phrase_tokens([item]) & leading else back).append(item)
    return front + back


def _score_skill_group(group: dict[str, Any], jobspec: dict[str, Any]) -> float:
    gtoks = _phrase_tokens(group.get("tags", [])) | _phrase_tokens(
        group.get("items", [])
    )
    score = 0.0
    for field, weight in _FIELD_WEIGHTS.items():
        value = jobspec.get(field, [])
        terms = [value] if isinstance(value, str) else (value or [])
        for term in terms:
            if _phrase_tokens([term]) & gtoks:
                score += weight
    return score


def build_skills(
    profile: dict[str, Any], jobspec: dict[str, Any], max_groups: int = 3
) -> list[dict[str, str]]:
    """Build the ordered skills block per the house rule:

    1. Languages (spoken) — always first.
    2. Programming Languages — second.
    3. Up to `max_groups` job-tailored technical lines, each with items led by
       the JD's must-haves.

    Returns a list of {"label", "value"} lines.
    """
    lines: list[dict[str, str]] = [
        {"label": "Languages", "value": ", ".join(profile.get("languages", []))},
        {
            "label": "Programming Languages",
            "value": ", ".join(
                order_items_by_jobspec(profile.get("programming_languages", []), jobspec)
            ),
        },
    ]

    groups = profile.get("skill_groups", [])
    indexed = list(enumerate(groups))
    ranked = sorted(
        indexed, key=lambda pair: (-_score_skill_group(pair[1], jobspec), pair[0])
    )
    chosen = [g for i, g in ranked if _score_skill_group(g, jobspec) > 0][:max_groups]
    # If nothing scored (sparse JobSpec), fall back to the first groups in order.
    if not chosen:
        chosen = groups[:max_groups]

    for group in chosen:
        lines.append(
            {
                "label": group["name"],
                "value": ", ".join(order_items_by_jobspec(group["items"], jobspec)),
            }
        )
    return lines


def tailor(
    jobspec: dict[str, Any],
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    top_projects: int = 3,
    max_skill_groups: int = 3,
) -> dict[str, Any]:
    """Top-level pure transform: JobSpec + data -> the tailoring decisions a
    renderer needs (ranked projects + ordered skills block)."""
    return {
        "top_projects": rank_projects(projects, jobspec, top=top_projects),
        "skills": build_skills(profile, jobspec, max_groups=max_skill_groups),
    }

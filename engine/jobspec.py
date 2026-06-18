"""Job description -> structured JobSpec (Claude API).

A JobSpec is the contract between the LLM half and the pure ranking half
(engine/rank.py). Keep this module's output a plain dict matching JOBSPEC_SCHEMA.
"""

from __future__ import annotations

from typing import Any

from . import llm

JOBSPEC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Job title"},
        "company": {"type": "string", "description": "Company / org name, or empty"},
        "seniority": {
            "type": "string",
            "enum": ["junior", "mid", "senior", "lead", "unknown"],
        },
        "must_haves": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Hard requirements: skills/tech/experience the role requires",
        },
        "nice_to_haves": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Preferred / bonus skills",
        },
        "stack": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Concrete technologies named in the posting",
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Salient domain terms (e.g. 'RAG', 'event-driven', 'fintech')",
        },
    },
    "required": [
        "title",
        "company",
        "seniority",
        "must_haves",
        "nice_to_haves",
        "stack",
        "keywords",
    ],
    "additionalProperties": False,
}

_SYSTEM = (
    "You extract a structured JobSpec from a job posting. Be faithful to the "
    "posting: do not invent requirements. Normalize technology names to their "
    "common form (e.g. 'Golang' -> 'Go', 'k8s' -> 'Kubernetes'). Put hard "
    "requirements in must_haves and preferred ones in nice_to_haves."
)


def extract_jobspec(job_text: str) -> dict[str, Any]:
    """Extract a JobSpec dict from raw job-posting text."""
    user = f"Job posting:\n\n{job_text.strip()}\n\nExtract the JobSpec."
    return llm.structured_json(_SYSTEM, user, JOBSPEC_SCHEMA, max_tokens=2000)

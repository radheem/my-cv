"""Core selection engine for static CV variants."""

from __future__ import annotations

import logging
import re
from typing import Any

from engine.shared import config
from engine.domains.tailoring import llm, rank

log = logging.getLogger("cv-tailor-variants")


_VARIANT_SELECTION_SYSTEM = (
    "You are an expert career strategist and technical recruiter. Your task is to analyze a "
    "job description and select the single most relevant domain cluster for classifying "
    "this job. You must strictly select one of the provided cluster names, and provide a "
    "concise, one-sentence summary of the job's core technical focus."
)

VARIANT_SELECTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "A concise, one-sentence summary of the job's core technical focus.",
        },
        "cluster": {
            "type": "string",
            "description": "The exact name of the best matching taxonomy cluster from the available choices.",
        },
    },
    "required": ["summary", "cluster"],
    "additionalProperties": False,
}


def match_cluster_via_llm(
    job_text: str,
    taxonomy: dict[str, Any],
) -> tuple[str, str]:
    """Analyze the job description with the LLM and match it to a taxonomy cluster."""
    from engine.domains.tailoring import prompts
    
    clusters = taxonomy.get("clusters", {})
    available_choices = list(clusters.keys())
    
    # Format choice descriptions for user prompt
    choices_text = "\n".join(
        f"- {name}: Focuses on tags {spec.get('tags', [])}"
        for name, spec in clusters.items()
    )
    
    user = (
        f"Available taxonomy clusters to select from:\n"
        f"{choices_text}\n\n"
        f"Job Description:\n"
        f"```\n{job_text.strip()}\n```\n\n"
        f"Analyze the job, summarize its technical focus in one sentence, and select the single "
        f"best matching cluster from the available choices (choose from: {', '.join(available_choices)})."
    )
    
    system, _ = prompts.load("variant", _VARIANT_SELECTION_SYSTEM)
    max_tokens = llm.resolve()["max_tokens"].get("variant", 1500)
    
    res = llm.structured_json(system, user, VARIANT_SELECTION_SCHEMA, max_tokens=max_tokens)
    
    summary = res.get("summary", "").strip()
    cluster = res.get("cluster", "").strip()
    
    # If cluster is not one of the available ones, fallback safely
    if cluster not in available_choices:
        log.warning(f"LLM returned invalid cluster '{cluster}'. Expected one of {available_choices}. Finding closest match...")
        # Simple case-insensitive matching fallback
        for name in available_choices:
            if name.lower() == cluster.lower():
                cluster = name
                break
        else:
            # Fallback to the first available choice
            cluster = available_choices[0] if available_choices else "platform-engineer"
            
    return summary, cluster


def select_best_cv_variant(
    jobspec: dict[str, Any],
    job_text: str,
    taxonomy: dict[str, Any],
    aliases: dict[str, str] | None = None,
) -> str:
    """Select the best CV variant filename for a target job.

    Uses an LLM to analyze the job description, summarize it, and match it to a taxonomy cluster.
    """
    # 1. Load config and variant mappings
    cfg = config.load()
    cv_variants = cfg.get("tailoring", {}).get("cv_variants", {})
    if not cv_variants:
        raise ValueError("No cv_variants mapping found in configuration.")

    # 2. Match cluster via LLM
    summary, chosen_cluster = match_cluster_via_llm(job_text, taxonomy)
    log.info(f"LLM Summary: {summary}")
    
    # Map the cluster to the variant filename
    chosen_file = cv_variants.get(chosen_cluster)
    if not chosen_file:
        # Fallback if the cluster isn't mapped
        log.warning(f"Chosen cluster '{chosen_cluster}' has no mapped CV variant. Fallback to platform-cloud-native.")
        chosen_file = cv_variants.get("platform-cloud-native", "platform-cloud-native.md")
        
    log.info(f"LLM-based CV variant selected: {chosen_file} for cluster '{chosen_cluster}'")
    return chosen_file


def extract_projects_from_cv(cv_text: str, projects_catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Parse project names from CV and return matching project dicts from the catalog."""
    # Find bullet points under ## Projects
    parts = re.split(r"(?m)^## Projects", cv_text)
    if len(parts) < 2:
        return []
    proj_section = re.split(r"(?m)^## ", parts[1])[0]
    
    # Extract bold titles, e.g. - **IRS Platform (Stealth)** — ...
    names = re.findall(r"(?m)^-\s*\*\*([^*]+)\*\*", proj_section)
    matched = []
    for name in names:
        name_clean = name.strip().lower()
        # Find matching project in catalog
        for p in projects_catalog:
            p_name = p.get("name", "").strip().lower()
            if p_name in name_clean or name_clean in p_name:
                matched.append(p)
                break
    return matched

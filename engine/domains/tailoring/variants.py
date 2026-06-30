"""Core selection engine for static CV variants."""

from __future__ import annotations

import logging
import re
from typing import Any

from engine.shared import config
from engine.domains.tailoring import llm, rank

log = logging.getLogger("cv-tailor-variants")


def score_job_clusters(
    jobspec: dict[str, Any],
    taxonomy: dict[str, Any] | None = None,
    aliases: dict[str, str] | None = None,
) -> dict[str, float]:
    """Calculate match scores for each cluster against the jobspec.

    The score is the weighted overlap of jobspec terms with cluster tags.
    """
    if not taxonomy:
        return {}

    # Invert aliases if not already done
    aliases_flat = rank.invert_aliases(taxonomy.get("aliases", {})) if aliases is None else aliases

    scores: dict[str, float] = {}
    for cl_name, cl_spec in taxonomy.get("clusters", {}).items():
        # Get canonical cluster tags
        cl_tags = rank._phrase_tokens(cl_spec.get("tags", []), aliases_flat)
        score = 0.0
        # Field weights match rank._FIELD_WEIGHTS
        weights = rank._FIELD_WEIGHTS
        for field, weight in weights.items():
            field_toks = rank._phrase_tokens(rank._as_terms(jobspec.get(field, [])), aliases_flat)
            overlap = cl_tags & field_toks
            score += len(overlap) * weight
        scores[cl_name] = score

    return scores


def select_best_cv_variant(
    jobspec: dict[str, Any],
    job_text: str,
    taxonomy: dict[str, Any],
    aliases: dict[str, str] | None = None,
) -> str:
    """Select the best CV variant filename for a target job.

    Uses deterministic weighted overlap first. If there is a tie among the top-scoring
    clusters, calls the LLM as a tie-breaker.
    """
    # 1. Load config and variant mappings
    cfg = config.load()
    cv_variants = cfg.get("tailoring", {}).get("cv_variants", {})
    if not cv_variants:
        raise ValueError("No cv_variants mapping found in configuration.")

    # 2. Score job against each cluster
    aliases_flat = rank.invert_aliases(taxonomy.get("aliases", {})) if aliases is None else aliases
    scores = score_job_clusters(jobspec, taxonomy, aliases_flat)

    if not scores:
        # Fallback to general platform-cloud-native if no taxonomy defined
        log.warning("No taxonomy scores calculated. Defaulting to platform-cloud-native.")
        return cv_variants.get("platform-cloud-native", "platform-cloud-native.md")

    # Filter scores to only include those that actually have a variant mapped
    valid_scores = {cl: val for cl, val in scores.items() if cl in cv_variants}
    if not valid_scores:
        raise ValueError("None of the scored taxonomy clusters have a mapped CV variant.")

    # 3. Find the maximum score and all candidates with that score
    max_score = max(valid_scores.values())
    
    # If the max score is 0, we have zero matches, let's treat it as a tie of all valid options
    if max_score == 0.0:
        candidates = list(valid_scores.keys())
    else:
        candidates = [cl for cl, score in valid_scores.items() if score == max_score]

    # 4. Single winner -> deterministic copy
    if len(candidates) == 1:
        chosen_cluster = candidates[0]
        chosen_file = cv_variants[chosen_cluster]
        log.info(f"Deterministic CV variant selected: {chosen_file} for cluster '{chosen_cluster}' (score: {max_score})")
        return chosen_file

    # 5. Tie-breaker -> call LLM with only the tied options
    log.info(f"CV Selection tie detected between clusters: {candidates} (score: {max_score}). Resolving with LLM...")
    tied_options = {cl: cv_variants[cl] for cl in candidates}
    
    system_prompt = (
        "You are an expert recruitment assistant and career strategist.\n"
        "Your task is to analyze the target Job Description and select the SINGLE best CV variant "
        "from the provided options that maximizes the candidate's relevance for this role.\n"
        "STRICT RULES:\n"
        "- Output ONLY the exact filename of the chosen variant (e.g. ml-ai.md).\n"
        "- No preamble, no explanation, no markdown formatting (no backticks, no quotes)."
    )

    options_text = "\n".join(f"- {fname} (specializing in {cl})" for cl, fname in tied_options.items())
    user_prompt = (
        f"Target Job Description:\n"
        f"```\n{job_text.strip()}\n```\n\n"
        f"Available CV Variant Options:\n"
        f"{options_text}\n\n"
        f"Select the single best variant filename from the options above. Output ONLY the filename."
    )

    try:
        raw_output = llm.stream_text(system_prompt, user_prompt, max_tokens=100)
        # Sanitize output (remove quotes, markdown backticks, and whitespace)
        chosen_file = re.sub(r"[`'\"\\n\\r]", "", raw_output).strip()
        
        # Validate that the LLM returned one of our tied options
        if chosen_file not in tied_options.values():
            raise ValueError(f"LLM returned invalid variant name '{chosen_file}'. Expected one of: {list(tied_options.values())}")
            
        log.info(f"LLM successfully resolved tie-breaker. Selected: {chosen_file}")
        return chosen_file
    except Exception as e:
        log.error(f"LLM tie-breaker failed: {str(e)}")
        # Abort and alert (as specified by human-in-the-loop choices)
        raise SystemExit(f"CRITICAL ERROR: CV selection tie-breaker failed: {str(e)}")


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

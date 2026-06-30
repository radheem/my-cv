"""Core engine for composable clustered job analysis and keyword gap checks."""

from __future__ import annotations

import logging
import re
import datetime
from typing import Any

from engine.shared.db import get_conn
from engine.domains.tailoring import rank

log = logging.getLogger("cv-tailor-analysis")

STOP_WORDS = {
    # English stop words
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about",
    "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up",
    "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
    # German stop words
    "ich", "mich", "mir", "mein", "meine", "wir", "uns", "unser", "unsere", "du", "dich", "dir", "dein", "deine",
    "ihr", "euch", "ihre", "er", "ihn", "ihm", "sein", "seine", "sie", "es", "ihnen", "was", "wer", "wie", "wo",
    "dies", "dieser", "diese", "dieses", "das", "der", "die", "den", "dem", "des", "ein", "eine", "eines", "einem",
    "einen", "einer", "und", "oder", "aber", "weil", "wenn", "als", "von", "zu", "an", "mit", "für", "über", "unter",
    "nach", "vor", "bei", "aus", "durch", "ohne", "gegen", "zwischen", "während", "sehr", "selbst", "auch", "noch",
    "nur", "schon", "jetzt", "immer", "nie", "alle", "viele", "manche", "andere", "nicht", "kein", "keine",
    # Generic JD noise terms
    "team", "experience", "work", "role", "years", "candidate", "development", "company", "software", "engineering",
    "skills", "knowledge", "design", "building", "systems", "processes", "environment", "solutions", "services",
    "technologies", "technology", "opportunity", "position", "ability", "requirements", "responsibilities", "project",
    "projects", "business", "applications", "data", "cloud", "platform", "infrastructure", "backend", "developer", "engineer",
    "expert", "specialist", "management", "tools", "support", "working", "tasks", "focus", "product", "products", "technical",
    "highly", "strong", "excellent", "good", "fluent", "german", "english", "deutsch", "germany", "location", "hybrid", "remote",
    "full-time", "part-time", "flexible", "benefits", "salary", "contract", "visa", "sponsorship"
}


def get_jobs_for_cluster(cluster_key: str, taxonomy: dict[str, Any], limit: int = 15) -> list[dict[str, Any]]:
    """Retrieve all saved jobs from DuckDB and dynamically filter the ones matching the target cluster."""
    aliases_flat = rank.invert_aliases(taxonomy.get("aliases", {}))
    cluster_spec = taxonomy.get("clusters", {}).get(cluster_key, {})
    if not cluster_spec:
        log.warning(f"Requested cluster '{cluster_key}' not found in taxonomy specification.")
        return []

    cluster_tags = rank._phrase_tokens(cluster_spec.get("tags", []), aliases_flat)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT slug, company, title, description, url FROM jobs WHERE description IS NOT NULL")
            rows = cur.fetchall()

    scored_jobs = []
    for r in rows:
        desc = r["description"] or ""
        tokens = rank._tokens(desc, aliases_flat)
        # Match score is intersection count of cluster tags with job tokens
        score = len(cluster_tags & tokens)
        if score > 0:
            scored_jobs.append({
                "slug": r["slug"],
                "company": r["company"],
                "title": r["title"],
                "description": desc,
                "url": r["url"],
                "score": score
            })

    # Sort by overlap score descending
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    return scored_jobs[:limit]


def _get_term_category(term: str, profile: dict[str, Any]) -> str:
    """Classify a given technical term using the profile definitions."""
    term_lower = term.lower()

    # 1. Check programming languages
    for lang in profile.get("programming_languages", []):
        if lang.lower() == term_lower:
            return "programming_languages"

    # 2. Check skill groups
    for group in profile.get("skill_groups", []):
        group_name = group.get("name", "")
        items_lower = [it.lower() for it in group.get("items", [])]
        tags_lower = [t.lower() for t in group.get("tags", [])]

        if term_lower in items_lower or term_lower in tags_lower:
            if "Database" in group_name or "Persistence" in group_name:
                return "databases_persistence"
            elif "Cloud-Native" in group_name or "Infra" in group_name:
                return "platforms_infrastructure"
            elif "Observability" in group_name or "Reliability" in group_name:
                return "observability_reliability"
            else:
                return "libraries_frameworks"

    return "libraries_frameworks"


def extract_cluster_signals(
    cluster_key: str,
    taxonomy: dict[str, Any],
    profile: dict[str, Any],
    limit: int = 15,
    noise_threshold: float = 0.15
) -> dict[str, Any]:
    """Execute Stage 1 Extractor.

    Retrieves cluster jobs, runs taxonomy-aware document frequency (DF) counting,
    and returns a standardized JSON payload with domain signals and unmapped market terms.
    """
    jobs = get_jobs_for_cluster(cluster_key, taxonomy, limit=limit)
    num_jobs = len(jobs)

    payload = {
        "analysis_metadata": {
            "target_cluster": cluster_key,
            "analyzed_jobs_count": num_jobs,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "noise_threshold": noise_threshold
        },
        "domain_signals": {
            "programming_languages": [],
            "libraries_frameworks": [],
            "databases_persistence": [],
            "platforms_infrastructure": [],
            "observability_reliability": []
        },
        "thematic_phrases": [],
        "unmapped_market_terms": []
    }

    if num_jobs == 0:
        return payload

    aliases_flat = rank.invert_aliases(taxonomy.get("aliases", {}))

    # All known terms in profile and taxonomy
    known_terms = set()
    for lang in profile.get("programming_languages", []):
        known_terms.add(lang.lower())
    for group in profile.get("skill_groups", []):
        for item in group.get("items", []):
            known_terms.add(item.lower())
        for tag in group.get("tags", []):
            known_terms.add(tag.lower())
    for canonical, variants in taxonomy.get("aliases", {}).items():
        known_terms.add(canonical.lower())
        for var in variants:
            known_terms.add(var.lower())

    # Document frequency counts
    term_doc_counts: dict[str, int] = {}
    unmapped_doc_counts: dict[str, int] = {}

    for j in jobs:
        desc = j["description"]
        tokens = rank._tokens(desc, aliases_flat)
        raw_tokens = rank._tokens(desc, None)

        # Count mapped / known terms
        seen_known = set()
        for t in tokens:
            if t in known_terms:
                seen_known.add(t)
        for t in seen_known:
            term_doc_counts[t] = term_doc_counts.get(t, 0) + 1

        # Count unmapped / raw market terms
        seen_unmapped = set()
        for t in raw_tokens:
            if t not in known_terms and t not in STOP_WORDS and len(t) >= 3 and t.isalnum():
                seen_unmapped.add(t)
        for t in seen_unmapped:
            unmapped_doc_counts[t] = unmapped_doc_counts.get(t, 0) + 1

    # Format domain signals
    category_map: dict[str, list[dict[str, Any]]] = {
        "programming_languages": [],
        "libraries_frameworks": [],
        "databases_persistence": [],
        "platforms_infrastructure": [],
        "observability_reliability": []
    }

    # Find canonical display names for terms
    display_names = {}
    # Load display names from profile
    for lang in profile.get("programming_languages", []):
        display_names[lang.lower()] = lang
    for group in profile.get("skill_groups", []):
        for item in group.get("items", []):
            display_names[item.lower()] = item

    for t, count in term_doc_counts.items():
        freq = count / num_jobs
        if freq >= noise_threshold:
            canonical_name = display_names.get(t, t.capitalize())
            category = _get_term_category(t, profile)
            
            # Check if it is a core cluster tag
            cluster_tags = [tag.lower() for tag in taxonomy.get("clusters", {}).get(cluster_key, {}).get("tags", [])]
            is_core = t in cluster_tags

            category_map[category].append({
                "term": canonical_name,
                "frequency": round(freq, 2),
                "is_core": is_core
            })

    # Sort each category by frequency descending
    for cat in payload["domain_signals"].keys():
        category_map[cat].sort(key=lambda x: x["frequency"], reverse=True)
        payload["domain_signals"][cat] = category_map[cat]

    # Format unmapped market terms
    unmapped_list = []
    for t, count in unmapped_doc_counts.items():
        freq = count / num_jobs
        if freq >= noise_threshold:
            unmapped_list.append({
                "term": t,
                "frequency": round(freq, 2),
                "suggested_action": "add_to_taxonomy"
            })
    unmapped_list.sort(key=lambda x: x["frequency"], reverse=True)
    payload["unmapped_market_terms"] = unmapped_list[:10]  # top 10 unmapped terms

    # Extract high-frequency thematic sentences as thematic phrases
    thematic_candidates = []
    for j in jobs:
        desc = j["description"]
        sentences = re.split(r"(?<=[.!?])\s+", desc)
        for s in sentences:
            s_clean = s.strip()
            # Look for rich, engineering-focused sentences containing core cluster tags
            if len(s_clean) > 50 and len(s_clean) < 180:
                s_tokens = rank._tokens(s_clean, aliases_flat)
                cluster_tags = {tag.lower() for tag in taxonomy.get("clusters", {}).get(cluster_key, {}).get("tags", [])}
                if len(s_tokens & cluster_tags) >= 2:
                    thematic_candidates.append(s_clean)

    # De-duplicate and select top 3 distinct thematic phrases
    unique_phrases = []
    for p in thematic_candidates:
        if p not in unique_phrases:
            # Simple heuristic: prioritize phrases with distinct word lengths
            if not any(rank._tokens(p, None) & rank._tokens(existing, None) for existing in unique_phrases):
                unique_phrases.append(p)
        if len(unique_phrases) >= 3:
            break
    payload["thematic_phrases"] = unique_phrases

    return payload


def gap_analyzer(analysis_json: dict[str, Any], cv_variant_content: str) -> dict[str, Any]:
    """Execute Consumer A.

    Compares extracted domain signals against a chosen CV variant's markdown
    to pinpoint missing high-frequency keywords.
    """
    cv_tokens = rank._tokens(cv_variant_content, None)

    gap_report = {
        "target_cluster": analysis_json.get("analysis_metadata", {}).get("target_cluster", ""),
        "total_signals_checked": 0,
        "matching_signals": [],
        "missing_signals": []
    }

    # Extract all terms from Stage 1 categories
    all_signals = []
    for category, signals in analysis_json.get("domain_signals", {}).items():
        for sig in signals:
            all_signals.append({
                "term": sig["term"],
                "frequency": sig["frequency"],
                "category": category,
                "is_core": sig["is_core"]
            })

    gap_report["total_signals_checked"] = len(all_signals)

    for sig in all_signals:
        term = sig["term"]
        term_lower = term.lower()
        
        # Check if the term exists in the CV
        # Simple sub-token check or exact word boundary match
        pattern = r"\b" + re.escape(term_lower) + r"\b"
        matches_cv = re.search(pattern, cv_variant_content.lower()) is not None

        sig_entry = {
            "term": term,
            "frequency": sig["frequency"],
            "category": sig["category"]
        }

        if matches_cv:
            gap_report["matching_signals"].append(sig_entry)
        else:
            gap_report["missing_signals"].append(sig_entry)

    # Sort reports by frequency descending
    gap_report["matching_signals"].sort(key=lambda x: x["frequency"], reverse=True)
    gap_report["missing_signals"].sort(key=lambda x: x["frequency"], reverse=True)

    return gap_report


def taxonomy_sync(analysis_json: dict[str, Any], taxonomy: dict[str, Any]) -> list[dict[str, Any]]:
    """Execute Consumer B.

    Filters unmapped market terms and returns formatted structure with suggestions.
    """
    suggestions = []
    for term_entry in analysis_json.get("unmapped_market_terms", []):
        freq = term_entry["frequency"]
        term = term_entry["term"]
        # Only suggest terms appearing in >15% of target JDs
        if freq >= 0.15:
            suggestions.append({
                "term": term,
                "frequency": freq,
                "suggested_action": f"Add '{term}' to aliases or tags under appropriate cluster in taxonomy.yml"
            })
    return suggestions

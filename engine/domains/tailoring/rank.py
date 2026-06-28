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

Two optional inputs steer ranking without changing the default behavior:

  * `taxonomy` (data/taxonomy.yml) — a controlled vocabulary: an `aliases` map
    (variant token -> canonical, e.g. k8s -> kubernetes) and `clusters` (named
    groups of canonical tags). Used to canonicalize tokens before matching and to
    classify both projects and job postings into shared clusters.
  * `ranking` (data/ranking.yml) — user knobs: `field_weights`, `cluster_affinity`,
    `top_projects`, `max_skill_groups`, `prefer_clusters`, `pinned`, `excluded`.

With neither supplied, scoring is byte-for-byte identical to the original
token-overlap ranker (every new parameter is default-inert).
"""

from __future__ import annotations

import re
from typing import Any

# Default weight applied to each JobSpec field when a project/skill term matches
# it. Overridable per-user via ranking.yml `field_weights`.
_FIELD_WEIGHTS = {
    "must_haves": 3.0,
    "stack": 2.0,
    "nice_to_haves": 1.5,
    "keywords": 1.0,
    "title": 1.0,
}

# Additive nudge per project that sits in a user's `prefer_clusters`.
_PREFER_CLUSTER_NUDGE = 0.5

_TOKEN_RE = re.compile(r"[a-z0-9+#.]+")


def _as_terms(value: Any) -> list[str]:
    """A JobSpec field is either a scalar (title) or a list — normalize to list."""
    return [value] if isinstance(value, str) else (value or [])


def invert_aliases(aliases: dict[str, list[str]] | None) -> dict[str, str]:
    """Turn a taxonomy `aliases` map (canonical -> [variants]) into a flat
    variant->canonical lookup. Raises on a variant claimed by two canonicals so
    authoring mistakes surface at generation time, not as silent mis-ranking."""
    out: dict[str, str] = {}
    for canonical, variants in (aliases or {}).items():
        for variant in variants or []:
            v = variant.lower()
            if v in out and out[v] != canonical:
                raise ValueError(
                    f"alias '{v}' maps to both '{out[v]}' and '{canonical}'"
                )
            out[v] = canonical
    return out


def _tokens(text: str, aliases: dict[str, str] | None = None) -> set[str]:
    """Lowercase a string into a set of comparable tokens.

    Keeps a few code-ish characters (+ # .) so things like 'c++', 'c#', and
    'node.js' survive, then also adds the de-dotted form ('nodejs'). When an
    `aliases` map is given, canonical forms are *added* (e.g. 'k8s' -> also
    'kubernetes') — additively, so the original token is never lost."""
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
    if aliases:
        toks |= {aliases[t] for t in toks if t in aliases}
    return toks


def _phrase_tokens(values: list[str], aliases: dict[str, str] | None = None) -> set[str]:
    """Token set for a list of phrases — both the whole phrase (spaces removed)
    and the individual words, so 'vector search' matches 'vector' and 'search'
    and 'vectorsearch'. Canonicalizes via `aliases` when supplied."""
    toks: set[str] = set()
    for v in values or []:
        toks |= _tokens(v, aliases)
        compact = re.sub(r"[^a-z0-9+#]", "", v.lower())
        if compact:
            toks.add(compact)
            if aliases and compact in aliases:
                toks.add(aliases[compact])
    return toks


def _project_tokens(project: dict[str, Any], aliases: dict[str, str] | None = None) -> set[str]:
    toks: set[str] = set()
    toks |= _phrase_tokens(project.get("tags", []), aliases)
    toks |= _phrase_tokens(project.get("stack", []), aliases)
    toks |= _phrase_tokens(project.get("domains", []), aliases)
    toks |= _tokens(project.get("summary", ""), aliases)
    toks |= _tokens(project.get("name", ""), aliases)
    return toks


def _clusters_for(toks: set[str], taxonomy: dict[str, Any] | None,
                  aliases: dict[str, str] | None) -> set[str]:
    """Clusters whose tag set intersects an (already canonicalized) token set."""
    out: set[str] = set()
    for name, spec in (taxonomy or {}).get("clusters", {}).items():
        if _phrase_tokens(spec.get("tags", []), aliases) & toks:
            out.add(name)
    return out


def project_clusters(project: dict[str, Any], taxonomy: dict[str, Any] | None = None,
                     aliases: dict[str, str] | None = None) -> set[str]:
    """A project's clusters — its explicit `clusters:` override if present, else
    derived from its tags via the taxonomy."""
    explicit = project.get("clusters")
    if explicit:
        return set(explicit)
    return _clusters_for(_project_tokens(project, aliases), taxonomy, aliases)


def job_clusters(jobspec: dict[str, Any], taxonomy: dict[str, Any] | None = None,
                 aliases: dict[str, str] | None = None) -> list[str]:
    """Classify a job posting into clusters from its JobSpec terms. Deterministic
    (sorted) so it can be written into a hub's front matter and diffed in git."""
    jtoks: set[str] = set()
    for field in _FIELD_WEIGHTS:
        jtoks |= _phrase_tokens(_as_terms(jobspec.get(field, [])), aliases)
    return sorted(_clusters_for(jtoks, taxonomy, aliases))


def score_project(
    project: dict[str, Any],
    jobspec: dict[str, Any],
    *,
    field_weights: dict[str, float] | None = None,
    aliases: dict[str, str] | None = None,
    taxonomy: dict[str, Any] | None = None,
    cluster_affinity: float = 0.0,
    prefer_clusters: tuple[str, ...] = (),
    job_clusters_set: frozenset[str] = frozenset(),
) -> float:
    """Relevance score of one project against a JobSpec (higher = better).

    score = (field-weight token overlap + cluster affinity) * project weight.
    With the defaults (no aliases/taxonomy, cluster_affinity=0, weight=1.0) this
    reduces exactly to the original token-overlap score."""
    weights = field_weights or _FIELD_WEIGHTS
    ptoks = _project_tokens(project, aliases)

    base = 0.0
    for field, weight in weights.items():
        for term in _as_terms(jobspec.get(field, [])):
            if _phrase_tokens([term], aliases) & ptoks:
                base += weight

    cluster = 0.0
    if cluster_affinity and taxonomy:
        pcl = project_clusters(project, taxonomy, aliases)
        cluster = cluster_affinity * len(pcl & job_clusters_set)
        if prefer_clusters:
            cluster += _PREFER_CLUSTER_NUDGE * len(pcl & set(prefer_clusters))

    return (base + cluster) * float(project.get("weight", 1.0))


def rank_projects(
    projects: list[dict[str, Any]],
    jobspec: dict[str, Any],
    top: int = 3,
    *,
    field_weights: dict[str, float] | None = None,
    aliases: dict[str, str] | None = None,
    taxonomy: dict[str, Any] | None = None,
    cluster_affinity: float = 0.0,
    prefer_clusters: tuple[str, ...] = (),
    pinned: tuple[str, ...] = (),
    excluded: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    """Return the `top` most relevant projects, highest first.

    `excluded` ids are removed entirely; `pinned` ids are floated to the front
    (still in score order among themselves). Ties — and the all-zero case where
    nothing matches — fall back to catalogue order, so the result is always
    deterministic."""
    jcl = (
        frozenset(job_clusters(jobspec, taxonomy, aliases))
        if (cluster_affinity and taxonomy)
        else frozenset()
    )
    excluded_set, pinned_set = set(excluded), set(pinned)
    pool = [(i, p) for i, p in enumerate(projects) if p.get("id") not in excluded_set]
    ranked = sorted(
        pool,
        key=lambda pair: (
            -score_project(
                pair[1], jobspec,
                field_weights=field_weights, aliases=aliases, taxonomy=taxonomy,
                cluster_affinity=cluster_affinity, prefer_clusters=prefer_clusters,
                job_clusters_set=jcl,
            ),
            pair[0],
        ),
    )
    pins = [p for _, p in ranked if p.get("id") in pinned_set]
    rest = [p for _, p in ranked if p.get("id") not in pinned_set]
    return (pins + rest)[:top]


def order_items_by_jobspec(
    items: list[str], jobspec: dict[str, Any], aliases: dict[str, str] | None = None
) -> list[str]:
    """Reorder a skill line's items so JD must-haves/stack lead, preserving the
    original relative order within each band."""
    leading = _phrase_tokens(jobspec.get("must_haves", []), aliases) | _phrase_tokens(
        jobspec.get("stack", []), aliases
    )
    front, back = [], []
    for item in items:
        (front if _phrase_tokens([item], aliases) & leading else back).append(item)
    return front + back


def _score_skill_group(
    group: dict[str, Any],
    jobspec: dict[str, Any],
    field_weights: dict[str, float] | None = None,
    aliases: dict[str, str] | None = None,
) -> float:
    weights = field_weights or _FIELD_WEIGHTS
    gtoks = _phrase_tokens(group.get("tags", []), aliases) | _phrase_tokens(
        group.get("items", []), aliases
    )
    score = 0.0
    for field, weight in weights.items():
        for term in _as_terms(jobspec.get(field, [])):
            if _phrase_tokens([term], aliases) & gtoks:
                score += weight
    return score


def build_skills(
    profile: dict[str, Any],
    jobspec: dict[str, Any],
    max_groups: int = 3,
    *,
    field_weights: dict[str, float] | None = None,
    aliases: dict[str, str] | None = None,
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
                order_items_by_jobspec(
                    profile.get("programming_languages", []), jobspec, aliases
                )
            ),
        },
    ]

    groups = profile.get("skill_groups", [])
    indexed = list(enumerate(groups))
    ranked = sorted(
        indexed,
        key=lambda pair: (
            -_score_skill_group(pair[1], jobspec, field_weights, aliases),
            pair[0],
        ),
    )
    chosen = [
        g for i, g in ranked
        if _score_skill_group(g, jobspec, field_weights, aliases) > 0
    ][:max_groups]
    # If nothing scored (sparse JobSpec), fall back to the first groups in order.
    if not chosen:
        chosen = groups[:max_groups]

    for group in chosen:
        lines.append(
            {
                "label": group["name"],
                "value": ", ".join(
                    order_items_by_jobspec(group["items"], jobspec, aliases)
                ),
            }
        )
    return lines


def tailor(
    jobspec: dict[str, Any],
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    top_projects: int = 3,
    max_skill_groups: int = 3,
    *,
    taxonomy: dict[str, Any] | None = None,
    ranking: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Top-level pure transform: JobSpec + data (+ optional taxonomy/ranking
    config) -> the tailoring decisions a renderer needs (ranked projects +
    ordered skills block). With no taxonomy/ranking it matches the original
    behavior exactly."""
    cfg = ranking or {}
    field_weights = cfg.get("field_weights") or _FIELD_WEIGHTS
    aliases = invert_aliases((taxonomy or {}).get("aliases", {})) if taxonomy else {}
    cluster_affinity = float(cfg.get("cluster_affinity", 0.0))
    top_projects = int(cfg.get("top_projects", top_projects))
    max_skill_groups = int(cfg.get("max_skill_groups", max_skill_groups))
    prefer_clusters = tuple(cfg.get("prefer_clusters") or ())
    pinned = tuple(cfg.get("pinned") or ())
    excluded = tuple(cfg.get("excluded") or ())

    return {
        "top_projects": rank_projects(
            projects, jobspec, top=top_projects,
            field_weights=field_weights, aliases=aliases, taxonomy=taxonomy,
            cluster_affinity=cluster_affinity, prefer_clusters=prefer_clusters,
            pinned=pinned, excluded=excluded,
        ),
        "skills": build_skills(
            profile, jobspec, max_groups=max_skill_groups,
            field_weights=field_weights, aliases=aliases,
        ),
    }

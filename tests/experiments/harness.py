"""Shared core for the cv-tailor benchmark — config, case loading, pure scoring.

Everything in this module is import-safe and (for the scoring functions) pure and
network-free, so `tests/test_experiments.py` can exercise it without a model. The
network-touching generation lives in `run.py`; the LLM judge lives in `evaluate.py`.

Layout produced/consumed:

    tests/experiments/
      split.yml                      train/test slug lists
      cases/<slug>/job-description.txt   input posting
      cases/<slug>/gold/cv.md            gold CV (engine-shape Markdown)
      cases/<slug>/gold/cover-letter.md  gold cover-letter body
      cases/<slug>/meta.yml              split, company, role, recipient
      outputs/<slug>/...                 generated artifacts   (gitignored)
      results/...                        scores + report       (gitignored)
"""

from __future__ import annotations

import dataclasses
import pathlib
import re
import sys
from typing import Any

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent                      # repo root (radr-cv/)
CASES = HERE / "cases"
OUTPUTS = HERE / "outputs"
RESULTS = HERE / "results"

# Make `from engine import ...` work when run as a plain script (python run.py).
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --------------------------------------------------------------------------- #
# Provider config — defaults target the lab Ollama box + qwen3.6:35b.          #
# Override any of these via the same CV_TAILOR_* env vars the engine reads.     #
# --------------------------------------------------------------------------- #
DEFAULT_OLLAMA_BASE_URL = "http://genai.ltc.hsnet:11434/v1"
DEFAULT_MODEL = "qwen3.6:35b"

REQUIRED_CV_SECTIONS = ("Experience", "Education", "Projects", "Skills")

# Tokens that say nothing about skill *coverage* — excluded from that metric.
_SKILL_STOPWORDS = {
    "languages", "language", "programming", "english", "fluent", "deutsch", "a2",
    "and", "the", "with", "for", "of", "to", "in", "on", "a", "an", "skills",
}


def ollama_env(model: str | None = None, base_url: str | None = None) -> dict[str, str]:
    """Env mapping that selects the Ollama backend for the engine."""
    return {
        "CV_TAILOR_PROVIDER": "ollama",
        "CV_TAILOR_MODEL": model or DEFAULT_MODEL,
        "CV_TAILOR_OLLAMA_BASE_URL": base_url or DEFAULT_OLLAMA_BASE_URL,
    }


# --------------------------------------------------------------------------- #
# Case / split loading                                                         #
# --------------------------------------------------------------------------- #

@dataclasses.dataclass(frozen=True)
class Case:
    slug: str
    split: str
    company: str
    role: str
    recipient: str
    job_text: str
    gold_cv: str
    gold_cover: str


def load_split() -> dict[str, list[str]]:
    data = yaml.safe_load((HERE / "split.yml").read_text(encoding="utf-8")) or {}
    return {"train": list(data.get("train") or []), "test": list(data.get("test") or [])}


def all_slugs() -> list[str]:
    s = load_split()
    return s["train"] + s["test"]


def load_case(slug: str) -> Case:
    d = CASES / slug
    meta = yaml.safe_load((d / "meta.yml").read_text(encoding="utf-8")) or {}
    return Case(
        slug=slug,
        split=meta.get("split", ""),
        company=meta.get("company", ""),
        role=meta.get("role", ""),
        recipient=meta.get("recipient", "") or "",
        job_text=(d / "job-description.txt").read_text(encoding="utf-8"),
        gold_cv=(d / "gold" / "cv.md").read_text(encoding="utf-8"),
        gold_cover=(d / "gold" / "cover-letter.md").read_text(encoding="utf-8"),
    )


def load_master_cv() -> str:
    return (ROOT / "data" / "master-cv.md").read_text(encoding="utf-8")


def load_projects_catalog() -> list[dict[str, Any]]:
    data = yaml.safe_load((ROOT / "data" / "projects.yml").read_text(encoding="utf-8"))
    return data["projects"]


# --------------------------------------------------------------------------- #
# Tokenization (reuse the engine's so coverage matches the ranker)             #
# --------------------------------------------------------------------------- #

def _tokens(text: str) -> set[str]:
    from engine import rank
    return rank._tokens(text)


# --------------------------------------------------------------------------- #
# Markdown structure helpers                                                   #
# --------------------------------------------------------------------------- #

def strip_front_matter(md: str) -> str:
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip("\n")
    return md


def cv_sections(md: str) -> dict[str, str]:
    """Map H2 section name -> its body text."""
    md = strip_front_matter(md)
    out: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^##\s+(.*?)\s*$", line)
        if m:
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def _section(md: str, name: str) -> str:
    for k, v in cv_sections(md).items():
        if name.lower() in k.lower():
            return v
    return ""


def cv_org_headers(md: str) -> list[str]:
    """The org part of each '### Org — Role' entry header."""
    orgs = []
    for line in strip_front_matter(md).splitlines():
        m = re.match(r"^###\s+(.*)$", line)
        if m:
            orgs.append(re.split(r"\s[—–-]\s", m.group(1), 1)[0].strip())
    return orgs


def featured_project_ids(md: str, catalog: list[dict[str, Any]]) -> set[str]:
    """Project ids whose name appears as a bold bullet in the Projects section."""
    proj = _section(md, "Projects")
    names = re.findall(r"^-\s+\*\*(.+?)\*\*", proj, flags=re.MULTILINE)
    ids: set[str] = set()
    for raw in names:
        nt = _tokens(raw)
        best, best_ov = None, 0
        for p in catalog:
            ov = len(nt & _tokens(p["name"]))
            if ov > best_ov:
                best, best_ov = p["id"], ov
        if best and best_ov >= 1:
            ids.add(best)
    return ids


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", strip_front_matter(text)) if p.strip()]


# --------------------------------------------------------------------------- #
# Pure metrics                                                                 #
# --------------------------------------------------------------------------- #

def cv_structure_score(md: str) -> float:
    secs = {k.lower() for k in cv_sections(md)}
    hit = sum(1 for s in REQUIRED_CV_SECTIONS if any(s.lower() in k for k in secs))
    return hit / len(REQUIRED_CV_SECTIONS)


def skill_tokens(md: str) -> set[str]:
    return {t for t in _tokens(_section(md, "Skills")) if t not in _SKILL_STOPWORDS and len(t) > 1}


def skills_coverage(gen_cv: str, gold_cv: str) -> float:
    """Fraction of the gold's skill tokens that also appear anywhere in the gen CV."""
    gold = skill_tokens(gold_cv)
    if not gold:
        return 1.0
    return len(gold & _tokens(gen_cv)) / len(gold)


def projects_match(gen_cv: str, gold_cv: str, catalog: list[dict[str, Any]]) -> float:
    """Recall of the gold's featured projects among the gen's featured projects."""
    gold = featured_project_ids(gold_cv, catalog)
    if not gold:
        return 1.0
    return len(gold & featured_project_ids(gen_cv, catalog)) / len(gold)


def jd_keyword_coverage(gen_cv: str, must_haves: list[str]) -> float:
    """Fraction of JD must-have phrases with at least one token present in the CV."""
    if not must_haves:
        return 1.0
    cv = _tokens(gen_cv)
    hit = sum(1 for m in must_haves if _tokens(m) & cv)
    return hit / len(must_haves)


# EN/DE org-name equivalences so a localized header (e.g. the German CV's
# "Technische Universität Ilmenau") still grounds against the English master CV.
# Applied at the STRING level before tokenizing, because the engine's ASCII
# tokenizer would otherwise split "universität" into "universit" + "t".
_ORG_NORM = {
    "universität": "university", "universitaet": "university", "universitat": "university",
    "technische": "technical", "technisches": "technical", "technischen": "technical",
    "hochschule": "university", "informatik": "informatics",
}


def _org_tokens(text: str) -> set[str]:
    t = text.lower()
    for de, en in _ORG_NORM.items():
        t = t.replace(de, en)
    return _tokens(t)


def truthfulness(gen_cv: str, master_cv: str, *, threshold: float = 0.6) -> dict[str, Any]:
    """Every org header in the gen CV must be grounded in the master CV.

    An org is 'grounded' when >= `threshold` of its (localization-normalized)
    tokens appear in the master CV token set. Returns {score, offenders}."""
    master = _org_tokens(master_cv)
    orgs = cv_org_headers(gen_cv)
    if not orgs:
        return {"score": 0.0, "offenders": ["<no experience/education entries>"]}
    offenders = []
    for org in orgs:
        ot = _org_tokens(org)
        if not ot or (len(ot & master) / len(ot)) < threshold:
            offenders.append(org)
    return {"score": 1.0 - len(offenders) / len(orgs), "offenders": offenders}


def _band(x: float, lo: float, hi: float, soft: float) -> float:
    """1.0 inside [lo,hi]; linear falloff to 0 over `soft` beyond each edge."""
    if lo <= x <= hi:
        return 1.0
    d = (lo - x) if x < lo else (x - hi)
    return max(0.0, 1.0 - d / soft)


_FORBIDDEN_OPENERS = re.compile(
    r"(?im)^\s*(dear\b|hello\b|sincerely\b|yours\b|mit freundlichen|best regards\b)"
)


def cover_metrics(gen_cover: str, company: str) -> dict[str, Any]:
    body = strip_front_matter(gen_cover).strip()
    wc = len(body.split())
    paras = paragraphs(gen_cover)
    no_salutation = 0.0 if _FORBIDDEN_OPENERS.search(body) else 1.0
    company_hit = 1.0
    if company:
        first = re.sub(r"[^a-z0-9]+", "", company.split()[0].lower())
        company_hit = 1.0 if first and first in _tokens(body) else 0.0
    return {
        "word_count": wc,
        "length_ok": round(_band(wc, 250, 400, 150), 3),
        "paragraphs": len(paras),
        "paragraphs_ok": 1.0 if 3 <= len(paras) <= 5 else 0.5,
        "no_salutation": no_salutation,
        "company_mention": company_hit,
    }


# Heuristic weights -> a single 0-1 score per case (judge score is separate).
_W = {
    "cv_structure": 0.15,
    "skills_coverage": 0.20,
    "projects_match": 0.15,
    "jd_coverage": 0.15,
    "truthfulness": 0.15,
    "cl_length": 0.05,
    "cl_no_salutation": 0.05,
    "cl_company": 0.05,
    "cl_paragraphs": 0.05,
}


def score_case(
    gen_cv: str,
    gen_cover: str,
    case: Case,
    must_haves: list[str],
    master_cv: str,
    catalog: list[dict[str, Any]],
) -> dict[str, Any]:
    cm = cover_metrics(gen_cover, case.company)
    truth = truthfulness(gen_cv, master_cv)
    parts = {
        "cv_structure": cv_structure_score(gen_cv),
        "skills_coverage": skills_coverage(gen_cv, case.gold_cv),
        "projects_match": projects_match(gen_cv, case.gold_cv, catalog),
        "jd_coverage": jd_keyword_coverage(gen_cv, must_haves),
        "truthfulness": truth["score"],
        "cl_length": cm["length_ok"],
        "cl_no_salutation": cm["no_salutation"],
        "cl_company": cm["company_mention"],
        "cl_paragraphs": cm["paragraphs_ok"],
    }
    heuristic = round(sum(_W[k] * parts[k] for k in _W), 4)
    return {
        "slug": case.slug,
        "split": case.split,
        "heuristic": heuristic,
        "parts": {k: round(v, 3) for k, v in parts.items()},
        "cover": cm,
        "truthfulness_offenders": truth["offenders"],
        "cv_word_count": len(strip_front_matter(gen_cv).split()),
    }

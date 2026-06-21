"""Run manifest — make a generated application re-derivable and verifiable.

Captures the provider/model/temperature/token-budgets/seed actually used, the
prompt versions + content hashes, and content hashes of the effective config and
every data input (master CV, profile, projects, taxonomy, ranking, guides,
exemplars). Written next to each application (docs/jobs/<slug>/manifest.json) and
each benchmark output. Two runs with the same effective_config_sha256 + prompt
hashes + provider/seed should reproduce the same result.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

from . import config, llm, prompts
from .jobspec import _SYSTEM as _JOBSPEC_SYSTEM
from .render import _COVER_SYSTEM, _CV_SYSTEM

SCHEMA = 1

# Data inputs whose content determines the output — hashed so a result is tied to
# the exact snapshot that produced it.
_INPUT_FILES = (
    "data/config.yml",
    "data/master-cv.md",
    "data/profile.yml",
    "data/projects.yml",
    "data/taxonomy.yml",
    "data/ranking.yml",
    "data/guides/how-to-write-a-cv.md",
    "data/guides/how-to-write-a-cover-letter.md",
    "data/prompts/exemplars/cover.yml",
)


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def build(*, decisions: dict[str, Any], generated_at: str = "",
          root: pathlib.Path | None = None) -> dict[str, Any]:
    """Assemble the manifest. `decisions` carries the run's choices already computed
    upstream (e.g. top_projects, clusters, tagline)."""
    root = root or config.ROOT
    cfg = llm.resolve()
    eff = config.load(root)

    inputs = {}
    for rel in _INPUT_FILES:
        p = root / rel
        if p.exists():
            inputs[rel] = sha256_of(p.read_text(encoding="utf-8"))

    return {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "config_version": eff.get("version"),
        "provider": cfg["provider"],
        "model": cfg["model"],
        "temperature": cfg["temperature"],
        "max_tokens": cfg["max_tokens"],
        "seed": cfg["seed"],
        "prompts": {
            "cv": prompts.meta("cv", _CV_SYSTEM, root=root),
            "cover": prompts.meta("cover", _COVER_SYSTEM, root=root),
            "jobspec": prompts.meta("jobspec", _JOBSPEC_SYSTEM, root=root),
        },
        "inputs_sha256": inputs,
        "effective_config_sha256": sha256_of(json.dumps(eff, sort_keys=True)),
        "decisions": decisions,
    }

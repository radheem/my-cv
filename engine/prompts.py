"""Versioned system prompts, loaded from data/prompts/ with an in-code fallback.

Each prompt file is Markdown with optional YAML front matter carrying `version:`.
When the file is absent, the caller's in-code default string is used — so deleting
data/prompts/ reproduces today's behavior. `load()` returns (text, meta); the meta
(version + content hash + source) flows into the run manifest so a generated
document is attributable to a specific prompt revision.
"""

from __future__ import annotations

import hashlib
import pathlib
from typing import Any

import yaml

from .shared import config


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _split_front_matter(md: str) -> tuple[dict, str]:
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) == 3:
            return (yaml.safe_load(parts[1]) or {}), parts[2].lstrip("\n")
    return {}, md


def load(name: str, default: str, *, root: pathlib.Path | None = None) -> tuple[str, dict]:
    """Return (prompt_text, meta) for prompt `name` (cv|cover|jobspec|judge).

    `default` is the in-code fallback used when the file is absent."""
    root = root or config.ROOT
    pcfg = config.load(root)["prompts"]
    fname = pcfg.get(name)
    if fname:
        path = root / pcfg.get("dir", "data/prompts") / fname
        if path.exists():
            meta, body = _split_front_matter(path.read_text(encoding="utf-8"))
            text = body.strip()
            return text, {
                "version": meta.get("version", 1),
                "sha256": _sha(text),
                "source": str(path.relative_to(root)),
            }
    return default, {"version": 0, "sha256": _sha(default), "source": "builtin"}


def meta(name: str, default: str, *, root: pathlib.Path | None = None) -> dict[str, Any]:
    """Just the {version, sha256, source} for `name` — for the run manifest."""
    return load(name, default, root=root)[1]

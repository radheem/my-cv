"""Layered configuration for cv-tailor.

One place resolves every knob that used to be a scattered constant: provider /
model, temperatures, token budgets, the Ollama endpoint, prompt selection, and the
ranking/taxonomy file paths. Precedence, highest first:

    CLI flag (mapped to env by the CLI)  >  env var  >  data/config.yml  >  _DEFAULTS

`_DEFAULTS` encodes EXACTLY the historical hardcoded values, so an absent
`data/config.yml` with no env overrides reproduces today's behavior — and
`tests/test_llm_config.py` keeps passing because env still wins over the file.
"""

from __future__ import annotations

import os
import pathlib
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Historical constants, centralized. Changing behavior = editing data/config.yml,
# not these.
_DEFAULTS: dict[str, Any] = {
    "version": 0,
    "llm": {
        "provider": "anthropic",
        "anthropic_model": "claude-sonnet-4-6",
        "ollama_model": "qwen3.5:35b",
        "temperature": {"json": 0.0, "text": 0.4},
        "max_tokens": {"jobspec": 2000, "cv": 16000, "cover": 8000, "judge": 1200},
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "min_json_tokens": 12000,
            "min_text_tokens": 24000,
        },
        "seed": None,
    },
    "prompts": {
        "dir": "data/prompts",
        "cv": "cv.md",
        "cover": "cover.md",
        "jobspec": "jobspec.md",
        "judge": "judge.md",
        "fewshot": True,
    },
    "tailoring": {
        "ranking_file": "data/ranking.yml",
        "taxonomy_file": "data/taxonomy.yml",
    },
}

_OLLAMA_ALIASES = {"ollama", "openai", "openai-compatible"}


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = _deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load(root: pathlib.Path | None = None) -> dict[str, Any]:
    """The merged config (defaults ⊕ data/config.yml). No env overlay — use this
    for hashing / the manifest's `effective_config`."""
    root = root or ROOT
    path = root / "data" / "config.yml"
    file_cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {} if path.exists() else {}
    return _deep_merge(_DEFAULTS, file_cfg)


def _env_float(key: str) -> float | None:
    v = os.environ.get(key)
    return float(v) if v not in (None, "") else None


def _env_int(key: str) -> int | None:
    v = os.environ.get(key)
    return int(v) if v not in (None, "") else None


def resolve_llm(root: pathlib.Path | None = None) -> dict[str, Any]:
    """Effective LLM settings with env overrides applied on top of the file/defaults.

    Returns the legacy `resolve()` keys (provider, model, and for ollama base_url /
    api_key) plus temperature/max_tokens/seed, so render.py and jobspec.py read one
    source. Env precedence is preserved (env > config.yml > defaults)."""
    cfg = load(root)["llm"]

    provider = os.environ.get("CV_TAILOR_PROVIDER", cfg["provider"]).strip().lower()
    is_ollama = provider in _OLLAMA_ALIASES

    temperature = dict(cfg["temperature"])
    t = _env_float("CV_TAILOR_TEXT_TEMPERATURE")
    if t is not None:
        temperature["text"] = t

    seed = cfg.get("seed")
    s = _env_int("CV_TAILOR_SEED")
    if s is not None:
        seed = s

    out: dict[str, Any] = {
        "provider": "ollama" if is_ollama else "anthropic",
        "temperature": temperature,
        "max_tokens": dict(cfg["max_tokens"]),
        "seed": seed,
    }
    if is_ollama:
        oll = cfg["ollama"]
        out.update(
            model=os.environ.get("CV_TAILOR_MODEL", cfg["ollama_model"]),
            base_url=os.environ.get("CV_TAILOR_OLLAMA_BASE_URL", oll["base_url"]),
            api_key=os.environ.get("CV_TAILOR_OLLAMA_API_KEY", oll["api_key"]),
            min_json_tokens=_env_int("CV_TAILOR_MIN_JSON_TOKENS") or oll["min_json_tokens"],
            min_text_tokens=_env_int("CV_TAILOR_MIN_TEXT_TOKENS") or oll["min_text_tokens"],
        )
    else:
        out["model"] = os.environ.get("CV_TAILOR_MODEL", cfg["anthropic_model"])
    return out


def data_path(rel: str, root: pathlib.Path | None = None) -> pathlib.Path:
    """Resolve a config-relative data path (e.g. tailoring.ranking_file)."""
    return (root or ROOT) / rel

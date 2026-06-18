"""Model access for jobspec.py and render.py — pluggable provider.

Local-only (generation never runs in CI). Two backends behind one API:

  - anthropic (default) — the official `anthropic` SDK; needs ANTHROPIC_API_KEY.
  - ollama   (opt-in)   — any OpenAI-compatible endpoint via the `openai` SDK;
                          e.g. a local Ollama server.

Selection (Anthropic default, Ollama opt-in):
  CV_TAILOR_PROVIDER       anthropic | ollama            (default: anthropic)
  CV_TAILOR_MODEL          model id                       (per-provider default)
  CV_TAILOR_OLLAMA_BASE_URL  OpenAI-compatible base URL   (default: localhost)
  CV_TAILOR_OLLAMA_API_KEY   key for that endpoint        (default: "ollama")

The CLI's --provider/--model/--ollama-url flags set these env vars.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_OLLAMA_MODEL = "qwen3.5:35b"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434/v1"

_OLLAMA_ALIASES = {"ollama", "openai", "openai-compatible"}


def resolve() -> dict[str, Any]:
    """Resolve the active provider config from the environment (pure)."""
    provider = os.environ.get("CV_TAILOR_PROVIDER", "anthropic").strip().lower()
    if provider in _OLLAMA_ALIASES:
        return {
            "provider": "ollama",
            "model": os.environ.get("CV_TAILOR_MODEL", DEFAULT_OLLAMA_MODEL),
            "base_url": os.environ.get(
                "CV_TAILOR_OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL
            ),
            "api_key": os.environ.get("CV_TAILOR_OLLAMA_API_KEY", "ollama"),
        }
    return {
        "provider": "anthropic",
        "model": os.environ.get("CV_TAILOR_MODEL", DEFAULT_ANTHROPIC_MODEL),
    }


def model() -> str:
    return resolve()["model"]


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested)                                                   #
# --------------------------------------------------------------------------- #

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _strip_think(text: str) -> str:
    """Remove qwen-style <think>…</think> reasoning blocks."""
    return _THINK_RE.sub("", text).strip()


def _json_from_text(text: str) -> str:
    """Extract a JSON object string from model output that may carry a <think>
    block, a ```json fence, or surrounding prose."""
    text = _strip_think(text)
    fence = _FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


# --------------------------------------------------------------------------- #
# Clients (lazy import)                                                        #
# --------------------------------------------------------------------------- #

def _anthropic_client():
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover - dependency guard
        raise SystemExit(
            "The Anthropic backend needs the 'anthropic' SDK. "
            "Install it with: pip install -e '.[generate]'"
        ) from e
    return anthropic.Anthropic()


def _openai_client(cfg: dict[str, Any]):
    try:
        from openai import OpenAI
    except ImportError as e:  # pragma: no cover - dependency guard
        raise SystemExit(
            "The Ollama / OpenAI-compatible backend needs the 'openai' SDK. "
            "Install it with: pip install -e '.[ollama]'"
        ) from e
    return OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #

def structured_json(
    system: str, user: str, schema: dict[str, Any], *, max_tokens: int = 4000
) -> dict[str, Any]:
    """One-shot call constrained to a JSON schema. Returns the parsed object."""
    cfg = resolve()
    if cfg["provider"] == "ollama":
        client = _openai_client(cfg)
        resp = client.chat.completions.create(
            model=cfg["model"],
            max_tokens=max_tokens,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "jobspec", "schema": schema, "strict": True},
            },
        )
        return json.loads(_json_from_text(resp.choices[0].message.content or ""))

    resp = _anthropic_client().messages.create(
        model=cfg["model"],
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    text = next((b.text for b in resp.content if b.type == "text"), "")
    return json.loads(text)


def stream_text(system: str, user: str, *, max_tokens: int = 16000) -> str:
    """Stream a (potentially long) text response and return the full string."""
    cfg = resolve()
    if cfg["provider"] == "ollama":
        client = _openai_client(cfg)
        parts: list[str] = []
        stream = client.chat.completions.create(
            model=cfg["model"],
            max_tokens=max_tokens,
            temperature=0.4,
            stream=True,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                parts.append(delta)
        return _strip_think("".join(parts))

    parts = []
    with _anthropic_client().messages.stream(
        model=cfg["model"],
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
        stream.get_final_message()  # surface any terminal error
    return "".join(parts)

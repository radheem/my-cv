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
import re
from typing import Any

from .shared import config


def resolve() -> dict[str, Any]:
    """Active LLM settings: provider/model (+ ollama base_url/api_key), temperature,
    max_tokens, seed, and ollama token floors. Layered: env > data/config.yml >
    defaults (see engine/config.py). Reasoning models (qwen3.x) emit a <think> block
    billed against max_tokens before the answer, so the ollama floors keep structured
    JSON and long prose from truncating to empty; thinking stays ON because disabling
    it (reasoning_effort="none") makes some Ollama builds ignore the JSON schema."""
    return config.resolve_llm()


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


def _seed_kwargs(cfg: dict[str, Any]) -> dict[str, Any]:
    """Pass a deterministic seed to the OpenAI-compatible endpoint when configured.
    (Anthropic has no public seed param; its determinism comes from temperature.)"""
    seed = cfg.get("seed")
    return {"seed": seed} if seed is not None else {}


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

        def _ask(mt: int) -> str:
            resp = client.chat.completions.create(
                model=cfg["model"],
                max_tokens=mt,
                temperature=cfg["temperature"]["json"],
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": "jobspec", "schema": schema, "strict": True},
                },
                **_seed_kwargs(cfg),
            )
            return resp.choices[0].message.content or ""

        budget = max(max_tokens, cfg["min_json_tokens"])
        raw = _ask(budget)
        try:
            return json.loads(_json_from_text(raw))
        except (json.JSONDecodeError, ValueError):
            # Most likely truncation (thinking ate the budget): retry once larger.
            return json.loads(_json_from_text(_ask(budget * 2)))

    resp = _anthropic_client().messages.create(
        model=cfg["model"],
        max_tokens=max_tokens,
        temperature=cfg["temperature"]["json"],
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
        # Thinking stays on; headroom so the prose isn't truncated after the
        # <think> block (which _strip_think removes from the returned text).
        stream = client.chat.completions.create(
            model=cfg["model"],
            max_tokens=max(max_tokens, cfg["min_text_tokens"]),
            temperature=cfg["temperature"]["text"],
            stream=True,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **_seed_kwargs(cfg),
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
        temperature=cfg["temperature"]["text"],
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
        stream.get_final_message()  # surface any terminal error
    return "".join(parts)

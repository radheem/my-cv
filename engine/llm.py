"""Thin Claude API helpers shared by jobspec.py and render.py.

Local-only (needs ANTHROPIC_API_KEY). Uses the official `anthropic` SDK.
Model defaults to Sonnet 4.6 (the approved choice for tailoring); override with
CV_TAILOR_MODEL=claude-opus-4-8 for harder reasoning.
"""

from __future__ import annotations

import json
import os
from typing import Any

# Approved default per the project plan; opus available via env for hard cases.
DEFAULT_MODEL = "claude-sonnet-4-6"


def model() -> str:
    return os.environ.get("CV_TAILOR_MODEL", DEFAULT_MODEL)


def _client():
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover - dependency guard
        raise SystemExit(
            "The generation engine needs the 'anthropic' SDK. "
            "Install it with: pip install -e '.[generate]'"
        ) from e
    # Resolves ANTHROPIC_API_KEY (or an `ant auth login` profile) from the env.
    return anthropic.Anthropic()


def structured_json(
    system: str, user: str, schema: dict[str, Any], *, max_tokens: int = 4000
) -> dict[str, Any]:
    """One-shot call constrained to a JSON schema. Returns the parsed object.

    Uses output_config.format (the canonical structured-output API) rather than
    forced tool use, so the first text block is guaranteed valid JSON.
    """
    resp = _client().messages.create(
        model=model(),
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    text = next((b.text for b in resp.content if b.type == "text"), "")
    return json.loads(text)


def stream_text(system: str, user: str, *, max_tokens: int = 16000) -> str:
    """Stream a (potentially long) text response and return the full string.

    Streaming avoids SDK HTTP timeouts on large max_tokens.
    """
    parts: list[str] = []
    with _client().messages.stream(
        model=model(),
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
        stream.get_final_message()  # surface any terminal error
    return "".join(parts)

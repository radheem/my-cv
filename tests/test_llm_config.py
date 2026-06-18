"""Tests for provider resolution and the pure parsing helpers in engine/llm.py.

No network, no SDKs required (resolve() and the helpers don't import them).
"""

import pytest

from engine import llm

_ENV_KEYS = [
    "CV_TAILOR_PROVIDER",
    "CV_TAILOR_MODEL",
    "CV_TAILOR_OLLAMA_BASE_URL",
    "CV_TAILOR_OLLAMA_API_KEY",
]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in _ENV_KEYS:
        monkeypatch.delenv(k, raising=False)


def test_default_is_anthropic_sonnet():
    cfg = llm.resolve()
    assert cfg["provider"] == "anthropic"
    assert cfg["model"] == "claude-sonnet-4-6"


def test_anthropic_model_override(monkeypatch):
    monkeypatch.setenv("CV_TAILOR_MODEL", "claude-opus-4-8")
    assert llm.resolve()["model"] == "claude-opus-4-8"


def test_ollama_defaults(monkeypatch):
    monkeypatch.setenv("CV_TAILOR_PROVIDER", "ollama")
    cfg = llm.resolve()
    assert cfg["provider"] == "ollama"
    assert cfg["model"] == "qwen3.5:35b"
    assert cfg["base_url"] == "http://localhost:11434/v1"
    assert cfg["api_key"] == "ollama"


def test_ollama_overrides(monkeypatch):
    monkeypatch.setenv("CV_TAILOR_PROVIDER", "ollama")
    monkeypatch.setenv("CV_TAILOR_MODEL", "qwen3.5:35b")
    monkeypatch.setenv("CV_TAILOR_OLLAMA_BASE_URL", "http://genai.example:11434/v1")
    monkeypatch.setenv("CV_TAILOR_OLLAMA_API_KEY", "secret")
    cfg = llm.resolve()
    assert cfg["base_url"] == "http://genai.example:11434/v1"
    assert cfg["api_key"] == "secret"


@pytest.mark.parametrize("alias", ["ollama", "openai", "openai-compatible", "OLLAMA"])
def test_provider_aliases(monkeypatch, alias):
    monkeypatch.setenv("CV_TAILOR_PROVIDER", alias)
    assert llm.resolve()["provider"] == "ollama"


def test_strip_think():
    assert llm._strip_think("<think>reasoning here</think>\nHello.") == "Hello."
    assert llm._strip_think("no think tags") == "no think tags"


def test_json_from_text_fenced():
    raw = '<think>plan</think>\n```json\n{"a": 1, "b": [2, 3]}\n```'
    assert llm._json_from_text(raw) == '{"a": 1, "b": [2, 3]}'


def test_json_from_text_with_prose():
    raw = 'Here is the JobSpec:\n{"title": "X"}\nThanks!'
    assert llm._json_from_text(raw) == '{"title": "X"}'

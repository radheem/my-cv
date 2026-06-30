"""Tests for CV variant selection engine (engine/domains/tailoring/variants.py)."""

import pytest
from unittest.mock import patch, MagicMock

from engine.domains.tailoring import variants


@pytest.fixture
def taxonomy_fixture():
    return {
        "aliases": {
            "kubernetes": ["k8s"],
            "go": ["golang"],
            "postgresql": ["postgres"],
        },
        "clusters": {
            "platform-cloud-native": {"tags": ["kubernetes", "k8s", "cilium", "helm"]},
            "ml-ai": {"tags": ["ml", "ai", "llm", "rag"]},
            "distributed-systems": {"tags": ["distributed", "microservices", "grpc", "go"]},
            "data-persistence": {"tags": ["postgresql", "postgres", "sql", "database"]},
        },
    }


def _spec(**kw):
    base = {
        "title": "",
        "company": "",
        "seniority": "mid",
        "must_haves": [],
        "nice_to_haves": [],
        "stack": [],
        "keywords": [],
    }
    base.update(kw)
    return base


def test_score_job_clusters(taxonomy_fixture):
    spec = _spec(must_haves=["Kubernetes", "Cilium"], stack=["Go", "gRPC"])
    # Score for platform should be positive since "Kubernetes" and "Cilium" are under platform-cloud-native
    # Must-haves score weight is 3.0, so 2 matches = 2 * 3.0 = 6.0
    scores = variants.score_job_clusters(spec, taxonomy_fixture)
    
    assert scores["platform-cloud-native"] > 0
    assert scores["distributed-systems"] > 0
    assert scores["ml-ai"] == 0


@patch("engine.shared.config.load")
def test_select_best_cv_variant_single_winner(mock_config_load, taxonomy_fixture):
    mock_config_load.return_value = {
        "tailoring": {
            "cv_variants": {
                "platform-cloud-native": "platform-cloud-native.md",
                "ml-ai": "ml-ai.md",
                "distributed-systems": "distributed-systems.md",
                "data-persistence": "data-persistence.md",
            }
        }
    }
    spec = _spec(must_haves=["Kubernetes", "Cilium", "Helm"])  # strongly platform
    
    selected = variants.select_best_cv_variant(spec, "Job description text", taxonomy_fixture)
    assert selected == "platform-cloud-native.md"


@patch("engine.shared.config.load")
@patch("engine.domains.tailoring.llm.stream_text")
def test_select_best_cv_variant_tie_breaker(mock_stream_text, mock_config_load, taxonomy_fixture):
    mock_config_load.return_value = {
        "tailoring": {
            "cv_variants": {
                "platform-cloud-native": "platform-cloud-native.md",
                "ml-ai": "ml-ai.md",
                "distributed-systems": "distributed-systems.md",
                "data-persistence": "data-persistence.md",
            }
        }
    }
    # Tying platform and ml-ai equally
    spec = _spec(must_haves=["Kubernetes", "ml"])
    
    # Mock LLM choosing "ml-ai.md"
    mock_stream_text.return_value = "ml-ai.md"
    
    selected = variants.select_best_cv_variant(spec, "Job description text", taxonomy_fixture)
    assert selected == "ml-ai.md"
    mock_stream_text.assert_called_once()


@patch("engine.shared.config.load")
@patch("engine.domains.tailoring.llm.stream_text")
def test_select_best_cv_variant_tie_breaker_invalid_choice_aborts(mock_stream_text, mock_config_load, taxonomy_fixture):
    mock_config_load.return_value = {
        "tailoring": {
            "cv_variants": {
                "platform-cloud-native": "platform-cloud-native.md",
                "ml-ai": "ml-ai.md",
            }
        }
    }
    spec = _spec(must_haves=["Kubernetes", "ml"])
    
    # Mock LLM returning garbage or an un-tied variant
    mock_stream_text.return_value = "unrelated-variant.md"
    
    with pytest.raises(SystemExit) as excinfo:
        variants.select_best_cv_variant(spec, "Job description text", taxonomy_fixture)
        
    assert "CRITICAL ERROR" in str(excinfo.value)


def test_extract_projects_from_cv():
    cv_markdown = """
---
tagline: "Test"
---

## Experience
- Worked at Acme.

## Projects
- **IRS Platform (Stealth)** — High performance backend messaging.
- **cv-tailor** — CV tailoring tools.
- **Duff Project** — Unrelated project.

## Skills
- Tech stack.
"""
    projects_catalog = [
        {"id": "irs-platform", "name": "IRS Platform (Stealth)"},
        {"id": "cv-tailor", "name": "cv-tailor"},
        {"id": "other-one", "name": "Another Project"},
    ]
    
    extracted = variants.extract_projects_from_cv(cv_markdown, projects_catalog)
    assert len(extracted) == 2
    assert extracted[0]["id"] == "irs-platform"
    assert extracted[1]["id"] == "cv-tailor"

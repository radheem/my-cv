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
            "platform-engineer": {"tags": ["kubernetes", "k8s", "cilium", "helm"]},
            "ai-ml": {"tags": ["ml", "ai", "llm", "rag"]},
            "distributed-system": {"tags": ["distributed", "microservices", "grpc", "go"]},
            "information-management": {"tags": ["postgresql", "postgres", "sql", "database"]},
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
    # Score for platform should be positive since "Kubernetes" and "Cilium" are under platform-engineer
    # Must-haves score weight is 3.0, so 2 matches = 2 * 3.0 = 6.0
    scores = variants.score_job_clusters(spec, taxonomy_fixture)
    
    assert scores["platform-engineer"] > 0
    assert scores["distributed-system"] > 0
    assert scores["ai-ml"] == 0


@patch("engine.shared.config.load")
def test_select_best_cv_variant_single_winner(mock_config_load, taxonomy_fixture):
    mock_config_load.return_value = {
        "tailoring": {
            "cv_variants": {
                "platform-engineer": "platform-engineer.md",
                "ai-ml": "ai-ml.md",
                "distributed-system": "distributed-system.md",
                "information-management": "information-management.md",
            }
        }
    }
    spec = _spec(must_haves=["Kubernetes", "Cilium", "Helm"])  # strongly platform
    
    selected = variants.select_best_cv_variant(spec, "Job description text", taxonomy_fixture)
    assert selected == "platform-engineer.md"


@patch("engine.shared.config.load")
@patch("engine.domains.tailoring.llm.stream_text")
def test_select_best_cv_variant_tie_breaker(mock_stream_text, mock_config_load, taxonomy_fixture):
    mock_config_load.return_value = {
        "tailoring": {
            "cv_variants": {
                "platform-engineer": "platform-engineer.md",
                "ai-ml": "ai-ml.md",
                "distributed-system": "distributed-system.md",
                "information-management": "information-management.md",
            }
        }
    }
    # Tying platform and ai-ml equally
    spec = _spec(must_haves=["Kubernetes", "ml"])
    
    # Mock LLM choosing "ai-ml.md"
    mock_stream_text.return_value = "ai-ml.md"
    
    selected = variants.select_best_cv_variant(spec, "Job description text", taxonomy_fixture)
    assert selected == "ai-ml.md"
    mock_stream_text.assert_called_once()


@patch("engine.shared.config.load")
@patch("engine.domains.tailoring.llm.stream_text")
def test_select_best_cv_variant_tie_breaker_invalid_choice_aborts(mock_stream_text, mock_config_load, taxonomy_fixture):
    mock_config_load.return_value = {
        "tailoring": {
            "cv_variants": {
                "platform-engineer": "platform-engineer.md",
                "ai-ml": "ai-ml.md",
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


@patch("engine.cli._jobs_dir")
@patch("engine.cli._load_data")
@patch("engine.fetch.fetch_job_text")
@patch("engine.domains.tailoring.jobspec.extract_jobspec")
@patch("engine.domains.tailoring.render.render_cover_letter")
@patch("engine.cli.ROOT")
def test_cmd_new_variants_pipeline_integration(
    mock_root, mock_render_cl, mock_extract, mock_fetch, mock_load_data, mock_jobs_dir, tmp_path
):
    import argparse
    from engine import cli
    
    # 1. Setup mock jobs directory
    mock_jobs_dir.return_value = tmp_path
    
    # 2. Setup mock data load
    profile = {"summary": "A developer."}
    projects_cat = [{"id": "irs-platform", "name": "IRS Platform"}]
    taxonomy = {
        "aliases": {},
        "clusters": {"platform-engineer": {"tags": ["kubernetes"]}}
    }
    mock_load_data.return_value = (profile, projects_cat, "master cv", "cv guide", "cl guide", taxonomy, {})
    
    # 3. Setup mock webpage fetch and jobspec extraction
    mock_fetch.return_value = "Wanted: Kubernetes expert."
    mock_extract.return_value = {
        "title": "Platform Engineer",
        "company": "Acme",
        "must_haves": ["Kubernetes"],
    }
    mock_render_cl.return_value = "Mocked cover letter body."
    
    # 4. Setup mock ROOT and variant file
    mock_root.resolve.return_value = mock_root
    mock_root.__truediv__.return_value = mock_root  # ROOT / "data"
    
    variant_file = tmp_path / "mock-variant.md"
    variant_file.write_text(
        "---\ntagline: \"Original Tagline\"\n---\n\n## Experience\n- Bullet.\n\n## Projects\n- **IRS Platform** — Description.\n",
        encoding="utf-8"
    )
    
    # We mock ROOT / "data" / "cv-variants" / "platform-engineer.md" to point to our temp file
    def mock_truediv_side_effect(other):
        if str(other) == "platform-engineer.md":
            return variant_file
        return mock_root
    
    mock_root.__truediv__.side_effect = mock_truediv_side_effect
    
    # 5. Run cmd_new
    args = argparse.Namespace(
        source="https://example.com/job/123",
        slug="acme-platform-123",
        provider="anthropic",
        model=None,
        ollama_url=None,
        no_translate=True,
        no_save_db=True,
        recipient=None
    )
    
    # We patch config.load inside cmd_new
    from engine.shared import config as shared_config
    real_config = shared_config.load()
    real_config["tailoring"]["cv_variants"] = {
        "platform-engineer": "platform-engineer.md"
    }
    
    with patch("engine.shared.config.load") as mock_cfg_load:
        mock_cfg_load.return_value = real_config
        rc = cli.cmd_new(args)
        
    assert rc == 0
    
    # Verify the generated application files
    app_folder = tmp_path / "acme-platform-123"
    assert app_folder.exists()
    
    # Read generated cv.md
    cv_content = (app_folder / "cv.md").read_text(encoding="utf-8")
    assert 'tagline: "Platform Engineer"' in cv_content
    assert '## Experience' in cv_content
    
    # Read generated cover-letter.md
    cl_content = (app_folder / "cover-letter.md").read_text(encoding="utf-8")
    assert "Mocked cover letter body." in cl_content


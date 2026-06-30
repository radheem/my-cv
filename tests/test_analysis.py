"""Unit tests for the composable analysis pipeline (engine/domains/tailoring/analysis.py)."""

import pytest
from engine.shared.db import get_conn, init_db
from engine.domains.tailoring import analysis


@pytest.fixture(autouse=True)
def clean_db():
    """Ensure clean transient test database state before and after each test."""
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jobs")
            cur.execute("DELETE FROM applications")
        conn.commit()


@pytest.fixture
def taxonomy_fixture():
    return {
        "aliases": {
            "kubernetes": ["k8s", "k3s"],
            "postgresql": ["postgres"],
            "go": ["golang"],
        },
        "clusters": {
            "platform-cloud-native": {
                "tags": ["kubernetes", "k8s", "cilium", "helm", "docker", "terraform"]
            },
            "ml-ai": {
                "tags": ["ml", "ai", "llm", "pytorch", "kserve", "pgvector"]
            }
        }
    }


@pytest.fixture
def profile_fixture():
    return {
        "programming_languages": ["Go", "Python", "SQL"],
        "skill_groups": [
            {
                "name": "Cloud-Native & Infra",
                "items": ["Kubernetes", "Cilium", "Helm", "Docker", "Terraform"],
                "tags": ["kubernetes", "cloud", "devops"]
            },
            {
                "name": "Databases & Persistence",
                "items": ["PostgreSQL", "pgvector"],
                "tags": ["database", "sql", "postgres"]
            },
            {
                "name": "AI / ML Integration",
                "items": ["PyTorch", "KServe"],
                "tags": ["ml", "ai", "llm"]
            }
        ]
    }


def seed_jobs_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Seed standard platform job
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES (
                    'job1', 'platform-engineer', 'Platform Inc', 'Cloud Engineer', 'file', 'other',
                    'We are looking for a Kubernetes expert. Experience with Helm, Docker, and Cilium is must. Go and Python are our languages.'
                )
            """)
            # Seed another platform job
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES (
                    'job2', 'infra-engineer', 'Infra Corp', 'SRE', 'file', 'other',
                    'Required: Kubernetes (k8s), Terraform, and Go. Managing multi-tenant clusters.'
                )
            """)
            # Seed AI/ML job with some unmapped terms (e.g., "vllm", "langchain")
            cur.execute("""
                INSERT INTO jobs (job_id, slug, company, title, source, platform, description)
                VALUES (
                    'job3', 'ml-engineer', 'AI Labs', 'MLOps Engineer', 'file', 'other',
                    'We need an ML engineer proficient in PyTorch, KServe, and pgvector vector-search. We also use vllm and langchain for indexing.'
                )
            """)
        conn.commit()


def test_get_jobs_for_cluster(taxonomy_fixture):
    seed_jobs_db()
    
    # Extract jobs heavily matched to "platform-cloud-native"
    platform_jobs = analysis.get_jobs_for_cluster("platform-cloud-native", taxonomy_fixture)
    assert len(platform_jobs) == 2
    # Verify proper ordering based on score
    # job1 has "Kubernetes", "Helm", "Docker", "Cilium" -> score 4
    # job2 has "Kubernetes", "Terraform" -> score 2 (k8s is alias of kubernetes)
    assert platform_jobs[0]["slug"] == "platform-engineer"
    assert platform_jobs[1]["slug"] == "infra-engineer"


def test_extract_cluster_signals(taxonomy_fixture, profile_fixture):
    seed_jobs_db()

    # Extract signals for ML-AI
    signals = analysis.extract_cluster_signals("ml-ai", taxonomy_fixture, profile_fixture, noise_threshold=0.1)

    assert signals["analysis_metadata"]["target_cluster"] == "ml-ai"
    assert signals["analysis_metadata"]["analyzed_jobs_count"] == 1

    # Verify programming languages
    # PyTorch description has PyTorch (libs), KServe (libs), pgvector (DB/persistence), vllm (unmapped), langchain (unmapped)
    assert len(signals["domain_signals"]["programming_languages"]) == 0

    # Verify categorized database persistence
    db_persistence = [d["term"] for d in signals["domain_signals"]["databases_persistence"]]
    assert "pgvector" in db_persistence

    # Verify libraries / frameworks
    libs = [l["term"] for d in signals["domain_signals"].values() for l in d]
    assert "PyTorch" in libs
    assert "KServe" in libs

    # Verify unmapped market terms
    unmapped = [u["term"] for u in signals["unmapped_market_terms"]]
    assert "vllm" in unmapped
    assert "langchain" in unmapped


def test_gap_analyzer():
    # Sample Stage 1 extraction output
    analysis_json = {
        "analysis_metadata": {"target_cluster": "platform-cloud-native"},
        "domain_signals": {
            "programming_languages": [{"term": "Go", "frequency": 0.8, "is_core": True}],
            "platforms_infrastructure": [
                {"term": "Kubernetes", "frequency": 0.9, "is_core": True},
                {"term": "Cilium", "frequency": 0.7, "is_core": False}
            ]
        }
    }

    # Sample CV variant content (missing "Cilium" but has "Go" and "Kubernetes")
    cv_content = """# My CV
    I am a Senior Engineer.
    Experience:
    - Built platforms with Go and Kubernetes.
    """

    report = analysis.gap_analyzer(analysis_json, cv_content)

    assert report["total_signals_checked"] == 3
    
    matching_terms = [m["term"] for m in report["matching_signals"]]
    missing_terms = [m["term"] for m in report["missing_signals"]]

    assert "Go" in matching_terms
    assert "Kubernetes" in matching_terms
    assert "Cilium" in missing_terms


def test_taxonomy_sync():
    analysis_json = {
        "unmapped_market_terms": [
            {"term": "vllm", "frequency": 0.3},
            {"term": "junk-low-frequency", "frequency": 0.05}
        ]
    }
    taxonomy = {}

    suggestions = analysis.taxonomy_sync(analysis_json, taxonomy)
    
    assert len(suggestions) == 1
    assert suggestions[0]["term"] == "vllm"
    assert "Add 'vllm'" in suggestions[0]["suggested_action"]


from unittest.mock import patch, MagicMock
import argparse

@patch("engine.cli._load_data")
@patch("engine.shared.config.load")
def test_cmd_analyze(mock_config_load, mock_load_data, taxonomy_fixture, profile_fixture, tmp_path, monkeypatch):
    from engine.cli import cmd_analyze

    # Isolate root variant paths
    monkeypatch.setattr("engine.cli.ROOT", tmp_path)
    variant_dir = tmp_path / "data" / "cv-variants"
    variant_dir.mkdir(parents=True, exist_ok=True)
    (variant_dir / "ml-ai.md").write_text("# My AI CV\nPyTorch, KServe")

    seed_jobs_db()
    
    mock_load_data.return_value = (profile_fixture, [], "", "", "", taxonomy_fixture, {})
    mock_config_load.return_value = {
        "tailoring": {
            "cv_variants": {
                "ml-ai": "ml-ai.md"
            }
        }
    }

    # Run cmd_analyze for ml-ai
    rc = cmd_analyze(argparse.Namespace(cluster="ml-ai"))
    assert rc == 0

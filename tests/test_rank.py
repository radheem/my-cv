"""Tests for the pure ranking core (engine/rank.py).

Exercises the real data/ catalogue against synthetic JobSpecs — no browser, no
API key, no network.
"""

import pathlib

import yaml

from engine import rank

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROFILE = yaml.safe_load((ROOT / "data" / "profile.yml").read_text())
PROJECTS = yaml.safe_load((ROOT / "data" / "projects.yml").read_text())["projects"]


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


def test_kubernetes_role_features_platform_projects():
    spec = _spec(
        title="Platform Engineer",
        must_haves=["Kubernetes", "Docker", "CI/CD"],
        nice_to_haves=["Cilium", "Terraform"],
        stack=["Kubernetes", "Cilium", "Prometheus"],
        keywords=["platform", "devops", "networking"],
    )
    top = rank.rank_projects(PROJECTS, spec, top=3)
    ids = {p["id"] for p in top}
    assert len(top) == 3
    # The two cluster/platform projects must surface for a Kubernetes role.
    assert "k3d" in ids
    assert "homelab" in ids


def test_ml_role_features_rag_and_mlops_projects():
    spec = _spec(
        title="ML Platform Engineer",
        must_haves=["Python", "RAG", "LLM"],
        nice_to_haves=["Kubeflow", "vector search"],
        stack=["Python", "pgvector", "KServe"],
        keywords=["ml", "ai", "mlops"],
    )
    ids = {p["id"] for p in rank.rank_projects(PROJECTS, spec, top=3)}
    assert "second-brain" in ids
    assert "oran-aiml" in ids


def test_ranking_is_deterministic_and_falls_back_to_order():
    empty = _spec()  # nothing matches -> catalogue order
    top = rank.rank_projects(PROJECTS, empty, top=3)
    assert [p["id"] for p in top] == [p["id"] for p in PROJECTS[:3]]


def test_score_orders_must_haves_above_nice_to_haves():
    must = _spec(must_haves=["Kubernetes"])
    nice = _spec(nice_to_haves=["Kubernetes"])
    proj = next(p for p in PROJECTS if p["id"] == "k3d")
    assert rank.score_project(proj, must) > rank.score_project(proj, nice)


def test_skills_block_house_order():
    spec = _spec(must_haves=["Kubernetes", "Cilium"], stack=["Docker"])
    skills = rank.build_skills(PROFILE, spec)
    # Languages first, Programming Languages second (the house rule).
    assert skills[0]["label"] == "Languages"
    assert skills[1]["label"] == "Programming Languages"
    # At least one tailored technical line follows.
    assert len(skills) >= 3
    # The most relevant technical group for a k8s role leads with the cloud group.
    assert any("Cloud" in line["label"] or "Infra" in line["label"] for line in skills[2:])


def test_skill_items_lead_with_must_haves():
    spec = _spec(must_haves=["Python"])
    ordered = rank.order_items_by_jobspec(PROFILE["programming_languages"], spec)
    assert ordered[0] == "Python"


def test_tailor_returns_projects_and_skills():
    spec = _spec(must_haves=["Kubernetes"])
    out = rank.tailor(spec, PROFILE, PROJECTS)
    assert len(out["top_projects"]) == 3
    assert out["skills"][0]["label"] == "Languages"

"""Tests for the pure ranking core (engine/rank.py).

Exercises the real data/ catalogue against synthetic JobSpecs — no browser, no
API key, no network.
"""

import pathlib

import pytest
import yaml

from engine.domains.tailoring import rank

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROFILE = yaml.safe_load((ROOT / "data" / "profile.yml").read_text())
PROJECTS = yaml.safe_load((ROOT / "data" / "projects.yml").read_text())["projects"]

# Small hermetic vocabulary fixtures (don't couple cluster/alias tests to the
# real data/taxonomy.yml, mirroring how _spec() builds synthetic JobSpecs).
TAXO = {
    "aliases": {"kubernetes": ["k8s"], "go": ["golang"]},
    "clusters": {
        "platform": {"tags": ["kubernetes", "platform"]},
        "ml": {"tags": ["ml", "rag"]},
    },
}
ALIASES = rank.invert_aliases(TAXO["aliases"])


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


# --- New: aliases, clusters, per-project weights, configurable selection --------


def test_defaults_reproduce_current_behavior():
    # tailor() with no taxonomy/ranking must equal the plain rank_projects path.
    for spec in (
        _spec(must_haves=["Kubernetes"]),
        _spec(must_haves=["Python", "RAG"], keywords=["ml"]),
        _spec(),
    ):
        tailor_ids = [p["id"] for p in rank.tailor(spec, PROFILE, PROJECTS)["top_projects"]]
        rank_ids = [p["id"] for p in rank.rank_projects(PROJECTS, spec, top=3)]
        assert tailor_ids == rank_ids


def test_alias_matching():
    # "k8s" only matches a kubernetes-tagged project once aliasing is applied.
    spec = _spec(must_haves=["k8s"])
    proj = next(p for p in PROJECTS if p["id"] == "k3d")  # tagged "kubernetes"
    assert rank.score_project(proj, spec, aliases=ALIASES) > 0
    assert rank.score_project(proj, spec) == 0  # no aliasing -> k8s != kubernetes


def test_cluster_affinity_boosts_correlated_projects():
    projects = [
        {"id": "other", "name": "O", "tags": ["frontend"]},
        {"id": "plat", "name": "P", "tags": ["kubernetes"]},  # later in catalogue
    ]
    spec = _spec(keywords=["platform"])  # hits the cluster tag, not the project token
    off = [p["id"] for p in rank.tailor(spec, PROFILE, projects,
                                        taxonomy=TAXO, ranking={"cluster_affinity": 0})["top_projects"]]
    on = [p["id"] for p in rank.tailor(spec, PROFILE, projects,
                                       taxonomy=TAXO, ranking={"cluster_affinity": 5})["top_projects"]]
    assert off == ["other", "plat"]   # no affinity -> catalogue order
    assert on == ["plat", "other"]    # affinity floats the correlated project up


def test_job_clusters_deterministic_and_sorted():
    spec = _spec(must_haves=["Kubernetes"], keywords=["rag"])
    out = rank.job_clusters(spec, TAXO, ALIASES)
    assert out == ["ml", "platform"]            # sorted, both matched
    assert rank.job_clusters(spec, TAXO, ALIASES) == out  # stable


def test_per_project_weight_ordering():
    projects = [
        {"id": "a", "name": "A", "tags": ["go"]},
        {"id": "b", "name": "B", "tags": ["go"], "weight": 2.0},
    ]
    spec = _spec(must_haves=["Go"])  # both match equally; weight breaks the tie
    top = rank.rank_projects(projects, spec, top=2)
    assert [p["id"] for p in top] == ["b", "a"]


def test_pin_includes_low_scorer():
    out = rank.tailor(_spec(), PROFILE, PROJECTS, ranking={"pinned": ["gitpress"]})
    assert "gitpress" in {p["id"] for p in out["top_projects"]}


def test_exclude_drops_top_scorer():
    spec = _spec(must_haves=["Kubernetes"], stack=["Cilium"])
    assert "k3d" in {p["id"] for p in rank.tailor(spec, PROFILE, PROJECTS)["top_projects"]}
    excl = rank.tailor(spec, PROFILE, PROJECTS, ranking={"excluded": ["k3d"]})
    assert "k3d" not in {p["id"] for p in excl["top_projects"]}


def test_config_overrides_field_weights():
    proj = next(p for p in PROJECTS if p["id"] == "k3d")
    fw = {"must_haves": 1.0, "stack": 2.0, "nice_to_haves": 3.0, "keywords": 1.0, "title": 1.0}
    must = _spec(must_haves=["Kubernetes"])
    nice = _spec(nice_to_haves=["Kubernetes"])
    # With nice_to_haves outweighing must_haves, the relationship flips.
    assert rank.score_project(proj, nice, field_weights=fw) > rank.score_project(proj, must, field_weights=fw)


def test_explicit_clusters_override_derived():
    proj = {"id": "x", "tags": ["kubernetes"], "clusters": ["ml"]}
    assert rank.project_clusters(proj, TAXO, ALIASES) == {"ml"}       # override wins
    derived = {"id": "y", "tags": ["kubernetes"]}
    assert rank.project_clusters(derived, TAXO, ALIASES) == {"platform"}  # derived from tags


def test_invert_aliases_rejects_collision():
    with pytest.raises(ValueError):
        rank.invert_aliases({"go": ["x"], "golang": ["x"]})


def test_taxonomy_file_is_well_formed():
    tax = yaml.safe_load((ROOT / "data" / "taxonomy.yml").read_text())
    rank.invert_aliases(tax.get("aliases", {}))  # raises on a duplicate variant
    for spec in tax.get("clusters", {}).values():
        for tag in spec["tags"]:
            assert isinstance(tag, str) and tag == tag.lower()

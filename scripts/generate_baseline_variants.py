#!/usr/bin/env python3
"""Bootstrap the 5 core static CV variants under data/cv-variants/ using the Anthropic SDK.

Reads data/master-cv.md, data/projects.yml, data/profile.yml, and data/taxonomy.yml,
then calls Anthropic to write a highly polished, cluster-focused CV variant for each.
"""

import os
import pathlib
import sys
import yaml

# Centralize ROOT and load engine modules
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.domains.tailoring import llm


SYSTEM_PROMPT = """You are an expert resume writer and career strategist specializing in software engineering.
Your task is to write a highly polished, tailored CV variant in GitHub-flavored Markdown for a specific engineering specialization.

STRICT CONSTRAINTS:
1. TRUTH ONLY: Use ONLY factual details, dates, employers, metrics, and technologies present in the provided Master CV and Project Catalog. Do NOT invent or extrapolate any facts.
2. STRUCTURE: Include ONLY the following sections in this exact order:
   - ## Experience: Include the 3 roles from the Master CV (Al Hilal Invest, Bluefin Exchange, Seed Labs). Reorder and rephrase the bullet points of each role (truthfully) to heavily emphasize and highlight experience related to the requested target cluster.
   - ## Education: Match exactly the Master CV education (TU Ilmenau and NU Fast).
   - ## Projects: Select and list EXACTLY the 3 specified projects for this cluster. Use the descriptions from the project catalog, slightly tuned if helpful to match the cluster's theme.
   - ## Skills: Order skills so the technical competencies most relevant to the cluster's tags lead the list. Ensure the Languages row is always at the top of the Skills section (English (fluent), Deutsch (A2)).
3. FORMAT:
   - Write a frontmatter block at the very top containing only the tagline, e.g.:
     ---
     tagline: "Senior Cloud Platform Engineer"
     ---
   - Do NOT include any name/contact header or summary paragraph; start the markdown body directly with '## Experience'.
   - Output ONLY the compiled Markdown. Do not include any preamble, introduction, markdown fences, or markdown commentary.
"""

USER_PROMPT = """Specialization Target Cluster: '{cluster_key}'
Cluster Description/Tags: {cluster_tags}
CV Tagline to Use: "{tagline}"

Target projects to include (top 3):
{projects_text}

---

Master CV (Source of Truth):
{master_cv}

---

Please output the completed, highly polished tailored CV variant now. Output ONLY Markdown.
"""


def load_projects_catalog():
    path = ROOT / "data" / "projects.yml"
    if not path.exists():
        return []
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("projects", [])


def load_master_cv():
    path = ROOT / "data" / "master-cv.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main():
    print("Loading source files...", file=sys.stderr)
    master_cv = load_master_cv()
    projects_catalog = load_projects_catalog()
    
    # 5 variants definitions mapping to taxonomy clusters
    variants_defs = [
        {
            "key": "platform-cloud-native",
            "tagline": "Senior Cloud Platform Engineer",
            "tags": "kubernetes, cilium, ebpf, helm, docker, gitops, devops, infra, platform, sre, networking",
            "projects": ["irs-platform", "cv-tailor", "second-brain"]
        },
        {
            "key": "ml-ai",
            "tagline": "AI & MLOps Platform Engineer",
            "tags": "ml, ai, llm, rag, mlops, kubeflow, kserve, pgvector, vector-search, data-science, python",
            "projects": ["second-brain", "cv-tailor", "oran-aiml"]
        },
        {
            "key": "distributed-systems",
            "tagline": "Senior Backend & Distributed Systems Engineer",
            "tags": "distributed, microservices, grpc, nats, event-driven, messaging, mcp, backend, go",
            "projects": ["irs-platform", "second-brain", "cv-tailor"]
        },
        {
            "key": "data-persistence",
            "tagline": "Senior Data Platform Engineer",
            "tags": "database, sql, postgresql, data, persistence, etl, analytics, charts, snowflake, bigquery",
            "projects": ["irs-platform", "second-brain", "cv-tailor"]
        },
        {
            "key": "5g-oran",
            "tagline": "Senior O-RAN & Systems Engineer",
            "tags": "5g, oran, ric, telecom, sdn, multus, open5gs, srsran",
            "projects": ["oran-testbed", "srsran-testbed", "oran-aiml"]
        }
    ]

    out_dir = ROOT / "data" / "cv-variants"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating 5 CV variants into {out_dir}...", file=sys.stderr)
    for variant in variants_defs:
        key = variant["key"]
        print(f"  * Generating '{key}' variant ({variant['tagline']})...", file=sys.stderr)
        
        # Build projects text from catalog
        p_list = []
        for pid in variant["projects"]:
            proj = next((p for p in projects_catalog if p.get("id") == pid), None)
            if proj:
                p_list.append(f"- **{proj.get('name')}** — {proj.get('summary')}")
        projects_text = "\n".join(p_list)

        user_content = USER_PROMPT.format(
            cluster_key=key,
            cluster_tags=variant["tags"],
            tagline=variant["tagline"],
            projects_text=projects_text,
            master_cv=master_cv
        )

        try:
            # We call stream_text for reliable prose generation
            raw_markdown = llm.stream_text(SYSTEM_PROMPT, user_content, max_tokens=6000)
            
            # Format filename
            filename = f"{key}.md"
            if key == "5g-oran":
                filename = "telecom-5g-oran.md"
                
            out_file = out_dir / filename
            
            # Prepend standard tagline block if missing
            if not raw_markdown.startswith("---"):
                raw_markdown = f"---\ntagline: \"{variant['tagline']}\"\n---\n\n" + raw_markdown
                
            out_file.write_text(raw_markdown.strip() + "\n", encoding="utf-8")
            print(f"    ✅ Saved to {out_file}", file=sys.stderr)
        except Exception as e:
            print(f"    ❌ Failed to generate '{key}': {e}", file=sys.stderr)
            sys.exit(1)

    print("\n🎉 CV variant bootstrapping complete! 5 variant files are saved in 'data/cv-variants/'", file=sys.stderr)


if __name__ == "__main__":
    main()

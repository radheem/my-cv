# Specification: Taxonomy Realignment & Cover Letter Structure Update

## Overview
This track modernizes the application generation engine by realigning the core taxonomy into 5 distinct, newly defined clusters (`information-management`, `ai-ml`, `platform-engineer`, `distributed-system`, `telecommunication`). Concurrently, the Cover Letter generation prompt will be updated to shift from a 3-heading format to a modern, punchy 2-heading structure (`Why [Company]?` and `Why me?`), blending logistical details (timing, availability, authorization) naturally into the first two paragraphs.

## Functional Requirements
### 1. Taxonomy & Config Realignment
- Update `data/taxonomy.yml` to define the 5 new clusters:
  - `information-management`: database, sql, postgresql, data, persistence, etl, analytics, charts, scrapers, webscraping, transactional, datalake, design
  - `ai-ml`: ml, ai, llm, rag, mlops, kubeflow, kserve, pgvector, vector-search, inference, model-training, deployment, agentic, agents, training
  - `platform-engineer`: kubernetes, cilium, ebpf, helm, docker, gitops, devops, platform, sre, networking, dns, cloud, observability, monitoring, metrics, tracing, reliability
  - `distributed-system`: distributed, microservices, grpc, nats, event-driven, messaging, mcp, backend, fullstack, web, react, node, api, architecture
  - `telecommunication`: 5g, oran, telecom, sdn, multus, open5gs, radio, ran, wireless
- Update `engine/shared/config.py` to map these 5 new cluster keys to `.md` files matching their names.

### 2. Automated Baseline Variant Regeneration
- Update `scripts/generate_baseline_variants.py` with the new cluster keys, taglines, and associated tags.
- Execute the script to securely wipe the old baseline CV variants and generate the 5 new optimized `.md` files in `data/cv-variants/`.
- Ensure old variant markdown files (e.g., `platform-cloud-native.md`) are deleted from git and disk.

### 3. Cover Letter Prompt Update
- Update `data/prompts/cover.md` to enforce a strict 2-heading structure:
  - `## 1. Why [Company]?`: Must include motivation *and* career timing fit.
  - `## 2. Why me?`: Must include technical proof points *and* seamlessly weave in availability/work authorization at the end.
- Explicitly remove any instructions referring to `## 3. Why now?`.

## Non-Functional Requirements
- Ensure tests still pass (e.g., `tests/test_variants.py`, `tests/test_analysis.py`) after renaming the clusters.
- The changes must be backwards-compatible for existing generated applications (we only affect future `.md` generation and ranking).

## Acceptance Criteria
- `data/cv-variants/` contains exactly 5 files matching the new cluster names.
- Running `cv-tailor analyze <slug>` correctly categorizes skills into the new clusters.
- Generating a new cover letter (`cv-tailor new <slug>`) results in exactly 2 H2 headings with no trailing "Why Now" section.
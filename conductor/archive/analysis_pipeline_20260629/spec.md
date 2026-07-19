# Specification: Composable Clustered Analysis Pipeline & Keyword Gap Analyzer

## Overview
Create a decoupled, composable data pipeline that extracts domain-specific market signals from saved job descriptions and feeds them into distinct, actionable consumers. Instead of treating all jobs equally, extraction is scoped to specific taxonomy clusters (e.g., `ml-ai`, `platform-cloud-native`). This ensures that the extracted technical skills, frameworks, and thematic phrases represent the distinct "signal" of a target engineering domain. 

## Functional Requirements
### Stage 1: The Extractor (Domain Signal Generation)
- **Dynamic Cluster Filtering:** Calculate cluster match scores in real-time across the jobs database using the existing ranking engine to dynamically identify the top jobs belonging to a requested cluster.
- **Taxonomy-Aware Noise Reduction:** Compute term frequencies but utilize `taxonomy.yml` to protect known core skills, ensuring that highly popular core skills (like "Python" or "Kubernetes") are not accidentally filtered out as "global noise".
- **Standardized JSON Output:** The extractor must yield a structured JSON payload representing the domain contract. This payload must include `analysis_metadata`, `domain_signals` (categorized by language, framework, database, etc.), `thematic_phrases`, and `unmapped_market_terms`.

### Stage 2: The Consumers
- **Consumer A (Gap Analyzer):** Takes the Extractor's JSON output and compares the `domain_signals` against the frontmatter and project bullets of the corresponding static CV variant (e.g., `ml-ai.md`). It produces a markdown report detailing which high-frequency market terms are missing from the CV.
- **Consumer B (Taxonomy Sync):** Analyzes the `unmapped_market_terms` from the JSON payload. If a term's frequency exceeds a predefined threshold (e.g., >15%), it generates a structured suggestion to add the term to the appropriate cluster in `taxonomy.yml`.

### Interface Requirements
- **Hybrid Invocation:** 
  - The pipeline must be executable via the CLI (e.g., `cv-tailor analyze --cluster ml-ai`).
  - The pipeline and its consumers must also be registered as MCP tools in `engine/mcp/server.py` so that LLM agents can trigger gap analyses and taxonomy syncs conversationally.

## Non-Functional Requirements
- **Composability:** The Extractor (Stage 1) must be strictly decoupled from the Consumers (Stage 2) via the standardized JSON contract, allowing future consumers (like Interview Prep generation) to be added without modifying the Extractor.
- **Performance:** Dynamic ranking and TF-IDF extraction across 200+ jobs should execute in under 3 seconds. 

## Acceptance Criteria
- Running the extraction for `platform-cloud-native` successfully identifies "Kubernetes" and "Terraform" as high-frequency signals while filtering out generic words.
- The Gap Analyzer successfully flags missing high-frequency keywords by reading a chosen CV variant from `data/cv-variants/`.
- The Taxonomy Sync identifies an unrecognized popular term (e.g., "vLLM") and suggests adding it.
- Both CLI commands and MCP tool calls correctly trigger the pipeline and return the expected reports.

## Out of Scope
- Implementing the Interview Prep Sheet consumer (Consumer C) in this track.
- Automated, destructive updates to `taxonomy.yml` (suggestions only).
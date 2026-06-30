# Implementation Plan: Composable Clustered Analysis Pipeline

## Phase 1: Core Extractor Logic (Stage 1)
- [ ] Task: Create `engine/domains/tailoring/analysis.py`.
    - [ ] Sub-task: Implement `get_jobs_for_cluster(cluster_key)` to retrieve descriptions for jobs heavily matched to a specific cluster.
    - [ ] Sub-task: Implement TF-IDF or term-frequency algorithm with `taxonomy.yml` awareness to protect core keywords and filter out general noise.
    - [ ] Sub-task: Implement payload generation to structure the output into the standardized JSON schema (`domain_signals`, `unmapped_market_terms`).
- [ ] Task: Write comprehensive unit tests in `tests/test_analysis.py` covering filtering, noise reduction, and payload structuring.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core Extractor Logic' (Protocol in workflow.md)

## Phase 2: Pipeline Consumers (Stage 2)
- [ ] Task: In `engine/domains/tailoring/analysis.py`, implement Consumer A (`gap_analyzer`). It must parse the Stage 1 JSON and the target CV variant Markdown to flag missing high-frequency keywords.
- [ ] Task: In `engine/domains/tailoring/analysis.py`, implement Consumer B (`taxonomy_sync`). It must parse the Stage 1 JSON and format a suggestion string for unrecognized high-frequency terms.
- [ ] Task: Add unit tests for both consumers to `tests/test_analysis.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Pipeline Consumers' (Protocol in workflow.md)

## Phase 3: Hybrid Interfaces (CLI & MCP)
- [ ] Task: Add the `analyze` subcommand to `engine/cli.py` (`cv-tailor analyze --cluster <key>`). It should execute the extractor and optionally the consumers, printing the results to the terminal.
- [ ] Task: In `engine/mcp/server.py`, register a new MCP tool `analyze_cluster_keywords(cluster)`.
- [ ] Task: In `engine/mcp/server.py`, register a new MCP tool `suggest_taxonomy_updates(cluster)`.
- [ ] Task: Add CLI execution logic tests and append MCP tool verification to `tests/test_mcp_e2e_client.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Hybrid Interfaces' (Protocol in workflow.md)

## Phase 4: End-to-End Testing
- [ ] Task: Execute the full `make test` test suite (including MCP E2E tests).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: End-to-End Testing' (Protocol in workflow.md)
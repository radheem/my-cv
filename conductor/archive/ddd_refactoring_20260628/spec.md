# Specification: Domain-Driven Design (DDD) Codebase Restructuring

## Overview
The `engine/` directory currently contains a flat mix of core logic, scraping scripts, and server interfaces. This track will restructure the entire codebase and its documentation to adhere to Domain-Driven Design (DDD) principles. This ensures a composable, extendable structure that adheres strictly to the DRY principle.

## Functional Requirements
1. **Domain Isolation**:
   Isolate the codebase into distinct, autonomous domains under a new folder structure:
   - **`engine/domains/gmail/`**: All logic related to Gmail alert ingestion, parsing, and query workflows.
   - **`engine/domains/linkedin/`**: LinkedIn-specific logic, including Playwright scrapers, session management, and guest API fetching.
   - **`engine/domains/fraunhofer/`**: Fraunhofer-specific scraping, job link extraction, and parsing logic.
   - **`engine/domains/tailoring/`**: Core application generation logic, including LLM interactions, prompts, jobspec extraction, pure ranking, and LaTeX rendering.

2. **Shared Infrastructure**:
   - Create a **`engine/shared/`** domain to house cross-domain infrastructure, including database connections (`db.py`), centralized configurations (`config.py`), and generic HTTP utilities.

3. **Presentation/Interface Layer**:
   - Isolate the MCP Server (`engine/mcp/`) and CLI (`engine/cli.py`) as presentation layers that orchestrate calls across the isolated domains.

4. **Documentation Overhaul**:
   - Create a new **`docs/domains/`** directory.
   - Author dedicated documentation files for each domain (`gmail.md`, `linkedin.md`, `fraunhofer.md`, `tailoring.md`) explaining their bounded contexts, inputs, and outputs.

## Acceptance Criteria
- [ ] Codebase is restructured into `domains/` and `shared/` directories without breaking existing functionality.
- [ ] Imports across the entire project (including `tests/`) are updated to reflect the new DDD paths.
- [ ] The `tests/` directory continues to pass 100% of cases, verifying that decoupling was successful.
- [ ] Documentation is decoupled into `docs/domains/` matching the code structure.

## Out of Scope
- This track is strictly an architectural refactoring. No new scraping features or LLM behaviors will be added.
# Implementation Plan: Domain-Driven Design (DDD) Restructuring

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the `engine/` directory into a Domain-Driven Design (DDD) architecture featuring isolated bounded contexts and dedicated domain documentation.

**Architecture:** We will create a `shared/` layer for infrastructure (DB, config) and a `domains/` layer housing autonomous modules (`gmail`, `linkedin`, `fraunhofer`, `tailoring`). The `mcp/` and `cli.py` components will remain at the root of `engine/` as presentation/interface layers.

---

## Phase 1: Shared Infrastructure Foundation

- [x] Task: Establish the `shared` domain c79a6f8
    - [x] Step 1.1: Create directory `engine/shared/`.
    - [x] Step 1.2: Move `engine/config.py`, `engine/db.py`, and generic utility files to `engine/shared/`.
    - [x] Step 1.3: Run a global search-and-replace to update all import paths pointing to `engine.db` and `engine.config`.
    - [x] Step 1.4: Run the test suite to ensure the database and config layers still load.

- [x] Task: Conductor - User Manual Verification 'Phase 1: Shared Infrastructure Foundation' (Protocol in workflow.md)


## Phase 2: Domain Isolation

- [ ] Task: Establish `gmail`, `linkedin`, and `fraunhofer` domains
    - [ ] Step 2.1: Create directories under `engine/domains/` for each specific domain.
    - [ ] Step 2.2: Move `engine/gmail.py` and related ingest workflows to `engine/domains/gmail/`.
    - [ ] Step 2.3: Move the existing `engine/linkedin/` and `engine/fraunhofer/` directories inside `engine/domains/`.
    - [ ] Step 2.4: Update global imports pointing to these files.

- [ ] Task: Establish the `tailoring` domain
    - [ ] Step 2.5: Create `engine/domains/tailoring/`.
    - [ ] Step 2.6: Move `engine/rank.py`, `engine/llm.py`, `engine/render.py`, `engine/latex.py`, `engine/jobspec.py`, and `engine/prompts.py` to the `tailoring` domain.
    - [ ] Step 2.7: Update global imports pointing to these files.

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Domain Isolation' (Protocol in workflow.md)


## Phase 3: Presentation Layer & Testing

- [ ] Task: Update Interfaces and Test Suite
    - [ ] Step 3.1: Update import statements in `engine/cli.py` to route through the new `domains.` and `shared.` paths.
    - [ ] Step 3.2: Update import statements in `engine/mcp/server.py` and `engine/mcp/sqlguard.py`.
    - [ ] Step 3.3: Recursively update imports in the entire `tests/` directory.
    - [ ] Step 3.4: Run the full `pytest` suite and resolve any lingering ModuleNotFound errors until 100% passing.

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Presentation Layer & Testing' (Protocol in workflow.md)


## Phase 4: Documentation Structure

- [ ] Task: Create Domain-Specific Documentation
    - [ ] Step 4.1: Create directory `docs/domains/`.
    - [ ] Step 4.2: Create `docs/domains/gmail.md` detailing the Gmail alert ingestion and discovery bounded context.
    - [ ] Step 4.3: Create `docs/domains/linkedin.md` detailing the scraping and session handling context.
    - [ ] Step 4.4: Create `docs/domains/fraunhofer.md` detailing the Fraunhofer scraping context.
    - [ ] Step 4.5: Create `docs/domains/tailoring.md` detailing the core ranking, LLM generation, and LaTeX compilation logic.

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Documentation Structure' (Protocol in workflow.md)
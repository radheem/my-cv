# Implementation Plan: 5 Core Static CV Variants

## Phase 1: Storage & Configuration
- [x] Task: Create the `data/cv-variants/` directory. (a944791)
- [x] Task: Update `engine/shared/config.py` (or similar configuration file) to include a mapping dictionary that links the taxonomy cluster keys (e.g., `ml-ai`) to their respective static markdown filenames (`ml-ai.md`). (a944791)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Storage & Configuration' (Protocol in workflow.md)

## Phase 2: Selection Engine Implementation
- [ ] Task: Create a new module or function (e.g., in `engine/rank.py` or `engine/workflows/application_actions.py`) named `select_best_cv_variant`.
    - [ ] Sub-task: Implement logic to read the cluster ranking scores for a job description.
    - [ ] Sub-task: Implement deterministic single-winner selection.
    - [ ] Sub-task: Implement the LLM tie-breaker logic. The prompt must inject the JD and the list of tied variant names, and extract the single best match.
    - [ ] Sub-task: Implement the explicit "Fail & Alert" fallback if the LLM call fails or returns an invalid option.
- [ ] Task: Write unit tests verifying deterministic selection, tie-breaker prompting, and failure fallbacks.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Selection Engine Implementation' (Protocol in workflow.md)

## Phase 3: Application Pipeline Integration
- [ ] Task: Refactor the `new` application generation command (likely `engine/cli.py` -> `cmd_new` or the underlying generative workflow).
    - [ ] Sub-task: Replace the full LLM CV generation step with a file copy from `data/cv-variants/<selected>.md` to `applications/<slug>/cv.md`.
    - [ ] Sub-task: Implement dynamic `tagline` retitling: parse the frontmatter of the copied file and overwrite the tagline with the target job title.
    - [ ] Sub-task: Update the cover letter generation prompt to use the text of the *selected static variant* as its factual context, instead of the generic `master-cv.md`.
- [ ] Task: Fix and update all relevant unit and integration tests to account for the new static-copy behavior.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Application Pipeline Integration' (Protocol in workflow.md)

## Phase 4: Initial Baseline Setup
- [ ] Task: Write a utility script `scripts/generate_baseline_variants.py` that utilizes the Anthropic API to read `data/master-cv.md` and dynamically generate the first draft of the 5 variant markdown files into `data/cv-variants/`.
- [ ] Task: Execute the script to bootstrap the variants.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Initial Baseline Setup' (Protocol in workflow.md)

## Phase 5: End-to-End Testing
- [ ] Task: Execute the full `make test` test suite (including MCP E2E tests).
- [ ] Task: Conductor - User Manual Verification 'Phase 5: End-to-End Testing' (Protocol in workflow.md)
# Implementation Plan: Landing Page CV & Scannable Cover Letter Optimization

## Phase 1: Prompt Restructuring
- [x] Task: Update `data/prompts/cv.md` with instructions for strict "landing page" constraints (max 3 bullets for recent roles, 2 for older roles, exactly 2-3 concise bullets per project). Emphasize ruthless brevity.
- [x] Task: Update `data/prompts/cover.md` to lower the target word count to ~150-250 words and enforce a 3-bullet-point list structure under `## 2. Why me?`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Prompt Restructuring' (Protocol in workflow.md)

## Phase 2: Variant Baseline Regeneration
- [x] Task: Run `uv run python scripts/generate_baseline_variants.py` to prompt the LLM to regenerate the 5 baseline `.md` CV variants using the new ultra-concise prompt rules.
- [x] Task: Review the newly generated variants to ensure they comfortably fit the page budget.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Variant Baseline Regeneration' (Protocol in workflow.md)
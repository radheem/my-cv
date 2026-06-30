# Implementation Plan: Taxonomy Realignment & Cover Letter Structure Update

## Phase 1: Taxonomy & Configuration Updates
- [x] Task: Update `data/taxonomy.yml` to replace the old clusters with the 5 new clusters (`information-management`, `ai-ml`, `platform-engineer`, `distributed-system`, `telecommunication`) and their associated tags.
- [x] Task: Update `engine/shared/config.py` `cv_variants` mapping to point the new cluster keys to the corresponding `.md` filenames.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Taxonomy & Configuration Updates' (Protocol in workflow.md)

## Phase 2: Variant Baseline Regeneration
- [x] Task: Update `scripts/generate_baseline_variants.py` with the new cluster keys, taglines, and tag structures.
- [x] Task: Delete the 5 old `.md` files from `data/cv-variants/` using `git rm`.
- [x] Task: Run `uv run python scripts/generate_baseline_variants.py` to prompt the LLM to generate the 5 new optimized markdown files.
- [x] Task: Commit the new markdown files.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Variant Baseline Regeneration' (Protocol in workflow.md)

## Phase 3: Cover Letter Prompt & Tests Adjustment
- [x] Task: Update `data/prompts/cover.md` to remove `## 3. Why now?` and merge its concepts into `## 1` and `## 2`. Update German fallback instructions similarly.
- [x] Task: Update `tests/test_variants.py` to mock/use the new cluster names (`platform-engineer`, `information-management`, etc.) instead of the old ones.
- [x] Task: Update `tests/test_analysis.py` to assert against the new cluster names.
- [x] Task: Update `tests/test_mcp_server.py` to use `platform-engineer` instead of `platform-cloud-native`.
- [x] Task: Run `make test` to ensure the entire suite is stable.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Cover Letter Prompt & Tests Adjustment' (Protocol in workflow.md)
# Implementation Plan: Centralize Prompts and Refactor Rendering Engine

## Phase 1: Create and Refine Prompt Templates on Disk
- [x] **Task: Create CV Prompt Template** (d5722da)
    - [x] Create `data/prompts/cv.md` incorporating the legacy CV guides and strict layout constraints. (d5722da)
- [x] **Task: Create Cover Letter Prompt Template with Subtle Tone Constraints** (d5722da)
    - [x] Create `data/prompts/cover.md` incorporating the H2 question structure, logistics closing, and the new subtle alignment / anti-hyperbole rules. (d5722da)
- [x] **Task: Create Translation Prompt Template** (d5722da)
    - [x] Create `data/prompts/translate.md` incorporating the German translation guidelines. (d5722da)
- [x] **Task: Update Main Prompts Configuration** (d5722da)
    - [x] Modify `data/config.yml` to map `cv`, `cover`, and `translate` to their respective new disk files. (d5722da)
- [x] **Task: Delete Deprecated Legacy Guides** (d5722da)
    - [x] Delete `data/guides/how-to-write-a-cv.md` and `data/guides/how-to-write-a-cover-letter.md` from disk. (d5722da)
- [x] **Task: Conductor - User Manual Verification 'Phase 1: Create and Refine Prompt Templates on Disk' (Protocol in workflow.md)** (d5722da)

## Phase 2: Refactor Rendering Engine (render.py and manifest.py)
- [ ] **Task: Refactor CV and Cover Letter Rendering Core**
    - [ ] Update `render_cv()` in `engine/domains/tailoring/render.py` to load `"cv"` from disk, remove hardcoded fallback, and stop guide file injection.
    - [ ] Update `render_cover_letter()` in `engine/domains/tailoring/render.py` to load `"cover"` from disk, remove hardcoded fallback, and stop guide file injection.
- [ ] **Task: Refactor Translation Core**
    - [ ] Update `translate_markdown()` in `engine/domains/tailoring/render.py` to load `"translate"` from disk and remove the old hardcoded `_TRANSLATE_SYSTEM` fallback.
- [ ] **Task: Refactor Manifest Logging**
    - [ ] Update `engine/manifest.py` to reference `_CV_SYSTEM_FALLBACK`, `_COVER_SYSTEM_FALLBACK`, and `_TRANSLATE_SYSTEM_FALLBACK` from `render.py`.
    - [ ] Update manifest build dictionary to log `translate` prompt metadata.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: Refactor Rendering Engine (render.py and manifest.py)' (Protocol in workflow.md)**

## Phase 3: Refactor Core Data Loader (cli.py), Caller Adjustments, and TDD/E2E Verification
- [ ] **Task: Refactor CLI Data Loader**
    - [ ] Refactor `_load_data()` in `engine/cli.py` to remove the deprecated guides, change signature to return 5 elements: `profile, projects, master_cv, taxonomy, ranking`.
- [ ] **Task: Refactor Callers and Tests to Match New Signature**
    - [ ] Update all references to `_load_data` in `engine/cli.py` to match the 5-element signature.
    - [ ] Update test files `tests/test_variants.py`, `tests/test_analysis.py`, and `tests/experiments/run.py` to match the 5-element signature.
- [ ] **Task: Run Test Suite and Verify Correctness (TDD Verification)**
    - [ ] Run the complete test suite `uv run --no-sync python3 -m pytest` and resolve any signature, compilation, or mock issues.
- [ ] **Task: Perform End-to-End Visual & Tone Verification**
    - [ ] Run a test application generation to verify that cover letters are generated with the new subtle, mature engineering tone with zero dramatic clichés.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: Refactor Core Data Loader (cli.py), Caller Adjustments, and TDD/E2E Verification' (Protocol in workflow.md)**

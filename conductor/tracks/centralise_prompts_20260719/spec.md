# Specification: Centralize Prompts and Refactor Rendering Engine

## 1. Overview
This track addresses the duplication, maintenance drift, and tone hyperbole of the LLM prompts. By establishing a strict separation of concerns, we will separate prompt templates on disk, completely eliminate multi-line hardcoded string prompts from Python, and discard deprecated external guides. Additionally, we will introduce subtle alignment constraints to prevent emotional hyperbole in cover letters, aligning candidate aspirations with the company's mission, tech stack, and goals in a mature, professional manner.

## 2. Functional Requirements
1. **Separated Disk-Based Templates:**
   - Create `data/prompts/cv.md` as the single source of truth for tailoring CVs.
   - Create `data/prompts/cover.md` as the single source of truth for tailoring Cover Letters.
   - Create `data/prompts/translate.md` as the single source of truth for German translation of CVs/letters.
2. **Remove Hardcoded Fallback Prompts:**
   - Remove `_CV_SYSTEM`, `_COVER_SYSTEM`, and `_TRANSLATE_SYSTEM` multiline strings from `engine/domains/tailoring/render.py`.
   - Update `render_cv()`, `render_cover_letter()`, and `translate_markdown()` to load their respective prompts from disk.
   - Add simpler, single-string in-code fallback system prompts in case files are missing.
3. **Discard Guide Files:**
   - Delete `data/guides/how-to-write-a-cv.md` and `data/guides/how-to-write-a-cover-letter.md` from disk.
   - Refactor `_load_data()` in `engine/cli.py` to stop loading these files and remove them from the function signature and returned tuple.
   - Update all callers of `_load_data()` (e.g. in `tests/`, `cli.py`, `experiments/run.py`) to match the new signature (returning 5 elements: `profile, projects, master_cv, taxonomy, ranking` instead of 7).
   - Refactor `render_cv` and `render_cover_letter` in `render.py` to remove the `guide` argument from their signatures and stop injecting guides.
   - Update `_INPUT_FILES` in `engine/manifest.py` to remove the guides from input hashes.
4. **Tone Refinement and Guidelines Integration:**
   - Merge the essential CV guidelines into `data/prompts/cv.md` and Cover Letter guidelines into `data/prompts/cover.md`.
   - In `data/prompts/cover.md`, add the anti-hyperbole rules and professional engineering-driven alignment guidelines to produce a subtle, mature, peer-to-peer tone.

## 3. Non-Functional Requirements
- Maintain complete compatibility with the bilingual LaTeX rendering system.
- Maintain deterministic JSON and text output temperature handling.
- Reduce input token usage by up to 500 tokens per call by dropping redundant guide files.

## 4. Acceptance Criteria
1. The 3 prompt files (`cv.md`, `cover.md`, `translate.md`) are successfully created on disk under `data/prompts/`.
2. The legacy guide files are completely removed from the file system.
3. All python modules compile and pass `uv run --no-sync python3 -m pytest` with 100% success (all unit tests green).
4. Running the live pipelines or evaluation harnesses confirms correct generation.
5. Cover letters generated using the new prompt show zero occurrences of high-emotional clichés (e.g., "goal in life", "precisely what I want to accomplish") and instead use mature alignment statements.

## 5. Out of Scope
- Modifying `jobspec.md`, `judge.md`, or `variant.md` prompt files.

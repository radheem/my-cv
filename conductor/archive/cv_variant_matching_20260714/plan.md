# Implementation Plan: CV Variant Matching Overhaul

This plan details the technical steps to fulfill the `spec.md` requirements for LLM-based variant selection and manual override capabilities.

## Phase 1: LLM-Based Summarization & Matching Engine
*Goal: Replace the heuristic token overlap logic with a more context-aware LLM classifier.*

1. **Update Prompt Modules (`engine/domains/tailoring/prompts.py` & `engine/manifest.py`)**
   - Create a new default system prompt `_VARIANT_SELECTION_SYSTEM` instructing the LLM to summarize the job description and output a JSON dictionary: `{"summary": "...", "cluster": "..."}`.
   - Define a JSON schema `VARIANT_SELECTION_SCHEMA` for the structured LLM output.

2. **Refactor Variant Engine (`engine/domains/tailoring/variants.py`)**
   - Delete the `score_job_clusters` heuristic function.
   - Write a new function: `match_cluster_via_llm(job_text: str, taxonomy: dict) -> tuple[str, str]` (returns summary, cluster_name).
     - Construct a user prompt injecting the `job_text` and the list of available clusters from the taxonomy (e.g., `- telecommunication: [tags]`, `- ai-ml: [tags]`).
     - Call `llm.structured_json()` using the new prompt and schema.
   - Refactor `select_best_cv_variant()` to call `match_cluster_via_llm()`.
     - Map the selected cluster to the filenames defined in `cv_variants`.
     - Log the LLM's summary and the chosen file.
     - Return the variant filename.

## Phase 2: CLI Override Parameter
*Goal: Plumb a manual bypass through the CLI into the tailoring pipeline.*

1. **Update Argument Parser (`engine/cli.py`)**
   - In `_build_parser()`, under the `new` subparser, add an optional argument: `--variant`.
     - `help="Manual override for the CV variant filename (e.g. ai-ml.md). Bypasses automatic taxonomy selection."`

2. **Plumb Override to Execution (`engine/cli.py`)**
   - In `cmd_new(args, _get_jobs_dir, _apply_provider_flags)`:
     - Check if `args.variant` is set.
     - If true, validate the file exists at `ROOT / "data" / "cv-variants" / args.variant`. If missing, `raise SystemExit`.
     - If false (or not provided), execute the newly refactored `variants.select_best_cv_variant(spec, job_text, taxonomy, aliases_flat)`.
     - Proceed with the generation pipeline using the resulting variant filename.

## Phase 3: MCP Visibility & Override Tools
*Goal: Expose the new capabilities to the LLM agent workflow.*

1. **Add `preview_cv_variant` Tool (`engine/mcp/server.py`)**
   - **Signature:** `@mcp.tool() def preview_cv_variant(slug: str) -> str`
   - **Logic:**
     - Query DB to verify the slug exists.
     - Read the raw job text from `/app/vault/jds/{slug}.txt`.
     - Load the taxonomy and `cv_variants` map from config.
     - Call `match_cluster_via_llm()` directly.
     - Return a JSON formatted string containing the `summary`, `selected_cluster`, and `predicted_variant_file`.

2. **Add `create_application_with_variant` Tool (`engine/mcp/server.py`)**
   - **Signature:** `@mcp.tool() def create_application_with_variant(slug: str, variant_filename: str) -> str`
   - **Logic:**
     - Identical guardrails to `create_application_from_job` (check DB, ensure not currently building).
     - Submit a tuple to the global `_tailor_queue` containing the override flag: `(slug, variant_filename)`.

3. **Update Tailor Worker (`engine/mcp/server.py`)**
   - Modify `_tailor_consumer_worker()` to unpack the queue tuple correctly.
   - If `variant_override` is provided, append `--variant {variant_override}` to the `cv-tailor new ...` subprocess command execution.

## Phase 4: Testing & Verification
*Goal: Ensure the pipeline remains stable and the new features function as intended.*

1. **Unit Tests:** Update or remove legacy tests in `tests/test_variants.py` that relied on the deterministic `score_job_clusters` overlap logic. Mock the new `match_cluster_via_llm` function.
2. **Integration Tests:** Ensure `test_cli_paths.py` and application generation e2e tests account for the LLM selection or use the `--variant` bypass to isolate test steps.
3. **Manual Verification:** Execute `uv run cv-tailor new <slug> --variant telecommunication.md` and verify the output uses the forced template. Run the MCP server and test both new tools.
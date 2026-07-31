# Specification: CV Variant Matching Overhaul

## Objective
Replace the heuristic, token-overlap-based CV variant selection with an LLM-summarization approach. Introduce MCP tools to allow user preview and manual override of the CV variant selection before expensive LaTeX generation and artifact processing begins.

## Requirements

### 1. LLM-Based Summarization and Matching
- **Input:** Raw job description text (`job_text`) and the parsed `taxonomy` (specifically the `clusters` mapping).
- **Process:** The LLM must generate a concise summary of the job description and then use that summary to classify the job into exactly one of the `clusters` defined in `data/taxonomy.yml`.
- **Output:** A JSON object containing the `summary` string and the string name of the selected `cluster`.
- **Integration:** The output of this function replaces the pure-Python heuristic overlap logic currently used in `select_best_cv_variant`.

### 2. Manual CLI Override
- The `cv-tailor new` command must accept a new optional argument: `--variant <filename>` (e.g., `--variant telecommunication.md`).
- If `--variant` is provided, the system skips all automatic variant selection logic (including LLM calls) and strictly uses the provided filename.
- The pipeline must validate that the provided file actually exists in `data/cv-variants/` before proceeding.

### 3. MCP Visibility Tool: `preview_cv_variant`
- **Purpose:** Allow the user to run the LLM selection logic *without* running the full application generation pipeline.
- **Parameters:** `slug: str`
- **Behavior:** Loads the raw job text for the given slug, runs the LLM summarization and matching, and returns the generated summary, the winning cluster, and the mapped variant filename.

### 4. MCP Override Tool: `create_application_with_variant`
- **Purpose:** Allow the user to bypass the automatic selection from within an agent context.
- **Parameters:** `slug: str`, `variant_filename: str`
- **Behavior:** Operates identically to `create_application_from_job`, but sends the `variant_filename` to the backend worker, which in turn invokes the CLI with the new `--variant` flag.

## Constraints & Security
- The LLM summarization prompt must mandate strict adherence to the provided taxonomy. It cannot hallucinate new cluster names.
- The backend must validate that manual variant overrides exist in the local filesystem (`data/cv-variants/`) to prevent directory traversal or file-not-found crashes during the pipeline execution.
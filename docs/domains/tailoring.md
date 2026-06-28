# Bounded Context: Application Tailoring & Generation Domain

## Overview
The `tailoring` domain is the generative and mathematical core of `cv-tailor`. It is responsible for parsing raw job descriptions into structured requirements, deterministically ranking career facts (skills and projects) to maximize relevance, orchestrating LLM-based CV/Cover letter prose compilation, and rendering compile-ready LaTeX PDFs bilingually.

## Domain Boundaries
*   **Included Concerns**:
    *   Extracting core requirements into structured `JobSpec` schemas using LLMs.
    *   Deterministically scoring and selecting top projects/skills based on the JobSpec.
    *   Injecting factual master CV files and profiles into Jinja2 prompts.
    *   Running LLM prose generations (Anthropic/Ollama) strictly bound to factual inputs.
    *   Translating Markdown text bilingually and compiling raw LaTeX code into high-fidelity PDFs.
    *   Emitting run-reproducibility manifests and validating build regression gates.
*   **Excluded Concerns**:
    *   Web scraping or email ingestion (handled by crawler and `gmail` domains).
    *   Exposing command lines or network tools (handled by CLI and MCP interfaces).

## Core Components
1.  **`jobspec.py` (Requirement Extractor)**:
    *   Leverages LLMs to extract keywords, skills, and organizational parameters from a job posting.
2.  **`rank.py` (Deterministic Ranker)**:
    *   **Core Principle:** Pure, 100% unit-tested, offline-capable ranking engine.
    *   Scores your portfolio projects against the jobspec without using an LLM, guaranteeing factual selection.
3.  **`render.py` (Prose Generator)**:
    *   Fills Jinja2 prompts with ranked facts, profile details, and exemplars.
    *   Calls the LLM to write the final tailored Markdown text.
4.  **`latex.py` (PDF Compiler)**:
    *   Transforms Markdown bilingually and runs local `latexmk` compilations.
5.  **`llm.py` (API Client Wrapper)**:
    *   Resolves configuration hierarchies (env > file > defaults) for OpenAI-compatible/Anthropic endpoints.
6.  **`prompts.py` (Jinja2 Loader)**:
    *   Manages Jinja2 prompt layouts and unescaped/escaped helper templates.

## Inputs & Outputs
*   **Inputs**:
    *   `raw_text` (string): Cleaned plain text of a job description.
    *   `master-cv.md` / `projects.yml` / `profile.yml`: Personal portfolio files (loaded from `data/`).
*   **Outputs**:
    *   Tailored CV Markdown (`cv.md`, `cv.de.md`).
    *   Tailored Cover Letter Markdown (`cover-letter.md`, `cover-letter.de.md`).
    *   Bilingual LaTeX PDFs compiled inside `applications/<slug>/`.

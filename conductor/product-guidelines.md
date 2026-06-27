# Product Guidelines

## Core Principles
1. **Automation Over Configuration:** The tool should aim to minimize manual intervention. Given a URL or alert, the pipeline should seamlessly generate, render, and track applications with sensible defaults.
2. **Impeccable Output Quality:** The generated LaTeX PDFs act as a professional proxy for the user. Formatting, grammar, and bilingual translations must be pristine, visually appealing, and highly legible.
3. **Data Isolation & Privacy:** Private application data (scraped JDs, generated CVs, company information) must strictly reside in `.gitignore`'d directories or local databases and must never be exposed via the MkDocs build.
4. **Resiliency & Fault Tolerance:** The CLI and background services (like MCP integrations) should gracefully handle network timeouts, missing front matter, or LLM generation failures without crashing the overall tracking state.

## CLI & Output UX
- **Concise Reporting:** CLI outputs should be quiet by default, emitting clear, actionable logs on successful completion or explicit errors when LLM/LaTeX builds fail.
- **Predictable Commands:** Command structure should follow a standard noun-verb or verb-noun paradigm (e.g., `cv-tailor new <url>`, `cv-tailor pdf <slug>`).
- **Idempotency:** Re-running commands (like `cmd_pdf` or `cmd_status`) should be safe and result in a consistent state without duplicating tracked data.

## Code Quality & Architecture
- **Modularity:** Maintain strict separation between core engine logic (LLM integrations, fetching), CLI wrappers, LaTeX builders, and web integrations (Apps Script, Google Drive).
- **Type Safety & Testing:** Leverage Python type hints heavily across the core engine. All workflows and data migrations must be verified by the `pytest` suite.
- **Portability:** Allow local dependencies to be substituted safely (e.g., preferring local TeX Live Docker containers to avoid forcing system-level `latexmk` dependencies on new machines).
# Technology Stack

## Core Technologies
- **Programming Language:** Python (>=3.12)
- **Database:** Local file-based DuckDB (using `duckdb>=1.0.0`)

## Document & Site Generation
- **Templating:** Jinja2
- **Data Parsing:** PyYAML (`pyyaml>=6`)
- **Document Output:** LaTeX (rendered locally via `latexmk` or via TeX Live Docker image)
- **Static Site Generator:** MkDocs with Material theme (`mkdocs-material>=9.5`, `markdown>=3.6`)

## Integrations & Automation
- **LLM Integrations:** Anthropic API (default) / Local Ollama support
- **Web Scraping:** Playwright (optional, for scraping dynamic job postings)
- **Cloud Integrations:** Google Drive via Google Apps Script (for PDF upload and tracking sync)

## Architecture
- **Structure:** Monolithic Python CLI application (`cv-tailor`)
- **Hosting:** GitHub Pages (for the public portfolio), local execution for the engine.
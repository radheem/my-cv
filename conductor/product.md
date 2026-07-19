# Initial Concept
The `cv-tailor` project is a localized Python CLI tool and static site generator that fully automates the job application tailoring process. Its primary goal is to generate job-tailored CVs and cover letters, render them as bilingual LaTeX PDFs, store them securely in Google Drive, track application statuses locally (via DuckDB), and maintain a public-facing MkDocs portfolio hosted on GitHub Pages.

# Target Audience
- **Primary User:** The project creator (Radheem Bin Razi), utilizing the tool for managing a highly efficient, automated personal job application process.
- **Secondary Audience:** Hiring managers and technical recruiters interacting with the generated PDFs or the public GitHub Pages portfolio.

# Core Value Proposition
- **High-Volume Personalization:** Allows the user to rapidly adapt a master CV and cover letter contextually using LLMs (Anthropic/Ollama) to fit specific job descriptions.
- **Data Privacy & Security:** Keeps application data (companies applied to, tailored responses) completely private within local Git tracking and a local database, while safely publishing *only* generic portfolio data to the public internet.
- **Professional Presentation:** Outputting cleanly typeset, bilingual (English/German) LaTeX documents that stand out to employers without the manual typesetting overhead.
- **Modular & Unified Pipeline:** Supports both a unified pipeline and a modular, on-demand trilogy (listing, detailed extraction, and application creation) to support interactive and incremental agent use.

# Key Features
1. **JD Ingestion & Scoring:** Scrapes job descriptions from URLs or Gmail alerts, evaluates them against the user profile, and stores them in a local DuckDB database file.
2. **AI-Assisted Tailoring:** Leverages LLMs and Jinja2 templates to rewrite prose, optimizing the CV/cover letter for the ingested JD requirements.
3. **Bilingual Support:** Automatically generates both English (`.md`) and German (`.de.md`) tailored artifacts.
4. **LaTeX to PDF Rendering:** Transforms Markdown content into polished `.tex` and `.pdf` files utilizing local `latexmk` or a Docker-based TeX Live environment.
5. **Google Drive Integration:** Uploads completed application packages securely via an Apps Script proxy.
6. **Public Portfolio Generation:** Runs MkDocs to build an attractive, public-facing portfolio website independent of the private job application data.
7. **Interactive Agentic Revision & Queue Control:** Exposes advanced, thread-safe MCP tools to revise existing cover letter/CV drafts via natural-language feedback, trigger on-demand German translations, perform smart full-purge regenerations, and cancel queued tasks in-memory.
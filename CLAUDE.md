# CLAUDE.md — my-cv

Working notes for agents (and humans). This repo is **two things**: a published **public
portfolio** (MkDocs → GitHub Pages at `radheem.github.io/my-cv`) and a private
**job-application workspace** (`applications/`). Remote: `radheem/my-cv`.

> **Commits:** omit the Claude `Co-Authored-By` footer in this repo. Keep credentials / PII
> out of commits. **Private, real data** — `data/` holds real contact details, employers, and
> projects.

## What this is

`cv-tailor` turns a **job posting** into a **tailored CV + cover letter**, then:
- renders them as **bilingual (English + German) PDFs** using a **LaTeX** template
  (`latex/resume.cls` / `latex/coverletter.cls`), the same system as the `resume` repo;
- stores those PDFs in **Google Drive** (one folder per application);
- tracks each application's **status in git** (`applications/<slug>/index.md` front matter + the
  `applications/README.md` table). Commits are the audit trail.

The **public site** publishes only the portfolio (Home, Projects, CV). `applications/` lives
**outside `docs/`** and is never built into the site — so no company name leaks. The only public
PDF is the generic CV (`latex/resume.tex` → `docs/assets/cv.pdf`, compiled in CI).

## The pipeline

```
cv-tailor ingest      → vault/jds/<slug>.txt        (LinkedIn capture; containerized)
cv-tailor new <jd>    → applications/<slug>/         cv.md (+cv.de.md), cover-letter.md (+.de),
                                                     job-description.md, index.md, manifest.json
cv-tailor translate   → cv.de.md / cover-letter.de.md  (German, LLM; run inside `new` by default)
cv-tailor pdf <slug>  → cv.tex/cover-letter.tex → cv.pdf/cover-letter.pdf  (engine/latex.py + latexmk)
cv-tailor upload <slug> → Google Drive (Apps Script); writes drive_url into index.md
cv-tailor status <slug> <state> → edits index.md + refreshes applications/README.md
```

Generation (`new`/`translate`) needs an LLM (Anthropic key or local Ollama) and runs **locally**.
PDF compile uses LaTeX — local `latexmk` or the `texlive/texlive` Docker image (auto-detected by
`scripts/build-application.sh`). CI needs neither — it only builds the portfolio + the public CV.

## How `.tex` is produced

The LLM writes structured **Markdown** (`cv.md` with `## Experience/Education/Projects/Skills`,
`cover-letter.md` paragraphs). **`engine/latex.py`** deterministically converts that Markdown into
LaTeX — it handles escaping, maps the structure onto the class macros (`\role`, `\edu`,
`\project`, `\bullets`; letter `\senderblock`/`\recipient`/`\opening`/`\closing`), and assembles
the **English-then-German** document. **The LLM never emits LaTeX.** German comes from a
translation pass (`render.translate_markdown` → `cv.de.md` / `cover-letter.de.md`), a faithful
translation of the approved English — **never invent facts in either language**.

Bilingual rules (mirroring the `resume` repo): each language is **one page** (so each PDF is 2
pages); **top-3 projects** most relevant first; skills order **Languages → Programming Languages →
tailored tech**; German headings Berufserfahrung / Ausbildung / Projekte / Kenntnisse.

## Status lifecycle

```
draft → applied → interview → offer | rejected | withdrawn
```
Edit via `cv-tailor status <slug> <state>` (regex-edits `index.md`, auto-refreshes the tracker),
then **commit** — the message + date are the record. `applications/README.md` is the at-a-glance
table (regenerate with `cv-tailor track`). One application = one logical commit.

## Layout

| Path | What |
|------|------|
| `data/` | source of truth: `master-cv.md`, `profile.yml`, `projects.yml`, `guides/`, ranking config, prompts |
| `engine/` | `rank` (pure top-3/skills), `jobspec`/`render` (LLM), `latex` (MD→LaTeX), `cli` |
| `latex/` | `resume.cls`, `coverletter.cls`, `resume.tex` (public CV) — shared LaTeX style |
| `applications/<slug>/` | one dir per application (md sources, .tex, index.md metadata); PDFs are gitignored (in Drive) |
| `applications/README.md` | the status tracker table |
| `apps-script/` | the Google Drive uploader (`Code.gs`) + setup runbook |
| `scripts/build-application.sh` | compile an app's `.tex` → PDFs (latexmk / texlive Docker) |
| `docs/` | published portfolio (Home, Projects, CV). Never put applications here. |

## Build / test

```bash
make build            # mkdocs build (public portfolio) → ./site
make serve            # live preview
make public-pdf       # compile latex/resume.tex → docs/assets/cv.pdf
pytest -q             # rank + render + latex tests (no browser, no API key)

# per application:
make translate SLUG=<slug>     # German .de.md (LLM)
make pdf SLUG=<slug>           # bilingual PDFs (LaTeX)
make upload SLUG=<slug>        # → Google Drive (needs .env; see apps-script/README.md)
make status SLUG=<slug> STATUS=applied
make track                     # refresh applications/README.md
```

## Conventions

- **Public site shows only the portfolio.** Don't move `applications/` under `docs/` or into the
  mkdocs `nav:`. The privacy guarantee is structural (applications are outside `docs/`).
- **Truthfulness first** — tailoring reorders and emphasizes facts from `data/`; never fabricates.
- **PDFs are not committed** (`*.pdf` gitignored) — they live in Drive; `.tex` is committed.
- Drive/Apps-Script secrets (`APPS_SCRIPT_URL`/`TOKEN`, `GDRIVE_FOLDER_ID`) live in `.env` only.

## Related repo

`radheem/portfolio` (`/home/radr/pers/resume`) is the LaTeX-only sibling this repo borrows the CV
template + build from; `radheem/cv-tailor` is the public John-Doe demo of the generation engine.

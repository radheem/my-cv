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
- tracks each application's **status** in `applications/tracker.csv` (git) + Google Sheet
  (live view); `applications/<slug>/index.md` is the per-app metadata store. Commits are the audit trail.

The **public site** publishes only the portfolio (Home, Projects, CV). `applications/` lives
**outside `doc-pages/`** and is never built into the site — so no company name leaks. The only
public PDF is the generic CV (`latex/resume.tex` → `doc-pages/assets/cv.pdf`, compiled in CI).

## The pipeline

```
cv-tailor hunt        → vault/jds/<slug>.txt        (run every search in config/search.yml)
cv-tailor ingest      → vault/jds/<slug>.txt        (one ad-hoc search via CLI flags)
cv-tailor capture <url> → vault/jds/<slug>.txt      (single job link; logged-in session; use when
                                                     `new <url>` would hit the LinkedIn auth wall)
cv-tailor screenshot <url-or-file> → vault/jds/<slug>.txt  (screenshot + Ollama vision extraction;
                                                     no LinkedIn session; any URL or local .png/.jpg;
                                                     needs: make install-screenshot + ollama pull qwen3-vl:32b)
cv-tailor new <jd>    → applications/<slug>/         cv.md (+cv.de.md), cover-letter.md (+.de),
                                                     job-description.md, index.md, manifest.json
cv-tailor translate   → cv.de.md / cover-letter.de.md  (German, LLM; run inside `new` by default)
cv-tailor pdf <slug>  → cv.tex/cover-letter.tex → cv.pdf/cover-letter.pdf  (engine/latex.py + latexmk)
cv-tailor upload <slug> → Google Drive (Apps Script); writes drive_url into index.md
cv-tailor status <slug> <state> → pull sheet → sync remote changes → apply → push CSV + sheet
cv-tailor sync-sheets → pull sheet → sync remote changes → push (explicit bidirectional sync)
```

## Search config (`config/search.yml`)

What to search lives in **`config/search.yml`**, loaded at **runtime** (`engine/config.resolve_search`,
path overridable via `CV_TAILOR_SEARCH_CONFIG`). It is **never baked into the image** — `.dockerignore`
excludes `config/`, and docker-compose mounts `./config:/app/config:ro`. Edit the file and re-run; no
rebuild. Shape: a `defaults:` block + a `searches:` list (each entry = one LinkedIn search/URL) + the
`scoring:` weights `scripts/score-jds.py` reads.

- `cv-tailor hunt` runs **every** search in one logged-in session (`.seen.json` dedups across all).
- `keywords` is passed verbatim, so LinkedIn **boolean** syntax works: `'"Go" OR "Golang" OR "Python"'`.
- `geo_id` (`&geoId=`, copied from a LinkedIn URL) is preferred over free-text `location`; also
  `distance`, `days_back` (`f_TPR`), `max_applicants`, `limit`, `easy_apply` (`f_EA=true`).
- `cv-tailor ingest --keywords ... [--geo-id --distance --easy-apply --location ...]` is the one-off
  escape hatch; URL assembly is the pure, unit-tested `engine/linkedin/jobs.build_search_url`.

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
Edit via `cv-tailor status <slug> <state>` — pulls the sheet first (to catch remote edits), applies
the local change, then pushes the updated CSV back. Commit after. `applications/tracker.csv` and
the Google Sheet are the two sources of truth; `index.md` is the per-app metadata store.
`cv-tailor sync-sheets` does a pull→merge→push without a status change. One application = one commit.

## Layout

| Path | What |
|------|------|
| `data/` | source of truth: `master-cv.md`, `profile.yml`, `projects.yml`, `guides/`, ranking config, prompts |
| `config/search.yml` | runtime search config (named searches + scoring); mounted, never baked into the image |
| `engine/` | `rank` (pure top-3/skills), `jobspec`/`render` (LLM), `latex` (MD→LaTeX), `config`, `cli` |
| `latex/` | `resume.cls`, `coverletter.cls`, `resume.tex` (public CV) — shared LaTeX style |
| `applications/<slug>/` | one dir per application (md sources, .tex, index.md metadata); PDFs are gitignored (in Drive) |
| `applications/tracker.csv` | source of truth for status in git (CSV; synced with Google Sheet) |
| `apps-script/` | the Google Drive uploader + Sheets syncer (`Code.gs`) + setup runbook |
| `scripts/build-application.sh` | compile an app's `.tex` → PDFs (latexmk / texlive Docker) |
| `doc-pages/` | MkDocs source: published portfolio (Home, Projects, CV). Never put applications here. |
| `docs/` | Private developer docs (architecture, setup, CLI, runbooks). Not published. |

## Build / test

```bash
make build            # mkdocs build (public portfolio from doc-pages/) → ./site
make serve            # live preview
make public-pdf       # compile latex/resume.tex → doc-pages/assets/cv.pdf
make hunt             # run every search in config/search.yml (host, Xvfb)
make docker-hunt      # same, in the container (config mounted at runtime)
pytest -q             # rank + render + latex + search-config tests (no browser, no API key)

# per application:
make translate ID=<id-or-slug>     # German .de.md (LLM)
make pdf ID=<id-or-slug>           # bilingual PDFs (LaTeX)
make upload ID=<id-or-slug>        # → Google Drive (needs .env; see apps-script/README.md)
make status ID=<id-or-slug> STATUS=applied
make archive ID=<id-or-slug>       # move Drive folder to Archive/, set status withdrawn
make track                         # regenerate tracker.csv from index.md files
make sync-sheets                   # bidirectional sync: pull sheet → merge → push
```

## Conventions

- **Public site shows only the portfolio.** Don't move `applications/` under `doc-pages/` or into
  the mkdocs `nav:`. The privacy guarantee is structural (applications are outside `doc-pages/`).
  Private dev docs (architecture, setup, runbooks, CLI) live in `docs/` — tracked in git but not published.
- **Truthfulness first** — tailoring reorders and emphasizes facts from `data/`; never fabricates.
- **PDFs are not committed** (`*.pdf` gitignored) — they live in Drive; `.tex` is committed.
- Drive/Apps-Script secrets (`APPS_SCRIPT_URL`/`TOKEN`, `GDRIVE_FOLDER_ID`) live in `.env` only.

## Related repo

`radheem/portfolio` (`/home/radr/pers/resume`) is the LaTeX-only sibling this repo borrows the CV
template + build from; `radheem/cv-tailor` is the public John-Doe demo of the generation engine.

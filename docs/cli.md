# CLI reference

`cv-tailor` is the local entrypoint. It captures jobs, generates a tailored CV + cover letter,
renders them as **bilingual (EN+DE) PDFs** with the LaTeX template, uploads the PDFs to Google
Drive, and tracks status in git. Applications live under `applications/<slug>/` — outside the
published `docs/` tree. See [Architecture](architecture.md).

```bash
pip install -e '.[generate,fetch]'   # Anthropic backend + URL fetch
# or: pip install -e '.[ollama]'     # local Ollama / OpenAI-compatible backend
```

## Commands at a glance

| Command | What it does |
|---|---|
| `cv-tailor new <source>` | job → tailored `cv.md`/`cover-letter.md` (+ German) + `index.md` + DB upsert |
| `cv-tailor translate <slug>` | (re)generate the German `cv.de.md` / `cover-letter.de.md` |
| `cv-tailor pdf <slug>` | render `.tex` and compile the bilingual PDFs (LaTeX) |
| `cv-tailor upload <slug>` | compile + upload the PDFs to Google Drive; write `drive_url` |
| `cv-tailor status <slug> <state>` | advance the lifecycle status directly in PostgreSQL |
| `cv-tailor status push` | push all database application statuses and metadata to Google Sheets |
| `cv-tailor status pull` | pull Google Sheets status modifications back to PostgreSQL |
| `cv-tailor db push [slug]` | push filesystem application markdown files to the database |
| `cv-tailor db pull [slug]` | pull database application markdown files to the filesystem |
| `cv-tailor db export` | export the entire database state to disk under `application-data/` |
| `cv-tailor ingest --keywords …` | capture LinkedIn JDs (containerized) — see [Runbooks](runbooks.md) |

## `cv-tailor new`

```
cv-tailor new <source> [--slug NAME] [--recipient NAME] [--no-translate]
                       [--provider anthropic|ollama] [--model ID] [--ollama-url URL]
```

| Argument / flag | Default | Purpose |
|---|---|---|
| `source` (positional) | — | Job posting **URL** (Playwright) or path to a **`.txt`/`.md`** file. |
| `--slug NAME` | company + title | Output dir name under `applications/`. |
| `--recipient NAME` | — | Cover-letter salutation → `Dear Jane Smith,`; omit → `Dear Hiring Team,`. |
| `--no-translate` | off | Skip the German translation pass (English only). |
| `--provider {anthropic,ollama}` | `anthropic` | Generation backend. |
| `--model ID` | per-provider | Model id override (e.g. `claude-opus-4-8`). |
| `--ollama-url URL` | `http://localhost:11434/v1` | OpenAI-compatible base URL (with `--provider ollama`). |

**Output:** `applications/<slug>/` with `cv.md` + `cv.de.md`, `cover-letter.md` + `cover-letter.de.md`,
`job-description.md`, `index.md` (metadata: `job_title`, `company`, `status: draft`, `clusters`,
`drive_url`), and `manifest.json`. Pure ranking picks the **top-3 projects** + skill order; the
LLM only writes prose around them (it never fabricates).

## `cv-tailor pdf` / `upload`

`pdf` renders `cv.tex` + `cover-letter.tex` from the Markdown via `engine/latex.py` (the LLM
never emits LaTeX), then compiles them with `scripts/build-application.sh` — local `latexmk` if
present, otherwise the `texlive/texlive` Docker image. Output: 2-page **English-then-German**
`cv.pdf` / `cover-letter.pdf` (gitignored — they live in Drive).

`upload` does the same, then POSTs the PDFs to the Google Apps Script endpoint
(`APPS_SCRIPT_URL` / `APPS_SCRIPT_TOKEN` in `.env` — see [apps-script/README.md](https://github.com/radheem/my-cv/blob/main/apps-script/README.md)),
writes `drive_url` / `drive_updated` into `index.md`, and refreshes the tracker.

## `cv-tailor status` / `track`

```bash
cv-tailor status <slug> applied   # draft → applied → interview → offer | rejected | withdrawn
cv-tailor track                   # rebuild applications/README.md from front matter
```
`status` regex-edits `index.md` and auto-refreshes `applications/README.md`. Commit the change —
the message + date are the audit trail.

## Model support

| Provider | Install | Default model | Auth | Selected by |
|---|---|---|---|---|
| **Anthropic** (default) | `.[generate]` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` | (default) |
| **Ollama** / OpenAI-compatible | `.[ollama]` | `qwen3.5:35b` | `CV_TAILOR_OLLAMA_API_KEY` | `--provider ollama` |

Flags map onto env (`--provider`→`CV_TAILOR_PROVIDER`, `--model`→`CV_TAILOR_MODEL`,
`--ollama-url`→`CV_TAILOR_OLLAMA_BASE_URL`); CLI flags win.

## Environment variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic backend auth (generation only) |
| `CV_TAILOR_PROVIDER` / `CV_TAILOR_MODEL` | provider + model (generation only) |
| `CV_TAILOR_OLLAMA_BASE_URL` / `CV_TAILOR_OLLAMA_API_KEY` | local endpoint config |
| `APPS_SCRIPT_URL` / `APPS_SCRIPT_TOKEN` / `GDRIVE_FOLDER_ID` | Google Drive upload |

CI never generates or uploads — it only builds the public portfolio + the public CV PDF.

See [Setup](setup.md) for the end-to-end flow.

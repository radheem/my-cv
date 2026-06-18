# CLAUDE.md — cv-tailor

Working notes for agents (and humans) on this repo. Read this before generating
applications or changing the gate.

## What this is

cv-tailor turns a **job posting** into a **tailored CV + cover letter**, versions every
application in **git**, and publishes them as a gated **MkDocs site on GitHub Pages**. The
public portfolio stays open; the per-job documents sit behind one password.

The product idea, in one line: **git + GitHub are the application-tracking system** — the
agent drafts each application, commits are the audit trail, and a `status` field drives the
lifecycle. There is no external tracker (no spreadsheet, no Trello, no GitHub Projects).

> **Public demo repo — fictional persona.** Ships no real personal data: "John Doe",
> `john.doe@example.com`, `github.com/johndoe`, and all employer names are invented. Never
> commit real names, emails, phone numbers, or personal links.

## The hard boundary

Two halves that never blur:

- **Generation** (`engine/`) runs **locally**, costs money, needs review, and commits
  Markdown. `engine/rank.py` is pure + unit-tested (picks top-3 projects, orders skills);
  only `jobspec`/`render` call an LLM. Source of truth lives in `data/`
  (`master-cv.md`, `profile.yml`, `projects.yml`, `guides/`).
- **Render + gate + deploy** (`build.py`, `encrypt.py`, `.github/workflows/deploy.yml`) runs
  in **CI with no API key**. It builds the site, makes PDFs, and AES-256-GCM encrypts the
  gated documents — and the manifest of applications — before deploy.

## New-application workflow

1. **Generate.** `cv-tailor new <job-url-or-file>` (see `docs/cli.md`). Writes
   `docs/jobs/<slug>/` with `cv.md`, `cover-letter.md`, `job-description.md`, and `index.md`
   (the gated hub). Slug derives from company + title; override with `--slug`.
2. **Review + edit** the generated Markdown — it is the source of truth for the deploy.
   **Never fabricate** experience, skills, metrics, or dates; if it isn't in
   `data/master-cv.md` / `data/profile.yml`, it doesn't go in. Tailoring is reordering and
   emphasis, not invention.
3. **No nav edit.** The build auto-lists every `docs/jobs/<slug>/` in the encrypted landing
   manifest behind the single **Tailored** sign-in page. New roles never touch `mkdocs.yml`
   and never leak in plaintext.
4. **Commit** the new application (one application = one logical commit).
5. **Push** → CI renders, gates, and deploys.

## Application lifecycle (status tracking)

Each hub `docs/jobs/<slug>/index.md` carries a `status:` field in its front matter. This is
the lifecycle mechanism: **git history records every transition, and the gated list shows a
status badge** (visible only after sign-in — status is inside the encrypted manifest, never
public).

```
draft → applied → interview → offer | rejected | withdrawn
```

- A freshly generated application starts at `draft`.
- To advance it, edit `status:` in the hub front matter and **commit** (e.g.
  `git commit -m "Mark Northwind Platform Engineer as applied"`). The commit message + date
  are the record; no separate tracking file is needed.
- `build.py` reads `status` into the encrypted manifest; `docs/assets/vault.js` renders it as
  a `.vault-badge` in the locked list. Status values map to badge colors in
  `docs/stylesheets/extra.css`.
- Keep to the vocabulary above (`engine/cli.py:_STATUSES`); an unknown value still renders,
  just with the neutral default badge.

## Repo conventions

- **Commits: omit the Claude `Co-Authored-By` footer** in this repo.
- **Public demo, no real PII** (see persona note above). Generated job Markdown stays
  committed in plaintext — it's the fake John Doe sample.
- **Bump `?v=` on `assets/vault.js`** in `mkdocs.yml` whenever you change `vault.js`. GitHub
  Pages serves assets with `Cache-Control: max-age=600` and no fingerprinting, so a stale
  cached `vault.js` will otherwise break the gate for returning visitors.
- `mkdocs.yml` contains `!!python/name:` tags — never `yaml.safe_load` it raw (the deploy
  workflow reads `site_url` via regex; `build.py` avoids loading it).

## Build / test

```bash
GATE_PASSWORD=test python build.py        # mkdocs build → PDFs → AES-seal (use .venv/bin/python)
python -m http.server -d site 8000        # then open http://localhost:8000/
pytest -q                                 # ranking logic — no browser, no API key
```

Env gotchas (this machine): the venv is **uv**-managed and has **no pip** — install with
`VIRTUAL_ENV=$PWD/.venv uv pip install ...`. `build.py` shells out to `mkdocs`, so put the
venv on PATH: `PATH="$PWD/.venv/bin:$PATH" GATE_PASSWORD=test .venv/bin/python build.py`.
WeasyPrint needs native libs (already installed here).

Verify a gate change end to end: build, then confirm nothing leaks pre-sign-in —
`grep -rl "<gated company>" site/ | grep -v '\.enc$'` and the same against
`site/search/search_index.json` are both empty.

## Suggested improvements (roadmap)

- **`cv-tailor status <slug> <state>` command** — flip the front-matter `status` and stage the
  edit, instead of hand-editing YAML (mirrors the manual rule above).
- **Status dates** — add `applied_on` / per-state timestamps to the front matter and badge so
  the manifest shows "applied 2026-06-17"; git already has the dates, this surfaces them.
- **Private notes file** — a `notes.md` per application (JD analysis, gaps, keywords-to-mirror)
  like the `resume` repo's template; keep it out of `site/` (it's already not gated-rendered).
- **Deadline / follow-up surfacing** — sort the gated list by status and flag stale `applied`
  rows that need a follow-up.
- **CI status summary** — have the deploy workflow print a per-status count to the run log.
- **Provider robustness** — the Ollama branch in `engine/llm.py` `structured_json()` can hit a
  `JSONDecodeError` when the endpoint ignores `json_schema` response-format; add a
  `json_object` + schema-in-prompt fallback.

## Related repo

The private **`radheem/portfolio`** (`/home/radr/pers/resume`) runs the same idea with LaTeX:
per-job dirs under `applications/`, a `status:` front-matter field, a master status table, and
git commits per transition. cv-tailor is the Markdown/MkDocs + encrypted-gate variant of that
workflow.

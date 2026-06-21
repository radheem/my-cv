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

> **Private repo — real data.** This is Radheem Bin Razi's personal CV repo (`radheem/my-cv`).
> `data/` holds real contact details, employers, and projects. The **public GitHub Pages site**
> shows the portfolio + master CV; per-job documents stay behind the password gate. Keep the
> gate strong — never let a tailored CV/cover-letter or company name leak into the plaintext
> site or search index (verify per **Build / test** below).

## The hard boundary

Two halves that never blur:

- **Generation** (`engine/`) runs **locally**, costs money, needs review, and commits
  Markdown. `engine/rank.py` is pure + unit-tested (picks top-3 projects, orders skills);
  only `jobspec`/`render` call an LLM. Source of truth lives in `data/`
  (`master-cv.md`, `profile.yml`, `projects.yml`, `guides/`, and the ranking config
  `taxonomy.yml` + `ranking.yml` — see **Ranking & tailoring** below).
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

## Ranking & tailoring

`engine/rank.py` is the **pure, deterministic** core that picks the top-3 projects and orders
the skills block. It scores projects by token overlap against the LLM-extracted JobSpec, plus
**cluster affinity** and a **per-project weight**. Two user-authored `data/` files steer it
(the selection counterpart to `data/guides/`, which steer prose) — both optional, both
default-inert:

- **`data/taxonomy.yml`** — a controlled vocabulary: an `aliases` map (`k8s→kubernetes`,
  `golang→go`…) normalized before matching, and `clusters` (named groups of canonical tags).
  Both **projects** and **job applications** are classified into the same clusters, so an agent
  can read a job's clusters and pull the correlating projects directly.
- **`data/ranking.yml`** — knobs: `field_weights`, `cluster_affinity`, `top_projects`,
  `max_skill_groups`, `prefer_clusters`, `pinned` (always-include ids), `excluded`.
- **`data/projects.yml`** per-project `weight:` (default 1.0) multiplies a project's score to
  favor flagships; optional `clusters:` overrides the tag-derived clusters.

Clusters for a **job** are computed deterministically from the JobSpec at `cv-tailor new` time
(`rank.job_clusters`) and written into the hub front matter as `clusters: [...]` — git-visible
alongside `status:`, and carried (passthrough) into the encrypted manifest by `build.py`. The
ranker never runs in CI. When changing scoring, keep it **pure** (taxonomy/ranking passed as
args) and **backward-compatible** (absent files reproduce the original token-overlap behavior —
`tests/test_rank.py:test_defaults_reproduce_current_behavior` guards this).

## Configuration, prompts & reproducibility

The knobs are centralized so generation is **configurable and reproducible**, not a
one-off. All three layers fall back to code defaults, so an absent file = today's
behavior, and **env still overrides the file** (`CLI flag > env > data/config.yml >
default`).

- **`data/config.yml`** (`engine/config.py`) — provider/model, temperatures, token
  budgets, the Ollama endpoint + reasoning-token floors, `seed`, prompt selection, and
  the ranking/taxonomy file paths. `engine/llm.py:resolve()` is a thin shim over it.
- **`data/prompts/{cv,cover,jobspec,judge}.md`** (`engine/prompts.py`) — the system
  prompts, versioned via front-matter `version:`; editing them needs no code change. The
  in-code constant in `render.py`/`jobspec.py` is the fallback when a file is absent.
  `data/prompts/exemplars/cover.yml` carries gold-derived, style-only opener exemplars.
- **`projects.yml` `highlights:`** — role-neutral facts (verbatim from `master-cv.md`)
  that the CV renderer **re-angles per role** (ETL framing for a data role, observability
  for devops). Without it the renderer falls back to the static `summary`.
- **`manifest.json`** (`engine/manifest.py`) — written next to every application:
  provider/model/temps/budgets/seed, prompt versions+hashes, and content hashes of the
  effective config + all data inputs. Lets a result be re-derived and verified. It is
  excluded from the built site (`mkdocs.yml exclude_docs`).
- **Benchmark gate** — `tests/experiments/evaluate.py --gate` enforces the per-split
  floors in `tests/experiments/gates.yml` (deterministic heuristic; judge advisory).
  `tests/test_data_consistency.py` guards `profile.yml`↔`master-cv.md` drift.

`master-cv.md` stays canonical for facts; `profile.yml` is the structured mirror the
engine needs — keep them in sync (the drift test enforces it).

## Repo conventions

- **Commits: omit the Claude `Co-Authored-By` footer** in this repo.
- **Private repo, real data** (see note above). Generated job Markdown is committed in
  plaintext in the repo but is **excluded from the built site** and AES-sealed by `build.py`
  before deploy — so the private GitHub repo holds the source, the public site stays gated.
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

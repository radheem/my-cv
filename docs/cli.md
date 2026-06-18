# CLI reference

`cv-tailor` is the local generation entrypoint. It takes a job posting, extracts a
structured **JobSpec**, ranks your projects/skills, and writes a tailored CV + cover letter
under `docs/jobs/<slug>/`. Rendering, gating, and deploy happen later in CI — see
[Architecture](architecture.md).

```bash
pip install -e '.[generate,fetch]'   # Anthropic backend + URL fetch
# or: pip install -e '.[ollama]'     # local Ollama / OpenAI-compatible backend
```

## `cv-tailor new`

```
cv-tailor new <source> [--slug NAME] [--recipient NAME]
                       [--provider anthropic|ollama] [--model ID] [--ollama-url URL]
```

Generate a tailored application from a job posting.

| Argument / flag | Default | Purpose |
|---|---|---|
| `source` (positional) | — | Job posting **URL** (fetched via Playwright) or path to a **`.txt`/`.md`** file. |
| `--slug NAME` | derived from company + title | Output directory name under `docs/jobs/`. |
| `--recipient NAME` | — | Cover-letter salutation. Set → `Dear Jane Smith,`; omit → `Dear Hiring Team,`. |
| `--provider {anthropic,ollama}` | `anthropic` | Generation backend. `ollama` = any OpenAI-compatible endpoint. |
| `--model ID` | per-provider (below) | Model id override. |
| `--ollama-url URL` | `http://localhost:11434/v1` | OpenAI-compatible base URL (only with `--provider ollama`). |

**Output:** `docs/jobs/<slug>/` with `cv.md`, `cover-letter.md`, `job-description.md`, and
`index.md` (the gated unlock hub, with `status: draft` and the role's `clusters:` in its front
matter). The command prints the featured projects and the job's clusters. **No `mkdocs.yml`
edit is needed** — the build auto-lists the application in the encrypted manifest behind the
single **Tailored** sign-in page.

## Tuning which projects get picked

Project selection is steered by version-controlled `data/` config (the selection counterpart to
`data/guides/`, which steer the prose). All optional — absent files reproduce the default
token-overlap ranking:

- **`data/taxonomy.yml`** — tag `aliases` (`k8s→kubernetes`…) and `clusters` (named tag groups).
  Both projects and jobs are classified into the same clusters, so a role's `clusters:` front
  matter correlates it with matching projects.
- **`data/ranking.yml`** — `field_weights`, `cluster_affinity`, `top_projects`,
  `max_skill_groups`, `prefer_clusters`, `pinned` (always feature), `excluded` (never feature).
- **`data/projects.yml`** — a per-project `weight:` (default 1.0) to favor flagships.

## Model support

Generation runs through one provider per invocation. Anthropic is the default; Ollama (or any
OpenAI-compatible server) is opt-in.

| Provider | SDK / install | Default model | Auth | Selected by |
|---|---|---|---|---|
| **Anthropic** (default) | `pip install -e '.[generate]'` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` | (nothing — default) |
| **Ollama** / OpenAI-compatible | `pip install -e '.[ollama]'` | `qwen3.5:35b` | `CV_TAILOR_OLLAMA_API_KEY` (default `ollama`) | `--provider ollama` |

Flags map onto env vars (`--provider`→`CV_TAILOR_PROVIDER`, `--model`→`CV_TAILOR_MODEL`,
`--ollama-url`→`CV_TAILOR_OLLAMA_BASE_URL`); set either form.

### Sample commands

```bash
# Anthropic (default), from a file
export ANTHROPIC_API_KEY=...
cv-tailor new path/to/job.txt

# Anthropic, harder reasoning with Opus
cv-tailor new path/to/job.txt --model claude-opus-4-8

# Anthropic, fetch the posting from a URL + personalize the salutation
cv-tailor new https://example.com/careers/123 --recipient "Jane Smith"

# Local Ollama — offline, no API key
cv-tailor new path/to/job.txt --provider ollama \
  --ollama-url http://localhost:11434/v1 --model qwen3.5:35b

# Same via env vars
CV_TAILOR_PROVIDER=ollama \
CV_TAILOR_OLLAMA_BASE_URL=http://localhost:11434/v1 \
CV_TAILOR_MODEL=qwen3.5:35b \
  cv-tailor new path/to/job.txt

# Custom output directory name
cv-tailor new path/to/job.txt --slug acme-platform-engineer
```

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Authenticates the Anthropic backend. |
| `CV_TAILOR_PROVIDER` | `anthropic` | `anthropic` or `ollama` (aliases: `openai`, `openai-compatible`). |
| `CV_TAILOR_MODEL` | `claude-sonnet-4-6` / `qwen3.5:35b` | Model id override (per provider). |
| `CV_TAILOR_OLLAMA_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible base URL. |
| `CV_TAILOR_OLLAMA_API_KEY` | `ollama` | Key for that endpoint. |

CLI flags take precedence over env vars. CI never generates, so none of these are needed in
the deploy workflow.

## After generating

1. **Review and edit** the generated Markdown — it is the source of truth for the deploy.
2. **Commit** it; the push triggers render → gate → deploy. No nav edit is needed.
3. **Track the lifecycle.** The hub starts at `status: draft`. As the application progresses,
   edit `status:` in `docs/jobs/<slug>/index.md`
   (`draft → applied → interview → offer / rejected / withdrawn`) and commit — the gated list
   shows a status badge and git history is the audit trail. See [CLAUDE.md](../CLAUDE.md).

See [Setup](setup.md) for the full end-to-end flow.

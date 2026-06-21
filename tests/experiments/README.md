# cv-tailor benchmark — local-model quality vs. hand-written gold

Goal: make the **local Ollama model** (`qwen3.6:35b` on the lab box) generate a CV +
cover letter that is **as good as the hand-written LaTeX applications** in the sibling
`resume` repo (`radheem/portfolio` → `applications/`).

This harness measures the gap. It is a **prompt/config benchmark, not fine-tuning** —
there is no weight training. The "training" split is the set you iterate the engine's
prompts, guides, and ranking on; the "test" split is held out so you can tell real
improvement from overfitting your guides to the examples you stared at.

```
CV_TAILOR_OLLAMA_BASE_URL = http://genai.ltc.hsnet:11434/v1   (default in harness.py)
CV_TAILOR_MODEL           = qwen3.6:35b                       (default in harness.py)
```

## The split (4 train / 2 test)

| split | case | role |
|---|---|---|
| train | `aroundhome-senior-software-engineer` | Senior SWE (Go / microservices) |
| train | `redcare-pharmacy-data-engineer` | Data Engineer |
| train | `intershop-devops-engineer-monitoring` | DevOps / observability |
| train | `t-systems-backend-engineer-container` | Backend / containers / SDN |
| test  | `alignerr-software-engineer-ai-training` | SWE / code-review / AI |
| test  | `teambank-model-monitoring-risk-controlling` | ML model-monitoring / quant |

Diverse domains in both splits. Edit `extract_gold.py`'s `CASES` and re-run it to change
the split. (`split.yml` is generated from it.)

## Layout

```
tests/experiments/
  extract_gold.py     one-off: snapshot JD + gold (EN) from ../../resume LaTeX → cases/
  split.yml           generated train/test slug lists
  cases/<slug>/
    job-description.txt   input posting (engine input)
    gold/cv.md            gold CV, engine-shape Markdown (human-written reference)
    gold/cover-letter.md  gold cover-letter body
    meta.yml              split, company, role, recipient, source
  harness.py          config + case loading + the PURE scoring core (unit-tested)
  run.py              generate outputs/<slug>/ with the engine (Ollama by default)
  evaluate.py         score outputs vs gold (heuristics + LLM judge) → results/
  outputs/            generated artifacts            (gitignored)
  results/            scores.json + report.md        (gitignored)
```

The gold under `cases/` is committed so the benchmark is self-contained. (`radr-cv` is a
private real-data repo, and `tests/` is outside `docs/`, so nothing here is ever built
into or gated on the public site.)

## Run it

```bash
# 0. one-time: Ollama backend dep (uv venv, no pip)
VIRTUAL_ENV=$PWD/.venv uv pip install -e '.[ollama]'

# 1. generate (defaults to the lab box + qwen3.6:35b)
.venv/bin/python tests/experiments/run.py --split train      # iterate on these
.venv/bin/python tests/experiments/run.py --split test       # held-out, final check
.venv/bin/python tests/experiments/run.py --only redcare-pharmacy-data-engineer
.venv/bin/python tests/experiments/run.py --split test --provider anthropic   # baseline

# 2. score (heuristics + LLM judge; --no-judge for offline heuristics only)
.venv/bin/python tests/experiments/evaluate.py --split all
cat tests/experiments/results/report.md

# 3. regression gate — non-zero exit if a split drops below gates.yml floors
.venv/bin/python tests/experiments/evaluate.py --split all --gate
```

Every generated case also writes `outputs/<slug>/manifest.json` (provider, model,
temperature, token budgets, seed, prompt versions+hashes, and content hashes of the
effective config + all data inputs) — so a score is attributable to an exact config
snapshot. Two runs with the same `effective_config_sha256` + prompt hashes +
provider/seed should reproduce within noise. Tune `gates.yml` floors just under your
achieved scores; the gate enforces the deterministic heuristic and treats the LLM
judge as advisory.

Generation is ~3 min/case on the 35B (it is a reasoning model — the `<think>` block is
billed against the token budget; `engine/llm.py` gives structured calls headroom and
retries, so the JobSpec step doesn't truncate to empty).

## What gets measured

**Heuristics** (pure, deterministic, in `harness.py`; weight in parentheses):

| metric | what |
|---|---|
| `cv_structure` (.15) | all of Experience / Education / Projects / Skills present |
| `skills_coverage` (.20) | fraction of the gold CV's skill tokens present in the generated CV |
| `projects_match` (.15) | recall of the gold's featured projects among the generated ones |
| `jd_coverage` (.15) | fraction of JobSpec `must_haves` present in the CV |
| `truthfulness` (.15) | every org header is grounded in `data/master-cv.md` (fabrication guard) |
| `cl_length` (.05) | cover letter in the 250–400-word band |
| `cl_no_salutation` (.05) | body only — no `Dear …` / `Sincerely …` (template adds those) |
| `cl_company` (.05) | the company is named |
| `cl_paragraphs` (.05) | 3–5 paragraphs |

→ one `heuristic` score in `[0,1]` per case, aggregated per split.

**LLM judge** (`evaluate.py`): compares each generated doc against its gold on
`tailoring / truthfulness / specificity / tone / overall` (1–5). Runs on the same Ollama
endpoint by default; `--no-judge` skips it.

`results/report.md` has the per-case table, the heuristic breakdown, per-split
aggregates, and any truthfulness flags.

## The iteration loop

1. `run.py --split train` then `evaluate.py --split train`.
2. Read `results/report.md` + diff `outputs/<slug>/cv.md` against `cases/<slug>/gold/cv.md`.
3. Improve the engine where the gap is — **not** the cases:
   - prose quality / tailoring → `data/guides/*.md`, the system prompts in `engine/render.py`
   - wrong projects / skills order → `data/ranking.yml`, `data/taxonomy.yml`,
     per-project `weight:` in `data/projects.yml`
   - JobSpec misses requirements → the prompt/schema in `engine/jobspec.py`
4. Re-run train; when it plateaus, run **test** once. A big train↔test gap = overfit guides.

## Tests

`tests/test_experiments.py` (runs under plain `pytest -q`, no network/model) validates the
split (4+2, unique), that every case is complete and consistent, that the pure metrics
clear the real gold (structure, self-consistency, truthfulness, body-only letters), and
that the fabrication guard fires on an unknown employer.

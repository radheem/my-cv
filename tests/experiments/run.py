#!/usr/bin/env python3
"""Generate tailored CV + cover letter for benchmark cases with the cv-tailor engine.

Drives the real engine (jobspec -> rank -> render) against each case's job posting,
using the Ollama backend by default (lab box + qwen3.6:35b). Writes one folder per
case under outputs/<slug>/ with the generated Markdown plus the JobSpec and tailoring
decisions, so evaluate.py can score them against the gold.

    # generate the whole training split (iterate guides/prompts on these):
    python tests/experiments/run.py --split train

    # one case, or the held-out test split:
    python tests/experiments/run.py --only redcare-pharmacy-data-engineer
    python tests/experiments/run.py --split test

    # point at a different endpoint / model / provider:
    python tests/experiments/run.py --split all --model qwen3.6:35b \
        --ollama-url http://genai.ltc.hsnet:11434/v1
    python tests/experiments/run.py --split test --provider anthropic   # baseline

Needs the Ollama backend dep:  VIRTUAL_ENV=.venv uv pip install -e '.[ollama]'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import harness  # noqa: E402  (adds repo root to sys.path on import)


def _select(args) -> list[str]:
    if args.only:
        return [args.only]
    split = harness.load_split()
    if args.split == "all":
        return split["train"] + split["test"]
    return split[args.split]


def generate_one(slug: str) -> dict:
    """Run the full pipeline for one case; write outputs/<slug>/. Returns a summary."""
    from engine import cli, jobspec as jobspec_mod, rank, render, llm

    case = harness.load_case(slug)
    profile, projects, master_cv, cv_guide, cl_guide, taxonomy, ranking = cli._load_data()

    t0 = time.time()
    spec = jobspec_mod.extract_jobspec(case.job_text)
    tailoring = rank.tailor(spec, profile, projects, taxonomy=taxonomy, ranking=ranking)
    tagline, cv_body = render.render_cv(spec, tailoring, master_cv, cv_guide)
    cl_body = render.render_cover_letter(
        spec, tailoring, profile.get("summary", ""), case.job_text, cl_guide
    )
    elapsed = round(time.time() - t0, 1)

    out = harness.OUTPUTS / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "cv.md").write_text(cv_body, encoding="utf-8")
    (out / "cover-letter.md").write_text(cl_body, encoding="utf-8")
    (out / "jobspec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    (out / "tailoring.json").write_text(
        json.dumps(
            {
                "tagline": tagline,
                "top_projects": [p["id"] for p in tailoring["top_projects"]],
                "skills": tailoring["skills"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    summary = {
        "slug": slug,
        "split": case.split,
        "ok": True,
        "model": llm.model(),
        "seconds": elapsed,
        "tagline": tagline,
        "top_projects": [p["id"] for p in tailoring["top_projects"]],
    }
    (out / "run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="generate benchmark applications")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--split", choices=["train", "test", "all"], default="train")
    g.add_argument("--only", help="a single case slug")
    ap.add_argument("--provider", choices=["anthropic", "ollama"], default="ollama")
    ap.add_argument("--model", default=None, help=f"model id (default {harness.DEFAULT_MODEL})")
    ap.add_argument("--ollama-url", default=None,
                    help=f"OpenAI-compatible base URL (default {harness.DEFAULT_OLLAMA_BASE_URL})")
    args = ap.parse_args(argv)

    # Wire the engine's provider env BEFORE any generation call.
    if args.provider == "ollama":
        os.environ.update(harness.ollama_env(args.model, args.ollama_url))
    else:
        os.environ["CV_TAILOR_PROVIDER"] = "anthropic"
        if args.model:
            os.environ["CV_TAILOR_MODEL"] = args.model

    slugs = _select(args)
    print(f"Generating {len(slugs)} case(s) with provider={args.provider} "
          f"model={os.environ.get('CV_TAILOR_MODEL', '(default)')}\n", file=sys.stderr)

    summaries = []
    for slug in slugs:
        print(f"→ {slug} ...", file=sys.stderr, flush=True)
        try:
            s = generate_one(slug)
            print(f"  ok  {s['seconds']}s  projects={','.join(s['top_projects'])}  "
                  f"tagline={s['tagline']!r}", file=sys.stderr)
        except Exception as e:  # keep going; record the failure
            s = {"slug": slug, "ok": False, "error": f"{type(e).__name__}: {e}"}
            (harness.OUTPUTS / slug).mkdir(parents=True, exist_ok=True)
            (harness.OUTPUTS / slug / "run.json").write_text(json.dumps(s, indent=2))
            print(f"  FAIL  {s['error']}", file=sys.stderr)
        summaries.append(s)

    ok = sum(1 for s in summaries if s.get("ok"))
    print(f"\nDone: {ok}/{len(summaries)} generated. Outputs in {harness.OUTPUTS}",
          file=sys.stderr)
    print("Next: python tests/experiments/evaluate.py", file=sys.stderr)
    return 0 if ok == len(summaries) else 1


if __name__ == "__main__":
    raise SystemExit(main())

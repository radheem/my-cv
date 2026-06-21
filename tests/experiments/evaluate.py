#!/usr/bin/env python3
"""Score generated applications against the gold references.

Two layers:
  * Heuristics (pure, in harness.py): structure, skills coverage, JD-keyword
    coverage, project match, truthfulness, cover-letter length/format/company.
  * LLM judge (optional, here): a rubric comparison of generated vs gold on
    tailoring / truthfulness / specificity / tone / overall (1-5). Runs on the
    same Ollama endpoint by default; --no-judge skips it (fully offline).

Reads outputs/<slug>/ (from run.py) + cases/<slug>/gold/. Writes
results/scores.json and a human-readable results/report.md, with per-split
(train vs test) aggregates.

    python tests/experiments/evaluate.py                 # heuristics + judge
    python tests/experiments/evaluate.py --no-judge      # heuristics only
    python tests/experiments/evaluate.py --judge-model qwen3.6:35b
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

import harness  # noqa: E402

_JUDGE_DIMS = ("tailoring", "truthfulness", "specificity", "tone", "overall")

_JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        **{d: {"type": "integer", "minimum": 1, "maximum": 5} for d in _JUDGE_DIMS},
        "notes": {"type": "string"},
    },
    "required": list(_JUDGE_DIMS) + ["notes"],
    "additionalProperties": False,
}

_JUDGE_SYSTEM = (
    "You are a meticulous hiring-grade reviewer comparing a CANDIDATE document "
    "against a human-written GOLD reference for the same job. Score the candidate "
    "1-5 on each axis (5 = matches or beats the gold):\n"
    "- tailoring: foregrounds what THIS job needs (its must-haves, domain).\n"
    "- truthfulness: no claims beyond the gold/master facts; no fabrication.\n"
    "- specificity: concrete, quantified proof over generic phrasing.\n"
    "- tone: professional, fluent, well-structured for the reader.\n"
    "- overall: holistic quality vs the gold.\n"
    "Return JSON only, matching the schema. Be strict and calibrated."
)


def _judge(kind: str, jobspec: dict, gen: str, gold: str) -> dict | None:
    from engine import llm, prompts

    user = (
        f"## Job\nTitle: {jobspec.get('title')}\nCompany: {jobspec.get('company')}\n"
        f"Must-haves: {', '.join(jobspec.get('must_haves', []))}\n\n"
        f"## GOLD {kind} (human-written reference)\n{gold.strip()}\n\n"
        f"## CANDIDATE {kind} (to score)\n{harness.strip_front_matter(gen).strip()}\n\n"
        f"Score the candidate {kind} against the gold."
    )
    try:
        system, _ = prompts.load("judge", _JUDGE_SYSTEM)
        mt = llm.resolve()["max_tokens"]["judge"]
        return llm.structured_json(system, user, _JUDGE_SCHEMA, max_tokens=mt)
    except Exception as e:  # endpoint may ignore json_schema, or be down
        return {"error": f"{type(e).__name__}: {e}"}


def _mean(xs: list[float]) -> float:
    return round(statistics.mean(xs), 3) if xs else 0.0


def evaluate(slugs: list[str], do_judge: bool) -> dict:
    master = harness.load_master_cv()
    catalog = harness.load_projects_catalog()
    rows = []
    for slug in slugs:
        out = harness.OUTPUTS / slug
        run = json.loads((out / "run.json").read_text()) if (out / "run.json").exists() else {}
        if not run.get("ok"):
            rows.append({"slug": slug, "missing": True, "error": run.get("error", "not generated")})
            continue
        case = harness.load_case(slug)
        gen_cv = (out / "cv.md").read_text(encoding="utf-8")
        gen_cl = (out / "cover-letter.md").read_text(encoding="utf-8")
        spec = json.loads((out / "jobspec.json").read_text(encoding="utf-8"))

        row = harness.score_case(
            gen_cv, gen_cl, case, spec.get("must_haves", []), master, catalog
        )
        row["seconds"] = run.get("seconds")
        row["model"] = run.get("model")

        if do_judge:
            cv_j = _judge("CV", spec, gen_cv, case.gold_cv)
            cl_j = _judge("cover letter", spec, gen_cl, case.gold_cover)
            row["judge"] = {"cv": cv_j, "cover": cl_j}
            scores = [
                j[d] for j in (cv_j, cl_j)
                if isinstance(j, dict) and "error" not in j
                for d in _JUDGE_DIMS if isinstance(j.get(d), int)
            ]
            row["judge_overall"] = _mean(
                [j["overall"] for j in (cv_j, cl_j)
                 if isinstance(j, dict) and isinstance(j.get("overall"), int)]
            )
            row["judge_mean"] = _mean(scores)
        rows.append(row)

    scored = [r for r in rows if not r.get("missing")]
    by_split: dict[str, dict] = {}
    for sp in ("train", "test"):
        g = [r for r in scored if r.get("split") == sp]
        if g:
            agg = {"n": len(g), "heuristic": _mean([r["heuristic"] for r in g])}
            if do_judge:
                agg["judge_mean"] = _mean([r["judge_mean"] for r in g if "judge_mean" in r])
                agg["judge_overall"] = _mean([r["judge_overall"] for r in g if "judge_overall" in r])
            by_split[sp] = agg

    from engine import config, manifest
    eff = config.load()
    return {
        "rows": rows,
        "by_split": by_split,
        "judged": do_judge,
        "config_version": eff.get("version"),
        "effective_config_sha256": manifest.sha256_of(json.dumps(eff, sort_keys=True)),
    }


def gate(result: dict, gates_file: pathlib.Path) -> list[str]:
    """Return a list of gate violations (empty = pass). Enforces min_heuristic per
    split; min_judge_mean is advisory (reported by the caller, not returned here)."""
    import yaml
    g = yaml.safe_load(gates_file.read_text(encoding="utf-8")) or {}
    floors = g.get("min_heuristic", {})
    violations = []
    for sp, agg in result["by_split"].items():
        floor = floors.get(sp)
        if floor is not None and agg["heuristic"] < floor:
            violations.append(f"{sp}: heuristic {agg['heuristic']} < floor {floor}")
    return violations


def _report_md(result: dict) -> str:
    judged = result["judged"]
    lines = ["# cv-tailor benchmark — results\n"]
    lines.append("Generated CV/cover-letter vs the hand-written gold (resume/applications).\n")
    head = "| case | split | heuristic |"
    sep = "|---|---|---|"
    if judged:
        head += " judge µ | judge overall |"
        sep += "---|---|"
    head += " sec |"
    sep += "---|"
    lines += [head, sep]
    for r in result["rows"]:
        if r.get("missing"):
            lines.append(f"| {r['slug']} | — | _not generated: {r.get('error','')}_ |"
                         + (" | |" if judged else "") + " |")
            continue
        cells = [r["slug"], r["split"], f"{r['heuristic']:.3f}"]
        if judged:
            cells += [f"{r.get('judge_mean','-')}", f"{r.get('judge_overall','-')}"]
        cells.append(str(r.get("seconds", "-")))
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("\n## Per-split aggregates\n")
    for sp, agg in result["by_split"].items():
        extra = ""
        if judged:
            extra = f", judge µ {agg.get('judge_mean')}, judge overall {agg.get('judge_overall')}"
        lines.append(f"- **{sp}** (n={agg['n']}): heuristic {agg['heuristic']}{extra}")

    lines.append("\n## Heuristic breakdown\n")
    keys = list(harness._W.keys())
    lines.append("| case | " + " | ".join(keys) + " |")
    lines.append("|---|" + "---|" * len(keys))
    for r in result["rows"]:
        if r.get("missing"):
            continue
        lines.append("| " + r["slug"] + " | "
                     + " | ".join(f"{r['parts'][k]:.2f}" for k in keys) + " |")

    flagged = [r for r in result["rows"]
               if not r.get("missing") and r.get("truthfulness_offenders")]
    if flagged:
        lines.append("\n## ⚠ Truthfulness flags (orgs not grounded in master CV)\n")
        for r in flagged:
            lines.append(f"- **{r['slug']}**: {', '.join(r['truthfulness_offenders'])}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="score generated applications vs gold")
    ap.add_argument("--split", choices=["train", "test", "all"], default="all")
    ap.add_argument("--only", help="a single case slug")
    ap.add_argument("--no-judge", action="store_true", help="heuristics only, no LLM judge")
    ap.add_argument("--judge-model", default=None, help="model for the judge (default qwen3.6:35b)")
    ap.add_argument("--judge-url", default=None, help="OpenAI-compatible base URL for the judge")
    ap.add_argument("--gate", action="store_true",
                    help="exit non-zero if any split is below its floor in gates.yml")
    args = ap.parse_args(argv)

    if args.only:
        slugs = [args.only]
    else:
        split = harness.load_split()
        slugs = split["train"] + split["test"] if args.split == "all" else split[args.split]

    do_judge = not args.no_judge
    if do_judge and os.environ.get("CV_TAILOR_PROVIDER", "").lower() not in (
        "anthropic",
    ):
        os.environ.update(harness.ollama_env(args.judge_model, args.judge_url))

    result = evaluate(slugs, do_judge)

    harness.RESULTS.mkdir(parents=True, exist_ok=True)
    (harness.RESULTS / "scores.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (harness.RESULTS / "report.md").write_text(_report_md(result), encoding="utf-8")

    for sp, agg in result["by_split"].items():
        extra = f"  judge µ={agg.get('judge_mean')}" if do_judge else ""
        print(f"{sp:5}  n={agg['n']}  heuristic={agg['heuristic']}{extra}", file=sys.stderr)
    print(f"\nWrote {harness.RESULTS/'report.md'} and scores.json", file=sys.stderr)

    if args.gate:
        violations = gate(result, harness.HERE / "gates.yml")
        if violations:
            print("GATE FAILED:", file=sys.stderr)
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
            return 1
        print("GATE PASSED (heuristic floors met)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

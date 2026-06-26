#!/usr/bin/env python3
"""Score captured JDs in vault/jds/ against master-cv skill keywords.

Usage:
    python3 scripts/score-jds.py [--top N] [--out ranked.json]

Reads the `scoring:` weights from the runtime search config (config/search.yml, or
$CV_TAILOR_SEARCH_CONFIG), falling back to the legacy data/search-terms.yml.  Prints a
ranked table and optionally writes a JSON file listing slugs in score order for
scripts/job-hunt.sh to consume.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
VAULT_JDS = ROOT / "vault" / "jds"


def _load_config() -> dict:
    """Find the first config file that defines `scoring:`. Prefers the runtime search
    config (env path, then config/search.yml); falls back to the legacy file."""
    candidates: list[pathlib.Path] = []
    env = os.environ.get("CV_TAILOR_SEARCH_CONFIG")
    if env:
        candidates.append(pathlib.Path(env))
    candidates += [ROOT / "config" / "search.yml", DATA / "search-terms.yml"]
    for cfg_path in candidates:
        if cfg_path.exists():
            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            if cfg.get("scoring"):
                return cfg
    sys.exit(f"No scoring config found (looked in: {', '.join(str(c) for c in candidates)})")


def _score(text: str, cfg: dict) -> tuple[int, list[str]]:
    lower = text.lower()
    hits: list[str] = []
    total = 0
    for kw in cfg.get("must_have", []):
        if re.search(r"\b" + re.escape(kw) + r"\b", lower):
            total += 3
            hits.append(f"+3 {kw}")
    for kw in cfg.get("nice_to_have", []):
        if re.search(r"\b" + re.escape(kw) + r"\b", lower):
            total += 1
            hits.append(f"+1 {kw}")
    for kw in cfg.get("language_penalty", []):
        if kw in lower:
            total -= 5
            hits.append(f"-5 {kw!r}")
    return total, hits


def _parse_frontmatter(txt: str) -> tuple[dict, str]:
    """Split YAML front-matter from body."""
    if not txt.startswith("---"):
        return {}, txt
    parts = txt.split("---", 2)
    if len(parts) < 3:
        return {}, txt
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, parts[2]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--top", type=int, default=10, help="number of top JDs to highlight")
    ap.add_argument("--out", default=None, help="write ranked slug list to JSON file")
    ap.add_argument("--jds-dir", default=str(VAULT_JDS),
                    help="directory of captured .txt JDs")
    ap.add_argument("--only-slugs", nargs="*", default=None, metavar="SLUG",
                    help="score only these slug stems (default: all files in --jds-dir)")
    ap.add_argument("--skip-existing-apps", action="store_true",
                    help="exclude JDs that already have an applications/<slug>/ dir")
    args = ap.parse_args()

    cfg = _load_config()
    scoring_cfg = cfg.get("scoring", {})

    jds_dir = pathlib.Path(args.jds_dir)
    rows: list[dict] = []
    db_mode = False

    # Check if we can connect to database first
    sys.path.insert(0, str(ROOT))
    try:
        from engine.db import get_conn
        with get_conn() as conn:
            db_mode = True
            with conn.cursor() as cur:
                if args.only_slugs is not None:
                    cur.execute("SELECT slug, company, title, description, url, score, location, applicants FROM jobs WHERE slug = ANY(%s)", (list(args.only_slugs),))
                else:
                    cur.execute("SELECT slug, company, title, description, url, score, location, applicants FROM jobs")
                db_rows = cur.fetchall()
                
                # Filter out existing applications if requested
                if args.skip_existing_apps:
                    cur.execute("SELECT slug FROM applications")
                    existing_apps = {row["slug"] for row in cur.fetchall()}
                    db_rows = [r for r in db_rows if r["slug"] not in existing_apps]
                    
                for r in db_rows:
                    desc = r["description"] or ""
                    score, hits = _score(desc, scoring_cfg)
                    cur.execute("UPDATE jobs SET score = %s WHERE slug = %s", (score, r["slug"]))
                    rows.append({
                        "slug": r["slug"],
                        "score": score,
                        "title": r["title"] or r["slug"],
                        "company": r["company"] or "Unknown",
                        "location": r["location"] or "",
                        "applicants": r["applicants"] if r["applicants"] is not None else "?",
                        "url": r["url"] or "",
                        "hits": hits,
                    })
            conn.commit()
    except Exception as exc:
        db_mode = False

    if not db_mode:
        if args.only_slugs is not None:
            txt_files = sorted(
                p for slug in args.only_slugs
                if (p := jds_dir / f"{slug}.txt").exists()
            )
        else:
            txt_files = sorted(jds_dir.glob("*.txt"))
        if not txt_files:
            sys.exit(f"No .txt files in {jds_dir}")

        apps_dir = ROOT / "applications"
        if args.skip_existing_apps:
            txt_files = [p for p in txt_files if not (apps_dir / p.stem).is_dir()]

        for p in txt_files:
            text = p.read_text(encoding="utf-8", errors="ignore")
            fm, body = _parse_frontmatter(text)
            score, hits = _score(body or text, scoring_cfg)
            slug = p.stem
            rows.append({
                "slug": slug,
                "score": score,
                "title": fm.get("title", slug),
                "company": fm.get("company", ""),
                "location": fm.get("location", ""),
                "applicants": fm.get("applicants", "?"),
                "url": fm.get("url", ""),
                "hits": hits,
            })

    rows.sort(key=lambda r: r["score"], reverse=True)

    col_w = 50
    print(f"\n{'Rank':<5} {'Score':<7} {'Applicants':<12} {'Company + Title':<{col_w}} Location")
    print("-" * (5 + 7 + 12 + col_w + 20))
    for i, r in enumerate(rows, 1):
        flag = " ◀ TOP" if i <= args.top else ""
        label = f"{r['company']}: {r['title']}"[:col_w]
        print(
            f"{i:<5} {r['score']:<7} {str(r['applicants']):<12} {label:<{col_w}} "
            f"{r['location']}{flag}"
        )

    print(f"\nTop {args.top} slugs:")
    top_slugs = [r["slug"] for r in rows[: args.top]]
    for s in top_slugs:
        print(f"  {s}")

    if args.out:
        out = pathlib.Path(args.out)
        out.write_text(json.dumps(top_slugs, indent=2))
        print(f"\nWrote {out}")


if __name__ == "__main__":
    main()

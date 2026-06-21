"""cv-tailor CLI — generate a tailored application from a job posting.

    cv-tailor new <job-url-or-file> [--slug NAME] [--provider anthropic|ollama]

Runs locally. Generation uses Anthropic by default (ANTHROPIC_API_KEY) or a local
Ollama / OpenAI-compatible endpoint with --provider ollama. Writes docs/jobs/<slug>/
with cv.md, cover-letter.md, job-description.md, and index.md (the gated unlock hub).
Review the output, commit it, and let CI render + encrypt + deploy.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

import yaml

from . import fetch, jobspec as jobspec_mod, manifest as manifest_mod, rank, render

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
JOBS = ROOT / "docs" / "jobs"


def _load_optional_yaml(path: pathlib.Path) -> dict:
    """Load a YAML mapping, or {} when the file is absent (optional config)."""
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_data() -> tuple[dict, list, str, str, str, dict, dict]:
    profile = yaml.safe_load((DATA / "profile.yml").read_text(encoding="utf-8"))
    projects = yaml.safe_load((DATA / "projects.yml").read_text(encoding="utf-8"))["projects"]
    master_cv = (DATA / "master-cv.md").read_text(encoding="utf-8")
    cv_guide = (DATA / "guides" / "how-to-write-a-cv.md").read_text(encoding="utf-8")
    cl_guide = (DATA / "guides" / "how-to-write-a-cover-letter.md").read_text(encoding="utf-8")
    # Optional, user-authored ranking config (engine/rank.py reads these).
    taxonomy = _load_optional_yaml(DATA / "taxonomy.yml")
    ranking = _load_optional_yaml(DATA / "ranking.yml")
    return profile, projects, master_cv, cv_guide, cl_guide, taxonomy, ranking


# Keep gated pages out of the public search index (build.py also scrubs it).
_NO_INDEX = "---\nsearch:\n  exclude: true\n---\n\n"


def _yaml(value: str) -> str:
    """Quote a scalar for a YAML front-matter value."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _slugify(*parts: str) -> str:
    raw = "-".join(p for p in parts if p)
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "tailored-application"


# Application lifecycle. Edit `status:` in the hub front matter (and commit) as a
# role progresses; the build surfaces it as a badge in the gated list. See CLAUDE.md.
_STATUSES = ("draft", "applied", "interview", "offer", "rejected", "withdrawn")


def _hub_page(
    title: str, company: str, slug: str, status: str = "draft", clusters: tuple = ()
) -> str:
    # Generic heading + search-excluded so a direct URL leaks no role/company.
    # job_title/company/status/clusters ride in the front matter (NOT the special
    # `title` key, which MkDocs would render into the page <title>) for build.py to
    # read into the encrypted landing manifest. `clusters` (taxonomy domains this
    # role maps to) lets an agent correlate the job with matching projects.
    clusters_line = ""
    if clusters:
        clusters_line = "clusters: [" + ", ".join(_yaml(c) for c in clusters) + "]\n"
    return (
        "---\nsearch:\n  exclude: true\n"
        f"job_title: {_yaml(title)}\n"
        f"company: {_yaml(company)}\n"
        f"status: {_yaml(status)}\n"
        f"{clusters_line}---\n\n"
        "# Tailored Application :material-lock:\n\n"
        "These documents are tailored for a specific role and protected by a "
        "password. If you reached this page directly, enter the password to view "
        "the CV and cover letter.\n\n"
        f'<div id="vault-app" data-slug="{slug}"></div>\n'
    )


def _apply_provider_flags(args: argparse.Namespace) -> None:
    """Map provider flags onto the env vars that engine.llm.resolve() reads."""
    if args.provider:
        os.environ["CV_TAILOR_PROVIDER"] = args.provider
    if args.model:
        os.environ["CV_TAILOR_MODEL"] = args.model
    if args.ollama_url:
        os.environ["CV_TAILOR_OLLAMA_BASE_URL"] = args.ollama_url


def cmd_new(args: argparse.Namespace) -> int:
    _apply_provider_flags(args)
    profile, projects, master_cv, cv_guide, cl_guide, taxonomy, ranking = _load_data()

    print(f"Fetching job from {args.source} ...", file=sys.stderr)
    job_text = fetch.fetch_job_text(args.source)

    print("Extracting JobSpec ...", file=sys.stderr)
    spec = jobspec_mod.extract_jobspec(job_text)

    tailoring = rank.tailor(spec, profile, projects, taxonomy=taxonomy, ranking=ranking)
    clusters = rank.job_clusters(spec, taxonomy, rank.invert_aliases(taxonomy.get("aliases", {})))

    slug = args.slug or _slugify(spec.get("company", ""), spec.get("title", ""))
    out = JOBS / slug
    out.mkdir(parents=True, exist_ok=True)

    print("Rendering CV ...", file=sys.stderr)
    tagline, cv_body = render.render_cv(spec, tailoring, master_cv, cv_guide)
    print("Rendering cover letter ...", file=sys.stderr)
    cl_body = render.render_cover_letter(
        spec, tailoring, profile.get("summary", ""), job_text, cl_guide,
        availability=profile.get("availability", ""),
        relocation=profile.get("relocation", ""),
    )

    cv_fm = f"---\nsearch:\n  exclude: true\ntagline: {_yaml(tagline)}\n---\n\n"
    cl_fm = (
        "---\nsearch:\n  exclude: true\n"
        f"recipient: {_yaml(args.recipient or '')}\n"
        f"company: {_yaml(spec.get('company', ''))}\n---\n\n"
    )
    (out / "cv.md").write_text(cv_fm + cv_body, encoding="utf-8")
    (out / "cover-letter.md").write_text(cl_fm + cl_body, encoding="utf-8")
    (out / "job-description.md").write_text(
        _NO_INDEX
        + f"# Job Description — {spec.get('title')}\n\n```\n{job_text.strip()}\n```\n",
        encoding="utf-8",
    )
    (out / "index.md").write_text(
        _hub_page(
            spec.get("title", "Role"), spec.get("company", ""), slug, clusters=clusters
        ),
        encoding="utf-8",
    )
    (out / "manifest.json").write_text(
        json.dumps(
            manifest_mod.build(
                decisions={
                    "top_projects": [p["id"] for p in tailoring["top_projects"]],
                    "clusters": list(clusters),
                    "tagline": tagline,
                },
                generated_at=datetime.datetime.now(datetime.timezone.utc)
                .isoformat(timespec="seconds"),
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nWrote docs/jobs/{slug}/ (cv, cover-letter, job-description, index, manifest).")
    print("Featured projects:", ", ".join(p["name"] for p in tailoring["top_projects"]))
    if clusters:
        print("Clusters:", ", ".join(clusters))
    print(
        "\nNo nav edit needed: the build auto-lists this application in the "
        "encrypted manifest behind the single 'Tailored' sign-in page. Review + commit."
    )
    print(
        "Status starts at 'draft'. Edit `status:` in the hub front matter and commit "
        f"as it progresses ({' → '.join(_STATUSES[:3])} → offer/rejected/withdrawn)."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cv-tailor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="generate a tailored application from a job")
    p_new.add_argument("source", help="job posting URL, or path to a .txt/.md file")
    p_new.add_argument("--slug", help="output dir name under docs/jobs/", default=None)
    p_new.add_argument(
        "--recipient",
        default=None,
        help="recipient name for the cover-letter salutation (e.g. 'Jane Smith'); "
        "omit for 'Dear Hiring Team,'",
    )
    p_new.add_argument(
        "--provider",
        choices=["anthropic", "ollama"],
        default=None,
        help="generation backend (default: anthropic; ollama = OpenAI-compatible endpoint)",
    )
    p_new.add_argument(
        "--model", default=None, help="model id override (e.g. claude-opus-4-8, qwen3.5:35b)"
    )
    p_new.add_argument(
        "--ollama-url",
        default=None,
        help="OpenAI-compatible base URL for --provider ollama "
        "(default: http://localhost:11434/v1)",
    )
    p_new.set_defaults(func=cmd_new)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

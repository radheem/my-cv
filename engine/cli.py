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


def _data_dir() -> pathlib.Path:
    """CV source facts. Override with CV_TAILOR_DATA_DIR (default ./data = John Doe).
    Real runs may mount a private data dir read-only and point this at it."""
    return pathlib.Path(os.environ.get("CV_TAILOR_DATA_DIR") or DATA)


def _jobs_dir() -> pathlib.Path:
    """Application output. Override with CV_TAILOR_JOBS_DIR (default ./docs/jobs).
    Real runs point this at gitignored vault/applications/ so nothing real is committed."""
    return pathlib.Path(os.environ.get("CV_TAILOR_JOBS_DIR") or JOBS)


def _load_optional_yaml(path: pathlib.Path) -> dict:
    """Load a YAML mapping, or {} when the file is absent (optional config)."""
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_data(data: pathlib.Path | None = None) -> tuple[dict, list, str, str, str, dict, dict]:
    data = data or _data_dir()
    profile = yaml.safe_load((data / "profile.yml").read_text(encoding="utf-8"))
    projects = yaml.safe_load((data / "projects.yml").read_text(encoding="utf-8"))["projects"]
    master_cv = (data / "master-cv.md").read_text(encoding="utf-8")
    cv_guide = (data / "guides" / "how-to-write-a-cv.md").read_text(encoding="utf-8")
    cl_guide = (data / "guides" / "how-to-write-a-cover-letter.md").read_text(encoding="utf-8")
    # Optional, user-authored ranking config (engine/rank.py reads these).
    taxonomy = _load_optional_yaml(data / "taxonomy.yml")
    ranking = _load_optional_yaml(data / "ranking.yml")
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
    out = _jobs_dir() / slug
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

    print(f"\nWrote {out}/ (cv, cover-letter, job-description, index, manifest).")
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


def cmd_ingest(args: argparse.Namespace) -> int:
    """Drive a logged-in LinkedIn session and capture JDs. Stop-before-submit (D4)."""
    import logging

    from playwright.sync_api import sync_playwright

    from .linkedin import jobs as J
    from .linkedin.humanize import human_pause
    from .linkedin.session import FileInboxResolver, LinkedInSession, StdinResolver

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    vault = os.environ.get("CV_TAILOR_VAULT", "vault")
    user_data_dir = os.environ.get("LINKEDIN_USER_DATA_DIR", f"{vault}/profile")
    out_dir = pathlib.Path(args.out)
    seen_path = out_dir / ".seen.json"

    challenge_timeout = float(os.environ.get("LINKEDIN_CHALLENGE_TIMEOUT", "300"))
    resolver = (
        StdinResolver()
        if sys.stdin.isatty()
        else FileInboxResolver(pathlib.Path(vault) / "challenges", timeout=challenge_timeout)
    )
    session = LinkedInSession(
        user_data_dir=user_data_dir,
        vault_dir=vault,
        resolver=resolver,
        challenge_timeout=challenge_timeout,
    )

    counts = {"captured": 0, "skipped": 0}

    def run(page) -> None:
        found = J.search(page, args.keywords, args.location, args.limit)
        seen = J.load_seen(seen_path)
        for job in found:
            if J.already_seen(job.job_id, seen):
                counts["skipped"] += 1
                continue
            try:
                text = J.capture_jd(page, job)
            except Exception as e:  # noqa: BLE001 — skip a bad card, keep going
                print(f"  skip {job.url}: {e}", file=sys.stderr)
                continue
            captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            path = J.write_jd(job, text, out_dir, captured_at)
            seen[job.job_id] = J.slugify(job.company, job.title, job.job_id)
            counts["captured"] += 1
            print(f"  captured {path}")
            human_pause(2.0, 5.0)  # human-paced gap between job opens
        J.save_seen(seen_path, seen)

    with sync_playwright() as p:
        session.context(p)
        try:
            session.with_session(run)
        finally:
            session.close()

    print(f"\ningest done: captured {counts['captured']}, skipped {counts['skipped']} (seen)")
    return 0


def cmd_pdf(args: argparse.Namespace) -> int:
    """Render plain (unsealed) CV + cover-letter PDFs for an application — for uploading.

    Unlike build.py (which AES-seals per-app PDFs for the gated public site), these are plain
    files written next to the application's Markdown. Real apps live under gitignored vault/."""
    from weasyprint import HTML

    from . import documents

    app = _jobs_dir() / args.slug
    if not app.is_dir():
        raise SystemExit(f"no such application: {app}")
    profile, *_ = _load_data()

    targets: list[tuple[str, str]] = []
    cv_md = app / "cv.md"
    if cv_md.exists():
        meta, body = documents.split_front_matter(cv_md.read_text(encoding="utf-8"))
        targets.append(("cv.pdf", documents.render_cv_html(body, meta.get("tagline", ""), profile)))
    cl_md = app / "cover-letter.md"
    if cl_md.exists():
        meta, body = documents.split_front_matter(cl_md.read_text(encoding="utf-8"))
        targets.append(("cover-letter.pdf", documents.render_letter_html(body, meta, profile)))
    if not targets:
        raise SystemExit(f"no cv.md / cover-letter.md in {app}")

    for name, html in targets:
        HTML(string=html).write_pdf(str(app / name))
        print(f"  wrote {app / name}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Advance an application's lifecycle status by editing the hub front matter."""
    hub = _jobs_dir() / args.slug / "index.md"
    if not hub.exists():
        raise SystemExit(f"no such application hub: {hub}")
    if args.state not in _STATUSES:
        print(
            f"warning: '{args.state}' is not a standard status ({', '.join(_STATUSES)})",
            file=sys.stderr,
        )
    text = hub.read_text(encoding="utf-8")
    new, n = re.subn(r"(?m)^status:.*$", f"status: {_yaml(args.state)}", text)
    if n == 0:
        raise SystemExit(f"no 'status:' field in {hub}")
    hub.write_text(new, encoding="utf-8")
    print(f"set {args.slug} status -> {args.state}  (review the diff, then commit)")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv()  # env still wins (override=False) — consistent with engine.config
    except ImportError:
        pass

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

    p_ingest = sub.add_parser(
        "ingest", help="search LinkedIn and capture job descriptions to vault/jds/"
    )
    p_ingest.add_argument("--keywords", required=True, help="job search keywords")
    p_ingest.add_argument("--location", default=None, help="location filter (e.g. 'Remote')")
    p_ingest.add_argument("--limit", type=int, default=10, help="max JDs to capture")
    p_ingest.add_argument("--out", default="vault/jds", help="output dir for JD files")
    p_ingest.set_defaults(func=cmd_ingest)

    p_pdf = sub.add_parser("pdf", help="render plain CV + cover-letter PDFs for an application")
    p_pdf.add_argument("slug", help="application slug under the jobs dir")
    p_pdf.set_defaults(func=cmd_pdf)

    p_status = sub.add_parser("status", help="advance an application's lifecycle status")
    p_status.add_argument("slug", help="application slug under the jobs dir")
    p_status.add_argument("state", help="draft|applied|interview|offer|rejected|withdrawn")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

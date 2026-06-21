"""cv-tailor CLI — generate a tailored application from a job posting.

    cv-tailor new <job-url-or-file> [--slug NAME] [--provider anthropic|ollama]

Runs locally. Generation uses Anthropic by default (ANTHROPIC_API_KEY) or a local
Ollama / OpenAI-compatible endpoint with --provider ollama. Writes applications/<slug>/
with cv.md (+ cv.de.md), cover-letter.md (+ .de), job-description.md, and index.md (the
metadata record). The tailored PDFs are rendered with the LaTeX template (latex/*.cls)
and uploaded to Google Drive; status is tracked in git. `applications/` is never built
into the public site.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.request

import yaml

from . import documents, fetch, jobspec as jobspec_mod, manifest as manifest_mod, rank, render

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
JOBS = ROOT / "applications"


def _data_dir() -> pathlib.Path:
    """CV source facts. Override with CV_TAILOR_DATA_DIR (default ./data)."""
    return pathlib.Path(os.environ.get("CV_TAILOR_DATA_DIR") or DATA)


def _jobs_dir() -> pathlib.Path:
    """Application records. Override with CV_TAILOR_JOBS_DIR (default ./applications)."""
    return pathlib.Path(os.environ.get("CV_TAILOR_JOBS_DIR") or JOBS)


def _load_optional_yaml(path: pathlib.Path) -> dict:
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
    taxonomy = _load_optional_yaml(data / "taxonomy.yml")
    ranking = _load_optional_yaml(data / "ranking.yml")
    return profile, projects, master_cv, cv_guide, cl_guide, taxonomy, ranking


def _yaml(value: str) -> str:
    """Quote a scalar for a YAML front-matter value."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _slugify(*parts: str) -> str:
    raw = "-".join(p for p in parts if p)
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "tailored-application"


# Application lifecycle. Edit `status:` (cv-tailor status) and commit as a role
# progresses; the tracker (applications/README.md) surfaces it. See CLAUDE.md.
_STATUSES = ("draft", "applied", "interview", "offer", "rejected", "withdrawn")


def _today() -> str:
    return datetime.datetime.now().astimezone().date().isoformat()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _hub_page(
    title: str, company: str, status: str = "draft", clusters: tuple = (), date_found: str = ""
) -> str:
    """The application's metadata record (front matter drives status + the tracker)."""
    clusters_line = ""
    if clusters:
        clusters_line = "clusters: [" + ", ".join(_yaml(c) for c in clusters) + "]\n"
    return (
        "---\n"
        f"job_title: {_yaml(title)}\n"
        f"company: {_yaml(company)}\n"
        f"status: {_yaml(status)}\n"
        f"{clusters_line}"
        f"date_found: {_yaml(date_found or _today())}\n"
        'drive_url: ""\n'
        'drive_updated: ""\n'
        "---\n\n"
        f"# {company} — {title}\n\n"
        "Tailored application. Source of truth: `cv.md` / `cover-letter.md` (+ `.de` German). "
        "PDFs are rendered with the LaTeX template and stored in Google Drive (`drive_url`).\n"
    )


def _set_front_matter_fields(path: pathlib.Path, fields: dict[str, str]) -> None:
    """Upsert front-matter keys without disturbing other lines (e.g. status:)."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit(f"no front matter in {path}")
    fm = m.group(1)
    for k, v in fields.items():
        line = f"{k}: {_yaml(v)}"
        fm, n = re.subn(rf"(?m)^{re.escape(k)}:.*$", line.replace("\\", "\\\\"), fm)
        if n == 0:
            fm = fm + "\n" + line
    path.write_text("---\n" + fm + "\n---\n" + text[m.end():], encoding="utf-8")


def _apply_provider_flags(args: argparse.Namespace) -> None:
    if getattr(args, "provider", None):
        os.environ["CV_TAILOR_PROVIDER"] = args.provider
    if getattr(args, "model", None):
        os.environ["CV_TAILOR_MODEL"] = args.model
    if getattr(args, "ollama_url", None):
        os.environ["CV_TAILOR_OLLAMA_BASE_URL"] = args.ollama_url


def _read_md(app: pathlib.Path, name: str) -> tuple[dict, str]:
    p = app / name
    if not p.exists():
        return {}, ""
    return documents.split_front_matter(p.read_text(encoding="utf-8"))


# ---- LaTeX render + compile -------------------------------------------------

def _render_tex(slug: str) -> pathlib.Path:
    """Write cv.tex + cover-letter.tex from the (bilingual) Markdown sources."""
    from . import latex

    app = _jobs_dir() / slug
    if not app.is_dir():
        raise SystemExit(f"no such application: {app}")
    profile, projects, *_ = _load_data()

    cv_meta, cv_en = _read_md(app, "cv.md")
    cv_de_meta, cv_de = _read_md(app, "cv.de.md")
    if cv_en:
        if not cv_de:
            print("  ! no cv.de.md — run `cv-tailor translate`; using English for both pages",
                  file=sys.stderr)
        tex = latex.render_cv_tex(
            cv_en, cv_de or cv_en, profile, projects,
            cv_meta.get("tagline", ""), cv_de_meta.get("tagline", "") or cv_meta.get("tagline", ""),
        )
        (app / "cv.tex").write_text(tex, encoding="utf-8")

    cl_meta, cl_en = _read_md(app, "cover-letter.md")
    _, cl_de = _read_md(app, "cover-letter.de.md")
    if cl_en:
        tex = latex.render_cover_tex(cl_en, cl_de or cl_en, cl_meta, profile)
        (app / "cover-letter.tex").write_text(tex, encoding="utf-8")
    return app


def _compile(app: pathlib.Path) -> None:
    subprocess.run([str(ROOT / "scripts" / "build-application.sh"), str(app)], check=True)


def _build_app(slug: str) -> list[pathlib.Path]:
    """Render .tex + compile to PDFs; return the (existing) PDF paths."""
    app = _render_tex(slug)
    _compile(app)
    return [p for p in (app / "cv.pdf", app / "cover-letter.pdf") if p.exists()]


# ---- commands ---------------------------------------------------------------

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
        availability=profile.get("availability", ""), relocation=profile.get("relocation", ""),
    )

    cv_fm = f"---\ntagline: {_yaml(tagline)}\n---\n\n"
    cl_fm = (
        "---\n"
        f"recipient: {_yaml(args.recipient or '')}\n"
        f"company: {_yaml(spec.get('company', ''))}\n---\n\n"
    )
    (out / "cv.md").write_text(cv_fm + cv_body, encoding="utf-8")
    (out / "cover-letter.md").write_text(cl_fm + cl_body, encoding="utf-8")
    (out / "job-description.md").write_text(
        f"# Job Description — {spec.get('title')}\n\n```\n{job_text.strip()}\n```\n",
        encoding="utf-8",
    )
    (out / "index.md").write_text(
        _hub_page(spec.get("title", "Role"), spec.get("company", ""), clusters=clusters),
        encoding="utf-8",
    )
    (out / "manifest.json").write_text(
        json.dumps(
            manifest_mod.build(
                decisions={
                    "top_projects": [p["id"] for p in tailoring["top_projects"]],
                    "clusters": list(clusters), "tagline": tagline,
                },
                generated_at=_now(),
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    if not args.no_translate:
        print("Translating to German ...", file=sys.stderr)
        _translate_app(slug, tagline)

    print(f"\nWrote {out}/ (cv, cover-letter [+ .de], job-description, index, manifest).")
    print("Featured projects:", ", ".join(p["name"] for p in tailoring["top_projects"]))
    print(
        "\nNext: `cv-tailor pdf %s` (render LaTeX → PDFs), `cv-tailor upload %s` (→ Google Drive),\n"
        "      `cv-tailor status %s applied` as it progresses; review + commit." % (slug, slug, slug)
    )
    return 0


def _translate_app(slug: str, en_tagline: str = "") -> None:
    app = _jobs_dir() / slug
    cv_meta, cv_body = _read_md(app, "cv.md")
    if cv_body:
        de_body = render.translate_markdown(cv_body, "cv")
        tagline = cv_meta.get("tagline", en_tagline)
        de_tagline = render.translate_markdown(tagline, "cv").strip().splitlines()[0] if tagline else ""
        (app / "cv.de.md").write_text(f"---\ntagline: {_yaml(de_tagline)}\n---\n\n{de_body}", encoding="utf-8")
        print(f"  wrote {app / 'cv.de.md'}")
    cl_meta, cl_body = _read_md(app, "cover-letter.md")
    if cl_body:
        de_body = render.translate_markdown(cl_body, "cover")
        fm = "---\n" + f"recipient: {_yaml(cl_meta.get('recipient', ''))}\ncompany: {_yaml(cl_meta.get('company', ''))}\n---\n\n"
        (app / "cover-letter.de.md").write_text(fm + de_body, encoding="utf-8")
        print(f"  wrote {app / 'cover-letter.de.md'}")


def cmd_translate(args: argparse.Namespace) -> int:
    """Generate German cv.de.md / cover-letter.de.md from the English sources (LLM)."""
    _apply_provider_flags(args)
    app = _jobs_dir() / args.slug
    if not app.is_dir():
        raise SystemExit(f"no such application: {app}")
    _translate_app(args.slug)
    print("Review the German output, then `cv-tailor pdf` to compile bilingual PDFs.")
    return 0


def cmd_pdf(args: argparse.Namespace) -> int:
    """Render the LaTeX CV + cover letter (bilingual) and compile to PDFs."""
    pdfs = _build_app(args.slug)
    if not pdfs:
        raise SystemExit("no PDFs produced (missing cv.md/cover-letter.md?)")
    for p in pdfs:
        print(f"  wrote {p}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Advance an application's lifecycle status and refresh the tracker."""
    hub = _jobs_dir() / args.slug / "index.md"
    if not hub.exists():
        raise SystemExit(f"no such application: {hub}")
    if args.state not in _STATUSES:
        print(f"warning: '{args.state}' is not a standard status ({', '.join(_STATUSES)})",
              file=sys.stderr)
    text = hub.read_text(encoding="utf-8")
    new, n = re.subn(r"(?m)^status:.*$", f"status: {_yaml(args.state)}", text)
    if n == 0:
        raise SystemExit(f"no 'status:' field in {hub}")
    hub.write_text(new, encoding="utf-8")
    _write_tracker()
    print(f"set {args.slug} status -> {args.state}  (review the diff, then commit)")
    return 0


def _write_tracker() -> pathlib.Path:
    jobs = _jobs_dir()
    rows = []
    for d in sorted(jobs.glob("*")):
        idx = d / "index.md"
        if not idx.is_file():
            continue
        meta, _ = documents.split_front_matter(idx.read_text(encoding="utf-8"))
        meta["slug"] = d.name
        rows.append(meta)
    order = {s: i for i, s in enumerate(_STATUSES)}
    rows.sort(key=lambda r: (order.get(str(r.get("status")), 99), str(r.get("company", "")).lower()))
    out = [
        "# Applications",
        "",
        "Status lifecycle: " + " → ".join(_STATUSES) + ".",
        "Tailored CVs/cover letters live in Google Drive (Drive column); this table is the tracker.",
        "",
        "| Company | Role | Status | Found | Drive | Updated |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        drive = f"[open]({r['drive_url']})" if r.get("drive_url") else "—"
        out.append("| {c} | {t} | **{s}** | {f} | {d} | {u} |".format(
            c=r.get("company", ""), t=r.get("job_title", ""), s=r.get("status", ""),
            f=r.get("date_found", "") or "—", d=drive, u=r.get("drive_updated", "") or "—"))
    path = jobs / "README.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return path


def cmd_track(args: argparse.Namespace) -> int:
    """Regenerate the applications/README.md status table from per-app front matter."""
    path = _write_tracker()
    print(f"wrote {path}")
    return 0


def cmd_upload(args: argparse.Namespace) -> int:
    """Compile the PDFs and upload them to Google Drive via the Apps Script endpoint."""
    url = os.environ.get("APPS_SCRIPT_URL")
    token = os.environ.get("APPS_SCRIPT_TOKEN")
    if not url or not token:
        raise SystemExit("set APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN in .env (see apps-script/README.md)")
    app = _jobs_dir() / args.slug
    if not app.is_dir():
        raise SystemExit(f"no such application: {app}")
    pdfs = _build_app(args.slug)
    if not pdfs:
        raise SystemExit("no PDFs to upload")
    meta, _ = documents.split_front_matter((app / "index.md").read_text(encoding="utf-8"))
    files = [{"name": p.name, "b64": base64.b64encode(p.read_bytes()).decode("ascii")} for p in pdfs]
    payload = {
        "token": token, "slug": args.slug, "company": meta.get("company", ""),
        "title": meta.get("job_title", ""), "status": meta.get("status", ""), "files": files,
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "text/plain;charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read().decode("utf-8"))
    if not resp.get("ok"):
        raise SystemExit(f"upload failed: {resp}")
    folder = resp.get("folderUrl", "")
    _set_front_matter_fields(app / "index.md", {"drive_url": folder, "drive_updated": _now()})
    _write_tracker()
    print(f"uploaded {args.slug} -> {folder}\ndrive_url written + tracker refreshed; review + commit")
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
        user_data_dir=user_data_dir, vault_dir=vault,
        resolver=resolver, challenge_timeout=challenge_timeout,
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
            except Exception as e:  # noqa: BLE001
                print(f"  skip {job.url}: {e}", file=sys.stderr)
                continue
            captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            path = J.write_jd(job, text, out_dir, captured_at)
            seen[job.job_id] = J.slugify(job.company, job.title, job.job_id)
            counts["captured"] += 1
            print(f"  captured {path}")
            human_pause(2.0, 5.0)
        J.save_seen(seen_path, seen)

    with sync_playwright() as p:
        session.context(p)
        try:
            session.with_session(run)
        finally:
            session.close()

    print(f"\ningest done: captured {counts['captured']}, skipped {counts['skipped']} (seen)")
    return 0


def _add_provider_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--provider", choices=["anthropic", "ollama"], default=None,
                   help="generation backend (default: anthropic; ollama = OpenAI-compatible)")
    p.add_argument("--model", default=None, help="model id override (e.g. claude-opus-4-8)")
    p.add_argument("--ollama-url", default=None, help="OpenAI-compatible base URL for ollama")


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv()  # env still wins (override=False)
    except ImportError:
        pass

    parser = argparse.ArgumentParser(prog="cv-tailor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="generate a tailored application from a job")
    p_new.add_argument("source", help="job posting URL, or path to a .txt/.md file")
    p_new.add_argument("--slug", help="output dir name under applications/", default=None)
    p_new.add_argument("--recipient", default=None, help="cover-letter salutation name")
    p_new.add_argument("--no-translate", action="store_true", help="skip the German translation")
    _add_provider_flags(p_new)
    p_new.set_defaults(func=cmd_new)

    p_tr = sub.add_parser("translate", help="generate German cv.de.md / cover-letter.de.md")
    p_tr.add_argument("slug", help="application slug")
    _add_provider_flags(p_tr)
    p_tr.set_defaults(func=cmd_translate)

    p_ingest = sub.add_parser("ingest", help="search LinkedIn and capture JDs to vault/jds/")
    p_ingest.add_argument("--keywords", required=True, help="job search keywords")
    p_ingest.add_argument("--location", default=None, help="location filter (e.g. 'Remote')")
    p_ingest.add_argument("--limit", type=int, default=10, help="max JDs to capture")
    p_ingest.add_argument("--out", default="vault/jds", help="output dir for JD files")
    p_ingest.set_defaults(func=cmd_ingest)

    p_pdf = sub.add_parser("pdf", help="render the LaTeX CV + cover letter and compile to PDFs")
    p_pdf.add_argument("slug", help="application slug")
    p_pdf.set_defaults(func=cmd_pdf)

    p_up = sub.add_parser("upload", help="compile + upload the PDFs to Google Drive")
    p_up.add_argument("slug", help="application slug")
    p_up.set_defaults(func=cmd_upload)

    p_status = sub.add_parser("status", help="advance an application's lifecycle status")
    p_status.add_argument("slug", help="application slug")
    p_status.add_argument("state", help="draft|applied|interview|offer|rejected|withdrawn")
    p_status.set_defaults(func=cmd_status)

    p_track = sub.add_parser("track", help="regenerate applications/README.md status table")
    p_track.set_defaults(func=cmd_track)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

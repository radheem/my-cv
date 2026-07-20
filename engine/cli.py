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
import csv
import datetime
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.request

import yaml

from .shared import config as config_mod
from .domains.gmail import client as gmail
from .domains.tailoring import (
    rank,
    render,
    jobspec as jobspec_mod,
)
from . import (
    documents,
    fetch,
    manifest as manifest_mod,
)

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


def _load_data(data: pathlib.Path | None = None) -> tuple[dict, list, str, dict, dict]:
    data = data or _data_dir()
    profile = yaml.safe_load((data / "profile.yml").read_text(encoding="utf-8"))
    projects = yaml.safe_load((data / "projects.yml").read_text(encoding="utf-8"))["projects"]
    master_cv = (data / "master-cv.md").read_text(encoding="utf-8")
    taxonomy = _load_optional_yaml(data / "taxonomy.yml")
    ranking = _load_optional_yaml(data / "ranking.yml")
    return profile, projects, master_cv, taxonomy, ranking


def _yaml(value: str) -> str:
    """Quote a scalar for a YAML front-matter value."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _slugify(*parts: str) -> str:
    raw = "-".join(p for p in parts if p)
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "tailored-application"


_JOB_ID_RE = re.compile(r"(\d{7,})/?$")


def _job_id_from_source(source: str) -> str:
    """Extract numeric job id from a vault JD file's frontmatter or URL."""
    src = pathlib.Path(source)
    if src.suffix == ".txt" and src.exists():
        try:
            fm, _ = documents.split_front_matter(src.read_text(encoding="utf-8"))
            jid = str(fm.get("job_id", "")).strip()
            if jid:
                return jid
            url = str(fm.get("url", "")).strip()
            m = _JOB_ID_RE.search(url.rstrip("/"))
            if m:
                return m.group(1)
        except Exception:
            pass
    if source.startswith(("http://", "https://")):
        m = _JOB_ID_RE.search(source.rstrip("/"))
        if m:
            return m.group(1)
    return ""


def _resolve_slug(arg: str) -> str:
    """Accept a numeric job id or full slug; return the full slug."""
    if not re.fullmatch(r"\d+", arg):
        return arg
    matches = [d.name for d in _jobs_dir().iterdir()
               if d.is_dir() and d.name.endswith(f"-{arg}")]
    if not matches:
        raise SystemExit(f"no application found with job id {arg}")
    if len(matches) > 1:
        raise SystemExit(f"ambiguous id {arg} — matches: {', '.join(sorted(matches))}")
    return matches[0]


_STUDENT_ROLE_RE = re.compile(
    r"\b(thesis|masterarbeit|bachelorarbeit|werkstudent|working[\s\-]student"
    r"|hilfskraft|hiwi|praktik\w*)\b",
    re.IGNORECASE,
)


def _student_relocation(title: str, relocation: str) -> str:
    """Strip the Blue Card sentence from relocation for student/thesis roles."""
    if relocation and _STUDENT_ROLE_RE.search(title):
        return re.sub(r"\s*Blue Card[^.]*\.", "", relocation, flags=re.IGNORECASE).strip()
    return relocation


# Application lifecycle. Edit `status:` (cv-tailor status) and commit as a role
# progresses; tracker.csv + Google Sheet are the at-a-glance view. See CLAUDE.md.
_STATUSES = ("draft", "applied", "interview", "offer", "rejected", "withdrawn")


def _today() -> str:
    return datetime.datetime.now().astimezone().date().isoformat()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _hub_page(
    title: str, company: str, status: str = "draft", clusters: tuple = (),
    date_found: str = "", job_url: str = ""
) -> str:
    """The application's metadata record (front matter drives status + the tracker)."""
    clusters_line = ""
    if clusters:
        clusters_line = "clusters: [" + ", ".join(_yaml(c) for c in clusters) + "]\n"
    return (
        "---\n"
        f"job_title: {_yaml(title)}\n"
        f"company: {_yaml(company)}\n"
        f"job_url: {_yaml(job_url)}\n"
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
    from .domains.tailoring import latex

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
    """Render .tex + compile to PDFs; return the PDF paths along with their source Markdown files."""
    app = _render_tex(slug)
    _compile(app)
    targets = [app / "cv.pdf", app / "cover-letter.pdf"]
    targets.extend(list(app.glob("*.md")))
    return [p for p in targets if p.exists() and p.name != "index.md"]


# ---- commands ---------------------------------------------------------------

def cmd_new(args: argparse.Namespace) -> int:
    _apply_provider_flags(args)
    profile, projects, master_cv, taxonomy, ranking = _load_data()

    print(f"Fetching job from {args.source} ...", file=sys.stderr)
    job_text = fetch.fetch_job_text(args.source)

    # Posting URL: a URL source is itself the link; a captured JD file has a .json sidecar.
    job_url = ""
    if str(args.source).startswith(("http://", "https://")):
        job_url = args.source
    else:
        sidecar = pathlib.Path(args.source).with_suffix(".json")
        if sidecar.exists():
            job_url = (json.loads(sidecar.read_text(encoding="utf-8")) or {}).get("url", "")
        else:
            # Fallback to database lookup for URL
            try:
                from .shared.db import get_conn
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT url FROM jobs WHERE slug = ? OR job_id = ?", (str(args.source), str(args.source)))
                        row = cur.fetchone()
                        if row and row["url"]:
                            job_url = row["url"]
            except Exception:
                pass
    print("Extracting JobSpec ...", file=sys.stderr)
    spec = jobspec_mod.extract_jobspec(job_text)
    tailoring = rank.tailor(spec, profile, projects, taxonomy=taxonomy, ranking=ranking)
    clusters = rank.job_clusters(spec, taxonomy, rank.invert_aliases(taxonomy.get("aliases", {})))

    job_id = _job_id_from_source(str(args.source))
    slug = args.slug or _slugify(spec.get("company", ""), spec.get("title", ""), job_id)
    out = _jobs_dir() / slug
    out.mkdir(parents=True, exist_ok=True)

    print("Selecting CV variant ...", file=sys.stderr)
    from .domains.tailoring import variants
    aliases_flat = rank.invert_aliases(taxonomy.get("aliases", {}))
    
    variant_override = getattr(args, "variant", None)
    if variant_override:
        variant_name = variant_override
        print(f"Using manually forced CV variant: {variant_name}", file=sys.stderr)
    else:
        variant_name = variants.select_best_cv_variant(spec, job_text, taxonomy, aliases_flat)
        
    variant_file = ROOT / "data" / "cv-variants" / variant_name
    if not variant_file.exists():
        raise SystemExit(
            f"CRITICAL ERROR: CV variant file '{variant_name}' does not exist in 'data/cv-variants/'. "
            "Please run 'scripts/generate_baseline_variants.py' or create it first."
        )
    variant_content = variant_file.read_text(encoding="utf-8")
    cv_meta, cv_body = documents.split_front_matter(variant_content)
    tagline = spec.get("title") or cv_meta.get("tagline") or "Senior Software Engineer"
    
    cv_projects = variants.extract_projects_from_cv(variant_content, projects)
    if cv_projects:
        tailoring["top_projects"] = cv_projects

    print("Rendering cover letter ...", file=sys.stderr)
    instructions = getattr(args, "instructions", None) or ""
    cl_body = render.render_cover_letter(
        spec, tailoring, profile.get("summary", ""), job_text,
        availability=profile.get("availability", ""),
        relocation=_student_relocation(spec.get("title", ""), profile.get("relocation", "")),
        custom_instructions=instructions,
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
        _hub_page(spec.get("title", "Role"), spec.get("company", ""),
                  clusters=clusters, job_url=job_url),
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
    args.slug = _resolve_slug(args.slug)
    app = _jobs_dir() / args.slug
    if not app.is_dir():
        raise SystemExit(f"no such application: {app}")
    _translate_app(args.slug)
    print("Review the German output, then `cv-tailor pdf` to compile bilingual PDFs.")
    return 0


def cmd_pdf(args: argparse.Namespace) -> int:
    """Render the LaTeX CV + cover letter (bilingual) and compile to PDFs."""
    args.slug = _resolve_slug(args.slug)
    pdfs = _build_app(args.slug)
    if not pdfs:
        raise SystemExit("no PDFs produced (missing cv.md/cover-letter.md?)")
    for p in pdfs:
        print(f"  wrote {p}")
    return 0


def _get_db_tracker_csv() -> str:
    from .shared.db import get_conn
    import csv, io
    _csv_fields = ["slug", "company", "job_title", "status", "date_found",
                   "job_url", "drive_url", "drive_updated", "clusters"]
    rows = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT j.slug, j.company, j.title as job_title, a.status, 
                       j.created_at::date as date_found, j.url as job_url, 
                       a.drive_url, a.updated_at::text as drive_updated, a.clusters
                FROM jobs j
                JOIN applications a ON j.slug = a.slug
                ORDER BY 
                    CASE a.status
                        WHEN 'draft' THEN 1
                        WHEN 'applied' THEN 2
                        WHEN 'interview' THEN 3
                        WHEN 'offer' THEN 4
                        WHEN 'rejected' THEN 5
                        WHEN 'withdrawn' THEN 6
                        ELSE 99
                    END, j.company ASC
            """)
            db_rows = cur.fetchall()
            for r in db_rows:
                rows.append({
                    "slug": r.get("slug", ""),
                    "company": r.get("company", ""),
                    "job_title": r.get("job_title", ""),
                    "status": r.get("status", ""),
                    "date_found": str(r.get("date_found", "")),
                    "job_url": r.get("job_url", "") or "",
                    "drive_url": r.get("drive_url", "") or "",
                    "drive_updated": r.get("drive_updated", "") or "",
                    "clusters": ";".join(r.get("clusters") or []),
                })
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_csv_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _sync_db_remote_statuses(sheet_statuses: dict[str, str]) -> list[str]:
    from .shared.db import get_conn
    changed = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            for slug, remote_status in sheet_statuses.items():
                cur.execute("SELECT status FROM applications WHERE slug = %s", (slug,))
                row = cur.fetchone()
                if row and row["status"] != remote_status:
                    cur.execute("UPDATE applications SET status = %s WHERE slug = %s", (remote_status, slug))
                    changed.append(f"{slug} → {remote_status}")
        conn.commit()
    return changed


def cmd_status(args: argparse.Namespace) -> int:
    """Pull sheet → sync remote changes → apply local status → push CSV back to sheet."""
    from .shared.db import init_db
    url, token = os.environ.get("APPS_SCRIPT_URL"), os.environ.get("APPS_SCRIPT_TOKEN")
    if not url or not token:
        raise SystemExit("set APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN in .env (see apps-script/README.md)")

    if args.slug == "push":
        print("Pushing local state to Google Sheets...")
        csv_path = _write_tracker()
        n = _push_to_sheets(url, token, csv_path)
        print(f"pushed {n} rows to sheet")
        return 0

    elif args.slug == "pull":
        print("pulling from sheet ...")
        sheet_statuses = _pull_sheet_statuses(url, token)
        changed = _sync_remote_statuses(sheet_statuses)
        if changed:
            print(f"  synced {len(changed)} remote change(s) directly to local files:")
            for c in changed:
                print(f"    {c}")
            # Refresh local DuckDB cache with new statuses
            init_db()
            # Regenerate tracker.csv with updated values
            _write_tracker()
        else:
            print("  no remote status changes")
        return 0

    # Else standard: cv-tailor status <slug> <state>
    slug = _resolve_slug(args.slug)
    hub = _jobs_dir() / slug / "index.md"
    if not hub.exists():
        raise SystemExit(f"no such application: {hub}")

    state = args.state
    if not state:
        raise SystemExit("Missing state argument (e.g. cv-tailor status acme applied)")
        
    if state not in _STATUSES:
        print(f"warning: '{state}' is not a standard status ({', '.join(_STATUSES)})",
              file=sys.stderr)

    # Update local index.md status (the single source of truth)
    hub = _jobs_dir() / slug / "index.md"
    if hub.exists():
        text = hub.read_text(encoding="utf-8")
        new, n = re.subn(r"(?m)^status:.*$", f"status: {_yaml(state)}", text)
        if n > 0:
            hub.write_text(new, encoding="utf-8")

    # Refresh local DuckDB cache
    init_db()

    # Always auto-generate tracker.csv on modification
    csv_path = _write_tracker()

    if url and token:
        _push_to_sheets(url, token, csv_path)
        print(f"set {slug} → {state} (synced with Files & Sheets)")
    else:
        print(f"set {slug} → {state} (review diff + commit)")
    return 0


def cmd_db_export(args: argparse.Namespace) -> int:
    from .shared.db import get_conn
    import csv, json, pathlib

    export_dir = pathlib.Path("application-data")
    export_dir.mkdir(parents=True, exist_ok=True)

    # Helper to dump table to CSV
    def dump_table_to_csv(table_name, filename):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {table_name}")
                rows = cur.fetchall()
                if not rows:
                    return
                fields = list(rows[0].keys())
                csv_path = export_dir / filename
                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fields)
                    writer.writeheader()
                    for r in rows:
                        row_copy = dict(r)
                        if "clusters" in row_copy and isinstance(row_copy["clusters"], list):
                            row_copy["clusters"] = ";".join(row_copy["clusters"])
                        writer.writerow(row_copy)
                print(f"  exported {table_name} table to {csv_path}")

    print("Exporting database state to flat files...")
    dump_table_to_csv("jobs", "jobs.csv")
    dump_table_to_csv("applications", "applications.csv")

    # Export JDs and applications folders
    jds_dir = export_dir / "jds"
    jds_dir.mkdir(parents=True, exist_ok=True)
    
    apps_dir = export_dir / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Export JDs
            cur.execute("SELECT slug, description FROM jobs WHERE description IS NOT NULL")
            for r in cur.fetchall():
                (jds_dir / f"{r['slug']}.txt").write_text(r["description"], encoding="utf-8")
                
            # Export applications folders
            cur.execute("""
                SELECT j.slug, j.company, j.title, j.url, a.status, a.recipient, 
                       a.cv_en, a.cv_de, a.cover_letter_en, a.cover_letter_de, 
                       a.drive_url, a.clusters
                FROM jobs j JOIN applications a ON j.job_id = a.job_id
            """)
            for r in cur.fetchall():
                slug = r["slug"]
                slug_dir = apps_dir / slug
                slug_dir.mkdir(parents=True, exist_ok=True)

                def write_file_safe(filename, content):
                    if content is not None:
                        (slug_dir / filename).write_text(content, encoding="utf-8")

                write_file_safe("cv.md", r["cv_en"])
                write_file_safe("cv.de.md", r["cv_de"])
                write_file_safe("cover-letter.md", r["cover_letter_en"])
                write_file_safe("cover-letter.de.md", r["cover_letter_de"])
                
                # Metadata JSON
                meta = {
                    "slug": slug,
                    "company": r["company"],
                    "title": r["title"],
                    "url": r["url"] or "",
                    "status": r["status"],
                    "recipient": r["recipient"] or "",
                    "drive_url": r["drive_url"] or "",
                    "clusters": r["clusters"] or [],
                }
                (slug_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Database exported successfully. Backup output is located at {export_dir}/")
    return 0


def _write_tracker() -> pathlib.Path:
    """Regenerate applications/tracker.csv from per-application index.md front matter."""
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
    _csv_fields = ["slug", "company", "job_title", "status", "date_found",
                   "job_url", "drive_url", "drive_updated", "clusters"]
    csv_rows = [{
        "slug": r.get("slug", ""),
        "company": r.get("company", ""),
        "job_title": r.get("job_title", ""),
        "status": r.get("status", ""),
        "date_found": r.get("date_found", "") or "",
        "job_url": r.get("job_url", "") or "",
        "drive_url": r.get("drive_url", "") or "",
        "drive_updated": r.get("drive_updated", "") or "",
        "clusters": ";".join(r.get("clusters") or []),
    } for r in rows]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_csv_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(csv_rows)
    csv_path = jobs / "tracker.csv"
    csv_path.write_text(buf.getvalue(), encoding="utf-8")
    return csv_path


def _pull_sheet_statuses(url: str, token: str) -> dict[str, str]:
    """Fetch the status column from the Google Sheet. Returns {slug: status}."""
    payload = {"token": token, "action": "get_tracker"}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "text/plain;charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode("utf-8"))
        if not resp.get("ok") or not resp.get("csv"):
            return {}
        reader = csv.DictReader(io.StringIO(resp["csv"]))
        return {row["slug"]: row["status"]
                for row in reader if row.get("slug") and row.get("status")}
    except Exception as exc:
        print(f"warning: could not pull from sheet: {exc}", file=sys.stderr)
        return {}


def _sync_remote_statuses(sheet_statuses: dict[str, str]) -> list[str]:
    """Update index.md status for any slug where the sheet has a different value."""
    changed = []
    for slug, remote_status in sheet_statuses.items():
        hub = _jobs_dir() / slug / "index.md"
        if not hub.exists():
            continue
        meta, _ = documents.split_front_matter(hub.read_text(encoding="utf-8"))
        if meta.get("status") != remote_status:
            text = hub.read_text(encoding="utf-8")
            new, n = re.subn(r"(?m)^status:.*$", f"status: {_yaml(remote_status)}", text)
            if n:
                hub.write_text(new, encoding="utf-8")
                changed.append(f"{slug} → {remote_status}")
    return changed


def _push_to_sheets(url: str, token: str, csv_path: pathlib.Path) -> int:
    """Push tracker.csv to the Google Sheet. Returns row count."""
    payload = {"token": token, "action": "sync_tracker",
               "csv": csv_path.read_text(encoding="utf-8")}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "text/plain;charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read().decode("utf-8"))
    if not resp.get("ok"):
        raise SystemExit(f"sheet push failed: {resp}")
    return resp.get("rows", 0)


def cmd_track(args: argparse.Namespace) -> int:
    """Regenerate applications/tracker.csv from per-app front matter."""
    csv_path = _write_tracker()
    print(f"wrote {csv_path}")
    return 0


def cmd_sync_sheets(args: argparse.Namespace) -> int:
    """Pull sheet status changes → merge locally → push updated CSV back to sheet."""
    url = os.environ.get("APPS_SCRIPT_URL")
    token = os.environ.get("APPS_SCRIPT_TOKEN")
    if not url or not token:
        raise SystemExit("set APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN in .env (see apps-script/README.md)")
    
    if getattr(args, "push_only", False):
        print("skip pull: force-pushing local tracker to Google Sheets...")
        csv_path = _write_tracker()
        n = _push_to_sheets(url, token, csv_path)
        print(f"pushed {n} rows to sheet")
        return 0

    print("pulling from sheet ...")
    sheet_statuses = _pull_sheet_statuses(url, token)
    changed = _sync_remote_statuses(sheet_statuses)
    if changed:
        print(f"  synced {len(changed)} remote change(s):")
        for c in changed:
            print(f"    {c}")
    else:
        print("  no remote status changes")
    csv_path = _write_tracker()
    n = _push_to_sheets(url, token, csv_path)
    print(f"pushed {n} rows to sheet")
    if changed:
        print("review the diff and commit to record the remote status changes")
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    """Move the Drive folder to Archive/, set status → withdrawn, sync CSV + sheet."""
    args.slug = _resolve_slug(args.slug)
    hub = _jobs_dir() / args.slug / "index.md"
    if not hub.exists():
        raise SystemExit(f"no such application: {hub}")

    url, token = os.environ.get("APPS_SCRIPT_URL"), os.environ.get("APPS_SCRIPT_TOKEN")
    if not url or not token:
        raise SystemExit("set APPS_SCRIPT_URL and APPS_SCRIPT_TOKEN in .env")

    if url and token:
        sheet_statuses = _pull_sheet_statuses(url, token)
        changed = _sync_remote_statuses(sheet_statuses)
        if changed:
            print(f"synced {len(changed)} remote change(s): {', '.join(changed)}")

    payload = {"token": token, "action": "archive_application", "slug": args.slug}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "text/plain;charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read().decode("utf-8"))
    if not resp.get("ok"):
        raise SystemExit(f"archive failed: {resp}")

    new_drive_url = resp.get("folderUrl", "")
    _set_front_matter_fields(hub, {"status": "withdrawn", "drive_url": new_drive_url})
    csv_path = _write_tracker()
    _push_to_sheets(url, token, csv_path)
    print(f"archived {args.slug}")
    print(f"drive → {new_drive_url}")
    print("review diff + commit")
    return 0


def cmd_upload(args: argparse.Namespace) -> int:
    """Compile the PDFs and upload them to Google Drive via the Apps Script endpoint."""
    args.slug = _resolve_slug(args.slug)
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


def _make_session():
    """Build a LinkedInSession from env. Shared by `ingest`/`hunt` and `capture`.

    A TTY resolves login challenges via stdin; otherwise (Xvfb/CI) it polls a file
    inbox under vault/challenges. The persistent profile (vault/profile) keeps us
    logged in across runs."""
    from .domains.linkedin.session import FileInboxResolver, LinkedInSession, StdinResolver

    vault = os.environ.get("CV_TAILOR_VAULT", "vault")
    user_data_dir = os.environ.get("LINKEDIN_USER_DATA_DIR", f"{vault}/profile")
    challenge_timeout = float(os.environ.get("LINKEDIN_CHALLENGE_TIMEOUT", "300"))
    resolver = (
        StdinResolver()
        if sys.stdin.isatty()
        else FileInboxResolver(pathlib.Path(vault) / "challenges", timeout=challenge_timeout)
    )
    return LinkedInSession(
        user_data_dir=user_data_dir, vault_dir=vault,
        resolver=resolver, challenge_timeout=challenge_timeout,
    )


def _drive_session(action) -> None:
    """Open the logged-in LinkedIn session, run action(page), and always close."""
    from playwright.sync_api import sync_playwright

    session = _make_session()
    with sync_playwright() as p:
        session.context(p)
        try:
            session.with_session(action)
        finally:
            session.close()


def _job_id_from_url(url: str) -> str:
    """Pull the numeric job id from a view URL (/jobs/view/<id>) or a search URL
    (...?currentJobId=<id>)."""
    m = re.search(r"(?:/jobs/view/|currentJobId=)(\d+)", url)
    if not m:
        raise SystemExit(
            f"no job id in URL (expected /jobs/view/<id> or currentJobId=<id>): {url}"
        )
    return m.group(1)


def _extract_title_company(page) -> tuple[str, str]:
    """Best-effort (title, company) for a logged-in job page: JSON-LD JobPosting
    first, then the 'Company hiring Title in Location' og:title / <title>."""
    try:
        data = page.evaluate(
            """() => {
                for (const s of document.querySelectorAll(
                        'script[type="application/ld+json"]')) {
                    try {
                        const j = JSON.parse(s.textContent);
                        for (const o of (Array.isArray(j) ? j : [j])) {
                            if (o && o['@type'] === 'JobPosting') {
                                const org = o.hiringOrganization;
                                return {title: o.title || '',
                                        company: org ? (org.name || '') : ''};
                            }
                        }
                    } catch (e) {}
                }
                const og = document.querySelector('meta[property="og:title"]');
                return {raw: (og && og.content) || document.title || ''};
            }"""
        ) or {}
    except Exception:
        data = {}
    title = (data.get("title") or "").strip()
    company = (data.get("company") or "").strip()
    if not (title and company):
        raw = (data.get("raw") or "").split(" | LinkedIn")[0]
        m = re.match(r"^(?P<company>.+?) hiring (?P<title>.+?) in .+$", raw)
        if m:
            title = title or m.group("title").strip()
            company = company or m.group("company").strip()
    return title, company


def _do_ingest(searches: list[dict], out_dir: pathlib.Path) -> dict:
    """Drive ONE logged-in LinkedIn session through a list of search specs and capture
    JDs. Stop-before-submit (D4). Each spec is a dict with keywords + the optional
    filter keys (location, geo_id, distance, days_back, max_applicants, easy_apply,
    limit, name). The session is reused across all searches, so one login covers them
    all and `.seen.json` dedups across the whole run."""
    import logging

    from .domains.linkedin import jobs as J
    from .domains.linkedin.humanize import human_pause

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    seen_path = out_dir / ".seen.json"
    counts = {"captured": 0, "skipped": 0}

    def run(page) -> None:
        seen = J.load_seen(seen_path)
        for spec in searches:
            max_applicants = spec.get("max_applicants")
            name = spec.get("name") or spec["keywords"]
            print(f"\n── search: {name} ──")
            found = J.search(
                page, spec["keywords"], spec.get("location"), spec.get("limit", 10),
                days_back=spec.get("days_back", 7), max_applicants=max_applicants,
                geo_id=spec.get("geo_id"), distance=spec.get("distance"),
                easy_apply=spec.get("easy_apply", False),
            )
            for job in found:
                if J.already_seen(job.job_id, seen):
                    counts["skipped"] += 1
                    continue
                try:
                    text = J.capture_jd(page, job)
                except Exception as e:  # noqa: BLE001
                    print(f"  skip {job.url}: {e}", file=sys.stderr)
                    continue
                if max_applicants is not None and job.applicants is not None:
                    if job.applicants > max_applicants:
                        print(f"  skip {job.url}: {job.applicants} applicants > {max_applicants}")
                        continue
                captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
                path = J.write_jd(job, text, out_dir, captured_at)
                seen[job.job_id] = J.slugify(job.company, job.title, job.job_id)
                counts["captured"] += 1
                applicants_str = (
                    f" ({job.applicants} applicants)" if job.applicants is not None else ""
                )
                print(f"  captured {path}{applicants_str}")
                human_pause(2.0, 5.0)
        J.save_seen(seen_path, seen)

    _drive_session(run)

    print(f"\ningest done: captured {counts['captured']}, skipped {counts['skipped']} (seen)")
    return counts


def cmd_ingest(args: argparse.Namespace) -> int:
    """Capture JDs for a single ad-hoc search (CLI flags). For the configured batch
    of searches, use `cv-tailor hunt`."""
    spec = {
        "keywords": args.keywords,
        "location": args.location,
        "limit": args.limit,
        "days_back": args.days,
        "max_applicants": args.max_applicants,
        "geo_id": args.geo_id,
        "distance": args.distance,
        "easy_apply": args.easy_apply,
    }
    _do_ingest([spec], pathlib.Path(args.out))
    return 0


def cmd_hunt(args: argparse.Namespace) -> int:
    """Run every search in the runtime config (config/search.yml) in one session.

    Dispatches by the optional `source:` key in each search entry (default: linkedin).
    LinkedIn searches share one logged-in Playwright session (needs Xvfb).
    Fraunhofer searches run in their own headless browser (no session needed).
    """
    import logging

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    cfg = config_mod.resolve_search()
    searches = cfg["searches"]
    if not searches:
        print(f"no searches defined in {cfg['path']}", file=sys.stderr)
        return 1
    names = ", ".join(s["name"] for s in searches)
    print(f"hunt: {len(searches)} search(es) from {cfg['path']} — {names}")

    out_dir = pathlib.Path(args.out)
    linkedin_searches = [s for s in searches if s.get("source", "linkedin") == "linkedin"]
    fraunhofer_searches = [s for s in searches if s.get("source") == "fraunhofer"]
    other_sources = [
        s["name"] for s in searches
        if s.get("source", "linkedin") not in ("linkedin", "fraunhofer")
    ]
    if other_sources:
        print(f"warning: unknown source in searches (skipped): {', '.join(other_sources)}",
              file=sys.stderr)

    if linkedin_searches:
        _do_ingest(linkedin_searches, out_dir)

    if fraunhofer_searches:
        from .domains.fraunhofer import jobs as FJ

        for spec in fraunhofer_searches:
            name = spec.get("name") or spec.get("keywords", "fraunhofer")
            print(f"\n── fraunhofer search: {name} ──")
            counts = FJ.hunt_and_capture(
                spec["keywords"],
                out_dir,
                location=spec.get("location"),
                limit=spec.get("limit", 10),
            )
            print(f"  captured {counts['captured']}, skipped {counts['skipped']} (seen), "
                  f"errors {counts['errors']}")

    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    """Capture ONE job link (a /jobs/view/<id> URL or a search URL carrying
    currentJobId=<id>) to vault/jds/<slug>.txt (+ .json sidecar), using the logged-in
    session — so we get the real description behind the auth wall. Feed the resulting
    file to `cv-tailor new` (which reads the sidecar for the posting URL)."""
    from .domains.linkedin import jobs as J

    job_id = _job_id_from_url(args.url)
    view_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
    out_dir = pathlib.Path(args.out)
    result: dict = {}

    def run(page) -> None:
        # capture_jd navigates + expands the description; read title/company after, off
        # the settled page (JSON-LD / og:title), then write_jd derives the slug from them.
        job = J.Job(job_id=job_id, title="role", company="company", location="", url=view_url)
        text = J.capture_jd(page, job)
        title, company = _extract_title_company(page)
        job.title = title or job.title
        job.company = company or job.company
        captured_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        result["path"] = J.write_jd(job, text, out_dir, captured_at)
        result["slug"] = J.slugify(job.company, job.title, job.job_id)
        result["title"], result["company"] = job.title, job.company

    _drive_session(run)

    if not result.get("path"):
        raise SystemExit("capture produced no JD")
    print(f"\ncaptured {result['path']}")
    print(f"  company: {result['company']}   title: {result['title']}")
    print(f"\nNext: cv-tailor new {result['path']} --slug {result['slug']}")
    return 0


def cmd_screenshot(args: argparse.Namespace) -> int:
    """Capture a job posting from a URL or local screenshot file via PixelRAG + Ollama vision.

    Renders the page to JPEG tiles using PixelRAG's Chrome CDP renderer (no LinkedIn
    session required), then calls an Ollama vision model to extract the title, company,
    location, and full JD body text. Works for any URL Chrome can render, plus local
    .png/.jpg files. Output is the same vault/jds/<slug>.txt + .json that `cv-tailor new`
    consumes unchanged."""
    try:
        from .pixel_capture import VISION_MODEL_DEFAULT, capture_screenshot
    except ImportError as exc:
        raise SystemExit(
            "Screenshot capture needs PixelRAG render. "
            "Run: make install-screenshot\n"
            "Then pull a vision model: ollama pull qwen3-vl:8b"
        ) from exc

    vision_model = args.vision_model or os.environ.get(
        "CV_TAILOR_VISION_MODEL", VISION_MODEL_DEFAULT
    )
    out_dir = pathlib.Path(args.out)
    path = capture_screenshot(
        args.source,
        out_dir,
        vision_model=vision_model,
        keep_tiles=args.keep_tiles,
    )
    sidecar = path.with_suffix(".json")
    slug = json.loads(sidecar.read_text())["slug"] if sidecar.exists() else path.stem
    print(f"\ncaptured {path}")
    print(f"\nNext: cv-tailor new {path} --slug {slug}")
    return 0


def cmd_gmail_search(args: argparse.Namespace) -> int:
    include_bodies = getattr(args, "include_bodies", False) or getattr(args, "json", False)
    threads = gmail.search_emails(args.query, args.limit, include_bodies)
    if args.json:
        print(json.dumps(threads, indent=2))
        return 0

    print(f"Found {len(threads)} threads:\n")
    for t in threads:
        status = []
        if t.get("isUnread"):
            status.append("UNREAD")
        if t.get("isStarred"):
            status.append("STARRED")
        if t.get("isImportant"):
            status.append("IMPORTANT")
        status_str = f"[{' '.join(status)}]" if status else ""
        print(f"ID: {t.get('id')} {status_str}")
        print(f"Sub: {t.get('subject')} | {t.get('snippet')}\n")
    return 0


def cmd_gmail_read(args: argparse.Namespace) -> int:
    t = gmail.get_thread(args.thread_id)
    if not t:
        print(f"Thread {args.thread_id} not found.")
        return 1
    print(f"Subject: {t.get('subject')}\n")
    for m in t.get("messages", []):
        print(f"--- From: {m.get('sender')} ---")
        print(m.get("body"))
        print("-" * 40 + "\n")
    return 0


def cmd_gmail_modify(args: argparse.Namespace) -> int:
    ids = sys.stdin.read().split() if args.thread_ids == ["-"] else args.thread_ids

    read_flag = None
    if args.read:
        read_flag = True
    elif args.unread:
        read_flag = False

    star_flag = None
    if args.star:
        star_flag = True
    elif args.unstar:
        star_flag = False

    imp_flag = None
    if args.important:
        imp_flag = True
    elif args.unimportant:
        imp_flag = False

    count = gmail.batch_modify_threads(ids, read_flag, star_flag, imp_flag)
    print(f"Modified {count} threads.")
    return 0


def cmd_gmail_send(args: argparse.Namespace) -> int:
    if args.bulk_file:
        emails = json.loads(pathlib.Path(args.bulk_file).read_text(encoding="utf-8"))
    else:
        if not args.to or not args.subject or not args.body:
            raise SystemExit("Missing --to, --subject, or --body")
        emails = [{"to": args.to, "subject": args.subject, "body": args.body}]

    res = gmail.batch_send_emails(emails)
    print(f"Sent {res.get('sentCount')} emails. Remaining quota: {res.get('remainingQuota')}")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    profile, _, _, taxonomy, _ = _load_data()
    from .domains.tailoring import analysis
    from engine.shared import config

    cluster_key = args.cluster
    cfg = config.load()
    cv_variants = cfg.get("tailoring", {}).get("cv_variants", {})
    
    print(f"\n======================================================================")
    print(f"  COMPOSE PIPELINE: CLUSTER ANALYSIS FOR '{cluster_key.upper()}'")
    print(f"======================================================================\n")

    # 1. Run Extractor
    signals = analysis.extract_cluster_signals(cluster_key, taxonomy, profile)
    num_jobs = signals["analysis_metadata"]["analyzed_jobs_count"]
    if num_jobs == 0:
        print(f"No job postings found heavily matching cluster '{cluster_key}' in the database.\n")
        return 0

    print(f"Analyzed {num_jobs} matching job descriptions from your database.")
    print(f"Timestamp: {signals['analysis_metadata']['timestamp']}\n")

    # 2. Print Signals
    print("--- HIGH-FREQUENCY TECHNICAL SIGNALS ---")
    for category, terms in signals["domain_signals"].items():
        if not terms:
            continue
        header = category.replace("_", " ").title()
        print(f"\n  [{header}]")
        for t in terms:
            core_marker = " [CORE]" if t["is_core"] else ""
            print(f"    - {t['term']} (Freq: {int(t['frequency']*100)}%){core_marker}")

    # 3. Print Thematic Phrases
    if signals["thematic_phrases"]:
        print("\n\n--- CORE THEMATIC PHRASES & CONTEXTS ---")
        for p in signals["thematic_phrases"]:
            print(f'\n  "... {p} ..."')

    # 4. Print Gap Analysis (Consumer A)
    variant_name = cv_variants.get(cluster_key)
    if variant_name:
        variant_file = ROOT / "data" / "cv-variants" / variant_name
        if variant_file.exists():
            print(f"\n\n--- KEYWORD GAP REPORT vs CV VARIANT '{variant_name}' ---")
            cv_content = variant_file.read_text(encoding="utf-8")
            gap = analysis.gap_analyzer(signals, cv_content)
            
            # Print matching
            print(f"\n  [Matching Keywords - {len(gap['matching_signals'])} found]")
            for m in gap["matching_signals"]:
                print(f"    ✔ {m['term']} (Freq: {int(m['frequency']*100)}%)")
                
            # Print missing
            print(f"\n  [Missing Keywords - {len(gap['missing_signals'])} missing] 🌟 Action Items")
            for m in gap["missing_signals"]:
                print(f"    ❌ {m['term']} (Freq: {int(m['frequency']*100)}%) --> Add to {variant_name}")
        else:
            print(f"\n\n[Variant Warning] CV variant file '{variant_name}' mapped but not found on disk at 'data/cv-variants/'.")

    # 5. Print Taxonomy Suggestions (Consumer B)
    suggestions = analysis.taxonomy_sync(signals, taxonomy)
    if suggestions:
        print("\n\n--- UNMAPPED MARKET TERMS (TAXONOMY UPDATE SUGGESTIONS) ---")
        for sug in suggestions:
            print(f"\n  - Suggested term: '{sug['term']}' (found in {int(sug['frequency']*100)}% of matching jobs)")
            print(f"    Action: {sug['suggested_action']}")
            
    print(f"\n======================================================================\n")
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
    p_new.add_argument("--variant", default=None, help="Force a specific CV variant filename (e.g. telecommunication.md) and bypass automatic classification.")
    p_new.add_argument("--instructions", default=None, help="Custom instructions or guidance for tailoring.")
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
    p_ingest.add_argument("--days", type=int, default=7,
                          help="only surface jobs posted within this many days (default: 7)")
    p_ingest.add_argument("--max-applicants", type=int, default=None, dest="max_applicants",
                          help="discard jobs with more than this many applicants")
    p_ingest.add_argument("--geo-id", default=None, dest="geo_id",
                          help="LinkedIn region id (&geoId=); preferred over --location")
    p_ingest.add_argument("--distance", type=float, default=None,
                          help="search radius in km (&distance=)")
    p_ingest.add_argument("--easy-apply", action="store_true", dest="easy_apply",
                          help="restrict to LinkedIn 'Easy Apply' listings (&f_EA=true)")
    p_ingest.add_argument("--out", default="vault/jds", help="output dir for JD files")
    p_ingest.set_defaults(func=cmd_ingest)

    p_hunt = sub.add_parser(
        "hunt", help="run every search in config/search.yml and capture JDs"
    )
    p_hunt.add_argument("--out", default="vault/jds", help="output dir for JD files")
    p_hunt.set_defaults(func=cmd_hunt)

    p_cap = sub.add_parser(
        "capture", help="capture ONE job link (view URL or ?currentJobId=) to vault/jds/"
    )
    p_cap.add_argument("url", help="LinkedIn job URL (/jobs/view/<id> or ...?currentJobId=<id>)")
    p_cap.add_argument("--out", default="vault/jds", help="output dir for the JD file")
    p_cap.set_defaults(func=cmd_capture)

    p_shot = sub.add_parser(
        "screenshot",
        help="capture a job posting via screenshot + Ollama vision (no LinkedIn session; any URL or local .png/.jpg)",
    )
    p_shot.add_argument(
        "source", help="job posting URL or path to a local screenshot file (.png/.jpg)"
    )
    p_shot.add_argument("--out", default="vault/jds", help="output dir for JD files")
    p_shot.add_argument(
        "--vision-model",
        default=None,
        dest="vision_model",
        help="Ollama vision model (default: qwen3-vl:8b; env: CV_TAILOR_VISION_MODEL)",
    )
    p_shot.add_argument(
        "--keep-tiles",
        action="store_true",
        dest="keep_tiles",
        help="keep rendered tile directory after extraction (for debugging)",
    )
    p_shot.set_defaults(func=cmd_screenshot)

    p_pdf = sub.add_parser("pdf", help="render the LaTeX CV + cover letter and compile to PDFs")
    p_pdf.add_argument("slug", help="application slug")
    p_pdf.set_defaults(func=cmd_pdf)

    p_up = sub.add_parser("upload", help="compile + upload the PDFs to Google Drive")
    p_up.add_argument("slug", help="application slug")
    p_up.set_defaults(func=cmd_upload)

    p_status = sub.add_parser("status", help="advance an application's lifecycle status")
    p_status.add_argument("slug", help="application slug, 'push', or 'pull'")
    p_status.add_argument("state", nargs="?", default=None, help="draft|applied|interview|offer|rejected|withdrawn")
    p_status.set_defaults(func=cmd_status)

    p_track = sub.add_parser("track", help="regenerate applications/tracker.csv from index.md files")
    p_track.set_defaults(func=cmd_track)

    p_sheets = sub.add_parser("sync-sheets", help="bidirectional pull→merge→push with Google Sheets")
    p_sheets.add_argument("--push-only", action="store_true",
                          help="force push local tracker.csv to Sheets without pulling/merging remote changes")
    p_sheets.set_defaults(func=cmd_sync_sheets)

    p_archive = sub.add_parser("archive", help="move Drive folder to Archive/, set status withdrawn")
    p_archive.add_argument("slug", help="application slug or numeric job id")
    p_archive.set_defaults(func=cmd_archive)

    p_analyze = sub.add_parser("analyze", help="analyze saved jobs for a specific cluster and check keyword gaps")
    p_analyze.add_argument("--cluster", required=True, help="the taxonomy cluster to analyze (e.g. ml-ai)")
    p_analyze.set_defaults(func=cmd_analyze)

    p_gmail = sub.add_parser("gmail", help="Gmail operations via Apps Script proxy")
    gmail_sub = p_gmail.add_subparsers(dest="gmail_cmd", required=True)

    pg_search = gmail_sub.add_parser("search", help="Search emails")
    pg_search.add_argument("--query", required=True, help="Gmail search query")
    pg_search.add_argument("--limit", type=int, default=20)
    pg_search.add_argument("--json", action="store_true")
    pg_search.add_argument("--include-bodies", action="store_true", dest="include_bodies",
                           help="include message bodies in the results")
    pg_search.set_defaults(func=cmd_gmail_search)

    pg_read = gmail_sub.add_parser("read", help="Read a full thread by ID")
    pg_read.add_argument("thread_id")
    pg_read.set_defaults(func=cmd_gmail_read)

    pg_mod = gmail_sub.add_parser("modify", help="Batch modify thread status")
    pg_mod.add_argument("--thread-ids", nargs="+", required=True, help="List of IDs or '-' for stdin")
    pg_mod.add_argument("--read", action="store_true")
    pg_mod.add_argument("--unread", action="store_true")
    pg_mod.add_argument("--star", action="store_true")
    pg_mod.add_argument("--unstar", action="store_true")
    pg_mod.add_argument("--important", action="store_true")
    pg_mod.add_argument("--unimportant", action="store_true")
    pg_mod.set_defaults(func=cmd_gmail_modify)

    pg_send = gmail_sub.add_parser("send", help="Send emails")
    pg_send.add_argument("--to")
    pg_send.add_argument("--subject")
    pg_send.add_argument("--body")
    pg_send.add_argument("--bulk-file", help="Path to JSON file with array of email objects")
    pg_send.set_defaults(func=cmd_gmail_send)

    p_db = sub.add_parser("db", help="Database administrative and synchronization utilities")
    db_sub = p_db.add_subparsers(dest="db_cmd", required=True)

    pdb_export = db_sub.add_parser("export", help="export the entire database state to application-data/ on disk")
    pdb_export.set_defaults(func=cmd_db_export)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

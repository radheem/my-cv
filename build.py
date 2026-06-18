"""Build the site: mkdocs -> standalone document HTML -> PDFs -> encrypt.

Pipeline:
  1. `mkdocs build` -> site/ (gated docs are excluded from this build).
  2. Render the public general CV to a clean PDF (site/assets/cv.pdf).
  3. For each docs/jobs/<slug>/ application, from the SOURCE Markdown:
       - render a standalone, theme-independent HTML document (engine.documents),
       - AES-seal that HTML (the unlock view) and its WeasyPrint PDF into
         site/jobs/<slug>/vault/*.enc,
       - inject the vault config (salt, iterations, manifest) into the public hub.

The same standalone HTML feeds both the PDF and the in-browser view, so they
match and carry no MkDocs Material chrome. No API key needed; $GATE_PASSWORD
seals the gated content.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import yaml

import encrypt
from engine import documents

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
DOCS_JOBS = DOCS / "jobs"

# Gated documents per application. PDF-backed ones also produce a download blob.
GATED = [
    {"name": "cv", "label": "CV", "pdf": True},
    {"name": "cover-letter", "label": "Cover Letter", "pdf": True},
    {"name": "job-description", "label": "Job Description", "pdf": False},
]


def _run_mkdocs() -> None:
    print("mkdocs build ...", file=sys.stderr)
    subprocess.run(["mkdocs", "build", "--clean"], cwd=ROOT, check=True)


def _profile() -> dict:
    return yaml.safe_load((DATA / "profile.yml").read_text(encoding="utf-8"))


def _pdf_from_html(html_str: str, pdf_path: pathlib.Path) -> None:
    from weasyprint import HTML

    # CSS is inlined in the document, so no base_url is needed.
    HTML(string=html_str).write_pdf(str(pdf_path))


def _render_gated_html(name: str, meta: dict, body: str, profile: dict) -> str:
    if name == "cv":
        return documents.render_cv_html(body, meta.get("tagline", ""), profile)
    if name == "cover-letter":
        return documents.render_letter_html(body, meta, profile)
    return documents.render_plain_html("", body)


def _seal_application(slug: str, key: bytes, salt: bytes, profile: dict) -> None:
    src = DOCS_JOBS / slug
    vault = SITE / "jobs" / slug / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    manifest = []

    for doc in GATED:
        md_path = src / f"{doc['name']}.md"
        if not md_path.exists():
            print(f"  ! missing source: jobs/{slug}/{doc['name']}.md", file=sys.stderr)
            continue
        meta, body = documents.split_front_matter(md_path.read_text(encoding="utf-8"))
        html = _render_gated_html(doc["name"], meta, body, profile)

        (vault / f"{doc['name']}.html.enc").write_text(
            encrypt.seal(html.encode("utf-8"), key), encoding="ascii"
        )
        entry = {"key": doc["name"], "label": doc["label"], "html": f"{doc['name']}.html.enc"}

        if doc["pdf"]:
            pdf_tmp = vault / f"{doc['name']}.pdf"
            _pdf_from_html(html, pdf_tmp)
            (vault / f"{doc['name']}.pdf.enc").write_text(
                encrypt.seal(pdf_tmp.read_bytes(), key), encoding="ascii"
            )
            pdf_tmp.unlink()
            entry["pdf"] = f"{doc['name']}.pdf.enc"

        manifest.append(entry)

    _inject_config(SITE / "jobs" / slug / "index.html", salt, manifest)
    print(f"  sealed jobs/{slug}/ ({len(manifest)} docs)", file=sys.stderr)


def _inject_config(hub_html: pathlib.Path, salt: bytes, manifest: list) -> None:
    config = {
        "salt": encrypt.b64(salt),
        "iterations": encrypt.PBKDF2_ITERATIONS,
        "assets": manifest,
    }
    script = (
        '<script id="vault-config" type="application/json">'
        + json.dumps(config)
        + "</script>"
    )
    html = hub_html.read_text(encoding="utf-8")
    hub_html.write_text(html.replace("</body>", script + "</body>", 1), encoding="utf-8")


def _public_cv_pdf(profile: dict) -> None:
    cv_md = DOCS / "cv.md"
    if not cv_md.exists():
        return
    _, body = documents.split_front_matter(cv_md.read_text(encoding="utf-8"))
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    _pdf_from_html(documents.render_cv_raw(body), SITE / "assets" / "cv.pdf")
    print("rendered public assets/cv.pdf", file=sys.stderr)


def _scrub_search_index(slugs: list[str]) -> None:
    """Defensive: drop any gated record from the search index. With exclude_docs
    the gated pages are never built, so this is normally a no-op."""
    index = SITE / "search" / "search_index.json"
    if not index.exists():
        return
    prefixes = tuple(f"jobs/{slug}/{doc['name']}/" for slug in slugs for doc in GATED)
    data = json.loads(index.read_text(encoding="utf-8"))
    kept = [d for d in data.get("docs", []) if not d.get("location", "").startswith(prefixes)]
    if len(kept) != len(data.get("docs", [])):
        data["docs"] = kept
        index.write_text(json.dumps(data), encoding="utf-8")


def main() -> int:
    password = os.environ.get("GATE_PASSWORD")
    if not password:
        print("GATE_PASSWORD is required to seal gated content.", file=sys.stderr)
        return 2

    _run_mkdocs()
    profile = _profile()
    _public_cv_pdf(profile)

    salt = encrypt.new_salt()
    key = encrypt.derive_key(password, salt)

    slugs = [d.name for d in sorted(DOCS_JOBS.glob("*")) if (d / "index.md").exists()]
    if not slugs:
        print("No applications under docs/jobs/ — nothing to gate.", file=sys.stderr)
    for slug in slugs:
        _seal_application(slug, key, salt, profile)

    _scrub_search_index(slugs)
    print("Build complete.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

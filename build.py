"""Build the site: mkdocs -> WeasyPrint PDFs -> encrypt gated content.

Pipeline:
  1. `mkdocs build` -> site/
  2. Render the public CV page to a public PDF (site/assets/cv.pdf).
  3. For each docs/jobs/<slug>/ application:
       - render cv & cover-letter pages to PDFs (WeasyPrint),
       - AES-seal each gated HTML page AND its PDF into site/jobs/<slug>/vault/*.enc,
       - delete the plaintext gated pages from site/,
       - inject the vault config (salt, iterations, asset manifest) into the
         public unlock hub (site/jobs/<slug>/index.html).

No API key needed — generation already happened locally. Requires
$GATE_PASSWORD to seal the gated content.

Env:
  GATE_PASSWORD        required — password that unlocks the gated documents.
  CV_TAILOR_BASE_URL   optional — <base href> injected into gated HTML so its
                       relative asset links resolve when rendered in the unlock
                       iframe. Defaults to site_url from mkdocs.yml. For local
                       testing of `site/` served at the web root, set it to "/".
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import encrypt

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "site"
DOCS_JOBS = ROOT / "docs" / "jobs"

# Gated documents per application. PDF-backed ones also produce a download blob.
GATED = [
    {"name": "cv", "label": "CV", "pdf": True},
    {"name": "cover-letter", "label": "Cover Letter", "pdf": True},
    {"name": "job-description", "label": "Job Description", "pdf": False},
]


def _run_mkdocs() -> None:
    # Not --strict: the public CV PDF (assets/cv.pdf) is generated *after* this
    # step, so mkdocs would flag its link as unresolved. Warnings still print.
    print("mkdocs build ...", file=sys.stderr)
    subprocess.run(["mkdocs", "build", "--clean"], cwd=ROOT, check=True)


def _site_url() -> str:
    # Read the site_url line directly — mkdocs.yml carries Material's
    # !!python/name: tags that yaml.safe_load rejects.
    text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    m = re.search(r"^site_url:\s*(\S+)", text, re.MULTILINE)
    base = (m.group(1) if m else "/").strip().strip("\"'")
    return base.rstrip("/") + "/"


def _render_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path) -> None:
    from weasyprint import HTML

    # base_url = the file's directory so relative CSS/img resolve from site/.
    HTML(filename=str(html_path), base_url=str(html_path.parent)).write_pdf(
        str(pdf_path)
    )


def _inject_base_href(html: str, base: str) -> str:
    """Give gated HTML an absolute root so its relative links work in an iframe."""
    tag = f'<base href="{base}">'
    lower = html.lower()
    i = lower.find("<head>")
    if i != -1:
        return html[: i + len("<head>")] + tag + html[i + len("<head>") :]
    return tag + html


def _built_html(slug: str, name: str) -> pathlib.Path | None:
    """Locate a built gated page (mkdocs use_directory_urls -> <name>/index.html)."""
    d = SITE / "jobs" / slug
    for cand in (d / name / "index.html", d / f"{name}.html"):
        if cand.exists():
            return cand
    return None


def _seal_application(slug: str, key: bytes, salt: bytes, base: str) -> None:
    job_dir = SITE / "jobs" / slug
    vault = job_dir / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    manifest = []

    for doc in GATED:
        html_path = _built_html(slug, doc["name"])
        if html_path is None:
            print(f"  ! missing built page: jobs/{slug}/{doc['name']}", file=sys.stderr)
            continue

        # PDF first (from the on-disk HTML so WeasyPrint resolves CSS locally).
        if doc["pdf"]:
            pdf_tmp = vault / f"{doc['name']}.pdf"
            _render_pdf(html_path, pdf_tmp)
            (vault / f"{doc['name']}.pdf.enc").write_text(
                encrypt.seal(pdf_tmp.read_bytes(), key), encoding="ascii"
            )
            pdf_tmp.unlink()

        # Then seal the HTML page (with an absolute <base> for iframe rendering).
        html = _inject_base_href(html_path.read_text(encoding="utf-8"), base)
        (vault / f"{doc['name']}.html.enc").write_text(
            encrypt.seal(html.encode("utf-8"), key), encoding="ascii"
        )

        # Drop the plaintext page so nothing gated ships in the clear.
        page_dir = html_path.parent
        if page_dir.name == doc["name"]:
            shutil.rmtree(page_dir)
        else:
            html_path.unlink()

        entry = {"key": doc["name"], "label": doc["label"], "html": f"{doc['name']}.html.enc"}
        if doc["pdf"]:
            entry["pdf"] = f"{doc['name']}.pdf.enc"
        manifest.append(entry)

    _inject_config(job_dir / "index.html", salt, manifest)
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
    html = html.replace("</body>", script + "</body>", 1)
    hub_html.write_text(html, encoding="utf-8")


def main() -> int:
    password = os.environ.get("GATE_PASSWORD")
    if not password:
        print("GATE_PASSWORD is required to seal gated content.", file=sys.stderr)
        return 2

    _run_mkdocs()

    base = os.environ.get("CV_TAILOR_BASE_URL") or _site_url()

    # Public general CV -> public (unencrypted) PDF.
    public_cv = SITE / "cv" / "index.html"
    if public_cv.exists():
        (SITE / "assets").mkdir(parents=True, exist_ok=True)
        _render_pdf(public_cv, SITE / "assets" / "cv.pdf")
        print("rendered public assets/cv.pdf", file=sys.stderr)

    salt = encrypt.new_salt()
    key = encrypt.derive_key(password, salt)

    slugs = [d.name for d in sorted(DOCS_JOBS.glob("*")) if (d / "index.md").exists()]
    if not slugs:
        print("No applications under docs/jobs/ — nothing to gate.", file=sys.stderr)
    for slug in slugs:
        _seal_application(slug, key, salt, base)

    _scrub_search_index(slugs)

    print("Build complete.", file=sys.stderr)
    return 0


def _scrub_search_index(slugs: list[str]) -> None:
    """Drop gated pages from the MkDocs search index.

    Front-matter `search: exclude` already keeps them out, but the search index
    is plaintext and would otherwise leak the gated CV/cover-letter text — so we
    also strip any record under a gated document path here as a guarantee.
    """
    index = SITE / "search" / "search_index.json"
    if not index.exists():
        return
    prefixes = tuple(
        f"jobs/{slug}/{doc['name']}/" for slug in slugs for doc in GATED
    )
    data = json.loads(index.read_text(encoding="utf-8"))
    before = len(data.get("docs", []))
    data["docs"] = [
        d for d in data.get("docs", []) if not d.get("location", "").startswith(prefixes)
    ]
    removed = before - len(data["docs"])
    if removed:
        index.write_text(json.dumps(data), encoding="utf-8")
        print(f"  scrubbed {removed} gated entries from search index", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""One-time migration: append job_id to application directory names that lack it.

Extracts job_id from the job_url in each applications/<slug>/index.md, then
runs `git mv` to rename the directory so the slug ends with the numeric id.
Skips apps with no job_url or no numeric id in the URL, and apps already
correctly named.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPS = ROOT / "applications"

_ID_RE = re.compile(r"(\d{7,})/?$")
_TRAILING_NUM_RE = re.compile(r"-\d+$")


def job_id_from_url(url: str) -> str:
    m = _ID_RE.search(url.rstrip("/"))
    return m.group(1) if m else ""


def desired_slug(current: str, job_id: str) -> str:
    """Strip any trailing partial numeric suffix, then append the full job_id."""
    base = _TRAILING_NUM_RE.sub("", current).rstrip("-")
    return f"{base}-{job_id}"


def main() -> int:
    renames = []
    for d in sorted(APPS.glob("*")):
        if not d.is_dir():
            continue
        idx = d / "index.md"
        if not idx.exists():
            continue
        slug = d.name
        text = idx.read_text(encoding="utf-8")
        m = re.search(r'^job_url:\s*"?([^"\n]+)"?', text, re.MULTILINE)
        if not m:
            print(f"  skip (no job_url): {slug}")
            continue
        job_id = job_id_from_url(m.group(1).strip())
        if not job_id:
            print(f"  skip (no numeric id in url): {slug}")
            continue
        if slug.endswith(f"-{job_id}"):
            print(f"  ok: {slug}")
            continue
        new_slug = desired_slug(slug, job_id)
        renames.append((d, APPS / new_slug, slug, new_slug))

    if not renames:
        print("nothing to rename")
        return 0

    print(f"\n{len(renames)} rename(s) to perform:")
    for _, new_dir, old, new in renames:
        print(f"  {old}  →  {new}")

    if "--dry-run" in sys.argv:
        print("\ndry-run: no changes made")
        return 0

    for old_dir, new_dir, old, new in renames:
        if new_dir.exists():
            print(f"  ERROR: target already exists: {new_dir}", file=sys.stderr)
            return 1
        subprocess.run(["git", "mv", str(old_dir), str(new_dir)], check=True, cwd=ROOT)
        print(f"  renamed: {old} → {new}")

    print("\nregenerate tracker: cv-tailor track && cv-tailor sync-sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

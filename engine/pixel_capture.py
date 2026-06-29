"""Screenshot-based JD capture using PixelRAG's render pipeline + Ollama vision.

Renders any job posting URL (or a local screenshot file) to JPEG tiles via PixelRAG's
Chrome CDP renderer, then calls an Ollama vision model to extract structured metadata
(title, company, location, applicants) and the full JD body text. Writes the standard
vault/jds/<slug>.txt + .json files that `cv-tailor new` consumes unchanged.

No LinkedIn session required — works for any URL Chrome can render, and for any
locally-saved screenshot (.png/.jpg).

Prerequisites:
    make install-screenshot          # installs pixelrag_render
    ollama pull qwen3-vl:8b         # on genai.ltc.hsnet
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import tempfile

VISION_MODEL_DEFAULT = "qwen3-vl:32b"

METADATA_PROMPT = (
    "You are extracting job posting metadata from a screenshot of a job listing page.\n"
    "Look at the image and return a JSON object with exactly these fields:\n"
    '  "title": job title (string, required)\n'
    '  "company": company name (string, required)\n'
    '  "location": location shown on the posting (string, empty string if not visible)\n'
    '  "applicants": number of applicants shown (integer or null if not shown)\n'
    '  "job_id": numeric/alphanumeric job ID visible on the page or in a URL fragment '
    "(string or null if not visible)\n"
    "Return ONLY the raw JSON object — no markdown, no code fences, no other text."
)

BODY_PROMPT = (
    "You are extracting the full text of a job description from screenshots of a job posting.\n"
    "Transcribe all visible text related to the job: summary, description, responsibilities, "
    "qualifications, requirements, and benefits. Preserve section headers and bullet points.\n"
    "Omit: navigation menus, site header/footer, sidebar content unrelated to the job posting.\n"
    "Output plain text only — no markdown formatting."
)


def _ollama_client():
    from openai import OpenAI

    return OpenAI(
        base_url=os.environ.get("CV_TAILOR_OLLAMA_BASE_URL", "http://genai.ltc.hsnet:11434/v1"),
        api_key=os.environ.get("CV_TAILOR_OLLAMA_API_KEY", "ollama"),
    )


def _encode_tile(p: pathlib.Path) -> str:
    return base64.b64encode(p.read_bytes()).decode()


def _mime(p: pathlib.Path) -> str:
    return "image/jpeg" if p.suffix.lower() in (".jpg", ".jpeg") else "image/png"


def render_to_tiles(source: str, tmp_dir: pathlib.Path) -> tuple[pathlib.Path, list[pathlib.Path]]:
    """Render a URL or local image file to JPEG tiles. Returns (tile_dir, sorted tile paths)."""
    try:
        from pixelrag_render.render import render_file, render_url
    except ImportError as exc:
        raise SystemExit(
            "pixelrag_render is not installed. Run: make install-screenshot"
        ) from exc

    if source.startswith(("http://", "https://")):
        dirs = render_url(source, str(tmp_dir))
    else:
        dirs = render_file(source, str(tmp_dir))

    if not dirs:
        raise SystemExit(f"Rendering produced no output for: {source}")

    tile_dir = dirs[0]
    tiles = sorted(tile_dir.glob("tile_*.jpg"))
    if not tiles:
        tiles = sorted(tile_dir.glob("tile_*.png"))
    if not tiles:
        raise SystemExit(f"No tile files found in {tile_dir}")
    return tile_dir, tiles


def _derive_source_and_job_id(source: str) -> tuple[str, str]:
    """Return (source_label, job_id).

    LinkedIn URL  → ("linkedin", numeric_id)
    Other URL     → ("web", md5_12char)
    Local file    → ("file", md5_12char)
    """
    from .domains.linkedin.jobs import extract_job_id

    if source.startswith(("http://", "https://")):
        job_id = extract_job_id(source)
        if job_id:
            return "linkedin", job_id
        return "web", hashlib.md5(source.encode()).hexdigest()[:12]
    return "file", hashlib.md5(source.encode()).hexdigest()[:12]


_NO_THINK = [{"role": "system", "content": "/no_think"}]


def extract_metadata(tile0: pathlib.Path, vision_model: str, client) -> dict:
    """Call Ollama vision on the first tile to extract structured job metadata as JSON."""
    content = [
        {"type": "image_url", "image_url": {"url": f"data:{_mime(tile0)};base64,{_encode_tile(tile0)}"}},
        {"type": "text", "text": METADATA_PROMPT},
    ]
    resp = client.chat.completions.create(
        model=vision_model,
        messages=_NO_THINK + [{"role": "user", "content": content}],
        max_tokens=2048,
        temperature=0.0,
    )
    raw = (resp.choices[0].message.content or "{}").strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def extract_body_text(tiles: list[pathlib.Path], vision_model: str, client) -> str:
    """Call Ollama vision on all tiles to extract the full JD body text."""
    content = [
        {"type": "image_url", "image_url": {"url": f"data:{_mime(t)};base64,{_encode_tile(t)}"}}
        for t in tiles
    ]
    content.append({"type": "text", "text": BODY_PROMPT})
    resp = client.chat.completions.create(
        model=vision_model,
        messages=_NO_THINK + [{"role": "user", "content": content}],
        max_tokens=8192,
        temperature=0.0,
    )
    return (resp.choices[0].message.content or "").strip()


def capture_screenshot(
    source: str,
    out_dir: pathlib.Path,
    *,
    vision_model: str = VISION_MODEL_DEFAULT,
    keep_tiles: bool = False,
) -> pathlib.Path:
    """Full pipeline: render → extract metadata + body → write JD files.

    Returns the Path to the written vault/jds/<slug>.txt file.
    """
    from .domains.linkedin.jobs import Job, clean_jd_text, write_jd

    client = _ollama_client()
    source_label, job_id = _derive_source_and_job_id(source)

    tmp_dir = pathlib.Path(tempfile.mkdtemp(prefix="cv-tailor-tiles-"))
    try:
        print(f"Rendering {source!r} ...")
        _, tiles = render_to_tiles(source, tmp_dir)
        print(f"  {len(tiles)} tile(s) rendered")

        print(f"Extracting metadata from tile 0 ({vision_model}) ...")
        meta = extract_metadata(tiles[0], vision_model, client)
        print(
            f"  title={meta.get('title')!r}  "
            f"company={meta.get('company')!r}  "
            f"location={meta.get('location')!r}"
        )

        if source_label != "linkedin" and meta.get("job_id"):
            job_id = str(meta["job_id"])

        print(f"Extracting body text ({len(tiles)} tile(s), {vision_model}) ...")
        body = extract_body_text(tiles, vision_model, client)
        print(f"  {len(body)} chars extracted")

        job = Job(
            job_id=job_id,
            title=meta.get("title") or "role",
            company=meta.get("company") or "company",
            location=meta.get("location") or "",
            url=source if source.startswith(("http://", "https://")) else "",
            applicants=meta.get("applicants"),
        )
        captured_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        path = write_jd(job, clean_jd_text(body), out_dir, captured_at, source=source_label)
    finally:
        if keep_tiles:
            print(f"Tiles kept at: {tmp_dir}")
        else:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return path

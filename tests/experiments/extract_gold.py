#!/usr/bin/env python3
"""Snapshot gold references for the cv-tailor benchmark from the LaTeX `resume` repo.

The hand-written, human-quality applications live in the sibling `radheem/portfolio`
repo (`/home/radr/pers/resume/applications/<slug>/`) as bilingual LaTeX. This script
extracts the **English** half of each `cv.tex` / `cover-letter.tex` and the raw job
posting, converts them to the same Markdown shape the cv-tailor engine emits (CV body
starting at `## Experience`; cover-letter = body paragraphs only, no salutation /
sign-off), and writes a self-contained case under `cases/<slug>/`.

Run once to (re)populate the benchmark; the outputs are committed so the cases are
self-contained and no longer depend on the resume repo being present.

    python tests/experiments/extract_gold.py            # default ../resume
    python tests/experiments/extract_gold.py --resume /path/to/resume

This is a provenance/repro tool, not part of the test run.
"""

from __future__ import annotations

import argparse
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_RESUME = HERE.parent.parent.parent / "resume"

# slug -> (split, company, role, recipient).  slug matches the resume app dir.
CASES: dict[str, tuple[str, str, str, str]] = {
    # --- training (iterate guides / prompts / ranking on these) ---
    "aroundhome-senior-software-engineer": (
        "train", "Aroundhome", "Senior Software Engineer", ""),
    "redcare-pharmacy-data-engineer": (
        "train", "Redcare Pharmacy", "Data Engineer (m/f/d)", ""),
    "intershop-devops-engineer-monitoring": (
        "train", "Intershop Communications", "(Senior) DevOps Engineer - Monitoring (m/w/d)", ""),
    "t-systems-backend-engineer-container": (
        "train", "T-Systems International GmbH", "Backend Engineer T Cloud Public – Container (m/f/d)", ""),
    # --- test (held out; final evaluation only) ---
    "alignerr-software-engineer-ai-training": (
        "test", "Alignerr", "Software Engineer (AI Training)", ""),
    "teambank-model-monitoring-risk-controlling": (
        "test", "TeamBank AG (easyCredit)",
        "Mathematiker, Physiker, Informatiker (d/m/w) — Modellüberwachung im Risikocontrolling", ""),
}

# --------------------------------------------------------------------------- #
# LaTeX -> text helpers (targeted at resume.cls / coverletter.cls macros)      #
# --------------------------------------------------------------------------- #

# Order matters: multi-char accent escapes before generic backslash stripping.
_ACCENTS = [
    (r'\"a', "ä"), (r'\"o', "ö"), (r'\"u', "ü"),
    (r'\"A', "Ä"), (r'\"O', "Ö"), (r'\"U', "Ü"),
    (r"\ss", "ß"), (r"\3", "ß"),
    (r"\'e", "é"), (r"\`e", "è"), (r"\'a", "á"),
]


def _strip_comments(s: str) -> str:
    """Drop LaTeX line comments (% ... to EOL), but not escaped \\%."""
    return re.sub(r"(?<!\\)%.*", "", s)


def _english_half(tex: str) -> str:
    """Everything between \\begin{document} and the first \\clearpage (the EN block)."""
    body = tex.split(r"\begin{document}", 1)[-1]
    body = re.split(r"\\clearpage", body, 1)[0]
    return _strip_comments(body)


def _deaccent(s: str) -> str:
    for tex, uni in _ACCENTS:
        s = s.replace(tex, uni)
    s = s.replace("\\&", "&").replace("\\%", "%").replace("\\#", "#")
    s = s.replace("\\_", "_").replace("\\$", "$")
    s = s.replace("\\,", "").replace("~", " ").replace("\\ ", " ")
    return s


def _inline(s: str) -> str:
    """Convert inline LaTeX markup in a fragment to Markdown/plain text."""
    s = _deaccent(s)
    s = s.replace("\n", " ")
    s = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", s)   # \href{url}{text} -> text
    s = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"*\1*", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", r"`\1`", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", s)
    s = s.replace(r"\textbar", "|")
    s = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", s)        # any remaining \cmd{arg}
    s = re.sub(r"\\[a-zA-Z]+", "", s)                       # bare \cmd
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"[ \t]+", " ", s).strip()


def _grp(s: str, start: int) -> tuple[str, int]:
    """Read a single {...}-balanced group beginning at s[start] == '{'."""
    assert s[start] == "{"
    depth, i = 0, start
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1 : i], i + 1
        i += 1
    return s[start + 1 :], len(s)


def _macro_args(s: str, after: int, n: int) -> tuple[list[str], int]:
    """Read n consecutive brace groups starting at/after index `after`."""
    args, i = [], after
    for _ in range(n):
        while i < len(s) and s[i] != "{":
            i += 1
        if i >= len(s):
            break
        g, i = _grp(s, i)
        args.append(g)
    return args, i


def cv_to_markdown(tex: str) -> str:
    """Convert the English half of a resume cv.tex to engine-shape Markdown."""
    s = _english_half(tex)
    lines: list[str] = []
    i = 0
    pending_entry: str | None = None  # org from \entry awaiting \entryrole
    pending_loc: str = ""
    while i < len(s):
        m = re.compile(r"\\(section|entry|entryrole|project|item|bulletsend)\b").search(s, i)
        if not m:
            break
        cmd = m.group(1)
        j = m.end()
        if cmd == "section":
            args, i = _macro_args(s, j, 1)
            lines.append(f"\n## {_inline(args[0])}\n")
        elif cmd == "entry":
            args, i = _macro_args(s, j, 2)
            pending_entry, pending_loc = _inline(args[0]), _inline(args[1])
        elif cmd == "entryrole":
            args, i = _macro_args(s, j, 2)
            role, dates = _inline(args[0]), _inline(args[1])
            org = pending_entry or ""
            head = f"\n### {org} — {role}" if role else f"\n### {org}"
            meta = " · ".join(x for x in (pending_loc, dates) if x)
            lines.append(head)
            if meta:
                lines.append(f"*{meta}*\n")
            pending_entry = None
        elif cmd == "item":
            # bullet runs to the next \item / \bulletsend / \project / \entry /
            # \section / \begin / \end (so a trailing \end{itemize} isn't slurped)
            nxt = re.compile(
                r"\\(item|bulletsend|project|entry|section|begin|end)\b").search(s, j)
            end = nxt.start() if nxt else len(s)
            text = _inline(s[j:end])
            if text:
                lines.append(f"- {text}")
            i = end
        elif cmd == "project":
            args, i = _macro_args(s, j, 3)
            name, url, desc = _inline(args[0]), args[1].strip(), _inline(args[2])
            lines.append(f"- **{name}** — {desc}")
        elif cmd == "bulletsend":
            i = j
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def cover_to_markdown(tex: str) -> str:
    """Extract the English cover-letter body (paragraphs between \\opening and \\closing)."""
    s = _english_half(tex)
    op = re.search(r"\\opening\{", s)
    cl = re.search(r"\\closing\b", s)
    body = s[op.end() if op else 0 : cl.start() if cl else len(s)]
    # drop the \opening{...} salutation group's closing brace remnants
    if op:
        # we started right after "\opening{"; consume to its matching close
        depth = 1
        k = 0
        while k < len(body) and depth:
            if body[k] == "{":
                depth += 1
            elif body[k] == "}":
                depth -= 1
            k += 1
        body = body[k:]
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    out = []
    for p in paras:
        # skip stray macro-only lines (e.g. comments)
        text = _inline(re.sub(r"%.*", "", p))
        if text:
            out.append(text)
    return "\n\n".join(out).strip() + "\n"


def _strip_front_matter(md: str) -> str:
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip("\n")
    return md


def _yaml_q(v: str) -> str:
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", default=str(DEFAULT_RESUME),
                    help="path to the resume repo (default ../../resume)")
    args = ap.parse_args()
    resume = pathlib.Path(args.resume).resolve()
    apps = resume / "applications"
    if not apps.is_dir():
        raise SystemExit(f"resume applications dir not found: {apps}")

    split: dict[str, list[str]] = {"train": [], "test": []}
    for slug, (which, company, role, recipient) in CASES.items():
        src = apps / slug
        cv_tex = (src / "cv.tex").read_text(encoding="utf-8")
        cl_tex = (src / "cover-letter.tex").read_text(encoding="utf-8")
        jd = _strip_front_matter((src / "job-description.md").read_text(encoding="utf-8"))

        case = HERE / "cases" / slug
        (case / "gold").mkdir(parents=True, exist_ok=True)
        (case / "job-description.txt").write_text(jd.strip() + "\n", encoding="utf-8")
        (case / "gold" / "cv.md").write_text(cv_to_markdown(cv_tex), encoding="utf-8")
        (case / "gold" / "cover-letter.md").write_text(cover_to_markdown(cl_tex), encoding="utf-8")
        (case / "meta.yml").write_text(
            f"slug: {_yaml_q(slug)}\n"
            f"split: {which}\n"
            f"company: {_yaml_q(company)}\n"
            f"role: {_yaml_q(role)}\n"
            f"recipient: {_yaml_q(recipient)}\n"
            f"source: {_yaml_q('resume/applications/' + slug)}\n",
            encoding="utf-8",
        )
        split[which].append(slug)
        print(f"  {which:5}  {slug}")

    (HERE / "split.yml").write_text(
        "# Train/test split for the cv-tailor benchmark (4 train, 2 test).\n"
        "# Iterate data/guides, prompts, and ranking on `train`; evaluate on `test`.\n"
        "train:\n" + "".join(f"  - {s}\n" for s in split["train"]) +
        "test:\n" + "".join(f"  - {s}\n" for s in split["test"]),
        encoding="utf-8",
    )
    print(f"\nWrote {len(CASES)} cases "
          f"({len(split['train'])} train, {len(split['test'])} test) under {HERE/'cases'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

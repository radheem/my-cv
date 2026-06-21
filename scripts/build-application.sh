#!/usr/bin/env bash
# Build cv.pdf and cover-letter.pdf for a job-application directory.
#
#   scripts/build-application.sh applications/<company>-<role-slug>
#   scripts/build-application.sh applications/<dir> --docker   # no local TeX needed
#
# Shared styles live in latex/ (resume.cls, coverletter.cls); they are resolved
# via TEXINPUTS so the per-job .tex files in applications/** stay content-only.
set -euo pipefail

DIR="${1:-}"
MODE="${2:-auto}"   # auto | --docker | --local
if [[ -z "$DIR" ]]; then
  echo "usage: $0 applications/<company>-<role-slug> [--docker|--local]" >&2
  exit 2
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$(cd "$DIR" && pwd)"   # absolute; fails loudly if missing
LATEX_DIR="$REPO/latex"

# Which .tex files to build (skip whichever is absent).
TARGETS=()
for f in cv cover-letter; do
  [[ -f "$DIR/$f.tex" ]] && TARGETS+=("$f.tex")
done
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "no cv.tex or cover-letter.tex found in $DIR" >&2
  exit 1
fi

latexmk_local() {
  TEXINPUTS="$LATEX_DIR:${TEXINPUTS:-}" \
    latexmk -pdf -interaction=nonstopmode -halt-on-error -cd "$DIR/$1"
}

latexmk_docker() {
  # Mount the repo so both the app dir and latex/ (the class files) are visible.
  # Run as the host user so build artefacts stay host-owned (HOME=/tmp for latexmk).
  docker run --rm -v "$REPO":/repo -w /repo \
    -u "$(id -u):$(id -g)" -e HOME=/tmp \
    -e TEXINPUTS="/repo/latex:" texlive/texlive:latest \
    latexmk -pdf -interaction=nonstopmode -halt-on-error \
      -cd "/repo/${DIR#"$REPO"/}/$1"
}

use_docker=false
case "$MODE" in
  --docker) use_docker=true ;;
  --local)  use_docker=false ;;
  auto)     command -v latexmk >/dev/null 2>&1 || use_docker=true ;;
esac

for t in "${TARGETS[@]}"; do
  echo ">> building $t  ($([ "$use_docker" = true ] && echo docker || echo local))"
  if [[ "$use_docker" = true ]]; then latexmk_docker "$t"; else latexmk_local "$t"; fi
done

echo "done -> $DIR/{${TARGETS[*]/.tex/.pdf}}"

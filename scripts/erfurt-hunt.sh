#!/usr/bin/env bash
# scripts/erfurt-hunt.sh — capture Erfurt backend+data JDs, generate top-N applications
#
# Usage:
#   ./scripts/erfurt-hunt.sh [--top N] [--dry-run]
#
# Steps:
#   1. Snapshot existing vault/jds/ slugs
#   2. Run cv-tailor ingest for backend engineer + data engineer (Erfurt geoId, 50km, limit 15)
#   3. Diff → new slugs from this run only
#   4. Score those new JDs, select top N (default 10)
#   5. Generate tailored CV + cover letter for each (skip if applications/<slug>/ exists)
#   6. Render bilingual PDFs (LaTeX)
#   7. Upload PDFs to Google Drive
#   8. Commit + push

set -euo pipefail
cd "$(dirname "$0")/.."

# ── config ───────────────────────────────────────────────────────────────────
TOP=${TOP:-10}
DRY_RUN=false
GEO_ID="102387116"   # Erfurt region (geoId from LinkedIn)
DISTANCE=50          # km radius — covers Jena, Ilmenau, Arnstadt, Gotha
LIMIT=15             # per search; 2 searches → up to 30 candidates, pick top N
DAYS=14              # look back 2 weeks to surface enough roles

while [[ $# -gt 0 ]]; do
  case "$1" in
    --top)    TOP="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -f .env ]]; then set -o allexport; source .env; set +o allexport; fi
if ! command -v cv-tailor &>/dev/null; then
  [[ -f .venv/bin/activate ]] && source .venv/bin/activate \
    || { echo "ERROR: cv-tailor not found. Run: pip install -e '.[generate,fetch]'" >&2; exit 1; }
fi

PYTHON=${PYTHON:-python3}
RANKED_JSON=vault/jds/.erfurt-ranked.json
XVFB="xvfb-run -a -s '-screen 0 1440x900x24'"

echo "════════════════════════════════════════════════════════"
echo " Erfurt Hunt Pipeline — $(date '+%Y-%m-%d')"
echo " geoId=${GEO_ID}  radius=${DISTANCE}km  limit=${LIMIT}/search  days=${DAYS}"
echo " Top N : ${TOP}   Dry run : ${DRY_RUN}"
echo "════════════════════════════════════════════════════════"

# ── step 1: snapshot existing vault/jds slugs ────────────────────────────────
echo ""
echo "── Step 1: snapshot existing JDs ───────────────────────"
mapfile -t BEFORE < <(ls vault/jds/*.txt 2>/dev/null | xargs -I{} basename {} .txt | sort)
echo "  ${#BEFORE[@]} JDs in vault/jds before ingest"

# ── step 2: ingest Erfurt backend + data ─────────────────────────────────────
echo ""
echo "── Step 2: LinkedIn ingest (Erfurt, backend + data) ────"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "  [dry-run] would run: cv-tailor ingest backend engineer + data engineer"
else
  $XVFB cv-tailor ingest \
    --keywords "backend engineer" \
    --geo-id "$GEO_ID" \
    --distance "$DISTANCE" \
    --days "$DAYS" \
    --limit "$LIMIT" \
    || echo "  WARNING: backend ingest returned non-zero — continuing"

  $XVFB cv-tailor ingest \
    --keywords '"data engineer" OR "software engineer"' \
    --geo-id "$GEO_ID" \
    --distance "$DISTANCE" \
    --days "$DAYS" \
    --limit "$LIMIT" \
    || echo "  WARNING: data ingest returned non-zero — continuing"
fi

# ── step 3: diff → new slugs ─────────────────────────────────────────────────
echo ""
echo "── Step 3: diff new captures ────────────────────────────"
mapfile -t AFTER < <(ls vault/jds/*.txt 2>/dev/null | xargs -I{} basename {} .txt | sort)

NEW_SLUGS=()
declare -A BEFORE_SET
for s in "${BEFORE[@]}"; do BEFORE_SET[$s]=1; done
for s in "${AFTER[@]}"; do
  if [[ -z "${BEFORE_SET[$s]+x}" ]]; then
    NEW_SLUGS+=("$s")
  fi
done

echo "  ${#NEW_SLUGS[@]} new JD(s) captured:"
for s in "${NEW_SLUGS[@]}"; do echo "    $s"; done

if [[ ${#NEW_SLUGS[@]} -eq 0 ]]; then
  echo "  Nothing new — all Erfurt jobs already seen (.seen.json). Done."
  exit 0
fi

# ── step 4: score new JDs and select top N ───────────────────────────────────
echo ""
echo "── Step 4: score + rank new JDs ────────────────────────"
ONLY_ARGS=()
for s in "${NEW_SLUGS[@]}"; do ONLY_ARGS+=("$s"); done

$PYTHON scripts/score-jds.py \
  --top "$TOP" \
  --only-slugs "${ONLY_ARGS[@]}" \
  --skip-existing-apps \
  --out "$RANKED_JSON"

mapfile -t TOP_SLUGS < <($PYTHON -c "
import json, sys
slugs = json.load(open(sys.argv[1]))
print('\n'.join(slugs))
" "$RANKED_JSON")

echo ""
echo "  Top ${#TOP_SLUGS[@]} selected:"
for s in "${TOP_SLUGS[@]}"; do echo "    $s"; done

if [[ ${#TOP_SLUGS[@]} -eq 0 ]]; then
  echo "  No JDs to generate. Done."
  exit 0
fi

# ── step 5: generate applications ────────────────────────────────────────────
echo ""
echo "── Step 5: generate applications ───────────────────────"
for slug in "${TOP_SLUGS[@]}"; do
  jd_file="vault/jds/${slug}.txt"
  app_dir="applications/${slug}"

  if [[ ! -f "$jd_file" ]]; then
    echo "  SKIP $slug — JD file not found"; continue
  fi
  if [[ -d "$app_dir" ]]; then
    echo "  SKIP $slug — application already exists"; continue
  fi

  echo ""
  echo "  Generating: $slug"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] would run: cv-tailor new '$jd_file' --slug '$slug'"
    continue
  fi

  cv-tailor new "$jd_file" --slug "$slug" \
    || { echo "  ERROR generating $slug — skipping"; continue; }
done

# ── step 6: render PDFs ───────────────────────────────────────────────────────
echo ""
echo "── Step 6: render PDFs ──────────────────────────────────"
for slug in "${TOP_SLUGS[@]}"; do
  app_dir="applications/${slug}"
  [[ -d "$app_dir" ]] || { echo "  SKIP $slug — no app dir"; continue; }

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] would run: make pdf SLUG=$slug"; continue
  fi
  make pdf SLUG="$slug" || echo "  WARNING: PDF compile failed for $slug"
done

# ── step 7: upload to Google Drive ───────────────────────────────────────────
echo ""
echo "── Step 7: upload PDFs to Google Drive ─────────────────"
for slug in "${TOP_SLUGS[@]}"; do
  app_dir="applications/${slug}"
  index_md="${app_dir}/index.md"
  [[ -d "$app_dir" ]] || { echo "  SKIP $slug — no app dir"; continue; }

  if grep -q "drive_url:.*https" "$index_md" 2>/dev/null; then
    echo "  SKIP $slug — already uploaded"; continue
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] would run: make upload SLUG=$slug"; continue
  fi
  make upload SLUG="$slug" || echo "  WARNING: upload failed for $slug"
done

# ── step 8: commit + push ────────────────────────────────────────────────────
echo ""
echo "── Step 8: commit + push ────────────────────────────────"
make track

if [[ "$DRY_RUN" == "true" ]]; then
  echo "  [dry-run] would commit and push"; echo ""; echo "Pipeline complete (dry run)."; exit 0
fi

git add applications/
if git diff --cached --quiet; then
  echo "  Nothing new to commit."
else
  DATE=$(date '+%Y-%m-%d')
  COUNT=${#TOP_SLUGS[@]}
  git commit -m "erfurt hunt ${DATE}: ${COUNT} applications (backend + data engineer)"
fi

git push
echo ""
echo "Pipeline complete — ${#TOP_SLUGS[@]} application(s) generated."

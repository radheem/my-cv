#!/usr/bin/env bash
# scripts/job-hunt.sh — full job-hunt pipeline
#
# Usage:
#   ./scripts/job-hunt.sh [--top N] [--dry-run]
#
# Steps:
#   1. Search LinkedIn in each configured city (data/search-terms.yml) and
#      capture JDs (posted this week, < 100 applicants)
#   2. Score all captured JDs and select the top N (default 10)
#   3. Generate tailored CV + cover letter for each top JD
#   4. Render bilingual PDFs (LaTeX)
#   5. Upload PDFs to Google Drive
#   6. Commit + push everything
#
# Prerequisites:
#   - .venv activated (or cv-tailor on PATH)
#   - .env loaded (ANTHROPIC_API_KEY / Ollama, APPS_SCRIPT_URL, GDRIVE_FOLDER_ID)
#   - LinkedIn session established in vault/profile/ (run make docker-login once)
#   - xvfb-run available (sudo apt install xvfb)
#
# The script is idempotent: already-captured JDs are skipped (vault/jds/.seen.json),
# already-generated applications are skipped (applications/<slug>/ exists).

set -euo pipefail
cd "$(dirname "$0")/.."

# ── config ───────────────────────────────────────────────────────────────────
TOP=${TOP:-10}           # top N JDs to generate applications for
DRY_RUN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --top)    TOP="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# Load .env (non-destructive: skip if already set)
if [[ -f .env ]]; then
  set -o allexport
  # shellcheck disable=SC1091
  source .env
  set +o allexport
fi

# Activate venv if cv-tailor not already on PATH
if ! command -v cv-tailor &>/dev/null; then
  if [[ -f .venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  else
    echo "ERROR: cv-tailor not found and no .venv. Run: pip install -e '.[generate,fetch]'" >&2
    exit 1
  fi
fi

PYTHON=${PYTHON:-python3}
KEYWORDS_FILE=data/search-terms.yml
RANKED_JSON=vault/jds/.ranked.json
XVFB="xvfb-run -a -s '-screen 0 1440x900x24'"

# Read config from search-terms.yml via Python
read_cfg() {
  $PYTHON - "$KEYWORDS_FILE" "$1" <<'PYEOF'
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1]))
key = sys.argv[2]
# dot-path support: "filters.per_city"
parts = key.split(".")
val = cfg
for p in parts:
    val = val[p]
if isinstance(val, list):
    print("\n".join(str(v) for v in val))
else:
    print(val)
PYEOF
}

DAYS=$(read_cfg "filters.days_back")
MAX_APPLICANTS=$(read_cfg "filters.max_applicants")
PER_CITY=$(read_cfg "filters.per_city")
mapfile -t CITIES < <(read_cfg "locations")
mapfile -t KEYWORDS < <(read_cfg "primary")

echo "════════════════════════════════════════════════════════"
echo " Job Hunt Pipeline — $(date '+%Y-%m-%d')"
echo " Cities    : ${CITIES[*]}"
echo " Keywords  : ${KEYWORDS[*]}"
echo " Per city  : $PER_CITY  |  Days back: $DAYS  |  Max applicants: $MAX_APPLICANTS"
echo " Top N     : $TOP"
echo " Dry run   : $DRY_RUN"
echo "════════════════════════════════════════════════════════"

# ── step 1: ingest ────────────────────────────────────────────────────────────
echo ""
echo "── Step 1: LinkedIn ingest ──────────────────────────────"

# Cycle through keywords across cities (first keyword per city to stay focused)
# Edit KEYWORDS array in data/search-terms.yml to change what is searched.
for i in "${!CITIES[@]}"; do
  city="${CITIES[$i]}"
  # Rotate through primary keywords: city 0 → kw[0], city 1 → kw[1], etc.
  kw_idx=$(( i % ${#KEYWORDS[@]} ))
  kw="${KEYWORDS[$kw_idx]}"

  echo ""
  echo "  [$((i+1))/${#CITIES[@]}] '$kw' in '$city'"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] would run: cv-tailor ingest --keywords '$kw' --location '$city' ..."
    continue
  fi

  $XVFB cv-tailor ingest \
    --keywords "$kw" \
    --location "$city" \
    --limit "$PER_CITY" \
    --days "$DAYS" \
    --max-applicants "$MAX_APPLICANTS" \
    --out vault/jds \
    || echo "  WARNING: ingest for '$city' returned non-zero — continuing"
done

# ── step 2: score and rank ────────────────────────────────────────────────────
echo ""
echo "── Step 2: score and rank captured JDs ─────────────────"
$PYTHON scripts/score-jds.py --top "$TOP" --out "$RANKED_JSON"

mapfile -t TOP_SLUGS < <($PYTHON -c "import json,sys; [print(s) for s in json.load(open(sys.argv[1]))]" "$RANKED_JSON")
echo ""
echo "  Top $TOP slugs selected:"
for s in "${TOP_SLUGS[@]}"; do
  echo "    $s"
done

# ── step 3: generate applications ────────────────────────────────────────────
echo ""
echo "── Step 3: generate applications ───────────────────────"
for slug in "${TOP_SLUGS[@]}"; do
  jd_file="vault/jds/${slug}.txt"
  app_dir="applications/${slug}"

  if [[ ! -f "$jd_file" ]]; then
    echo "  SKIP $slug — JD file not found: $jd_file"
    continue
  fi

  if [[ -d "$app_dir" ]]; then
    echo "  SKIP $slug — application already exists"
    continue
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

# ── step 4: render PDFs ───────────────────────────────────────────────────────
echo ""
echo "── Step 4: render PDFs ──────────────────────────────────"
for slug in "${TOP_SLUGS[@]}"; do
  app_dir="applications/${slug}"
  cv_tex="$app_dir/cv.tex"

  if [[ ! -d "$app_dir" ]]; then
    echo "  SKIP $slug — application dir not found"
    continue
  fi
  if [[ -f "$cv_tex" ]]; then
    echo "  $slug — .tex already rendered, recompiling PDFs"
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] would run: make pdf SLUG=$slug"
    continue
  fi

  make pdf SLUG="$slug" \
    || echo "  WARNING: PDF compile failed for $slug"
done

# ── step 5: upload to Google Drive ───────────────────────────────────────────
echo ""
echo "── Step 5: upload PDFs to Google Drive ─────────────────"
for slug in "${TOP_SLUGS[@]}"; do
  app_dir="applications/${slug}"
  index_md="$app_dir/index.md"

  if [[ ! -d "$app_dir" ]]; then
    echo "  SKIP $slug — application dir not found"
    continue
  fi

  # Check if already uploaded (drive_url present in index.md)
  if grep -q "drive_url:.*https" "$index_md" 2>/dev/null; then
    echo "  SKIP $slug — already uploaded (drive_url set)"
    continue
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] would run: make upload SLUG=$slug"
    continue
  fi

  make upload SLUG="$slug" \
    || echo "  WARNING: upload failed for $slug"
done

# ── step 6: commit and push ───────────────────────────────────────────────────
echo ""
echo "── Step 6: commit and push ──────────────────────────────"

# Refresh the applications tracker table
make track

if [[ "$DRY_RUN" == "true" ]]; then
  echo "  [dry-run] would commit and push"
  echo ""
  echo "Pipeline complete (dry run)."
  exit 0
fi

# Stage everything except gitignored files (PDFs etc.)
git add applications/ data/search-terms.yml

# Only commit if there are staged changes
if git diff --cached --quiet; then
  echo "  Nothing new to commit."
else
  DATE=$(date '+%Y-%m-%d')
  CITIES_STR=$(IFS=', '; echo "${CITIES[*]}")
  git commit -m "job hunt ${DATE}: ${TOP} applications — ${CITIES_STR}"
fi

git push
echo ""
echo "Pipeline complete."

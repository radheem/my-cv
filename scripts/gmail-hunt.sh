#!/usr/bin/env bash
# scripts/gmail-hunt.sh — Gmail job hunt pipeline
#
# Usage:
#   ./scripts/gmail-hunt.sh [--filter "query"] [--limit N] [--order top|fifo] [--dry-run]
#

set -euo pipefail
cd "$(dirname "$0")/.."

FILTER="subject:\"linkedin job alert\" is:unread"
LIMIT=10
ORDER="top"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --filter) FILTER="$2"; shift 2 ;;
    --limit)  LIMIT="$2"; shift 2 ;;
    --order)  ORDER="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ "$ORDER" != "top" && "$ORDER" != "fifo" ]]; then
    echo "ERROR: --order must be 'top' or 'fifo'" >&2
    exit 1
fi

if [[ -f .env ]]; then
  set -o allexport
  source .env
  set +o allexport
fi

if ! command -v cv-tailor &>/dev/null; then
  if [[ -f .venv/bin/activate ]]; then
    source .venv/bin/activate
  else
    echo "ERROR: cv-tailor not found and no .venv. Run: pip install -e '.[generate,fetch]'" >&2
    exit 1
  fi
fi

PYTHON=${PYTHON:-python3}
xvfb_run() { xvfb-run -a -s "-screen 0 1440x900x24" "$@"; }

echo "════════════════════════════════════════════════════════"
echo " Gmail Job Hunt Pipeline — $(date '+%Y-%m-%d')"
echo " Filter    : $FILTER"
echo " Limit     : $LIMIT"
echo " Order     : $ORDER"
echo " Dry run   : $DRY_RUN"
echo "════════════════════════════════════════════════════════"

echo ""
echo "── Step 1: Search Gmail and extract URLs ───────────────"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "  [dry-run] would search gmail with query: $FILTER"
  URLS=("https://www.linkedin.com/jobs/view/1234567")
else
  # Use the newly-added --include-bodies flag to make sure we parse the email bodies
  mapfile -t URLS < <(cv-tailor gmail search --query "$FILTER" --json --include-bodies | $PYTHON scripts/extract-email-urls.py)
fi

echo "  Found ${#URLS[@]} unseen job URLs."

if [[ ${#URLS[@]} -eq 0 ]]; then
  echo "  No new jobs to process. Exiting."
  exit 0
fi

echo ""
echo "── Step 2: Capture Job Descriptions ─────────────────────"

NEW_SLUGS=()
for url in "${URLS[@]}"; do
    echo "  Capturing: $url"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "    [dry-run] xvfb_run cv-tailor capture \"$url\""
        NEW_SLUGS+=("dry-run-slug-${RANDOM}")
    else
        # capture command outputs: captured vault/jds/<slug>.txt
        # we parse it to extract the slug
        out=$(xvfb_run cv-tailor capture "$url" | grep -oP '(?<=captured vault/jds/).*(?=\.txt)') || {
             echo "    WARNING: capture failed for $url — continuing"
             continue
        }
        if [[ -n "$out" ]]; then
             NEW_SLUGS+=("$out")
             echo "    -> captured $out"
        fi
    fi
done

if [[ ${#NEW_SLUGS[@]} -eq 0 ]]; then
  echo "  No jobs were successfully captured. Exiting."
  exit 0
fi

echo ""
echo "── Step 3: Select Top/Fifo Jobs ────────────────────────"

SELECTED_SLUGS=()

if [[ "$ORDER" == "fifo" ]]; then
    # Slice the first LIMIT slugs
    for ((i=0; i<LIMIT && i<${#NEW_SLUGS[@]}; i++)); do
        SELECTED_SLUGS+=("${NEW_SLUGS[i]}")
    done
else
    # ORDER == top
    # Score the newly captured JDs, skipping any that already have applications
    RANKED_JSON=vault/jds/.ranked_new.json
    if [[ "$DRY_RUN" == "true" ]]; then
         echo "  [dry-run] scoring captured JDs"
         SELECTED_SLUGS=("${NEW_SLUGS[@]:0:$LIMIT}")
    else
         echo "  Scoring captured JDs..."
         $PYTHON scripts/score-jds.py --only-slugs "${NEW_SLUGS[@]}" --skip-existing-apps --top "$LIMIT" --out "$RANKED_JSON"
         
         # Read ranked json
         mapfile -t SELECTED_SLUGS < <($PYTHON -c "import json,sys; [print(s) for s in json.load(open(sys.argv[1]))]" "$RANKED_JSON")
    fi
fi

echo "  Selected ${#SELECTED_SLUGS[@]} jobs to process:"
for s in "${SELECTED_SLUGS[@]}"; do
  echo "    $s"
done

echo ""
echo "── Step 4: Generate Applications and Upload ─────────────"

for slug in "${SELECTED_SLUGS[@]}"; do
  jd_file="vault/jds/${slug}.txt"
  
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] cv-tailor new \"$jd_file\" --slug \"$slug\""
    echo "  [dry-run] cv-tailor pdf \"$slug\""
    echo "  [dry-run] cv-tailor upload \"$slug\""
  else
    echo "  >> Processing: $slug"
    cv-tailor new "$jd_file" --slug "$slug"
    
    echo "  >> Rendering PDF: $slug"
    cv-tailor pdf "$slug"
    
    echo "  >> Uploading to Drive: $slug"
    cv-tailor upload "$slug"
  fi
done

echo ""
echo "── Step 5: Sync Status ──────────────────────────────────"
if [[ "$DRY_RUN" == "true" ]]; then
  echo "  [dry-run] cv-tailor track"
  echo "  [dry-run] cv-tailor sync-sheets"
else
  cv-tailor track
  cv-tailor sync-sheets
fi

echo "════════════════════════════════════════════════════════"
echo " Pipeline complete!"

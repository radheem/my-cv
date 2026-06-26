# Gmail Job Hunt Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automate an end-to-end pipeline (`make gmail-hunt`) that fetches job alerts via Gmail, filters unseen jobs, ranks or queues them based on an `ORDER` parameter (`top` or `fifo`), limits generated applications via `LIMIT`, generates applications, and uploads PDFs to Google Drive.

**Architecture:** We will create a Python helper script (`scripts/extract-email-urls.py`) to parse JSON output from `cv-tailor gmail search`, extract numeric LinkedIn job IDs, and filter out seen jobs using `vault/jds/.seen.json`. We will orchestrate this with a bash script (`scripts/gmail-hunt.sh`) that iterates over the urls, captures JDs, scores them (filtering for new jobs only), generates tailored cv/cover letters, and uploads them to Google Drive. A Makefile target `gmail-hunt` will expose the parameters.

**Tech Stack:** Python 3 (json, re), Bash, Makefile.

---

### Task 1: Create Python Extractor Helper (`scripts/extract-email-urls.py`)

**Files:**
- Create: `scripts/extract-email-urls.py`
- Test: manual execution using a dummy json payload.

- [ ] **Step 1: Write the extractor script**
  Create `scripts/extract-email-urls.py` to read stdin, parse the `messages` body, extract LinkedIn job URLs, and filter against the seen ledger.

```python
#!/usr/bin/env python3
"""
Extract unseen LinkedIn job URLs from cv-tailor gmail search JSON output.
Usage: cv-tailor gmail search --query "..." --json | python3 scripts/extract-email-urls.py
"""
import sys
import json
import re
import pathlib
from engine.linkedin.jobs import load_seen

def main():
    payload = sys.stdin.read()
    if not payload.strip():
        return
        
    try:
        threads = json.loads(payload)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON from stdin", file=sys.stderr)
        sys.exit(1)

    seen_ledger = load_seen(pathlib.Path("vault/jds/.seen.json"))
    unseen_urls = []
    found_ids = set()

    for t in threads:
        for m in t.get("messages", []):
            body = m.get("body", "")
            # Match LinkedIn job URLs, e.g., https://www.linkedin.com/jobs/view/1234567/
            matches = re.finditer(r"linkedin\.com/jobs/view/(\d+)", body)
            for match in matches:
                job_id = match.group(1)
                if job_id not in seen_ledger and job_id not in found_ids:
                    found_ids.add(job_id)
                    unseen_urls.append(f"https://www.linkedin.com/jobs/view/{job_id}/")

    for url in unseen_urls:
        print(url)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Make the script executable**
  Run: `chmod +x scripts/extract-email-urls.py`
- [ ] **Step 3: Test manually**
  Run: `echo '[{"messages": [{"body": "Check this job: https://www.linkedin.com/jobs/view/999999/"}]}]' | python3 scripts/extract-email-urls.py`
  Expected Output: `https://www.linkedin.com/jobs/view/999999/`
- [ ] **Step 4: Commit**
  ```bash
  git add scripts/extract-email-urls.py
  git commit -m "feat(scripts): add helper to extract unseen linkedin urls from gmail search json"
  ```

---

### Task 2: Create Orchestration Bash Script (`scripts/gmail-hunt.sh`)

**Files:**
- Create: `scripts/gmail-hunt.sh`

- [ ] **Step 1: Write the bash script**
  Create `scripts/gmail-hunt.sh` that ties the pipeline together.

```bash
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
  URLS=()
else
  mapfile -t URLS < <(cv-tailor gmail search --query "$FILTER" --json | $PYTHON scripts/extract-email-urls.py)
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
    # Score the new JDs
    RANKED_JSON=vault/jds/.ranked_new.json
    if [[ "$DRY_RUN" == "true" ]]; then
         echo "  [dry-run] scoring captured JDs"
         SELECTED_SLUGS=("${NEW_SLUGS[@]:0:$LIMIT}")
    else
         echo "  Scoring captured JDs..."
         $PYTHON scripts/score-jds.py --top "$LIMIT" --out "$RANKED_JSON"
         
         # Read ranked json, filter to only slugs that were just captured (NEW_SLUGS)
         # We need to do this carefully since score-jds.py scores EVERYTHING in the directory.
         mapfile -t RANKED_ALL < <($PYTHON -c "import json,sys; [print(s) for s in json.load(open(sys.argv[1]))]" "$RANKED_JSON")
         
         count=0
         for s in "${RANKED_ALL[@]}"; do
             if [[ " ${NEW_SLUGS[*]} " =~ [[:space:]]${s}[[:space:]] ]]; then
                 SELECTED_SLUGS+=("$s")
                 ((count++))
                 if [[ $count -eq $LIMIT ]]; then break; fi
             fi
         done
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
  # Note: sync-sheets depends on tracking being done first
  cv-tailor sync-sheets
fi

echo "════════════════════════════════════════════════════════"
echo " Pipeline complete!"
```

- [ ] **Step 2: Make executable**
  Run: `chmod +x scripts/gmail-hunt.sh`
- [ ] **Step 3: Test dry run**
  Run: `./scripts/gmail-hunt.sh --limit 1 --dry-run`
- [ ] **Step 4: Commit**
  ```bash
  git add scripts/gmail-hunt.sh
  git commit -m "feat(scripts): add gmail-hunt pipeline to extract, capture, and generate apps from emails"
  ```

---

### Task 3: Update Makefile

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Add the `gmail-hunt` target**
  Open `Makefile` and add the new target under the `job-hunt` section:

```makefile
FILTER  ?= "linkedin job alert"
LIMIT   ?= 10
ORDER   ?= top

.PHONY: gmail-hunt
gmail-hunt: ## Search Gmail for alerts, capture, and generate applications: make gmail-hunt [FILTER="..."] [LIMIT=10] [ORDER=top|fifo]
	bash scripts/gmail-hunt.sh --filter $(FILTER) --limit $(LIMIT) --order $(ORDER)
```

- [ ] **Step 2: Verify help output**
  Run: `make help | grep gmail-hunt`
- [ ] **Step 3: Commit**
  ```bash
  git add Makefile
  git commit -m "feat(makefile): add gmail-hunt target to drive the new gmail job pipeline"
  ```
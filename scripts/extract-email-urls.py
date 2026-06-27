#!/usr/bin/env python3
"""
Extract unseen LinkedIn job URLs from cv-tailor gmail search JSON output.
Usage: cv-tailor gmail search --query "..." --json | python3 scripts/extract-email-urls.py
"""
import sys
import json
import re
import pathlib

# Fix for module import in bash pipes
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.linkedin.jobs import load_seen
from engine.workflows.gmail_ingest import extract_urls_from_text, parse_and_normalize_job_url

def main():
    payload = sys.stdin.read()
    if not payload.strip():
        return
        
    try:
        threads = json.loads(payload)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON from stdin", file=sys.stderr)
        sys.exit(1)

    if not isinstance(threads, list):
        print(f"Error: Expected JSON list, got {type(threads).__name__}", file=sys.stderr)
        sys.exit(1)

    seen_ledger = load_seen(pathlib.Path("vault/jds/.seen.json"))
    unseen_urls = []
    found_ids = set()

    for t in threads:
        if not isinstance(t, dict):
            continue
        for m in t.get("messages", []):
            if not isinstance(m, dict):
                continue
            body = m.get("body") or ""
            # Match any vendor-agnostic job URLs
            for url in extract_urls_from_text(body):
                parsed = parse_and_normalize_job_url(url)
                job_id = parsed["job_id"]
                if job_id not in seen_ledger and job_id not in found_ids:
                    found_ids.add(job_id)
                    unseen_urls.append(url)

    for url in unseen_urls:
        print(url)

if __name__ == "__main__":
    main()

# Runbook — Search Jobs on Fraunhofer

This runbook covers how to search and ingest job descriptions from the public **Fraunhofer Career Portal** (`jobs.fraunhofer.de`). 

Because Fraunhofer's job portal is public, **no login session or VNC browser interaction is required**.

---

## 1. Batch Search via Configuration (`config/search.yml`)

You can define repeatable, structured job searches for Fraunhofer inside your `config/search.yml` configuration.

### Step 1: Add a search entry
Open `config/search.yml` and add an entry with `source: fraunhofer`:

```yaml
searches:
  - name: "Fraunhofer Data Science"
    source: "fraunhofer"
    keywords: "Data Science"
    limit: 5
  - name: "Fraunhofer Scientific Staff"
    source: "fraunhofer"
    keywords: "Scientific Staff"
    limit: 3
```

### Step 2: Run the hunt
Execute the batch search to fetch matching jobs and save them:
```bash
cv-tailor hunt
```

The system will start a headless browser, navigate the Fraunhofer career portal, extract job posting details, and write them to:
📁 `vault/jds/<slug>.txt` (Job description)
📁 `vault/jds/<slug>.json` (Title, company, URL, and job metadata)

---

## 2. Ingest Verification & Troubleshooting

Every job successfully ingested is recorded in the seen ledger `vault/jds/.seen.json` to prevent duplicates. Re-running `cv-tailor hunt` will automatically skip postings that have already been imported.

*   To inspect captured descriptions, list files under:
    ```bash
    ls vault/jds/ | grep fraunhofer
    ```
*   To force re-ingestion of an already seen job posting, delete its corresponding entry in `vault/jds/.seen.json` or clear the file entirely.

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
Execute the batch search to fetch matching jobs and save them inside the container:
```bash
make hunt
```

The system will start a headless browser, navigate the Fraunhofer career portal, extract job posting details, and write them directly into the database:
📁 DuckDB `jobs` Table cache
📁 `vault/jds/<slug>.txt` (Job description backup - single source of truth)
📁 `vault/jds/<slug>.json` (Title, company, URL, and job metadata backup - single source of truth)

---

## 2. Ingest Verification & Troubleshooting

Every job successfully ingested is recorded in the database. Re-running `make hunt` will automatically skip postings that have already been imported by querying the database.

*   To inspect captured descriptions, list files under:
    ```bash
    ls vault/jds/ | grep fraunhofer
    ```
*   To force re-ingestion of an already seen job posting, delete its corresponding backup files under `vault/jds/` (e.g., `rm vault/jds/slug.txt vault/jds/slug.json`).

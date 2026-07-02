# Runbook — Search Jobs on LinkedIn

This runbook covers how to search for job openings on LinkedIn using an authenticated Playwright session.

---

## 1. Credentials Setup (One-time)
Make sure your LinkedIn credentials are set up in your `.env` (which is gitignored):
```bash
LINKEDIN_USER=your_email@gmail.com
LINKEDIN_PASS=your_secure_password
```

---

## 2. Step 1: Session Warmup (Solving Security Checks)
The first time you log in from a fresh browser environment, LinkedIn will likely challenge the login (OTP/reCAPTCHA). 

Run the warmup target over VNC once to solve the CAPTCHA and warm up the browser profile saved in `vault/profile`:

```bash
make docker-login
```
Then connect to `127.0.0.1:5900` using a VNC viewer (such as TigerVNC or RealVNC), solve any challenges presented in the browser window, and let the login complete. The profile is now authenticated as a "recognized device."

---

## 3. Search and Ingest Job Descriptions

Once you have a warm browser session, you can run automated searches inside the container (zero host setup needed).

### Option A: Ad-Hoc CLI Search
To quickly search for a specific role and location directly from the CLI:

```bash
make ingest KEYWORDS="Platform Engineer" LOCATION="Remote" LIMIT=5
```

#### Available CLI Search Flags (overridable via `make` variables):
*   `KEYWORDS` (Required): Search keywords (boolean syntax works: `"Go" OR "Golang"`).
*   `LOCATION`: Geographic region text (e.g. `"Remote"`, `"Berlin"`).
*   `LIMIT`: Maximum number of jobs to fetch (default: `5`).
*   `DAYS`: Filter postings by age (default: `7` days back).
*   `EASY_APPLY`: Restrict searches to LinkedIn "Easy Apply" roles.
*   `MAX_APPLICANTS`: Automatically discard roles that have more than a specified number of applicants.

### Option B: Batch Config-Based Hunt
To run a sequence of multiple pre-configured searches defined in `config/search.yml`:

```bash
make hunt
```

---

## 4. Verification & Output Location

Job details are captured directly as files under `vault/jds/` and cached inside the local DuckDB database:
*   `vault/jds/<slug>.txt` — Cleaned text of the job description (single source of truth).
*   `vault/jds/<slug>.json` — Job title, company, URL, and metadata (single source of truth).
*   DuckDB `jobs` Table — Cached database table for querying.
*   Database queries are executed automatically to deduplicate subsequent searches (avoiding any duplicate JDs).

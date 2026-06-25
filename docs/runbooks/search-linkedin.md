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
VNC_PASSWORD=my_secure_password cv-tailor ingest --keywords warmup --limit 0
```
Then connect to `127.0.0.1:5900` using a VNC viewer (such as TigerVNC or RealVNC), solve any challenges presented in the browser window, and let the login complete. The profile is now authenticated as a "recognized device."

---

## 3. Search and Ingest Job Descriptions

Once you have a warm browser session, you can run automated searches.

### Option A: Ad-Hoc CLI Search
To quickly search for a specific role and location directly from the CLI:

```bash
cv-tailor ingest --keywords "Platform Engineer" --location "Remote" --limit 5
```

#### Available CLI Search Flags:
*   `--keywords` (Required): Search keywords (boolean syntax works: `"Go" OR "Golang"`).
*   `--location`: Geographic region text (e.g. `"Remote"`, `"Berlin"`).
*   `--limit`: Maximum number of jobs to fetch (default: `10`).
*   `--days`: Filter postings by age (default: `7` days back).
*   `--easy-apply`: Restrict searches to LinkedIn "Easy Apply" roles.
*   `--max-applicants`: Automatically discard roles that have more than a specified number of applicants.

### Option B: Batch Config-Based Hunt
To run a sequence of multiple pre-configured searches defined in `config/search.yml`:

```bash
cv-tailor hunt
```

---

## 4. Verification & Output Location

Job details are captured under `vault/jds/`:
*   `vault/jds/<slug>.txt` — Cleaned text of the job description.
*   `vault/jds/<slug>.json` — Job title, company, URL, and metadata.
*   `vault/jds/.seen.json` — Seen ledger used to automatically deduplicate subsequent searches.

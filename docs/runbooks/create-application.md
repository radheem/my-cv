# Runbook — Create Tailored Application

This runbook covers how to generate a tailored CV, cover letter, and tracking hub for a job description, whether it comes from a local text file, LinkedIn, or the Fraunhofer portal.

---

## 1. Option A: Create Application from a Text File

If you have a job description saved locally in a text or markdown file, you can trigger the tailor generation directly.

### Step 1: Save the Job Description
Paste the raw text of the job description into a local file:
```bash
cat << 'EOF' > my-job-description.txt
Acme Corp is hiring a Senior Backend Engineer.
Requirements:
- 5+ years Go development
- Experience with Kubernetes and microservices
- Fluency in English
EOF
```

### Step 2: Run the Tailoring Engine
Run the `new` command, specifying the path to your file. You can optionally supply a `SLUG` and `RECIPIENT` name:
```bash
make new SOURCE=my-job-description.txt SLUG=acme-corp-backend-engineer RECIPIENT="Jane Smith"
```

The engine will:
1. Parse requirements into a JobSpec.
2. Select the top-3 matching projects and order skills deterministically.
3. Call the LLM to write beautifully tailored CV and cover letter prose.
4. Output Markdown files and indexes under: `applications/acme-corp-backend-engineer/`.
5. Automatically register the newly generated application in your local DuckDB cache.

---

## 2. Option B: Create Application from LinkedIn

### Pathway 1: Direct Generation from URL (Dynamic Ingestion)
If you have a direct job URL, `cv-tailor` can dynamically fetch the job description inside the container using Playwright, parse it, and generate the tailored files in a single step:

```bash
make new SOURCE="https://www.linkedin.com/jobs/view/123456789/" RECIPIENT="Hiring Manager"
```

### Pathway 2: Generating from an Ingested File / Slug
If you have already run `make ingest` or `make hunt` and have a captured job in your database cache:
1. Find the slug of the job using:
   ```bash
   make score
   ```
2. Run the generator using that slug directly! Because `fetch_job_text` supports database lookup fallbacks, you do **not** need a local text file:
   ```bash
   make new SOURCE=acme-software-engineer-4412345 RECIPIENT="John Doe"
   ```

---

## 3. Option C: Create Application from Fraunhofer

### Pathway 1: Direct Generation from URL (Dynamic Ingestion)
You can generate a tailored application directly from a public Fraunhofer job posting URL. No login is needed:

```bash
make new SOURCE="https://jobs.fraunhofer.de/job/Ilmenau-Research-Associate-Secure-Development-98693/1234567/"
```

### Pathway 2: Generating from an Ingested Slug
If the job has been captured via `make hunt` and lives inside the database cache:
```bash
make new SOURCE=fraunhofer-institute-research-associate-12345
```

---

## 4. Post-Generation Verification & Compiling PDFs

Once the application is created under `applications/<slug>/`:

### Step 1: Review & Manual Edits
Review the generated `cv.md` and `cover-letter.md` inside `applications/<slug>/`. The local files are your absolute source of truth. Any edits you make here will be immediately reflected in your PDF compilation and automatically cached in DuckDB.

### Step 2: Compile to PDF (Bilingual EN/DE)
Render and compile the bilingual PDFs using the LaTeX template in the scraper container:
```bash
make pdf ID=<slug>
```

This compiles a clean, professional PDF:
*   `applications/<slug>/cv.pdf`
*   `applications/<slug>/cover-letter.pdf`
*   (Optional) Run `make upload ID=<slug>` to compile and automatically sync them to your Google Drive!
*   (Optional) Run `make sheet-push` to sync all application statuses with Google Sheets!

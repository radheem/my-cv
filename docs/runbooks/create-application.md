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
Run the `new` command, specifying the path to your file. You can optionally supply a `--slug` and `--recipient` name:
```bash
cv-tailor new my-job-description.txt --slug acme-corp-backend-engineer --recipient "Jane Smith"
```

The engine will:
1. Parse requirements into a JobSpec.
2. Select the top-3 matching projects and order skills deterministically.
3. Call the LLM to write beautifully tailored CV and cover letter prose.
4. Output Markdown files and indexes under: `applications/acme-corp-backend-engineer/`.

---

## 2. Option B: Create Application from LinkedIn

### Pathway 1: Direct Generation from URL (Dynamic Ingestion)
If you have a direct job URL, `cv-tailor` can dynamically fetch the job description using Playwright, parse it, and generate the tailored files in a single step:

```bash
cv-tailor new "https://www.linkedin.com/jobs/view/123456789/" --recipient "Hiring Manager"
```

### Pathway 2: Generating from an Ingested File
If you have already run `cv-tailor ingest` or `cv-tailor hunt` and have a captured job in `vault/jds/`:
1. Find the path of the job text file under `vault/jds/`:
   ```bash
   ls vault/jds/ | grep acme
   ```
2. Run the generator using that file path:
   ```bash
   cv-tailor new vault/jds/acme-software-engineer-4412345.txt --recipient "John Doe"
   ```

---

## 3. Option C: Create Application from Fraunhofer

### Pathway 1: Direct Generation from URL (Dynamic Ingestion)
You can generate a tailored application directly from a public Fraunhofer job posting URL. No login is needed:

```bash
cv-tailor new "https://jobs.fraunhofer.de/job/Ilmenau-Research-Associate-Secure-Development-98693/1234567/"
```

### Pathway 2: Generating from an Ingested File
If the job has been captured via `cv-tailor hunt` and lives under `vault/jds/`:
```bash
cv-tailor new vault/jds/fraunhofer-institute-research-associate-12345.txt
```

---

## 4. Post-Generation Verification & Compiling PDFs

Once the application is created under `applications/<slug>/`:

### Step 1: Review & Manual Edits
Review the generated `cv.md` and `cover-letter.md` inside `applications/<slug>/`. You can make manual tweaks directly to these files—they are your source of truth.

### Step 2: Compile to PDF (Bilingual EN/DE)
Render and compile the bilingual PDFs using the local LaTeX toolchain or Docker container:
```bash
cv-tailor pdf <slug>
```

This compiles a clean, professional PDF:
*   `applications/<slug>/cv.pdf`
*   `applications/<slug>/cover-letter.pdf`
*   (Optional) Run `cv-tailor upload <slug>` to compile and automatically sync them to your Google Drive!

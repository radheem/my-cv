import json
import re
import sys
from engine.mcp.server import (
    list_gmail_linkedin_jobs,
    fetch_public_job_url,
    save_job_description,
    create_application_from_job
)

print("🚀 Step 1: Querying Gmail alerts for a live job listing...")
try:
    jobs_json = list_gmail_linkedin_jobs(limit=1)
    jobs = json.loads(jobs_json)
except Exception as e:
    print(f"❌ Failed to read Gmail alerts: {e}")
    sys.exit(1)

if not jobs:
    print("⚠️ No unread LinkedIn job alerts found in your Gmail!")
    sys.exit(0)

job = jobs[0]
print(f"✅ Discovered live job from Gmail: '{job['company']}' - '{job['role']}'")
print(f"   URL: {job['job_url']}")

print("\n🚀 Step 2: Lightweight fetching of the public webpage (bypassing Playwright)...")
raw_text = fetch_public_job_url(job['job_url'])
if "ERROR" in raw_text:
    print(f"❌ Failed to fetch public page: {raw_text}")
    sys.exit(1)
print(f"✅ Webpage fetched successfully! Cleaned text length: {len(raw_text)} chars.")
print(f"   Snippet: {repr(raw_text[:200])}...")

print("\n🚀 Step 3: Directly saving the job description to PostgreSQL & vault/jds...")
save_res = save_job_description(
    company=job['company'],
    title=job['role'],
    url=job['job_url'],
    description=raw_text
)
print(f"💾 Save Result: {save_res}")

if "ERROR" in save_res:
    sys.exit(1)

# Extract generated slug
slug_match = re.search(r"slug '([^']+)'", save_res)
if not slug_match:
    print("❌ Failed to extract job slug from save result.")
    sys.exit(1)
slug = slug_match.group(1)

print(f"\n🚀 Step 4: Running application-tailoring pipeline for slug '{slug}'...")
app_res = create_application_from_job(slug)
print(f"📄 Tailor Result:\n{app_res}")

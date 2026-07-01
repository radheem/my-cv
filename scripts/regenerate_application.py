import sys
import subprocess
import shutil
import pathlib
from engine.shared.db import get_conn, init_db

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/regenerate_application.py <id-or-slug>")
        sys.exit(1)
        
    input_id = sys.argv[1]
    
    # Initialize database and locate slug + job_slug
    init_db()
    slug = None
    job_slug = None
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1. Try to find the parent job_slug and application slug with explicit aliases
            cur.execute("""
                SELECT a.slug as app_slug, j.slug as job_slug
                FROM applications a
                JOIN jobs j ON a.job_id = j.job_id
                WHERE a.slug = ? OR a.job_id = ?
            """, (input_id, input_id))
            row = cur.fetchone()
            if row:
                slug = row["app_slug"]
                job_slug = row["job_slug"]
            else:
                # 2. Try to find from applications alone
                cur.execute("SELECT slug, job_id FROM applications WHERE slug = ?", (input_id,))
                row = cur.fetchone()
                if row:
                    slug = row["slug"]
                    job_id = row["job_id"]
                    # Try to find job from jobs table
                    cur.execute("SELECT slug as job_slug FROM jobs WHERE job_id = ?", (job_id,))
                    j_row = cur.fetchone()
                    if j_row:
                        job_slug = j_row["job_slug"]
                        
    if not slug:
        slug = input_id
    if not job_slug:
        job_slug = slug
        
    print(f"🔄 Starting smart regeneration pipeline...")
    print(f"  * Application Slug: '{slug}'")
    print(f"  * Parent Job Slug:  '{job_slug}'")
    
    # 1. Delete database application row
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM applications WHERE slug = ?", (slug,))
        conn.commit()
    print(f"  * Deleted application record '{slug}' from DuckDB.")
    
    # 2. Delete filesystem directory
    app_dir = pathlib.Path("applications") / slug
    if app_dir.exists():
        shutil.rmtree(app_dir)
        print(f"  * Deleted directory: {app_dir}")
        
    # 3. Run cv-tailor new with the parent job_slug and custom application slug
    print(f"🚀 Running: cv-tailor new '{job_slug}' --slug '{slug}'...")
    res = subprocess.run(["cv-tailor", "new", job_slug, "--slug", slug], capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        print(f"❌ Failed to run cv-tailor new:\n{res.stderr}")
        sys.exit(res.returncode)
    print(res.stdout)
    
    # 4. Run cv-tailor pdf
    print(f"🚀 Running: cv-tailor pdf '{slug}'...")
    res = subprocess.run(["cv-tailor", "pdf", slug], capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        print(f"❌ Failed to run cv-tailor pdf:\n{res.stderr}")
        sys.exit(res.returncode)
    print(res.stdout)
    
    # 5. Run cv-tailor upload
    print(f"🚀 Running: cv-tailor upload '{slug}'...")
    res = subprocess.run(["cv-tailor", "upload", slug], capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        print(f"❌ Failed to run cv-tailor upload:\n{res.stderr}")
        sys.exit(res.returncode)
    print(res.stdout)
    
    print(f"🎉 Regeneration of '{slug}' completed successfully and uploaded to Google Drive!")

if __name__ == "__main__":
    main()

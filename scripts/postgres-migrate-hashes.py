#!/usr/bin/env python3
import os
import re
import hashlib
import psycopg
from psycopg.rows import dict_row

def compute_new_id(url, title):
    if url and url.strip():
        clean_url = url.strip().rstrip("/")
        return hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:12]
    # Clean up the title to be alphanumeric/space only to ensure stable hashing
    clean_title = "".join(ch for ch in title.lower() if ch.isalnum() or ch.isspace()).strip()
    return hashlib.md5(clean_title.encode("utf-8")).hexdigest()[:12]

def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cv_tailor")
    
    # If running inside Docker, replace localhost/127.0.0.1 with Compose db hostname
    if os.path.exists("/.dockerenv"):
        for local_host in ("localhost", "127.0.0.1"):
            if local_host in db_url:
                db_url = db_url.replace(local_host, "db")

    print(f"Connecting to database: {db_url}")
    conn = psycopg.connect(db_url, row_factory=dict_row)
    
    # 1. Fetch old data
    with conn.cursor() as cur:
        # Check if tables exist
        cur.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'jobs')")
        if not cur.fetchone()["exists"]:
            print("No existing tables found. Nothing to migrate.")
            return

        cur.execute("SELECT * FROM jobs")
        old_jobs = cur.fetchall()
        
        cur.execute("SELECT * FROM applications")
        old_apps = cur.fetchall()

    print(f"Loaded {len(old_jobs)} jobs and {len(old_apps)} applications from original schema.")

    # 2. Map old slug -> new computed job_id, and prepare rows
    slug_to_new_id = {}
    new_jobs_rows = []
    
    for job in old_jobs:
        new_id = compute_new_id(job["url"], job["title"])
        slug_to_new_id[job["slug"]] = new_id
        
        # Prepare the row
        new_jobs_rows.append((
            new_id, job["slug"], job["company"], job["title"], job["location"], 
            job["url"], job["description"], job["score"], job["applicants"], 
            job["source"], job["platform"], job["created_at"]
        ))

    new_apps_rows = []
    for app in old_apps:
        new_id = slug_to_new_id.get(app["slug"])
        if not new_id:
            print(f"WARNING: Application with slug '{app['slug']}' has no matching job! Skipping.")
            continue
            
        new_apps_rows.append((
            new_id, app["slug"], app["status"], app["recipient"], app["cv_en"], 
            app["cv_de"], app["cover_letter_en"], app["cover_letter_de"], 
            app["drive_url"], app["clusters"], app["updated_at"]
        ))

    # 3. Drop tables and create under new schema
    with conn.cursor() as cur:
        print("Dropping old tables...")
        cur.execute("DROP TABLE IF EXISTS applications CASCADE")
        cur.execute("DROP TABLE IF EXISTS jobs CASCADE")
        
        print("Creating new schema...")
        cur.execute("""
        CREATE TABLE jobs (
            job_id VARCHAR(100) PRIMARY KEY,
            slug VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            location VARCHAR(255),
            url TEXT,
            description TEXT,
            score INTEGER,
            applicants INTEGER,
            source VARCHAR(50) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        cur.execute("""
        CREATE TABLE applications (
            job_id VARCHAR(100) PRIMARY KEY REFERENCES jobs(job_id) ON DELETE CASCADE,
            slug VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'draft',
            recipient VARCHAR(255),
            cv_en TEXT,
            cv_de TEXT,
            cover_letter_en TEXT,
            cover_letter_de TEXT,
            drive_url TEXT,
            clusters TEXT[],
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 4. Insert migrated data
        print("Inserting migrated jobs...")
        cur.executemany("""
            INSERT INTO jobs (
                job_id, slug, company, title, location, url, description, 
                score, applicants, source, platform, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, new_jobs_rows)
        
        print("Inserting migrated applications...")
        cur.executemany("""
            INSERT INTO applications (
                job_id, slug, status, recipient, cv_en, cv_de, 
                cover_letter_en, cover_letter_de, drive_url, clusters, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, new_apps_rows)
        
    conn.commit()
    conn.close()
    print("Database migration completed successfully!")

if __name__ == "__main__":
    main()

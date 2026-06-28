import time
import json
import sys
from engine.mcp.server import create_application_from_job
from engine.shared.db import get_conn

slugs = [
    "1komma5-senior-iot-cloud-engineer-m-f-d-7a3301710006",
    "bwi-gmbh-cloud-engineer-m-w-d-3e92ec6aa083"
]

print("🚀 Step 1: Retrying application generation for the 2 slugs...")
for slug in slugs:
    res_json = create_application_from_job(slug)
    res = json.loads(res_json)
    if "error" in res:
        print(f"❌ Failed to trigger '{slug}': {res['error']}")
    else:
        print(f"✅ Successfully triggered '{slug}': status = {res['status']}")

print("\n📡 Step 2: Monitoring application lifecycle status...")
start_time = time.time()
try:
    while True:
        all_done = True
        print(f"\n⏱️ Elapsed time: {int(time.time() - start_time)} seconds")
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for slug in slugs:
                    cur.execute("SELECT status, updated_at FROM applications WHERE slug = %s", (slug,))
                    row = cur.fetchone()
                    if row:
                        status = row["status"]
                        updated_at = row["updated_at"]
                        print(f"  - {slug}: status = '{status}' (updated {updated_at})")
                        if status == "generating":
                            all_done = False
                    else:
                        print(f"  - {slug}: No record found in applications table.")
                        all_done = False
                        
        if all_done:
            print("\n🎉 All jobs have finished processing!")
            break
            
        time.sleep(5)
except KeyboardInterrupt:
    print("\n👋 Monitoring stopped by user.")

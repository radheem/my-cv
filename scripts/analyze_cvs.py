import pathlib
import json
import re
from collections import Counter
from engine import documents

def analyze():
    apps_dir = pathlib.Path(__file__).resolve().parent.parent / "applications"
    if not apps_dir.exists():
        print("Applications directory not found.")
        return

    total_cvs = 0
    taglines = []
    project_counts = Counter()
    cluster_counts = Counter()
    skills_lines = []
    
    # Track which projects are selected for which taxonomy clusters
    projects_by_cluster = {}

    for d in apps_dir.iterdir():
        if not d.is_dir() or d.name.startswith(".") or d.name == "__pycache__":
            continue
        
        cv_path = d / "cv.md"
        index_path = d / "index.md"
        if not cv_path.exists() or not index_path.exists():
            continue
            
        total_cvs += 1
        
        # 1. Parse index.md for clusters
        try:
            index_content = index_path.read_text(encoding="utf-8")
            meta, _ = documents.split_front_matter(index_content)
        except Exception:
            meta = {}
            
        clusters = meta.get("clusters") or []
        if isinstance(clusters, str):
            clusters = [c.strip() for c in clusters.split(";") if c.strip()]
        
        for c in clusters:
            cluster_counts[c] += 1
            
        # 2. Parse cv.md for tagline, projects, skills
        try:
            cv_content = cv_path.read_text(encoding="utf-8")
            cv_meta, cv_body = documents.split_front_matter(cv_content)
        except Exception:
            cv_meta = {}
            cv_body = ""
            
        tagline = cv_meta.get("tagline") or ""
        if tagline:
            taglines.append(tagline)
            
        # Extract projects
        # Bullet format: - **Project Name** — description
        project_bullets = re.findall(r"(?m)^-\s*\*\*([^*]+)\*\*", cv_body)
        for proj in project_bullets:
            project_counts[proj] += 1
            for c in clusters:
                if c not in projects_by_cluster:
                    projects_by_cluster[c] = Counter()
                projects_by_cluster[c][proj] += 1
                
        # Extract skill categories
        skills_sect = re.findall(r"(?m)^-\s*\*\*([^*]+)\*\*\s*—\s*(.*)$", cv_body)
        for cat, sks in skills_sect:
            skills_lines.append(cat.strip())

    # Print Report
    print("====================================================")
    print("          CV VARIANTS QUANTITATIVE REPORT")
    print("====================================================\n")
    print(f"Total Applications Analyzed: {total_cvs}\n")
    
    print("--- 1. Header Tagline Variants (Role Specialization) ---")
    tagline_summary = Counter(taglines)
    for tag, count in tagline_summary.most_common():
        print(f"  * {tag:<45} : {count} occurrences")
    print()
    
    print("--- 2. Taxonomy Cluster Associations ---")
    for cl, count in cluster_counts.most_common():
        print(f"  * {cl:<35} : {count} occurrences")
    print()
    
    print("--- 3. Project Selection Frequencies ---")
    for proj, count in project_counts.most_common():
        print(f"  * {proj:<35} : {count} inclusions")
    print()
    
    print("--- 4. Project Selection by Cluster ---")
    for cl, projs in projects_by_cluster.items():
        print(f"  * Cluster: {cl}")
        for proj, count in projs.most_common(3):
            print(f"    - {proj:<35} : {count} times")
    print()

if __name__ == "__main__":
    analyze()

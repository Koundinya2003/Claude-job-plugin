#!/usr/bin/env python3
"""CLI entry point for the job search pipeline.

Usage:
    python run_search.py queries     - Generate search queries
    python run_search.py report      - Generate daily report
    python run_search.py stats       - Show pipeline stats
    python run_search.py queue       - Show application queue
    python run_search.py resumes     - List available resume variants
    python run_search.py init        - Initialize database
"""

import sys
import json
from job_search.pipeline import JobSearchPipeline
from job_search.applications.resume_selector import list_available_resumes
from job_search.storage.database import init_db


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]

    if command == "init":
        init_db()
        print("Database initialized.")
        return

    pipeline = JobSearchPipeline()

    if command == "queries":
        queries = pipeline.get_search_queries()
        print("=== General Queries ===")
        for q in queries["general"]:
            print(f"  [{q['tier']}] {q['query']}")
        print("\n=== LinkedIn Queries ===")
        for q in queries["linkedin"]:
            print(f"  {q}")
        print("\n=== ATS Queries ===")
        for q in queries["ats"]:
            print(f"  {q}")

    elif command == "report":
        print(pipeline.get_daily_report())

    elif command == "stats":
        stats = pipeline.get_stats()
        print(json.dumps(stats, indent=2))

    elif command == "queue":
        queue = pipeline.get_application_queue()
        if not queue:
            print("No jobs in application queue.")
        else:
            for app in queue:
                print(f"  {app['company']} - {app['title']}")
                print(f"    Resume: {app['resume_version']}")
                print(f"    URL: {app['application_url']}")
                print(f"    Needs review: {app['requires_human_review']}")
                print()

    elif command == "resumes":
        resumes = list_available_resumes()
        for r in resumes:
            status = "EXISTS" if r["exists"] else "MISSING"
            print(f"  [{status}] {r['variant']}: {r['filename']} - {r['description']}")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Job Application Automation Plugin - Main Entry Point.

This is the primary interface for the Claude job search plugin.
It provides commands for discovery, reporting, and application management.

Usage as Claude plugin:
    "Find today's best AI Product and APM jobs in Bengaluru"
    "Show my job search report"
    "Show application queue"
    "Apply to qualified jobs"
"""

import json
import sys
from datetime import datetime

from job_search.pipeline import JobSearchPipeline
from job_search.applications.resume_selector import list_available_resumes
from job_search.applications.application_manager import get_application_queue, prepare_application
from job_search.outreach.recruiter_outreach import generate_outreach_message
from job_search.storage.database import init_db, get_all_jobs, get_todays_jobs


def discover(pipeline=None):
    if pipeline is None:
        pipeline = JobSearchPipeline()

    queries = pipeline.get_search_queries()
    print("Generated search queries for job discovery:")
    print(f"  General: {len(queries['general'])} queries")
    print(f"  LinkedIn: {len(queries['linkedin'])} queries")
    print(f"  ATS: {len(queries['ats'])} queries")
    print()
    print("Use these queries with WebSearch/FireCrawl to discover jobs,")
    print("then feed results through pipeline.process_search_result().")
    return queries


def report(pipeline=None):
    if pipeline is None:
        pipeline = JobSearchPipeline()

    report_text = pipeline.get_daily_report()
    print(report_text)
    return pipeline.get_report_data()


def queue(pipeline=None):
    if pipeline is None:
        pipeline = JobSearchPipeline()

    app_queue = pipeline.get_application_queue()
    if not app_queue:
        print("No jobs in application queue.")
        return []

    print(f"Application Queue: {len(app_queue)} jobs ready")
    print("=" * 60)
    for i, app in enumerate(app_queue, 1):
        print(f"\n{i}. {app['company']} - {app['title']}")
        print(f"   Resume: {app['resume_version']}")
        print(f"   URL: {app['application_url']}")
        if app['requires_human_review']:
            print(f"   *** REQUIRES HUMAN REVIEW: {', '.join(app['sensitive_fields_detected'])}")
        print(f"   Status: {app['status']}")

    return app_queue


def stats(pipeline=None):
    if pipeline is None:
        pipeline = JobSearchPipeline()

    s = pipeline.get_stats()
    print(f"Job Search Statistics ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"  Total tracked: {s['total_jobs']}")
    print(f"  Today:         {s['todays_jobs']}")
    print(f"  High priority: {s['high_priority']}")
    print(f"  Good match:    {s['good_match']}")
    print(f"  Mode:          {s['mode']}")
    return s


def outreach(pipeline=None):
    if pipeline is None:
        pipeline = JobSearchPipeline()

    jobs = get_todays_jobs()
    qualified = [j for j in jobs if j.get("relevance_score", 0) >= 70]

    if not qualified:
        print("No qualified jobs for outreach.")
        return []

    messages = []
    for job in qualified:
        if job.get("recruiter_name") or job.get("recruiter_email") or job.get("recruiter_linkedin"):
            msg = generate_outreach_message(job)
            messages.append(msg)
            print(f"\n--- Outreach for {job['company']} - {job['title']} ---")
            if msg['recruiter_email']:
                print(f"To: {msg['recruiter_email']}")
            if msg['recruiter_linkedin']:
                print(f"LinkedIn: {msg['recruiter_linkedin']}")
            print(msg['message'])

    if not messages:
        print("No recruiter contact info found for qualified jobs.")

    return messages


def main():
    if len(sys.argv) < 2:
        print("Job Application Automation Plugin")
        print("=" * 40)
        print()
        print("Commands:")
        print("  python plugin.py discover  - Generate search queries")
        print("  python plugin.py report    - Daily job report")
        print("  python plugin.py queue     - Application queue")
        print("  python plugin.py stats     - Pipeline statistics")
        print("  python plugin.py outreach  - Recruiter messages")
        print("  python plugin.py resumes   - Resume variants")
        print("  python plugin.py init      - Initialize database")
        return

    command = sys.argv[1]
    commands = {
        "discover": discover,
        "report": report,
        "queue": queue,
        "stats": stats,
        "outreach": outreach,
        "resumes": lambda: [print(f"  [{('EXISTS' if r['exists'] else 'MISSING')}] {r['variant']}: {r['description']}") for r in list_available_resumes()],
        "init": lambda: (init_db(), print("Database initialized.")),
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

from datetime import datetime
from job_search.storage.database import (
    update_job_status, log_application_action, get_jobs_by_score
)
from job_search.applications.resume_selector import select_resume


SENSITIVE_FIELDS = [
    "legal declaration",
    "criminal record",
    "background check consent",
    "compensation expectation",
    "salary expectation",
    "expected ctc",
    "current ctc",
    "eeo",
    "equal employment opportunity",
    "demographic",
    "disability",
    "veteran status",
    "gender identity",
    "race",
    "ethnicity",
    "work authorization",
    "visa status",
    "relocation",
    "non-compete",
    "non-disclosure",
    "payment",
    "credit card",
    "bank account",
    "ssn",
    "aadhaar",
    "pan card",
]


def prepare_application(job_data):
    resume = select_resume(job_data.get("title", ""), job_data.get("description", ""))

    application = {
        "job_id": job_data.get("id"),
        "company": job_data.get("company"),
        "title": job_data.get("title"),
        "application_url": job_data.get("application_url"),
        "resume_version": resume["variant"],
        "resume_path": resume["path"],
        "resume_exists": resume["exists"],
        "prepared_at": datetime.now().isoformat(),
        "status": "prepared",
        "sensitive_fields_detected": [],
        "requires_human_review": False,
    }

    if job_data.get("description"):
        sensitive = check_sensitive_fields(job_data["description"])
        if sensitive:
            application["sensitive_fields_detected"] = sensitive
            application["requires_human_review"] = True
            application["status"] = "needs_review"

    return application


def check_sensitive_fields(text):
    text_lower = text.lower()
    found = []
    for field in SENSITIVE_FIELDS:
        if field in text_lower:
            found.append(field)
    return found


def get_application_queue(min_score=70):
    jobs = get_jobs_by_score(min_score)
    queue = []
    for job in jobs:
        if job.get("application_status") == "not_applied" and job.get("status") != "rejected":
            app = prepare_application(job)
            queue.append(app)
    return queue


def mark_applied(job_id, resume_version="", notes=""):
    update_job_status(
        job_id,
        "applied",
        application_status="applied",
        date_applied=datetime.now().isoformat(),
        resume_version=resume_version,
    )
    log_application_action(job_id, "applied", notes)


def mark_rejected(job_id, reason=""):
    update_job_status(
        job_id,
        "rejected",
        application_status="rejected",
        rejection_date=datetime.now().isoformat(),
        response_notes=reason,
    )
    log_application_action(job_id, "rejected", reason)


def mark_needs_review(job_id, reason=""):
    update_job_status(job_id, "needs_review", notes=reason)
    log_application_action(job_id, "flagged_for_review", reason)

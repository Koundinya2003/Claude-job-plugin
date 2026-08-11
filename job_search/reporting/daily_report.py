from datetime import datetime
from job_search.storage.database import (
    get_high_priority_jobs, get_good_match_jobs,
    get_todays_jobs, get_job_count, get_applied_jobs,
)


def generate_daily_report():
    today = datetime.now().strftime("%Y-%m-%d")
    report = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "summary": {},
        "high_priority": [],
        "good_match": [],
        "rejected": [],
        "stats": {},
    }

    all_today = get_todays_jobs()
    high_priority = get_high_priority_jobs()
    good_match = get_good_match_jobs()
    applied = get_applied_jobs()
    total = get_job_count()

    report["summary"] = {
        "total_jobs_in_db": total,
        "discovered_today": len(all_today),
        "high_priority_count": len(high_priority),
        "good_match_count": len(good_match),
        "total_applied": len(applied),
    }

    for job in high_priority:
        report["high_priority"].append(_format_job_entry(job))

    for job in good_match:
        report["good_match"].append(_format_job_entry(job))

    for job in all_today:
        if job.get("relevance_score", 0) < 70:
            report["rejected"].append({
                "company": job.get("company", ""),
                "title": job.get("title", ""),
                "score": job.get("relevance_score", 0),
                "reason": _determine_rejection_reason(job),
            })

    return report


def _format_job_entry(job):
    return {
        "id": job.get("id"),
        "company": job.get("company", ""),
        "title": job.get("title", ""),
        "location": job.get("location", ""),
        "work_mode": job.get("work_mode", ""),
        "score": job.get("relevance_score", 0),
        "priority": job.get("priority_label", ""),
        "experience_requirement": job.get("experience_requirement", ""),
        "job_url": job.get("job_url", ""),
        "application_url": job.get("application_url", ""),
        "recruiter_name": job.get("recruiter_name", ""),
        "recruiter_email": job.get("recruiter_email", ""),
        "resume_version": job.get("resume_version", ""),
        "application_status": job.get("application_status", ""),
        "date_posted": job.get("date_posted", ""),
        "date_discovered": job.get("date_discovered", ""),
    }


def _determine_rejection_reason(job):
    reasons = []
    score = job.get("relevance_score", 0)

    if score < 30:
        reasons.append("irrelevant role")
    elif score < 50:
        reasons.append("poor match")

    if job.get("status") == "rejected":
        if job.get("response_notes"):
            reasons.append(job["response_notes"])

    if not job.get("is_active"):
        reasons.append("expired")

    if not job.get("company_legitimate"):
        reasons.append("suspicious")

    if not reasons:
        reasons.append("below score threshold")

    return "; ".join(reasons)


def format_report_text(report):
    lines = []
    lines.append(f"# Job Search Report - {report['date']}")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")

    summary = report["summary"]
    lines.append("## Summary")
    lines.append(f"- Total jobs tracked: {summary['total_jobs_in_db']}")
    lines.append(f"- Discovered today: {summary['discovered_today']}")
    lines.append(f"- High priority: {summary['high_priority_count']}")
    lines.append(f"- Good match: {summary['good_match_count']}")
    lines.append(f"- Total applied: {summary['total_applied']}")
    lines.append("")

    if report["high_priority"]:
        lines.append("## HIGH PRIORITY (Score 85+)")
        lines.append("")
        for job in report["high_priority"]:
            lines.append(f"### {job['company']} - {job['title']}")
            lines.append(f"- Score: {job['score']}")
            lines.append(f"- Location: {job['location']} ({job['work_mode']})")
            lines.append(f"- Experience: {job['experience_requirement']}")
            if job.get("job_url"):
                lines.append(f"- Job URL: {job['job_url']}")
            if job.get("application_url"):
                lines.append(f"- Apply: {job['application_url']}")
            if job.get("recruiter_name"):
                lines.append(f"- Recruiter: {job['recruiter_name']}")
            if job.get("recruiter_email"):
                lines.append(f"- Contact: {job['recruiter_email']}")
            lines.append(f"- Resume: {job.get('resume_version', 'not selected')}")
            lines.append(f"- Status: {job['application_status']}")
            lines.append("")
    else:
        lines.append("## HIGH PRIORITY")
        lines.append("No high priority jobs found today.")
        lines.append("")

    if report["good_match"]:
        lines.append("## GOOD MATCH (Score 70-84)")
        lines.append("")
        for job in report["good_match"]:
            lines.append(f"### {job['company']} - {job['title']}")
            lines.append(f"- Score: {job['score']}")
            lines.append(f"- Location: {job['location']} ({job['work_mode']})")
            if job.get("job_url"):
                lines.append(f"- Job URL: {job['job_url']}")
            if job.get("application_url"):
                lines.append(f"- Apply: {job['application_url']}")
            lines.append(f"- Status: {job['application_status']}")
            lines.append("")
    else:
        lines.append("## GOOD MATCH")
        lines.append("No good match jobs found today.")
        lines.append("")

    if report["rejected"]:
        lines.append("## REJECTED")
        lines.append("")
        for job in report["rejected"][:10]:
            lines.append(f"- {job['company']} - {job['title']} (Score: {job['score']}) - {job['reason']}")
        if len(report["rejected"]) > 10:
            lines.append(f"- ... and {len(report['rejected']) - 10} more")
        lines.append("")

    return "\n".join(lines)

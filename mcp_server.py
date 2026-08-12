#!/usr/bin/env python3
"""MCP server exposing the job search pipeline to Claude Desktop.

Register in claude_desktop_config.json, then ask Claude things like
"find today's best APM jobs in Bengaluru" and it will call these tools.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import MCPServer

from job_search.pipeline import JobSearchPipeline
from job_search.applications.answer_generator import draft_application_answers
from job_search.applications.resume_selector import list_available_resumes
from job_search.outreach.recruiter_outreach import generate_outreach_message
from job_search.storage.database import (
    get_all_jobs,
    get_todays_jobs,
    log_application_action,
    update_job_status,
)

CONFIG_PATH = os.environ.get("JOB_PLUGIN_CONFIG")

mcp = MCPServer(
    name="job-search",
    version="1.0.0",
    instructions=(
        "Quality-first job discovery and application tracking for APM, Product Analyst "
        "and AI Product roles. Typical flow: call get_search_queries, run those queries "
        "with your own web search, then pass what you find to submit_job_listings — it "
        "validates, deduplicates and scores each listing. Then read get_daily_report or "
        "get_application_queue.\n\n"
        "Rules: never invent a company, recruiter, email, URL or date — omit any field you "
        "did not actually find. Only call record_application for a submission you have "
        "confirmed. Anything the tools flag for human review must go to the user, not be "
        "answered on their behalf."
    ),
)

_pipeline: JobSearchPipeline | None = None


def pipeline() -> JobSearchPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = JobSearchPipeline(CONFIG_PATH)
    return _pipeline


@mcp.tool()
def get_search_queries() -> dict:
    """Generate search queries for job discovery, grouped into general, LinkedIn and ATS queries.

    Run these with web search, then pass the listings you find to submit_job_listings.
    """
    return pipeline().get_search_queries()


@mcp.tool()
def submit_job_listings(listings: list[dict[str, Any]]) -> dict:
    """Validate, deduplicate, score and store job listings found via web search.

    Each listing accepts: company and title (required), plus location, work_mode,
    experience_requirement, date_posted, job_url, application_url, job_source,
    description, requirements, recruiter_name, recruiter_email, recruiter_linkedin.

    Omit any field you did not actually find rather than guessing it. Returns the
    outcome per listing: added (with score and priority), rejected, duplicate or scam.
    """
    if not listings:
        return {"error": "No listings supplied."}
    result = pipeline().process_batch(listings)
    return {**result, "counts": {k: len(v) for k, v in result.items()}}


@mcp.tool()
def get_daily_report(format: Literal["text", "json"] = "text") -> Any:
    """Daily report of discovered jobs, split into HIGH PRIORITY (85+), GOOD MATCH (70-84) and REJECTED."""
    p = pipeline()
    return p.get_report_data() if format == "json" else p.get_daily_report()


@mcp.tool()
def get_application_queue() -> list[dict]:
    """Jobs at or above the score threshold not yet applied to.

    Each entry carries its selected resume variant and any sensitive fields that need
    human review before the application can proceed.
    """
    return pipeline().get_application_queue()


@mcp.tool()
def get_stats() -> dict:
    """Counts of tracked, today's, high-priority and good-match jobs, plus the current mode."""
    return pipeline().get_stats()


@mcp.tool()
def list_jobs(today_only: bool = False, min_score: float = 0) -> list[dict]:
    """List stored jobs, optionally limited to today or filtered by minimum relevance score."""
    jobs = get_todays_jobs() if today_only else get_all_jobs()
    return [j for j in jobs if (j.get("relevance_score") or 0) >= min_score]


@mcp.tool()
def draft_answers(questions: list[str]) -> list[dict]:
    """Draft application answers strictly from the stored candidate profile.

    Questions needing judgement, or touching legal, compensation, demographic or
    work-authorization territory, come back flagged for human review rather than
    answered. Surface those to the user instead of filling them in.
    """
    return draft_application_answers(questions)


@mcp.tool()
def draft_recruiter_message(job_id: int) -> dict:
    """Draft a personalized outreach message for one stored job.

    Picks a proof point matching the role. Drafts only — this does not send anything.
    """
    job = next((j for j in get_all_jobs() if j["id"] == job_id), None)
    if job is None:
        return {"error": f"No stored job with id {job_id}."}
    return generate_outreach_message(job)


@mcp.tool()
def list_resume_variants() -> list[dict]:
    """Resume variants and whether each file is present on disk."""
    return list_available_resumes()


@mcp.tool()
def record_application(
    job_id: int,
    outcome: Literal["applied", "rejected", "needs_review"],
    resume_version: str = "",
    notes: str = "",
) -> str:
    """Record a confirmed application outcome and write it to the audit log.

    Only call this with outcome="applied" for a submission you have actually confirmed —
    never to mark intent.
    """
    now = datetime.now().isoformat()

    if outcome == "applied":
        update_job_status(
            job_id,
            "applied",
            application_status="applied",
            date_applied=now,
            resume_version=resume_version,
        )
    elif outcome == "rejected":
        update_job_status(
            job_id,
            "rejected",
            application_status="rejected",
            rejection_date=now,
            response_notes=notes,
        )
    else:
        update_job_status(job_id, "needs_review", notes=notes)

    log_application_action(job_id, outcome, notes)
    return f"Recorded '{outcome}' for job {job_id}."


if __name__ == "__main__":
    mcp.run()

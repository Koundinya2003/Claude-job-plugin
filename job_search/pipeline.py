"""Main job search pipeline orchestrator.

Coordinates the full discovery -> validation -> scoring -> reporting flow.
Designed to be called by the Claude plugin or CLI.
"""

import json
import logging
from datetime import datetime

from job_search.config.loader import load_config, get_search_config, get_mode
from job_search.sources.web_search import (
    generate_search_queries, generate_linkedin_queries, generate_ats_queries,
)
from job_search.extraction.job_parser import (
    parse_job_listing, detect_work_mode, extract_experience_requirement,
    extract_recruiter_info, normalize_date,
)
from job_search.validation.job_validator import validate_job
from job_search.validation.duplicate_checker import is_duplicate
from job_search.validation.scam_detector import detect_scam
from job_search.ranking.relevance_scorer import score_job
from job_search.storage.database import (
    init_db, insert_job, log_search, get_todays_jobs,
    get_high_priority_jobs, get_good_match_jobs, get_job_count,
)
from job_search.applications.resume_selector import select_resume
from job_search.applications.application_manager import prepare_application, get_application_queue
from job_search.reporting.daily_report import generate_daily_report, format_report_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("job_search")


class JobSearchPipeline:
    def __init__(self, config_path=None):
        self.config = load_config(config_path)
        self.search_config = get_search_config(self.config)
        self.mode = get_mode(self.config)
        init_db()
        logger.info("Pipeline initialized (mode=%s)", self.mode)

    def get_search_queries(self):
        queries = generate_search_queries(self.config)
        linkedin_queries = generate_linkedin_queries(self.config)
        ats_queries = generate_ats_queries(self.config)
        return {
            "general": queries,
            "linkedin": linkedin_queries,
            "ats": ats_queries,
        }

    def process_search_result(self, result):
        """Process a single search result into a validated, scored job entry.

        Args:
            result: dict with keys: company, title, location, job_url,
                    application_url, description, date_posted, job_source,
                    and optionally: work_mode, experience_requirement,
                    recruiter_name, recruiter_email, recruiter_linkedin

        Returns:
            dict with job data and processing result, or None if rejected
        """
        company = (result.get("company") or "").strip()
        title = (result.get("title") or "").strip()

        if not company or not title:
            logger.debug("Skipping result with missing company/title")
            return None

        if is_duplicate(company, title, result.get("job_url")):
            logger.debug("Duplicate: %s - %s", company, title)
            return {"status": "duplicate", "company": company, "title": title}

        job_data = {
            "company": company,
            "title": title,
            "location": result.get("location", ""),
            "work_mode": result.get("work_mode") or detect_work_mode(result.get("description", "")),
            "experience_requirement": result.get("experience_requirement") or extract_experience_requirement(result.get("description", "")),
            "date_posted": normalize_date(result.get("date_posted", "")),
            "job_url": result.get("job_url", ""),
            "application_url": result.get("application_url", ""),
            "job_source": result.get("job_source", "web_search"),
            "description": result.get("description", ""),
            "requirements": result.get("requirements", ""),
            "recruiter_name": result.get("recruiter_name", ""),
            "recruiter_email": result.get("recruiter_email", ""),
            "recruiter_linkedin": result.get("recruiter_linkedin", ""),
            "company_legitimate": 1,
        }

        if result.get("description"):
            rec_info = extract_recruiter_info(result["description"])
            if not job_data["recruiter_email"] and rec_info["email"]:
                job_data["recruiter_email"] = rec_info["email"]
            if not job_data["recruiter_linkedin"] and rec_info["linkedin"]:
                job_data["recruiter_linkedin"] = rec_info["linkedin"]

        scam_result = detect_scam(job_data)
        if scam_result["is_scam"]:
            logger.info("Scam detected: %s - %s (%s)", company, title, scam_result["signals"])
            return {"status": "scam", "company": company, "title": title, "signals": scam_result["signals"]}

        validation = validate_job(job_data, self.config)
        if not validation["valid"]:
            logger.debug("Invalid: %s - %s (%s)", company, title, validation["reasons"])
            return {"status": "rejected", "company": company, "title": title, "reasons": validation["reasons"]}

        scoring = score_job(job_data, self.config)
        job_data["relevance_score"] = scoring["total_score"]
        job_data["priority_label"] = scoring["priority"]

        resume = select_resume(title, job_data.get("description", ""))
        job_data["resume_version"] = resume["variant"]

        if scoring["total_score"] >= self.search_config.get("minimum_relevance_score", 70):
            job_data["status"] = "qualified"
        else:
            job_data["status"] = "below_threshold"

        job_id = insert_job(job_data)
        if job_id:
            logger.info(
                "Added: %s - %s (score=%.1f, priority=%s)",
                company, title, scoring["total_score"], scoring["priority"],
            )

        return {
            "status": "added",
            "job_id": job_id,
            "company": company,
            "title": title,
            "score": scoring["total_score"],
            "priority": scoring["priority"],
            "breakdown": scoring["breakdown"],
            "warnings": validation.get("warnings", []),
            "resume_version": resume["variant"],
        }

    def process_batch(self, results):
        processed = {"added": [], "rejected": [], "duplicates": [], "scams": [], "errors": []}

        max_daily = self.search_config.get("max_daily_jobs", 30)
        today_count = len(get_todays_jobs())

        for result in results:
            if today_count + len(processed["added"]) >= max_daily:
                logger.info("Daily limit reached (%d)", max_daily)
                break

            try:
                outcome = self.process_search_result(result)
                if outcome is None:
                    continue
                elif outcome["status"] == "added":
                    processed["added"].append(outcome)
                elif outcome["status"] == "duplicate":
                    processed["duplicates"].append(outcome)
                elif outcome["status"] == "scam":
                    processed["scams"].append(outcome)
                elif outcome["status"] == "rejected":
                    processed["rejected"].append(outcome)
            except Exception as e:
                logger.error("Error processing result: %s", str(e))
                processed["errors"].append({"error": str(e), "result": str(result)[:200]})

        return processed

    def get_daily_report(self):
        report = generate_daily_report()
        return format_report_text(report)

    def get_report_data(self):
        return generate_daily_report()

    def get_application_queue(self):
        return get_application_queue(self.search_config.get("minimum_relevance_score", 70))

    def get_stats(self):
        return {
            "total_jobs": get_job_count(),
            "todays_jobs": len(get_todays_jobs()),
            "high_priority": len(get_high_priority_jobs()),
            "good_match": len(get_good_match_jobs()),
            "mode": self.mode,
        }

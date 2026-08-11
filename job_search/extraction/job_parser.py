import re
from datetime import datetime, timedelta


def parse_job_listing(raw_text, source="unknown"):
    job = {
        "company": "",
        "title": "",
        "location": "",
        "work_mode": "",
        "experience_requirement": "",
        "date_posted": "",
        "job_url": "",
        "application_url": "",
        "job_source": source,
        "description": "",
        "requirements": "",
        "recruiter_name": "",
        "recruiter_email": "",
        "recruiter_linkedin": "",
        "company_legitimate": 1,
    }

    job["description"] = raw_text
    job["work_mode"] = detect_work_mode(raw_text)
    job["experience_requirement"] = extract_experience_requirement(raw_text)

    return job


def detect_work_mode(text):
    text_lower = text.lower()
    if "remote" in text_lower and "hybrid" in text_lower:
        return "Hybrid/Remote"
    if "fully remote" in text_lower or "100% remote" in text_lower:
        return "Remote"
    if "remote" in text_lower:
        return "Remote"
    if "hybrid" in text_lower:
        return "Hybrid"
    if "on-site" in text_lower or "onsite" in text_lower or "in-office" in text_lower:
        return "On-site"
    return "Not specified"


def extract_experience_requirement(text):
    text_lower = text.lower()

    patterns = [
        r"(\d+)\s*[-–to]+\s*(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)",
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)",
        r"minimum\s+(\d+)\s*(?:years?|yrs?)",
        r"at\s+least\s+(\d+)\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(0)

    if any(w in text_lower for w in ["fresher", "fresh graduate", "entry level", "entry-level", "0 experience"]):
        return "Fresher/Entry Level"

    if "intern" in text_lower:
        return "Internship"

    return "Not specified"


def extract_recruiter_info(text):
    info = {"name": "", "email": "", "linkedin": ""}

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    if emails:
        info["email"] = emails[0]

    linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+"
    linkedin_matches = re.findall(linkedin_pattern, text)
    if linkedin_matches:
        info["linkedin"] = linkedin_matches[0]

    return info


def normalize_date(date_str):
    if not date_str:
        return ""

    date_str = date_str.strip().lower()

    relative_patterns = {
        "today": 0,
        "just now": 0,
        "1 day ago": 1,
        "yesterday": 1,
        "2 days ago": 2,
        "3 days ago": 3,
        "1 week ago": 7,
        "2 weeks ago": 14,
        "1 month ago": 30,
    }

    for pattern, days in relative_patterns.items():
        if pattern in date_str:
            return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    day_match = re.search(r"(\d+)\s*days?\s*ago", date_str)
    if day_match:
        days = int(day_match.group(1))
        return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    week_match = re.search(r"(\d+)\s*weeks?\s*ago", date_str)
    if week_match:
        weeks = int(week_match.group(1))
        return (datetime.now() - timedelta(weeks=weeks)).strftime("%Y-%m-%d")

    return date_str


def extract_salary_info(text):
    patterns = [
        r"(?:₹|INR|Rs\.?)\s*[\d,]+(?:\s*[-–to]+\s*(?:₹|INR|Rs\.?)\s*[\d,]+)?(?:\s*(?:LPA|lpa|per\s*annum|/yr|/year))?",
        r"[\d,]+\s*[-–to]+\s*[\d,]+\s*(?:LPA|lpa|per\s*annum)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ""

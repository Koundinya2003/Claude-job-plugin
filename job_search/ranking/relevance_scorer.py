import re
from datetime import datetime, timedelta
from job_search.config.loader import get_scoring_weights, get_target_roles, get_locations


TIER1_KEYWORDS = [
    "associate product manager", "apm", "product analyst",
    "ai product analyst", "ai product management", "ai product manager",
    "product management intern", "ai product management intern",
]

TIER2_KEYWORDS = [
    "product operations", "product ops", "business analyst",
    "growth analyst", "product strategy", "data analyst",
    "product operations analyst",
]

PRODUCT_DESCRIPTION_SIGNALS = [
    "product roadmap", "product metrics", "user research",
    "product requirements", "prd", "product strategy",
    "a/b testing", "product analytics", "feature prioritization",
    "stakeholder management", "product lifecycle", "product discovery",
    "user stories", "sprint planning", "okr", "kpi",
    "customer insights", "market research", "competitive analysis",
    "product-market fit", "go-to-market",
]

CANDIDATE_FIT_KEYWORDS = [
    "data analysis", "python", "sql", "analytics", "metrics",
    "data visualization", "excel", "tableau", "power bi",
    "product analytics", "user research", "stakeholder",
    "ai", "machine learning", "llm", "rag", "nlp",
    "prompt engineering", "openai", "embeddings",
    "product discovery", "prd", "mvp", "roadmap",
    "rice", "prioritization", "a/b test", "experimentation",
    "north star", "kpi", "funnel", "activation",
    "etl", "api", "rest api", "fastapi",
    "manufacturing", "iot", "dashboard",
    "computer science", "b.tech", "fresher", "fresh graduate",
    "entry level", "intern", "0-1 years", "0-2 years",
    "streamlit", "next.js", "typescript",
]


def score_job(job_data, config=None):
    weights = get_scoring_weights(config)
    scores = {}

    scores["role_relevance"] = _score_role_relevance(
        job_data.get("title", ""),
        job_data.get("description", "")
    )

    scores["candidate_fit"] = _score_candidate_fit(
        job_data.get("description", ""),
        job_data.get("requirements", "")
    )

    scores["experience_fit"] = _score_experience_fit(
        job_data.get("experience_requirement", "")
    )

    scores["location_fit"] = _score_location_fit(
        job_data.get("location", ""),
        job_data.get("work_mode", ""),
        config
    )

    scores["company_quality"] = _score_company_quality(
        job_data.get("company", ""),
        job_data.get("application_url", ""),
        job_data.get("company_legitimate", 1)
    )

    scores["recency"] = _score_recency(
        job_data.get("date_posted", "")
    )

    scores["application_quality"] = _score_application_quality(
        job_data.get("application_url", ""),
        job_data.get("job_source", "")
    )

    total = 0
    for key, score in scores.items():
        weight = weights.get(key, 0)
        total += (score / 100) * weight

    priority = "DO NOT APPLY"
    if total >= 85:
        priority = "HIGH PRIORITY"
    elif total >= 70:
        priority = "GOOD MATCH"

    return {
        "total_score": round(total, 1),
        "breakdown": scores,
        "priority": priority,
    }


def _score_role_relevance(title, description):
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""
    score = 0

    for keyword in TIER1_KEYWORDS:
        if keyword in title_lower:
            score = 95
            break

    if score == 0:
        for keyword in TIER2_KEYWORDS:
            if keyword in title_lower:
                score = 70
                break

    if score == 0 and desc_lower:
        signal_count = sum(1 for s in PRODUCT_DESCRIPTION_SIGNALS if s in desc_lower)
        if signal_count >= 5:
            score = 60
        elif signal_count >= 3:
            score = 40
        elif signal_count >= 1:
            score = 20

    return min(score, 100)


def _score_candidate_fit(description, requirements):
    text = f"{description} {requirements}".lower()
    if not text.strip():
        return 60

    matches = sum(1 for kw in CANDIDATE_FIT_KEYWORDS if kw in text)
    score = min(matches * 10, 100)
    return max(score, 45)


def _score_experience_fit(exp_req):
    if not exp_req:
        return 75

    exp_lower = exp_req.lower()

    if any(w in exp_lower for w in ["fresher", "entry level", "entry-level", "internship", "intern", "0 experience"]):
        return 100

    range_match = re.search(r"(\d+)\s*[-–to]+\s*(\d+)", exp_lower)
    if range_match:
        min_y, max_y = int(range_match.group(1)), int(range_match.group(2))
        if min_y == 0:
            return 100
        if min_y <= 1:
            return 85
        if min_y <= 2:
            return 65
        return 20

    year_match = re.search(r"(\d+)\s*\+?\s*(?:years?|yrs?)", exp_lower)
    if year_match:
        years = int(year_match.group(1))
        if years == 0:
            return 100
        if years == 1:
            return 85
        if years == 2:
            return 60
        return 15

    return 75


def _score_location_fit(location, work_mode, config=None):
    locations = get_locations(config)
    loc_lower = location.lower() if location else ""
    mode_lower = work_mode.lower() if work_mode else ""

    if "remote" in mode_lower or "remote" in loc_lower:
        if "india" in loc_lower or not loc_lower or "remote" == loc_lower.strip():
            return 90

    primary = [l.lower() for l in locations.get("primary", [])]
    for p in primary:
        if p in loc_lower or loc_lower in p:
            return 100

    if "bengaluru" in loc_lower or "bangalore" in loc_lower:
        return 100

    acceptable = [l.lower() for l in locations.get("acceptable", [])]
    for a in acceptable:
        if a in loc_lower:
            return 85

    other_india = [l.lower() for l in locations.get("other_india", [])]
    for o in other_india:
        if o in loc_lower:
            return 50

    if "india" in loc_lower:
        return 45

    return 20


def _score_company_quality(company, app_url, is_legitimate):
    if not is_legitimate:
        return 10

    score = 50

    if company and len(company) > 2:
        score += 20

    if app_url:
        legitimate_domains = [
            "greenhouse.io", "lever.co", "workday.com", "ashbyhq.com",
            "linkedin.com", "careers", "jobs", "icims.com",
            "smartrecruiters.com", "myworkdayjobs.com",
        ]
        for domain in legitimate_domains:
            if domain in (app_url or "").lower():
                score += 30
                break

    return min(score, 100)


def _score_recency(date_posted):
    if not date_posted:
        return 50

    try:
        posted = datetime.strptime(date_posted, "%Y-%m-%d")
        days_ago = (datetime.now() - posted).days

        if days_ago <= 1:
            return 100
        if days_ago <= 3:
            return 90
        if days_ago <= 7:
            return 75
        if days_ago <= 14:
            return 55
        if days_ago <= 30:
            return 35
        return 15
    except (ValueError, TypeError):
        return 50


def _score_application_quality(app_url, source):
    score = 50

    if app_url:
        official_indicators = [
            "greenhouse.io", "lever.co", "workday.com", "ashbyhq.com",
            "careers.", "jobs.", "/apply", "icims.com",
        ]
        for indicator in official_indicators:
            if indicator in (app_url or "").lower():
                score = 90
                break

    source_quality = {
        "linkedin": 80,
        "company_careers": 95,
        "greenhouse": 90,
        "lever": 90,
        "workday": 85,
        "ashby": 90,
        "web_search": 60,
    }
    score = max(score, source_quality.get(source, 50))

    return min(score, 100)

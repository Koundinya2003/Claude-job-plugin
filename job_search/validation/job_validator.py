import re
from job_search.config.loader import get_reject_roles, get_experience_filter, get_target_roles


SUSPICIOUS_INDICATORS = [
    "pay to apply",
    "registration fee",
    "processing fee",
    "guaranteed placement",
    "earn from home",
    "work from home typing",
    "data entry operator earn",
    "mlm",
    "network marketing",
    "multi-level",
    "commission only",
    "commission-only",
    "no salary",
    "unpaid",
    "pay us",
    "deposit required",
]

SUSPICIOUS_DOMAINS = [
    "bit.ly",
    "tinyurl.com",
    "goo.gl",
    "t.co",
    "rebrand.ly",
]


def validate_job(job_data, config=None):
    result = {
        "valid": True,
        "reasons": [],
        "warnings": [],
    }

    if not job_data.get("company") or not job_data.get("title"):
        result["valid"] = False
        result["reasons"].append("Missing company or title")
        return result

    if is_rejected_role(job_data.get("title", ""), config):
        result["valid"] = False
        result["reasons"].append("Role matches rejection list")
        return result

    if not is_relevant_role(job_data.get("title", ""), job_data.get("description", ""), config):
        result["valid"] = False
        result["reasons"].append("Role not relevant to target positions")
        return result

    if is_experience_mismatch(job_data.get("experience_requirement", ""), config):
        result["valid"] = False
        result["reasons"].append("Experience requirement too high")
        return result

    if is_suspicious(job_data):
        result["valid"] = False
        result["reasons"].append("Suspicious listing detected")
        return result

    if not job_data.get("job_url") and not job_data.get("application_url"):
        result["warnings"].append("No application URL found")

    if not job_data.get("date_posted"):
        result["warnings"].append("Post date unknown")

    return result


def is_rejected_role(title, config=None):
    reject_list = get_reject_roles(config)
    title_lower = title.lower()

    for reject_role in reject_list:
        if reject_role.lower() in title_lower:
            return True

    reject_patterns = [
        r"\bsoftware\s+(?:developer|engineer)\b",
        r"\bbackend\s+(?:developer|engineer)\b",
        r"\bfrontend\s+(?:developer|engineer)\b",
        r"\bfull\s*stack\s+(?:developer|engineer)\b",
        r"\bdevops\b",
        r"\bsre\b",
        r"\bqa\s+(?:engineer|analyst|tester)\b",
        r"\btest\s+(?:engineer|automation)\b",
        r"\bdata\s+engineer\b",
        r"\bml\s+engineer\b",
        r"\bmachine\s+learning\s+engineer\b",
        r"\bit\s+support\b",
        r"\btechnical\s+support\b",
        r"\bcustomer\s+(?:support|service|success)\b",
        r"\bsales\s+(?:executive|representative|manager)\b",
        r"\btelecall(?:er|ing)\b",
        r"\bhr\s+(?:executive|manager|generalist)\b",
    ]

    for pattern in reject_patterns:
        if re.search(pattern, title_lower):
            return True

    return False


def is_relevant_role(title, description="", config=None):
    roles = get_target_roles(config)
    all_roles = roles.get("all", [])

    title_lower = title.lower()

    relevance_keywords = [
        "product manager", "product management", "product analyst",
        "apm", "associate product", "product operations",
        "business analyst", "growth analyst", "product strategy",
        "ai product", "data analyst", "product ops",
        "product intern", "pm intern",
    ]

    for keyword in relevance_keywords:
        if keyword in title_lower:
            return True

    for role in all_roles:
        if role.lower() in title_lower:
            return True

    if description:
        desc_lower = description.lower()
        product_signals = [
            "product roadmap", "product metrics", "user research",
            "product requirements", "prd", "product strategy",
            "a/b testing", "product analytics", "feature prioritization",
            "stakeholder management", "product lifecycle",
            "product discovery", "user stories", "sprint planning",
        ]
        signal_count = sum(1 for s in product_signals if s in desc_lower)
        if signal_count >= 3:
            return True

    return False


def is_experience_mismatch(exp_req, config=None):
    if not exp_req:
        return False

    exp_filter = get_experience_filter(config)
    reject_min = exp_filter.get("reject_min_years", 3)
    max_flexible = exp_filter.get("max_flexible_years", 2)

    exp_lower = exp_req.lower()

    if any(w in exp_lower for w in ["fresher", "entry level", "entry-level", "internship", "intern"]):
        return False

    for level in exp_filter.get("reject_levels", []):
        if level.lower() in exp_lower:
            return True

    range_match = re.search(r"(\d+)\s*[-–to]+\s*(\d+)", exp_lower)
    if range_match:
        min_years = int(range_match.group(1))
        if min_years >= reject_min:
            return True
        return False

    year_match = re.search(r"(\d+)\s*\+?\s*(?:years?|yrs?)", exp_lower)
    if year_match:
        years = int(year_match.group(1))
        if years >= reject_min:
            return True

    return False


def is_suspicious(job_data):
    text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('company', '')}".lower()

    for indicator in SUSPICIOUS_INDICATORS:
        if indicator in text:
            return True

    job_url = job_data.get("job_url", "")
    app_url = job_data.get("application_url", "")
    for domain in SUSPICIOUS_DOMAINS:
        if domain in job_url or domain in app_url:
            return True

    return False

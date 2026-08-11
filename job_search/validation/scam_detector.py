import re


SCAM_SIGNALS = {
    "payment_required": [
        "pay to apply", "registration fee", "processing fee",
        "security deposit", "refundable deposit", "training fee",
    ],
    "too_good_to_be_true": [
        "guaranteed job", "guaranteed placement", "100% placement",
        "earn \\d+ lakhs? from home", "easy money", "no experience needed earn",
    ],
    "mlm_network": [
        "network marketing", "multi-level", "mlm", "direct selling opportunity",
        "build your team", "recruit others", "downline",
    ],
    "vague_employer": [
        "company name confidential", "reputed company", "mnc company",
        "top company", "leading company hiring",
    ],
    "suspicious_contact": [
        "whatsapp only", "telegram only", "call this number",
        "send resume to whatsapp",
    ],
}

LEGITIMATE_ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "ashbyhq.com",
    "icims.com", "smartrecruiters.com", "jobvite.com",
    "taleo.net", "myworkdayjobs.com", "bamboohr.com",
    "recruitee.com", "breezy.hr", "jazz.co", "hire.lever.co",
    "boards.greenhouse.io", "jobs.lever.co", "jobs.ashbyhq.com",
    "linkedin.com/jobs", "careers.", "jobs.",
]


def detect_scam(job_data):
    result = {"is_scam": False, "confidence": 0, "signals": []}
    text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('company', '')}".lower()

    for category, patterns in SCAM_SIGNALS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                result["signals"].append(f"{category}: {pattern}")
                result["confidence"] += 20

    if result["confidence"] >= 40:
        result["is_scam"] = True

    return result


def is_legitimate_application_url(url):
    if not url:
        return False

    url_lower = url.lower()
    for domain in LEGITIMATE_ATS_DOMAINS:
        if domain in url_lower:
            return True

    if any(pattern in url_lower for pattern in ["careers", "jobs", "apply", "hiring"]):
        return True

    return False

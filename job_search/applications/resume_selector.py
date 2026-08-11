import re
from pathlib import Path

RESUME_DIR = Path(__file__).parent.parent.parent / "resumes"

RESUME_VARIANTS = {
    "apm": {
        "filename": "resume_apm.pdf",
        "roles": ["associate product manager", "apm", "product management intern",
                   "product manager", "ai product management intern"],
        "description": "APM / Product Management focused resume",
    },
    "product_analytics": {
        "filename": "resume_product_analytics.pdf",
        "roles": ["product analyst", "ai product analyst", "product strategy analyst",
                   "growth analyst"],
        "description": "Product Analytics focused resume",
    },
    "ai_product": {
        "filename": "resume_ai_product.pdf",
        "roles": ["ai product", "ai product manager", "ai product analyst",
                   "ai product management"],
        "description": "AI Product focused resume",
    },
    "business_analyst": {
        "filename": "resume_business_analyst.pdf",
        "roles": ["business analyst", "data analyst", "product operations",
                   "product operations analyst"],
        "description": "Business/Data Analyst focused resume",
    },
    "general": {
        "filename": "resume_general.pdf",
        "roles": [],
        "description": "General purpose resume",
    },
}


def select_resume(job_title, job_description=""):
    title_lower = job_title.lower()
    desc_lower = (job_description or "").lower()

    best_match = None
    best_score = 0

    for variant_key, variant in RESUME_VARIANTS.items():
        if variant_key == "general":
            continue

        score = 0
        for role_keyword in variant["roles"]:
            if role_keyword in title_lower:
                score += 10
            if role_keyword in desc_lower:
                score += 3

        if score > best_score:
            best_score = score
            best_match = variant_key

    if best_match is None:
        best_match = "general"

    variant = RESUME_VARIANTS[best_match]
    resume_path = RESUME_DIR / variant["filename"]

    return {
        "variant": best_match,
        "filename": variant["filename"],
        "path": str(resume_path),
        "exists": resume_path.exists(),
        "description": variant["description"],
    }


def list_available_resumes():
    available = []
    for key, variant in RESUME_VARIANTS.items():
        path = RESUME_DIR / variant["filename"]
        available.append({
            "variant": key,
            "filename": variant["filename"],
            "exists": path.exists(),
            "description": variant["description"],
        })
    return available

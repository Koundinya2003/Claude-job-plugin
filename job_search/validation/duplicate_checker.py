import re
from job_search.storage.database import get_connection


def is_duplicate(company, title, job_url=None):
    conn = get_connection()

    if job_url:
        row = conn.execute(
            "SELECT id FROM jobs WHERE job_url = ?", (job_url,)
        ).fetchone()
        if row:
            conn.close()
            return True

    norm_company = normalize_company(company)
    norm_title = normalize_title(title)

    rows = conn.execute(
        "SELECT company, title FROM jobs"
    ).fetchall()
    conn.close()

    for row in rows:
        if normalize_company(row["company"]) == norm_company and normalize_title(row["title"]) == norm_title:
            return True

    return False


def normalize_company(name):
    name = name.lower().strip()
    name = re.sub(r"\b(pvt\.?|ltd\.?|inc\.?|llc|corp\.?|limited|private|technologies|tech)\b", "", name)
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


def normalize_title(title):
    title = title.lower().strip()
    title = re.sub(r"\s*[-–(].*$", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()

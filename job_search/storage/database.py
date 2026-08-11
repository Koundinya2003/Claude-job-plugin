import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "job_applications.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            work_mode TEXT,
            experience_requirement TEXT,
            date_posted TEXT,
            date_discovered TEXT NOT NULL DEFAULT (datetime('now')),
            is_active INTEGER DEFAULT 1,
            job_url TEXT,
            application_url TEXT,
            job_source TEXT,
            recruiter_name TEXT,
            recruiter_email TEXT,
            recruiter_linkedin TEXT,
            company_legitimate INTEGER DEFAULT 1,
            description TEXT,
            requirements TEXT,
            relevance_score REAL DEFAULT 0,
            priority_label TEXT,
            status TEXT DEFAULT 'discovered',
            resume_version TEXT,
            cover_letter TEXT,
            date_applied TEXT,
            application_status TEXT DEFAULT 'not_applied',
            rejection_date TEXT,
            response_notes TEXT,
            notes TEXT,
            raw_data TEXT,
            UNIQUE(company, title, job_url)
        );

        CREATE TABLE IF NOT EXISTS search_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_date TEXT NOT NULL DEFAULT (datetime('now')),
            query TEXT,
            source TEXT,
            results_count INTEGER DEFAULT 0,
            qualified_count INTEGER DEFAULT 0,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS application_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            details TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        );

        CREATE INDEX IF NOT EXISTS idx_jobs_company_title ON jobs(company, title);
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(relevance_score);
        CREATE INDEX IF NOT EXISTS idx_jobs_date ON jobs(date_discovered);
    """)
    conn.commit()
    conn.close()


def insert_job(job_data):
    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO jobs (
                company, title, location, work_mode, experience_requirement,
                date_posted, job_url, application_url, job_source,
                recruiter_name, recruiter_email, recruiter_linkedin,
                company_legitimate, description, requirements,
                relevance_score, priority_label, status, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_data.get("company", ""),
            job_data.get("title", ""),
            job_data.get("location", ""),
            job_data.get("work_mode", ""),
            job_data.get("experience_requirement", ""),
            job_data.get("date_posted", ""),
            job_data.get("job_url", ""),
            job_data.get("application_url", ""),
            job_data.get("job_source", ""),
            job_data.get("recruiter_name", ""),
            job_data.get("recruiter_email", ""),
            job_data.get("recruiter_linkedin", ""),
            job_data.get("company_legitimate", 1),
            job_data.get("description", ""),
            job_data.get("requirements", ""),
            job_data.get("relevance_score", 0),
            job_data.get("priority_label", ""),
            job_data.get("status", "discovered"),
            json.dumps(job_data.get("raw_data", {})),
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def job_exists(company, title, job_url=None):
    conn = get_connection()
    if job_url:
        row = conn.execute(
            "SELECT id FROM jobs WHERE company = ? AND title = ? AND job_url = ?",
            (company, title, job_url)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM jobs WHERE company = ? AND title = ?",
            (company, title)
        ).fetchone()
    conn.close()
    return row is not None


def get_jobs_by_status(status):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM jobs WHERE status = ? ORDER BY relevance_score DESC",
        (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_jobs_by_score(min_score, max_score=100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM jobs WHERE relevance_score >= ? AND relevance_score <= ? ORDER BY relevance_score DESC",
        (min_score, max_score)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_high_priority_jobs(threshold=85):
    return get_jobs_by_score(threshold)


def get_good_match_jobs(low=70, high=84):
    return get_jobs_by_score(low, high)


def update_job_status(job_id, status, **kwargs):
    conn = get_connection()
    updates = ["status = ?"]
    values = [status]
    for key, value in kwargs.items():
        updates.append(f"{key} = ?")
        values.append(value)
    values.append(job_id)
    conn.execute(
        f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()


def log_application_action(job_id, action, details=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO application_log (job_id, action, details) VALUES (?, ?, ?)",
        (job_id, action, details)
    )
    conn.commit()
    conn.close()


def log_search(query, source, results_count, qualified_count, notes=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO search_log (query, source, results_count, qualified_count, notes) VALUES (?, ?, ?, ?, ?)",
        (query, source, results_count, qualified_count, notes)
    )
    conn.commit()
    conn.close()


def get_all_jobs():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM jobs ORDER BY relevance_score DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_todays_jobs():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT * FROM jobs WHERE date_discovered LIKE ? ORDER BY relevance_score DESC",
        (f"{today}%",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_applied_jobs():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM jobs WHERE application_status != 'not_applied' ORDER BY date_applied DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_job_count():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM jobs").fetchone()
    conn.close()
    return row["cnt"]

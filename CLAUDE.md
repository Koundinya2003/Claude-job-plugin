# Job Application Automation Plugin

## Overview
Quality-first job application automation for APM/Product roles in Bengaluru.

## Architecture
- `job_search/config/` - Candidate profile YAML and config loader
- `job_search/sources/` - Search query generators for web/LinkedIn/ATS
- `job_search/extraction/` - Job listing parser and recruiter info extractor
- `job_search/validation/` - Job validator, duplicate checker, scam detector
- `job_search/ranking/` - Relevance scorer (0-100 scale, 7 weighted dimensions)
- `job_search/applications/` - Resume selector, application manager, answer generator
- `job_search/outreach/` - Recruiter outreach message generator
- `job_search/storage/` - SQLite database for persistent application tracking
- `job_search/reporting/` - Daily report generator
- `job_search/pipeline.py` - Main orchestrator

## Key Commands
```bash
python plugin.py discover   # Generate search queries
python plugin.py report     # Daily job report
python plugin.py queue      # Application queue
python plugin.py stats      # Pipeline stats
```

## Scoring
Jobs scored 0-100: role relevance (30%), candidate fit (20%), experience fit (15%),
location fit (10%), company quality (10%), recency (10%), application quality (5%).
85+ = HIGH PRIORITY, 70-84 = GOOD MATCH, <70 = DO NOT APPLY.

## Modes
- **Discovery**: Search, validate, score, rank. No submissions.
- **Application**: Prepare and submit with human approval for sensitive fields.

## Database
SQLite at `data/job_applications.db`. Auto-initialized on first run.

## Dependencies
Python 3.11+, PyYAML

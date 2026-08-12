# Job Application Automation Plugin

Quality-first job discovery and application tracking for APM, Product Analyst and
AI Product roles. Runs as an MCP server inside Claude Desktop, or as a standalone CLI.

It finds jobs, throws out the ones that waste your time, scores what's left against
your actual profile, and keeps a permanent record so you never apply twice.

## What it does

- **Discovers** jobs via search queries tuned to your target roles and location
- **Validates** every listing: rejects engineering/sales/support roles, senior
  postings, scams, MLM schemes and listings with no working application route
- **Deduplicates** against everything you've already seen, including the same job
  reposted through a different source
- **Scores** 0-100 across seven weighted dimensions
- **Selects** the right resume variant for each role
- **Drafts** application answers and recruiter outreach — flagging anything that
  needs your judgement instead of guessing
- **Tracks** every application in SQLite with a full audit log

## Scoring

| Dimension | Weight |
|---|---|
| Role relevance | 30 |
| Candidate fit | 20 |
| Experience fit | 15 |
| Location fit | 10 |
| Company quality | 10 |
| Recency | 10 |
| Application quality | 5 |

**85+** HIGH PRIORITY · **70-84** GOOD MATCH · **below 70** DO NOT APPLY

## Install for Claude Desktop

**1. Unzip somewhere permanent.** The plugin stores your job database next to its
own files, so don't run it from Downloads or a temp folder.

**2. Install dependencies:**

```bash
cd /path/to/claude-job-plugin
pip install -r requirements.txt
```

**3. Add it to `claude_desktop_config.json`:**

- macOS — `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows — `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "job-search": {
      "command": "python3",
      "args": ["/absolute/path/to/claude-job-plugin/mcp_server.py"]
    }
  }
}
```

Use an absolute path, and `python` instead of `python3` on Windows.

**4. Restart Claude Desktop.** The job-search tools appear in the tools menu.

## Set up your profile

Edit `job_search/config/candidate_profile.yaml` — name, contact links, education,
experience, projects, target roles, locations, thresholds. Everything the scorer
and answer drafter uses lives in this one file; no code changes needed.

Then drop your resumes in `resumes/`:

```
resume_apm.pdf                 APM / Product Management
resume_product_analytics.pdf   Product Analytics
resume_ai_product.pdf          AI Product
resume_business_analyst.pdf    Business / Data Analyst
resume_general.pdf             Fallback
```

Start with the same file copied five times if you don't have tailored variants yet —
`list_resume_variants` will tell you which slots are filled.

## Using it

Once installed, ask Claude in plain language:

> Find today's best AI Product and APM jobs in Bengaluru

Claude calls `get_search_queries`, runs the searches, and passes results to
`submit_job_listings`, which validates and scores them.

> Show me my job report

> What's in my application queue?

> Draft a recruiter message for job 12

### Tools

| Tool | Purpose |
|---|---|
| `get_search_queries` | Generate discovery queries |
| `submit_job_listings` | Validate, dedupe, score and store found listings |
| `get_daily_report` | HIGH PRIORITY / GOOD MATCH / REJECTED report |
| `get_application_queue` | Qualified jobs not yet applied to |
| `get_stats` | Pipeline counts |
| `list_jobs` | Query stored jobs |
| `draft_answers` | Draft answers from your profile |
| `draft_recruiter_message` | Personalized outreach draft |
| `list_resume_variants` | Which resume files exist |
| `record_application` | Log a confirmed submission |

## CLI

The same pipeline without Claude Desktop:

```bash
python plugin.py discover   # generate search queries
python plugin.py report     # daily report
python plugin.py queue      # application queue
python plugin.py stats      # pipeline stats
python plugin.py outreach   # recruiter messages
python plugin.py resumes    # resume variants
```

## Two modes

**Discovery** (default) — searches, validates, scores, ranks. Never submits anything.

**Application** — prepares applications and fills non-sensitive fields, then stops.
Set `mode: application` in the config.

It always stops for legal declarations, compensation expectations, EEO and
demographic questions, work authorization, relocation commitments, anything binding,
and anything involving payment or financial details. Those come back to you.

## What it won't do

- Invent a recruiter, email, job ID, URL or company
- Fabricate experience, metrics or certifications you don't have
- Claim an application was submitted unless submission was confirmed
- Submit a duplicate application
- Bypass CAPTCHA, MFA or bot protection

If a site can't be reached, it's marked unavailable rather than reported as processed.

## Data

SQLite at `data/job_applications.db`, created on first run. Three tables: `jobs`,
`search_log`, `application_log`. Your database and resumes stay local and are
excluded from version control.

## Requirements

Python 3.11+ · PyYAML · MCP SDK 2.0+

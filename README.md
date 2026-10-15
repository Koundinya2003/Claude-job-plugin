<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/01_hero_dark.svg">
  <img src="docs/readme/01_hero_light.svg" width="100%" alt="Job Search, a Claude plugin and CLI for APM, Product Analyst and AI Product roles. Quality first job discovery: it finds jobs, throws out the ones that waste your time, scores what is left against your actual profile, and keeps a permanent record so you never apply twice. Facts: 7 weighted scoring dimensions, 3 Claude skills, 10 MCP tools, 1 SQLite database with a full audit log. Animated departures board with example rows whose status cells flip from checking to a verdict: Associate PM in Bengaluru, high priority; Product Analyst, remote, good match; AI Product Analyst, hybrid Bengaluru, high priority; Backend Engineer, rejected role; Pay to apply listing, scam, rejected; Senior Product Manager, experience too high, rejected.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/02_pipeline_dark.svg">
  <img src="docs/readme/02_pipeline_light.svg" width="100%" alt="How a listing travels. Eight stops: discover (search queries tuned to target roles and location, general, LinkedIn and ATS), extract (company, title, location, work mode, experience, dates, URLs), validate, deduplicate (against everything already seen, including the same job reposted through a different source), score (0 to 100), select resume (the right variant per role), draft (application answers and recruiter outreach, flagging what needs your judgement), track (SQLite with a full audit log). Validation throws out engineering roles, sales roles, support roles, senior postings, scams, MLM schemes, and listings with no working application route. The scam detector checks five signal families: payment required (registration or processing fee, deposits), too good to be true (guaranteed placement), MLM and network marketing, vague employer (company name confidential), and suspicious contact (WhatsApp or Telegram only). Each matched signal adds 20 to a confidence score and 40 or more flags the listing as a scam.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/03_scoring_dark.svg">
  <img src="docs/readme/03_scoring_light.svg" width="100%" alt="Scoring, 0 to 100 across seven weighted dimensions: role relevance 30, candidate fit 20, experience fit 15, location fit 10, company quality 10, recency 10, application quality 5. Verdicts: 85 and above is high priority, 70 to 84 is a good match, below 70 is do not apply. Role relevance carries the most weight because a perfect company with the wrong role is still the wrong job. Weights live in the candidate profile YAML, so they can be changed without code.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/04_inside_dark.svg">
  <img src="docs/readme/04_inside_light.svg" width="100%" alt="Inside Claude and on the command line. Three skills: /job-search:find-jobs discovers, validates and scores new openings; /job-search:job-report gives the report, queue and stats from stored jobs; /job-search:apply-jobs prepares applications and outreach drafts. Claude also invokes them on its own when you ask in plain language, for example: find today's best AI Product and APM jobs in Bengaluru. Ten MCP tools: get_search_queries, submit_job_listings, get_daily_report, get_application_queue, get_stats, list_jobs, draft_answers, draft_recruiter_message, list_resume_variants, record_application. The same pipeline runs without Claude Desktop through plugin.py with discover, report, queue, stats, outreach and resumes commands.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/05_guardrails_dark.svg">
  <img src="docs/readme/05_guardrails_light.svg" width="100%" alt="Guardrails. Two modes: discovery, the default, searches, validates, scores and ranks and never submits anything; application mode (set mode: application in the config) prepares applications and fills non sensitive fields, then stops. It always stops and hands back to you for legal declarations, compensation expectations, EEO and demographic questions, work authorization, relocation commitments, anything binding, and anything involving payment or financial details. It will not invent a recruiter, email, job ID, URL or company; fabricate experience, metrics or certifications; claim an application was submitted unless submission was confirmed; submit a duplicate application; or bypass CAPTCHA, MFA or bot protection. If a site cannot be reached it is marked unavailable rather than reported as processed.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/06_setup_dark.svg">
  <img src="docs/readme/06_setup_light.svg" width="100%" alt="Setup in three steps. 1, install the Python dependencies: pip install pyyaml and mcp 2.0 or newer. 2, load the plugin with claude --plugin-dir pointing at the folder or the zip. 3, run /plugin and look for job-search; the Errors tab reports a server that failed to start. Then edit job_search/config/candidate_profile.yaml with your name, links, education, experience, projects, target roles, locations and thresholds, and drop five resume variants in resumes/: resume_apm.pdf for APM and product management, resume_product_analytics.pdf for product analytics, resume_ai_product.pdf for AI product, resume_business_analyst.pdf for business and data analyst roles, resume_general.pdf as the fallback. The database job_applications.db has three tables (jobs, search_log, application_log) and stays local. Requires Python 3.11+, PyYAML and the MCP SDK 2.0+.">
</picture>

# Job Application Automation Plugin

Quality first job discovery and application tracking for APM, Product Analyst and AI Product roles. Runs as an MCP server inside Claude Desktop, or as a standalone CLI.

It finds jobs, throws out the ones that waste your time, scores what's left against your actual profile, and keeps a permanent record so you never apply twice.

## What it does

* **Discovers** jobs via search queries tuned to your target roles and location
* **Validates** every listing: rejects engineering, sales and support roles, senior postings, scams, MLM schemes and listings with no working application route
* **Deduplicates** against everything you've already seen, including the same job reposted through a different source
* **Scores** 0 to 100 across seven weighted dimensions
* **Selects** the right resume variant for each role
* **Drafts** application answers and recruiter outreach, flagging anything that needs your judgement instead of guessing
* **Tracks** every application in SQLite with a full audit log

## Scoring

<table>
  <tr><th>Dimension</th><th>Weight</th></tr>
  <tr><td>Role relevance</td><td>30</td></tr>
  <tr><td>Candidate fit</td><td>20</td></tr>
  <tr><td>Experience fit</td><td>15</td></tr>
  <tr><td>Location fit</td><td>10</td></tr>
  <tr><td>Company quality</td><td>10</td></tr>
  <tr><td>Recency</td><td>10</td></tr>
  <tr><td>Application quality</td><td>5</td></tr>
</table>

**85+** HIGH PRIORITY · **70 to 84** GOOD MATCH · **below 70** DO NOT APPLY

## Install

The package is a Claude plugin: a `.claude-plugin/plugin.json` manifest, three skills, and an MCP server wired up in `.mcp.json`.

**1. Install the Python dependencies.** The MCP server needs these on the `python3` that Claude will launch:

```bash
pip install pyyaml "mcp>=2.0.0"
```

**2. Load the plugin.** Point Claude at the zip or the unzipped directory:

```bash
claude --plugin-dir ./job-search
claude --plugin-dir ./job-search.zip
```

To keep it loaded across sessions without the flag, unzip it into your skills directory as `~/.claude/skills/job-search/`; it auto loads from there.

**3. Check it registered.** Run `/plugin` and look for `job-search`; the Errors tab reports a server that failed to start. A missing dependency shows up there.

Your database lives at `~/.claude-job-plugin/job_applications.db`, outside the plugin directory, so plugin updates never wipe your application history. Override with `JOB_PLUGIN_DATA_DIR` if you want it elsewhere.

### Skills

<table>
  <tr><th>Skill</th><th>Use</th></tr>
  <tr><td><code>/job-search:find-jobs</code></td><td>Discover, validate and score new openings</td></tr>
  <tr><td><code>/job-search:job-report</code></td><td>Report, queue and stats from stored jobs</td></tr>
  <tr><td><code>/job-search:apply-jobs</code></td><td>Prepare applications and outreach drafts</td></tr>
</table>

Claude also invokes these on its own when you ask in plain language.

## Set up your profile

Edit `job_search/config/candidate_profile.yaml`: name, contact links, education, experience, projects, target roles, locations, thresholds. Everything the scorer and answer drafter uses lives in this one file; no code changes needed.

Then drop your resumes in `resumes/`:

```
resume_apm.pdf                 APM / Product Management
resume_product_analytics.pdf   Product Analytics
resume_ai_product.pdf          AI Product
resume_business_analyst.pdf    Business / Data Analyst
resume_general.pdf             Fallback
```

Start with the same file copied five times if you don't have tailored variants yet; `list_resume_variants` will tell you which slots are filled. See [`resumes/README.md`](resumes/README.md) for which roles each variant covers.

## Using it

Once installed, ask Claude in plain language:

> Find today's best AI Product and APM jobs in Bengaluru

Claude calls `get_search_queries`, runs the searches, and passes results to `submit_job_listings`, which validates and scores them.

> Show me my job report

> What's in my application queue?

> Draft a recruiter message for job 12

### Tools

<table>
  <tr><th>Tool</th><th>Purpose</th></tr>
  <tr><td><code>get_search_queries</code></td><td>Generate discovery queries</td></tr>
  <tr><td><code>submit_job_listings</code></td><td>Validate, dedupe, score and store found listings</td></tr>
  <tr><td><code>get_daily_report</code></td><td>HIGH PRIORITY / GOOD MATCH / REJECTED report</td></tr>
  <tr><td><code>get_application_queue</code></td><td>Qualified jobs not yet applied to</td></tr>
  <tr><td><code>get_stats</code></td><td>Pipeline counts</td></tr>
  <tr><td><code>list_jobs</code></td><td>Query stored jobs</td></tr>
  <tr><td><code>draft_answers</code></td><td>Draft answers from your profile</td></tr>
  <tr><td><code>draft_recruiter_message</code></td><td>Personalized outreach draft</td></tr>
  <tr><td><code>list_resume_variants</code></td><td>Which resume files exist</td></tr>
  <tr><td><code>record_application</code></td><td>Log a confirmed submission</td></tr>
</table>

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

**Discovery** (default): searches, validates, scores, ranks. Never submits anything.

**Application**: prepares applications and fills non sensitive fields, then stops. Set `mode: application` in the config.

It always stops for legal declarations, compensation expectations, EEO and demographic questions, work authorization, relocation commitments, anything binding, and anything involving payment or financial details. Those come back to you.

## What it won't do

* Invent a recruiter, email, job ID, URL or company
* Fabricate experience, metrics or certifications you don't have
* Claim an application was submitted unless submission was confirmed
* Submit a duplicate application
* Bypass CAPTCHA, MFA or bot protection

If a site can't be reached, it's marked unavailable rather than reported as processed.

## Data

SQLite at `data/job_applications.db` when running from a source checkout that has a `data/` folder, otherwise at `~/.claude-job-plugin/job_applications.db` (or wherever `JOB_PLUGIN_DATA_DIR` points). Created on first run. Three tables: `jobs`, `search_log`, `application_log`. Your database and resumes stay local and are excluded from version control.

## Project layout

* `.claude-plugin/plugin.json`: plugin manifest
* `.mcp.json`: MCP server wiring (`mcp_server.py`)
* `skills/`: the `find-jobs`, `job-report` and `apply-jobs` skills
* `plugin.py`, `run_search.py`: CLI entry points
* `job_search/config/`: candidate profile YAML and config loader
* `job_search/sources/`: search query generators for web, LinkedIn and ATS
* `job_search/extraction/`: job listing parser and recruiter info extractor
* `job_search/validation/`: job validator, duplicate checker, scam detector
* `job_search/ranking/`: relevance scorer
* `job_search/applications/`: resume selector, application manager, answer generator
* `job_search/outreach/`: recruiter outreach message generator
* `job_search/storage/`: SQLite database for persistent application tracking
* `job_search/reporting/`: daily report generator
* `job_search/pipeline.py`: main orchestrator
* `docs/readme/`: the panels at the top of this page

## Requirements

Python 3.11+ · PyYAML · MCP SDK 2.0+

## Rebuilding the panels

The panels at the top are SVG images generated from one HTML page. Edit `docs/readme/one_sheet.html`, then run:

```bash
node docs/readme/build_readme_svgs.js docs/readme/one_sheet.html docs/readme 960
```

This needs Node with Playwright and curl (fonts are fetched from Google Fonts and embedded). It writes a light and a dark SVG for every panel.

## Author and license

Aditya K Koundinya. Declared as MIT in `.claude-plugin/plugin.json`. Repository: https://github.com/Koundinya2003/Claude-job-plugin

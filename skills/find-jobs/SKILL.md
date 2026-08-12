---
description: Discover, validate and score new job openings for the user's target roles. Use when they ask to find jobs, run a job search, check for new openings, or ask what's worth applying to today.
---

# Find jobs

Run a discovery pass and hand back a ranked, validated list. Quality over volume —
seven real matches beat thirty padded ones. Never pad the list to hit a number.

## Workflow

**1. Get the queries.** Call `get_search_queries`. It returns general, LinkedIn and
ATS query sets built from the user's configured roles and locations.

**2. Search.** Run the queries with WebSearch or Firecrawl. Prioritise, in order:
LinkedIn Jobs, official company career pages, and established ATS hosts —
Greenhouse, Lever, Workday, Ashby. Aggregators are fine for discovery, but trace
each hit back to the employer's own posting where you can.

If `$ARGUMENTS` names a role, company or location, narrow the search to it instead
of running the full sweep.

**3. Extract.** For each listing pull company, title, location, work mode,
experience requirement, date posted, job URL, application URL, source, and the
description. Include recruiter details only when the listing itself publishes them.

Omit any field you did not actually find. A guessed date or invented recruiter is
worse than a blank — blanks are handled, fabrications corrupt the database.

**4. Submit.** Pass everything to `submit_job_listings` in one call. It validates,
deduplicates, scores 0-100 and assigns a resume variant. Don't pre-filter: submit
borderline listings too and let the scorer decide.

**5. Report.** Call `get_daily_report` and present the results.

## Presenting results

Lead with HIGH PRIORITY (85+), then GOOD MATCH (70-84). For each: company, role,
location, score, why it fits, the application URL, and the recommended resume.

Summarise rejections in one or two lines by reason — irrelevant role, expired,
duplicate, scam, experience mismatch, location mismatch, poor application path.
Do not list them individually.

If a source was unreachable, say so plainly. Never present an unreachable listing
as processed.

## Rules

- A search result is not proof a job is still open
- Never invent a company, recruiter, email, job ID, date or URL
- Report the count you actually found, even when it's small

---
description: Show the current job report, application queue or pipeline stats from already-discovered jobs. Use when the user asks what's in their queue, what they should apply to, or how their search is going.
---

# Job report

Read out what's already in the database. This is a reporting skill — it does not
search. If the user wants new listings, use the find-jobs skill instead.

## Which tool

- **"what did you find" / "show my report"** → `get_daily_report`
- **"what should I apply to" / "my queue"** → `get_application_queue`
- **"how's it going" / counts** → `get_stats`
- **anything more specific** → `list_jobs` with `min_score` or `today_only`

## Presenting

Lead with the jobs worth acting on. For each: company, role, location, score,
application URL, recommended resume variant, and current status.

Call out anything in the queue flagged as needing human review, and say what the
flag is — those are blocked until the user answers.

If nothing qualifies, say so directly and offer to run a fresh search. Don't pad
the report with low scorers to make it look fuller.

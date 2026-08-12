---
description: Prepare applications for qualified jobs — select the resume, draft answers and outreach, and stop at anything needing human judgement. Use when the user asks to apply to jobs, prepare an application, or draft a recruiter message.
---

# Apply to jobs

Prepare applications for jobs that already qualify. Optimise for interview
probability, not application count.

## Workflow

**1. Pull the queue.** Call `get_application_queue` — qualified jobs not yet applied
to, each with its resume variant and any flags.

**2. Confirm the target.** If the user named specific jobs, use those. Otherwise show
the queue and ask which to prepare. Never start submitting through the whole queue
on your own initiative.

**3. Per job:**
- Re-read the posting against the user's profile and say whether it's genuinely
  worth applying to. Recommending a skip is a valid outcome.
- Confirm the resume variant from `list_resume_variants`. Flag a missing file.
- Call `draft_answers` for the application's questions.
- Write a cover letter only where it actually helps, tailored to that company,
  product and role. Never a generic one.

**4. Outreach.** Where the listing names a recruiter, call `draft_recruiter_message`.
Personalise every message — no identical sends across recruiters. Drafts go to the
user to send; never send on their behalf.

**5. Record.** After the user confirms a submission actually went through, call
`record_application` with `outcome: "applied"`. Never call it to mark intent — that
field is the audit trail.

## Stop and ask

Hand these back to the user rather than answering:

- Legal declarations, criminal or background questions
- Compensation expectations, current or expected CTC
- Demographic and EEO questions
- Work authorization, visa or relocation commitments
- Consent for unusual data processing, or anything legally binding
- Payment or financial details
- Anything requiring information the profile doesn't contain

`draft_answers` already flags these. Surface the flags, don't fill them in.

## Never

- Fabricate experience, metrics, employers, achievements, technologies or certifications
- Claim a submission happened without confirmation
- Submit a duplicate — the queue already excludes applied jobs; trust it
- Bypass CAPTCHA, MFA or bot protection, or work around site restrictions

Rewording real experience to match a posting's language is fine. Inventing it is not.

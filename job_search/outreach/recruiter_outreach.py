from job_search.config.loader import get_candidate_info


def generate_outreach_message(job_data, config=None):
    candidate = get_candidate_info(config)

    company = job_data.get("company", "the company")
    role = job_data.get("title", "the role")
    recruiter_name = job_data.get("recruiter_name", "")
    description = job_data.get("description", "").lower()

    greeting = f"Hi {recruiter_name}," if recruiter_name else "Hi,"

    name = candidate.get("name", "")
    education = candidate.get("education", {})
    experience = candidate.get("experience", [])
    fellowships = candidate.get("fellowships", [])
    projects = candidate.get("projects", [])

    proof_point = _select_proof_point(description, experience, fellowships, projects)

    message = f"""{greeting}

I'm {name}, a {education.get('degree', '')} {education.get('field', '')} graduate from {education.get('university', '')} ({education.get('graduation_year', '')}) and NextLeap Product Management Fellow. I'm writing to express my interest in the {role} position at {company}.

{proof_point}

I'd welcome the chance to discuss how my background aligns with what you're looking for.

Best regards,
{name}
{candidate.get('linkedin', '')}"""

    return {
        "message": message.strip(),
        "recruiter_name": recruiter_name,
        "recruiter_email": job_data.get("recruiter_email", ""),
        "recruiter_linkedin": job_data.get("recruiter_linkedin", ""),
        "company": company,
        "role": role,
    }


def _select_proof_point(description, experience, fellowships, projects):
    if any(w in description for w in ["ai product", "llm", "ai/ml", "machine learning", "artificial intelligence"]):
        for p in projects:
            if "ai" in p.get("name", "").lower() or "llm" in p.get("tagline", "").lower():
                highlights = p.get("highlights", [])
                return f"I built {p['name']} ({p.get('tagline', '')}), {highlights[0].lower() if highlights else 'an end-to-end AI product'}."

    if any(w in description for w in ["analytics", "data", "metrics", "kpi", "dashboard"]):
        if experience:
            latest = experience[0]
            return f"At {latest.get('company', '')}, I {latest.get('highlights', ['built data solutions'])[0].lower()}."

    if any(w in description for w in ["product roadmap", "product strategy", "prd", "user research"]):
        return "As a NextLeap PM Fellow, I've built product teardowns, growth PRDs, and shipped 5 AI products end-to-end with defined metrics and user research."

    if experience:
        latest = experience[0]
        highlights = latest.get("highlights", [])
        return f"At {latest.get('company', '')}, I {highlights[0].lower() if highlights else 'worked on product and data solutions'}."

    return "I've built and deployed 5 AI products spanning conversational commerce, voice-of-customer analysis, and financial planning, each with defined product metrics."

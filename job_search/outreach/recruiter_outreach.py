from job_search.config.loader import get_candidate_info


def generate_outreach_message(job_data, config=None):
    candidate = get_candidate_info(config)

    company = job_data.get("company", "the company")
    role = job_data.get("title", "the role")
    recruiter_name = job_data.get("recruiter_name", "")

    greeting = f"Hi {recruiter_name}," if recruiter_name else "Hi,"

    name = candidate.get("name", "")
    education = candidate.get("education", {})
    experience = candidate.get("experience", [])
    fellowships = candidate.get("fellowships", [])

    proof_point = ""
    if experience:
        latest = experience[0]
        proof_point = f"I recently completed a {latest.get('role', '')} role at {latest.get('company', '')}, where I worked on {latest.get('department', 'product and analytics initiatives')}."
    if fellowships:
        latest_fellowship = fellowships[0]
        if proof_point:
            proof_point += f" I'm also a {latest_fellowship.get('name', '')} fellow."
        else:
            proof_point = f"I'm a {latest_fellowship.get('name', '')} fellow with a strong interest in product management."

    message = f"""{greeting}

I'm {name}, a {education.get('degree', '')} {education.get('field', '')} graduate from {education.get('university', '')} ({education.get('graduation_year', '')}). I'm writing to express my interest in the {role} position at {company}.

{proof_point}

I'd love the opportunity to discuss how my background in product analytics, data analysis, and AI products aligns with what you're looking for. Would you be open to a brief conversation?

Best regards,
{name}"""

    return {
        "message": message.strip(),
        "recruiter_name": recruiter_name,
        "recruiter_email": job_data.get("recruiter_email", ""),
        "recruiter_linkedin": job_data.get("recruiter_linkedin", ""),
        "company": company,
        "role": role,
    }

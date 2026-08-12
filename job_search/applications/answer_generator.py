from job_search.config.loader import get_candidate_info


def generate_cover_letter_context(job_data, config=None):
    candidate = get_candidate_info(config)

    context = {
        "candidate_name": candidate.get("name", ""),
        "candidate_positioning": candidate.get("positioning", ""),
        "candidate_education": candidate.get("education", {}),
        "candidate_experience": candidate.get("experience", []),
        "candidate_fellowships": candidate.get("fellowships", []),
        "candidate_skills": candidate.get("skills", {}),
        "candidate_projects": candidate.get("projects", []),
        "candidate_certifications": candidate.get("certifications", []),
        "company": job_data.get("company", ""),
        "role": job_data.get("title", ""),
        "job_description": job_data.get("description", ""),
        "requirements": job_data.get("requirements", ""),
        "location": job_data.get("location", ""),
    }

    return context


def draft_application_answers(questions, config=None):
    candidate = get_candidate_info(config)
    answers = []

    for question in questions:
        q_lower = question.lower()
        answer = {
            "question": question,
            "answer": "",
            "needs_human_review": False,
            "reason": "",
        }

        if any(w in q_lower for w in ["name", "full name"]):
            answer["answer"] = candidate.get("name", "")

        elif any(w in q_lower for w in ["email", "e-mail"]):
            answer["answer"] = candidate.get("email", "")

        elif any(w in q_lower for w in ["phone", "mobile", "contact number"]):
            answer["answer"] = candidate.get("phone", "")

        elif "linkedin" in q_lower:
            answer["answer"] = candidate.get("linkedin", "")

        elif "github" in q_lower:
            answer["answer"] = candidate.get("github", "")

        elif any(w in q_lower for w in ["portfolio", "website", "personal site"]):
            answer["answer"] = candidate.get("portfolio", "")

        elif any(w in q_lower for w in ["university", "college", "education", "degree"]):
            edu = candidate.get("education", {})
            answer["answer"] = f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('university', '')}, {edu.get('graduation_year', '')} (GPA: {edu.get('gpa', '')})"

        elif any(w in q_lower for w in ["experience", "years of experience", "work experience"]):
            exp = candidate.get("experience", [])
            if exp:
                latest = exp[0]
                answer["answer"] = f"{latest.get('role', '')} at {latest.get('company', '')} ({latest.get('start_date', '')} - {latest.get('end_date', '')}). {latest.get('description', '')}"
            else:
                answer["answer"] = "Fresher / Recent Graduate"

        elif any(w in q_lower for w in ["project", "portfolio project", "relevant project"]):
            projects = candidate.get("projects", [])
            if projects:
                top = projects[:2]
                parts = []
                for p in top:
                    highlights = "; ".join(p.get("highlights", [])[:2])
                    parts.append(f"{p.get('name', '')}: {p.get('tagline', '')} ({p.get('tech', '')}). {highlights}")
                answer["answer"] = " | ".join(parts)

        elif any(w in q_lower for w in ["skill", "technical skill", "tools"]):
            skills = candidate.get("skills", {})
            if isinstance(skills, dict):
                all_skills = []
                for category, skill_list in skills.items():
                    all_skills.extend(skill_list[:3])
                answer["answer"] = ", ".join(all_skills)
            elif isinstance(skills, list):
                answer["answer"] = ", ".join(skills[:10])

        elif any(w in q_lower for w in ["location", "city", "where are you based"]):
            answer["answer"] = candidate.get("location", "Bengaluru, India")

        elif any(w in q_lower for w in ["notice period", "when can you join", "availability", "start date"]):
            answer["answer"] = "Immediately available"

        elif any(w in q_lower for w in ["why this role", "why interested", "motivation", "why do you want"]):
            answer["needs_human_review"] = True
            answer["reason"] = "Motivation question requires personalized response"

        elif any(w in q_lower for w in [
            "salary", "compensation", "ctc", "expected ctc",
            "visa", "work authorization", "criminal", "disability",
            "gender", "race", "veteran", "relocat",
            "legal", "consent", "payment", "bank account",
            "aadhaar", "pan card", "ssn",
        ]):
            answer["needs_human_review"] = True
            answer["reason"] = "Sensitive/legal question requiring human input"

        else:
            answer["needs_human_review"] = True
            answer["reason"] = "Question requires manual review"

        answers.append(answer)

    return answers

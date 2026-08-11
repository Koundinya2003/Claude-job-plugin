from job_search.config.loader import get_candidate_info


def generate_cover_letter_context(job_data, config=None):
    candidate = get_candidate_info(config)

    context = {
        "candidate_name": candidate.get("name", ""),
        "candidate_positioning": candidate.get("positioning", ""),
        "candidate_education": candidate.get("education", {}),
        "candidate_experience": candidate.get("experience", []),
        "candidate_fellowships": candidate.get("fellowships", []),
        "candidate_skills": candidate.get("skills", []),
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
            phone = candidate.get("phone", "")
            if phone:
                answer["answer"] = phone
            else:
                answer["needs_human_review"] = True
                answer["reason"] = "Phone number not in profile"

        elif any(w in q_lower for w in ["linkedin", "portfolio", "website", "github"]):
            answer["answer"] = candidate.get("linkedin", "") or candidate.get("portfolio", "")
            if not answer["answer"]:
                answer["needs_human_review"] = True
                answer["reason"] = "Profile URL not configured"

        elif any(w in q_lower for w in ["university", "college", "education", "degree"]):
            edu = candidate.get("education", {})
            answer["answer"] = f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('university', '')}, {edu.get('graduation_year', '')}"

        elif any(w in q_lower for w in ["experience", "years of experience", "work experience"]):
            exp = candidate.get("experience", [])
            if exp:
                latest = exp[0]
                answer["answer"] = f"{latest.get('role', '')} at {latest.get('company', '')} ({latest.get('start_date', '')} - {latest.get('end_date', '')})"
            else:
                answer["answer"] = "Fresher / Recent Graduate"

        elif any(w in q_lower for w in ["why this role", "why interested", "motivation", "why do you want"]):
            answer["needs_human_review"] = True
            answer["reason"] = "Motivation question requires personalized response"

        elif any(w in q_lower for w in [
            "salary", "compensation", "ctc", "expected ctc", "notice period",
            "visa", "work authorization", "criminal", "disability",
            "gender", "race", "veteran", "relocat",
        ]):
            answer["needs_human_review"] = True
            answer["reason"] = "Sensitive/legal question requiring human input"

        else:
            answer["needs_human_review"] = True
            answer["reason"] = "Question requires manual review"

        answers.append(answer)

    return answers

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from backend.models.schemas import ExtractedJob

load_dotenv()

logger = logging.getLogger(__name__)

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
PRIMARY_MODEL = "nvidia/nemotron-4-340b-instruct"


def get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        # Fast timeout to prevent application lag or hanging
        return OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key, timeout=3.0)
    except Exception as e:
        logger.error(f"Failed to instantiate OpenAI client for Nemotron: {e}")
        return None


def sanitize_email_body(body: str) -> str:
    """Strips any redundant Subject: header line from the message body."""
    if not body:
        return ""
    # Strip leading 'Subject: ...' or 'Subject Line: ...'
    cleaned = re.sub(r'(?i)^\s*Subject(?:\s*Line)?\s*[:\-].*?\n+', '', body.strip())
    return cleaned.strip()


def generate_email_content(job: ExtractedJob, candidate_profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates a personalized application email body and subject.
    Fast fallback to deterministic template generator if API fails or times out.
    """
    cand_name = candidate_profile.get("name", "Yash Nagapure")
    exp = job.experience or "Fresher"

    # Clean up company & role names
    job.company_name = re.sub(r'(?i)^(?:Company|🏢)\s*[:\-]*\s*', '', job.company_name or '').strip()
    job.role = re.sub(r'(?i)^(?:Role|Position|👤)\s*[:\-]*\s*', '', job.role or '').strip()

    if not job.company_name:
        job.company_name = "your company"
    if not job.role:
        job.role = "Software Developer"

    if job.explicit_subject and job.explicit_subject.strip():
        subject = job.explicit_subject.strip()
    else:
        subject = f"Application for {job.role} – {exp} | {cand_name}"

    client = get_openai_client()
    if not client:
        email_body = generate_template_email(job, candidate_profile)
        return {"subject": subject, "body": sanitize_email_body(email_body)}

    try:
        degree = candidate_profile.get("degree", "B.Tech Computer Science Engineering")
        college = candidate_profile.get("college", "AISSMS IOIT, Pune")
        grad_year = candidate_profile.get("graduation_year", "2027")
        cand_email = candidate_profile.get("email", "yashnagapure25@gmail.com")
        skills = candidate_profile.get("skills", [])
        projects = candidate_profile.get("projects", [])

        linkedin = candidate_profile.get("linkedin_url", "https://linkedin.com/in/yashnagapure")
        github = candidate_profile.get("github_url", "https://github.com/yashnagapure")
        portfolio = candidate_profile.get("portfolio_url", "https://yashnagapure.dev")

        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        projects_str = ", ".join(projects) if isinstance(projects, list) else str(projects)

        system_prompt = (
            "You are generating a highly tailored, professional job application email for a real candidate.\n"
            "CRITICAL RULES:\n"
            "1. Match the job description requirements against the candidate's actual skills. Mention ONLY skills the candidate possesses.\n"
            "2. Do NOT include any 'Subject:' line inside the body text. Start directly with 'Dear Hiring Team,' or 'Dear Hiring Manager,'.\n"
            "3. Ensure the role and company name are clean. NEVER include emojis, promotional headers ('FREE JOB ALERT'), or messy text in the email.\n"
            "4. Keep the email professional, natural, concise, and suitable for a fresher/graduating student.\n"
            "5. Format the bottom signature EXACTLY as follows:\n"
            "Best regards,\n"
            f"{cand_name}\n"
            f"{degree}\n"
            f"{college}\n"
            f"LinkedIn: {linkedin}\n"
            f"GitHub: {github}\n"
            f"Portfolio: {portfolio}\n\n"
            "Return ONLY the plain text email body."
        )

        user_prompt = f"""Candidate Profile:
- Name: {cand_name}
- Email: {cand_email}
- Qualification: {degree} at {college} ({grad_year} Batch)
- Actual Possessed Skills: {skills_str}
- Projects: {projects_str}

Job Details:
- Company Name: {job.company_name}
- Target Role: {job.role}
- Description: {job.job_description}

Generate the clean application email body:"""

        completion = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        full_content = completion.choices[0].message.content
        if full_content and full_content.strip():
            clean_body = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()
            return {"subject": subject, "body": sanitize_email_body(clean_body)}

    except Exception as e:
        logger.warning(f"Fast Nemotron call fallback to template engine: {e}")

    email_body = generate_template_email(job, candidate_profile)
    return {"subject": subject, "body": sanitize_email_body(email_body)}


def generate_template_email(job: ExtractedJob, candidate_profile: Dict[str, Any]) -> str:
    cand_name = candidate_profile.get("name", "Yash Nagapure")
    degree = candidate_profile.get("degree", "B.Tech Computer Science Engineering")
    college = candidate_profile.get("college", "AISSMS IOIT, Pune")
    grad_year = candidate_profile.get("graduation_year", "2027")

    linkedin = candidate_profile.get("linkedin_url", "https://linkedin.com/in/yashnagapure")
    github = candidate_profile.get("github_url", "https://github.com/yashnagapure")
    portfolio = candidate_profile.get("portfolio_url", "https://yashnagapure.dev")

    company = job.company_name or "your company"
    role = job.role or "Software Developer"
    exp = job.experience or "Fresher"

    # Match ONLY relevant skills candidate actually possesses
    cand_skills = candidate_profile.get("skills", [])
    matched_skills = []
    if isinstance(cand_skills, list):
        job_desc_lower = ((job.job_description or "") + " " + (job.skills or "")).lower()
        for s in cand_skills:
            if s.lower() in job_desc_lower:
                matched_skills.append(s)

    if not matched_skills and isinstance(cand_skills, list):
        matched_skills = cand_skills[:5]

    matched_skills_str = ", ".join(matched_skills[:6]) if matched_skills else "Python, SQL, JavaScript"

    if "analyst" in role.lower() or "data" in role.lower():
        project_mention = "I have hands-on experience in data analysis, SQL database queries, data reporting, and Python scripting, along with building projects like DocuForge AI."
        interest_mention = "I am particularly interested in data analysis and reporting because I enjoy extracting actionable insights from data to solve business problems."
    elif "ai" in role.lower() or "automation" in role.lower() or "ml" in role.lower():
        project_mention = "I have hands-on experience building DocuForge AI, an AI-powered document generation platform, alongside Face Recognition Attendance System."
        interest_mention = "I am particularly interested in AI automation because I enjoy combining software development, APIs, and AI to automate repetitive processes."
    elif "backend" in role.lower() or "node" in role.lower() or "python" in role.lower():
        project_mention = "I have developed full-stack and backend projects such as Hotel Mitraya and Travel-Friend utilizing Node.js, Express.js, REST APIs, and databases."
        interest_mention = "I am passionate about backend engineering, REST API integration, and clean data architectures."
    else:
        project_mention = "I have hands-on experience building web and software applications including DocuForge AI and Travel-Friend."
        interest_mention = "I am passionate about software engineering and eager to contribute to real-world development initiatives."

    signature_lines = [
        "Best regards,",
        cand_name,
        f"{degree}",
        f"{college}",
    ]
    if linkedin: signature_lines.append(f"LinkedIn: {linkedin}")
    if github: signature_lines.append(f"GitHub: {github}")
    if portfolio: signature_lines.append(f"Portfolio: {portfolio}")
    signature_block = "\n".join(signature_lines)

    email_body = f"""Dear Hiring Team,

I am writing to apply for the {role} position at {company}.

I am a final-year {degree} student at {college}, graduating in {grad_year}. I have a strong technical foundation in software development and practical experience in {matched_skills_str}.

{project_mention}

{interest_mention} As a {exp.lower() if exp and exp != 'Fresher' else 'fresher'}, I bring a strong problem-solving mindset, technical dedication, and a fast-learning approach.

Please find my resume attached for your consideration. I would appreciate the opportunity to contribute to your team at {company}.

Thank you for your time and consideration.

{signature_block}"""

    return sanitize_email_body(email_body)


def extract_job_with_nemotron(text_chunk: str) -> List[ExtractedJob]:
    client = get_openai_client()
    if not client:
        return []

    try:
        prompt = f"""Extract clean structured job details from text:
"{text_chunk}"

Return ONLY a JSON array of objects with keys: "company_name", "role", "experience", "recipient_email", "explicit_subject", "skills", "location"."""

        completion = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        content = completion.choices[0].message.content
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            items = json.loads(json_match.group(0))
            extracted = []
            for item in items:
                extracted.append(ExtractedJob(
                    company_name=item.get("company_name", "Company"),
                    role=item.get("role", "Software Developer"),
                    experience=item.get("experience", "Fresher"),
                    recipient_email=item.get("recipient_email"),
                    job_description=text_chunk,
                    explicit_subject=item.get("explicit_subject"),
                    skills=item.get("skills", ""),
                    location=item.get("location", ""),
                    source_text=text_chunk
                ))
            return extracted
    except Exception as e:
        logger.warning(f"Error extracting with Nemotron: {e}")

    return []

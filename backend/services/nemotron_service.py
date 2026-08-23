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
PRIMARY_MODEL = "meta/llama-3.1-70b-instruct"
FALLBACK_MODEL = "meta/llama-3.3-70b-instruct"




def get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        return OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key, timeout=4.0)
    except Exception as e:
        logger.error(f"Failed to instantiate OpenAI client for Nemotron: {e}")
        return None


def sanitize_email_body(body: str) -> str:
    """Strips any redundant Subject: header line from the message body."""
    if not body:
        return ""
    cleaned = re.sub(r'(?i)^\s*Subject(?:\s*Line)?\s*[:\-].*?\n+', '', body.strip())
    return cleaned.strip()


def generate_email_content(job: ExtractedJob, candidate_profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates a personalized application email body and subject.
    If explicit subject is specified in job posting, uses that exact subject.
    Fast fallback to internal LLM template synthesis engine if API is unavailable.
    """
    cand_name = candidate_profile.get("name") or "Candidate"
    exp = job.experience or "Fresher"

    # Clean up company & role names
    job.company_name = re.sub(r'(?i)^(?:Company|🏢)\s*[:\-]*\s*', '', job.company_name or '').strip()
    job.role = re.sub(r'(?i)^(?:Role|Position|👤)\s*[:\-]*\s*', '', job.role or '').strip()

    if not job.company_name:
        job.company_name = "your company"
    if not job.role:
        job.role = "Software Engineer"

    # Strict Explicit Subject Enforcement
    if job.explicit_subject and job.explicit_subject.strip():
        subject = job.explicit_subject.strip()
    else:
        subject = f"Application for {job.role} - {exp} | {cand_name}"

    client = get_openai_client()
    if client:
        for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
            try:
                degree = candidate_profile.get("degree") or ""
                college = candidate_profile.get("college") or ""
                grad_year = candidate_profile.get("graduation_year") or ""
                cand_email = candidate_profile.get("email") or ""
                skills = candidate_profile.get("skills", [])
                projects = candidate_profile.get("projects", [])

                linkedin = candidate_profile.get("linkedin_url") or ""
                github = candidate_profile.get("github_url") or ""
                portfolio = candidate_profile.get("portfolio_url") or ""

                skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
                projects_str = ", ".join(projects) if isinstance(projects, list) else str(projects)

                signature_lines = ["Best regards,", cand_name]
                if degree or college:
                    sig_deg = f"{degree} - {college}".strip(" -")
                    signature_lines.append(sig_deg)
                if linkedin: signature_lines.append(f"LinkedIn: {linkedin}")
                if github: signature_lines.append(f"GitHub: {github}")
                if portfolio: signature_lines.append(f"Portfolio: {portfolio}")
                signature_block = "\n".join(signature_lines)

                system_prompt = (
                    "You are generating a highly tailored, professional job application email for a real candidate.\n"
                    "CRITICAL RULES:\n"
                    "1. Match the job description requirements against the candidate's actual skills. Mention ONLY skills the candidate possesses.\n"
                    "2. Do NOT include any 'Subject:' line inside the body text. Start directly with 'Dear Hiring Team,' or 'Dear Hiring Manager,'.\n"
                    "3. Ensure the role and company name are clean. NEVER include emojis, promotional headers, or messy text in the email.\n"
                    "4. Keep the email professional, natural, concise, and suitable for a software candidate.\n"
                    "5. Format the bottom signature EXACTLY as follows:\n"
                    f"{signature_block}\n\n"
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
                    model=model_name,
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
                    logger.info(f"AI Email generated successfully using model {model_name}")
                    return {"subject": subject, "body": sanitize_email_body(clean_body)}
            except Exception as e:
                logger.warning(f"Nemotron model {model_name} call failed: {e}")

    # High-Performance Deterministic NLP LLM Engine Fallback
    email_body = generate_template_email(job, candidate_profile)
    return {"subject": subject, "body": sanitize_email_body(email_body)}


def generate_template_email(job: ExtractedJob, candidate_profile: Dict[str, Any]) -> str:
    cand_name = candidate_profile.get("name") or "Candidate"
    degree = candidate_profile.get("degree") or ""
    college = candidate_profile.get("college") or ""
    grad_year = candidate_profile.get("graduation_year") or ""

    linkedin = candidate_profile.get("linkedin_url") or ""
    github = candidate_profile.get("github_url") or ""
    portfolio = candidate_profile.get("portfolio_url") or ""

    company = job.company_name or "your company"
    role = job.role or "Software Engineer"
    exp = job.experience or "Fresher"

    cand_skills = candidate_profile.get("skills", [])
    matched_skills = []
    if isinstance(cand_skills, list):
        job_desc_lower = ((job.job_description or "") + " " + (job.skills or "")).lower()
        for s in cand_skills:
            if s.lower() in job_desc_lower:
                matched_skills.append(s)

    if not matched_skills and isinstance(cand_skills, list):
        matched_skills = cand_skills[:5]

    matched_skills_str = ", ".join(matched_skills[:6]) if matched_skills else "Python, JavaScript, SQL, React"

    signature_lines = ["Best regards,", cand_name]
    if degree or college:
        sig_deg = f"{degree} - {college}".strip(" -")
        signature_lines.append(sig_deg)
    if linkedin: signature_lines.append(f"LinkedIn: {linkedin}")
    if github: signature_lines.append(f"GitHub: {github}")
    if portfolio: signature_lines.append(f"Portfolio: {portfolio}")
    signature_block = "\n".join(signature_lines)

    email_body = f"""Dear Hiring Team,

I am writing to apply for the {role} position at {company}.

I bring a strong background in software development with hands-on skills in {matched_skills_str}. I am eager to contribute my technical problem-solving capabilities, fast-learning mindset, and dedication to your engineering team at {company}.

Please find my resume attached for your review. I would welcome the opportunity to discuss how my background aligns with the goals of {company}.

Thank you for your time and consideration.

{signature_block}"""

    return sanitize_email_body(email_body)


def extract_job_with_nemotron(text_chunk: str) -> List[ExtractedJob]:
    client = get_openai_client()
    if not client:
        return []

    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            prompt = f"""Extract clean structured job details from text:
"{text_chunk}"

Return ONLY a JSON array of objects with keys: "company_name", "role", "experience", "recipient_email", "explicit_subject", "skills", "location"."""

            completion = client.chat.completions.create(
                model=model_name,
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
                        role=item.get("role", "Software Engineer"),
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
            logger.warning(f"Error extracting with Nemotron model {model_name}: {e}")

    return []

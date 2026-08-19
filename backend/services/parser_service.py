import re
import logging
from typing import List, Dict, Any
from backend.models.schemas import ExtractedJob

logger = logging.getLogger(__name__)

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
EMOJI_REGEX = r'[\U00010000-\U0010ffff\u2600-\u27ff\u2300-\u23ff\u2000-\u206f\u2b00-\u2bff\u2934\u2935\u25b6\u25c0\u2200-\u22ff]'

def clean_text_noise(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(EMOJI_REGEX, ' ', text)
    cleaned = re.sub(r'[\u200b-\u200d\ufeff]', '', cleaned)
    return cleaned.strip()


def parse_job_text(text: str, fallback_to_llm: bool = True) -> List[ExtractedJob]:
    """
    Parses raw text (single or multi-job text with up to 10+ jobs) into clean ExtractedJob objects.
    """
    if not text or not text.strip():
        return []

    raw_text = text.strip()
    blocks = split_into_job_blocks(raw_text)

    parsed_jobs: List[ExtractedJob] = []

    for block in blocks:
        if not block.strip():
            continue
        
        job = extract_single_job_deterministic(block)
        
        # If email missing or company/role missing, try LLM fallback if enabled
        is_clean = (
            job.company_name and job.company_name != "Unknown Company" and len(job.company_name) < 80 and
            job.role and job.role != "Job Applicant" and len(job.role) < 80 and
            job.recipient_email
        )
        
        if not is_clean and fallback_to_llm:
            try:
                from backend.services.nemotron_service import extract_job_with_nemotron
                llm_jobs = extract_job_with_nemotron(block)
                if llm_jobs:
                    for lj in llm_jobs:
                        lj.company_name = sanitize_field(lj.company_name)
                        lj.role = sanitize_field(lj.role)
                    parsed_jobs.extend(llm_jobs)
                    continue
            except Exception as e:
                logger.warning(f"Nemotron extraction fallback failed: {e}")

        job.company_name = sanitize_field(job.company_name)
        job.role = sanitize_field(job.role)
        parsed_jobs.append(job)

    # Deduplicate by email & company
    final_jobs = []
    seen = set()
    for j in parsed_jobs:
        key = (j.company_name.lower().strip(), j.role.lower().strip(), (j.recipient_email or "").lower().strip())
        if key not in seen:
            seen.add(key)
            final_jobs.append(j)

    return final_jobs


def split_into_job_blocks(text: str) -> List[str]:
    """
    Splits multi-job text into individual job blocks.
    Identifies delimiters like '🏢 Company:', 'Company:', or email clusters.
    """
    # 1. Split on 'Company:' or '🏢 Company:' occurrences
    company_splits = re.split(r'(?=(?:^|\n|\s)\s*(?:🏢\s*)?Company\s*[:\-])', text, flags=re.IGNORECASE)
    cleaned_splits = [s.strip() for s in company_splits if s.strip() and re.search(EMAIL_REGEX, s)]
    
    if len(cleaned_splits) > 1:
        return cleaned_splits

    # 2. Split on 'FREE JOB ALERT' or 'FREE REFERRAL ALERT' or 'FREE HIRING ALERT'
    alert_splits = re.split(r'(?=(?:🚨|🎉|\s)*(?:FREE JOB ALERT|FREE REFERRAL ALERT|FREE HIRING ALERT))', text, flags=re.IGNORECASE)
    cleaned_alert_splits = [s.strip() for s in alert_splits if s.strip() and re.search(EMAIL_REGEX, s)]
    if len(cleaned_alert_splits) > 1:
        return cleaned_alert_splits

    # 3. Fallback: split on multiple emails with surrounding paragraphs
    emails = list(re.finditer(EMAIL_REGEX, text))
    if len(emails) > 1:
        paragraphs = re.split(r'\n\s*\n+', text)
        if len(paragraphs) > 1:
            blocks = []
            current_block = []
            for para in paragraphs:
                current_block.append(para)
                if re.search(EMAIL_REGEX, para):
                    blocks.append("\n\n".join(current_block))
                    current_block = []
            if current_block:
                if blocks:
                    blocks[-1] += "\n\n" + "\n\n".join(current_block)
                else:
                    blocks.append("\n\n".join(current_block))
            return [b for b in blocks if re.search(EMAIL_REGEX, b)]

    return [text]


def sanitize_field(val: str) -> str:
    """Sanitizes extracted company or role fields from leftover emojis, prefixes, or tags."""
    if not val:
        return ""
    val = clean_text_noise(val)
    val = re.sub(r'(?i)^(?:Company|Role|Position|Job Title|Title|Looking for|Hiring for|🏢|👤|📍|🎓|💰|⚙️|📩)\s*[:\-]*\s*', '', val)
    val = re.sub(r'\s+', ' ', val).strip()
    return val if val else "Software Developer"


def extract_single_job_deterministic(block: str) -> ExtractedJob:
    clean_block = clean_text_noise(block)

    company = ""
    role = ""
    experience = "Fresher"
    email = None
    explicit_subject = None
    skills = ""
    location = ""

    # Extract Recipient Email
    email_match = re.search(EMAIL_REGEX, block)
    if email_match:
        email = email_match.group(0)

    # 1. Company Name Regex (handles '🏢 Company: HaystackAnalytics' or 'Company: Rectitude Consulting Services')
    m_comp = re.search(r'(?i)(?:🏢\s*)?Company\s*[:\-]\s*([A-Za-z0-9\s&\.\-\(\)]+?)(?=\s*(?:👤|Role|Position|Location|📍|🎓|Batch|💰|Stipend|Salary|⚙️|Skills|📩|Email|Send|$|\n))', block)
    if m_comp:
        company = m_comp.group(1).strip()

    # 2. Role Name Regex (handles '👤 Role: Data Analyst Intern' or 'Role: Frontend Angular Intern')
    m_role = re.search(r'(?i)(?:👤\s*)?Role\s*[:\-]\s*([A-Za-z0-9\s&/\.\-\(\)]+?)(?=\s*(?:📍|Location|🎓|Batch|💰|Stipend|Salary|⏳|Duration|🏆|PPO|⚙️|Skills|📩|Email|Send|$|\n))', block)
    if m_role:
        role = m_role.group(1).strip()

    # 3. Location Regex
    m_loc = re.search(r'(?i)(?:📍\s*)?Location\s*[:\-]\s*([A-Za-z0-9\s,\.\-/]+?)(?=\s*(?:🎓|Batch|💰|Stipend|Salary|⏳|Duration|⚙️|Skills|📩|Email|Send|$|\n))', block)
    if m_loc:
        location = m_loc.group(1).strip()

    # 4. Experience / Batch
    m_exp = re.search(r'(?i)(?:🎓\s*)?(?:Batch|Experience|Exp Req|Eligibility)\s*[:\-]\s*([A-Za-z0-9\s/–\.\-&]+?)(?=\s*(?:💰|Stipend|Salary|⏳|Duration|⚙️|Skills|📩|Email|Send|$|\n))', block)
    if m_exp:
        experience = m_exp.group(1).strip()

    # 5. Skills
    m_skills = re.search(r'(?i)(?:⚙️\s*)?(?:Skills|Tech Stack)\s*[:\-]\s*([A-Za-z0-9\s,•/\.\-&]+?)(?=\s*(?:📩|Email|Send your resume|$|\n))', block, re.DOTALL)
    if m_skills:
        raw_skills = m_skills.group(1).strip()
        skills = ", ".join([s.strip('• ').strip() for s in raw_skills.splitlines() if s.strip()])

    # 6. Explicit Subject
    m_subj = re.search(r'(?i)(?:Subject|Sub)\s*[:\-]\s*(.+?)(?=\n|$)', block)
    if m_subj:
        explicit_subject = m_subj.group(1).strip()

    # Fallbacks
    if not company and email:
        domain_part = email.split('@')[-1].split('.')[0]
        if domain_part and domain_part.lower() not in ['gmail', 'yahoo', 'outlook', 'hotmail', 'e-solutionsinc', 'secureroot']:
            company = domain_part.capitalize()

    if not role:
        m_role_kw = re.search(r'(?i)\b([A-Z][a-zA-Z0-9\s/]+(?:Developer|Engineer|Intern|Analyst|Executive|Automation|Architect|Consultant))\b', clean_block)
        if m_role_kw:
            role = m_role_kw.group(1).strip()

    company = sanitize_field(company)
    role = sanitize_field(role)

    if not experience or re.search(r'\d{4}', experience):
        experience = "Fresher"

    return ExtractedJob(
        company_name=company,
        role=role,
        experience=experience,
        recipient_email=email,
        job_description=block,
        explicit_subject=explicit_subject,
        skills=skills,
        location=location,
        source_text=block
    )

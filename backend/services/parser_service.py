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

def parse_job_text(text: str, fallback_to_llm: bool = False) -> List[ExtractedJob]:
    """
    Parses raw job descriptions into structured ExtractedJob objects.
    Supports single or multi-job text inputs.
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
        parsed_jobs.append(job)

    # Deduplicate by company, role & recipient email
    final_jobs = []
    seen = set()
    for j in parsed_jobs:
        key = (j.company_name.lower().strip(), j.role.lower().strip(), (j.recipient_email or "").lower().strip())
        if key not in seen:
            seen.add(key)
            final_jobs.append(j)

    return final_jobs

def split_into_job_blocks(text: str) -> List[str]:
    # 1. Split on 'Company:' or '🏢 Company:' or 'Company name -'
    company_splits = re.split(r'(?=(?:^|\n|\s)\s*(?:🏢\s*)?Company(?:\s*name)?\s*[:\-])', text, flags=re.IGNORECASE)
    cleaned_splits = [s.strip() for s in company_splits if s.strip() and re.search(EMAIL_REGEX, s)]
    
    if len(cleaned_splits) > 1:
        return cleaned_splits

    # 2. Split on 'FREE JOB ALERT' or 'FREE REFERRAL ALERT'
    alert_splits = re.split(r'(?=(?:🚨|🎉|\s)*(?:FREE JOB ALERT|FREE REFERRAL ALERT|FREE HIRING ALERT))', text, flags=re.IGNORECASE)
    cleaned_alert_splits = [s.strip() for s in alert_splits if s.strip() and re.search(EMAIL_REGEX, s)]
    if len(cleaned_alert_splits) > 1:
        return cleaned_alert_splits

    return [text]

def sanitize_field(val: str) -> str:
    if not val:
        return ""
    val = clean_text_noise(val)
    val = re.sub(r'(?i)^(?:Company|Company name|Role|Position|Job Title|Title|Looking for|Hiring for|HR Email id|HR Email|🏢|👤|📍|🎓|💰|⚙️|📩)\s*[:\-]*\s*', '', val)
    val = re.sub(r'\s+', ' ', val).strip()
    return val

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
        email = email_match.group(0).rstrip('.,;:)>\'"')

    # 1. Company Name Matching
    m_comp = re.search(r'(?i)(?:🏢\s*)?Company(?:\s*name)?\s*[:\-]\s*([A-Za-z0-9\s&\.\-\(\)]+?)(?=\s*(?:👤|Role|Position|HR Email|Location|📍|🎓|Batch|💰|Stipend|Salary|⚙️|Skills|📩|Email|Send|$|\n))', block)
    if m_comp:
        company = m_comp.group(1).strip()
    else:
        # Check first line if company pattern missing
        first_line = block.splitlines()[0].strip() if block.splitlines() else ""
        if len(first_line) < 50 and not re.search(EMAIL_REGEX, first_line):
            company = first_line

    # 2. Role / Position Name Matching
    # First try: capture role text on the same line as "Role:" (most reliable)
    m_role_line = re.search(r'(?i)(?:👤\s*)?(?:Role|Position|Job Title)\s*[:\-]\s*(.+)', block)
    if m_role_line:
        raw_role = m_role_line.group(1).strip()
        # Clean trailing emojis and whitespace
        raw_role = re.sub(r'[\U00010000-\U0010ffff\u2600-\u27ff\u2300-\u23ff\u2b00-\u2bff]+.*$', '', raw_role).strip()
        # Remove trailing metadata labels that leaked in (e.g., if role and location are on same line)
        raw_role = re.sub(r'(?i)\s*(?:📍|Location|🎓|Batch|💰|Stipend).*$', '', raw_role).strip()
        role_lines = [rl.strip() for rl in raw_role.splitlines() if rl.strip()]
        if len(role_lines) > 1:
            role = " or ".join(role_lines)
        else:
            role = raw_role
    else:
        # Fallback: keyword-based role detection
        m_role_kw = re.search(r'(?i)\b([A-Z][a-zA-Z0-9\s/\-–&]+(?:Developer|Engineer|Intern|Analyst|Executive|Automation|Architect|Consultant))\b', clean_block)
        if m_role_kw:
            role = m_role_kw.group(1).strip()

    # 3. Explicit Subject Line Checking
    m_subj = re.search(r'(?i)(?:Subject|Sub|Subject Line)\s*[:\-]\s*(.+?)(?=\n|$)', block)
    if m_subj:
        explicit_subject = m_subj.group(1).strip()

    # 4. Location Matching
    m_loc = re.search(r'(?i)(?:📍\s*)?Location\s*[:\-]\s*([A-Za-z0-9\s,\.\-/]+?)(?=\s*(?:🎓|Batch|💰|Stipend|Salary|⏳|Duration|⚙️|Skills|📩|Email|Send|$|\n))', block)
    if m_loc:
        location = m_loc.group(1).strip()

    # 5. Experience / Batch Matching
    m_exp = re.search(r'(?i)(?:🎓\s*)?(?:Batch|Experience|Exp Req|Eligibility)\s*[:\-]\s*([A-Za-z0-9\s/–\.\-&]+?)(?=\s*(?:💰|Stipend|Salary|⏳|Duration|⚙️|Skills|📩|Email|Send|$|\n))', block)
    if m_exp:
        experience = m_exp.group(1).strip()

    # 6. Skills Matching
    m_skills = re.search(r'(?i)(?:⚙️\s*)?(?:Skills|Tech Stack)\s*[:\-]\s*([A-Za-z0-9\s,•/\.\-&]+?)(?=\s*(?:📩|Email|Send your resume|$|\n))', block, re.DOTALL)
    if m_skills:
        raw_skills = m_skills.group(1).strip()
        skills = ", ".join([s.strip('• ').strip() for s in raw_skills.splitlines() if s.strip()])

    # Domain Fallback for Company
    if (not company or company.lower() == "company") and email:
        domain_part = email.split('@')[-1].split('.')[0]
        if domain_part and domain_part.lower() not in ['gmail', 'yahoo', 'outlook', 'hotmail', 'e-solutionsinc', 'secureroot']:
            company = domain_part.capitalize()

    company = sanitize_field(company) or "Target Company"
    role = sanitize_field(role) or "Software Developer"

    if not experience:
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

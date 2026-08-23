import re
import logging
from typing import Dict, Any, List
from backend.models.schemas import ExtractedJob

logger = logging.getLogger(__name__)

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[\U00010000-\U0010ffff\u2600-\u27ff\u2300-\u23ff\u2000-\u206f\u2b00-\u2bff]', '', text)
    cleaned = re.sub(r'[\u200b-\u200d\ufeff]', '', cleaned)
    return cleaned.strip()

def sanitize_email_body(body: str) -> str:
    if not body:
        return ""
    cleaned = re.sub(r'(?i)^\s*Subject(?:\s*Line)?\s*[:\-].*?\n+', '', body.strip())
    return cleaned.strip()

def clean_url(url: str) -> str:
    if not url:
        return ""
    clean = re.sub(r'^https?://(?:www\.)?', '', url.strip())
    return clean.rstrip('/')

def _has_keyword(text: str, keywords: List[str]) -> bool:
    """Check if any keyword matches as a whole word (word-boundary match) to avoid false positives."""
    for kw in keywords:
        # Use word boundary regex so 'ai' doesn't match 'Collegehai' or 'ml' doesn't match 'html'
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text):
            return True
    return False

def detect_job_domain(role: str, description: str, skills_text: str) -> str:
    """
    Classifies a job into one of 9 domains based on role title, description, and skills.
    Uses word-boundary matching to prevent false positives.
    Priority order ensures specific domains are matched before general ones.
    """
    combined = (role + " " + description + " " + skills_text).lower()
    role_lower = role.lower()

    # --- 1. Check role-title-based domains first (highest priority, most specific) ---

    # DevOps / Cloud / Infrastructure
    is_devops = _has_keyword(role_lower, ['devops', 'sre', 'site reliability', 'infrastructure', 'cloud engineer', 'platform engineer'])
    if not is_devops:
        is_devops = _has_keyword(combined, ['devops', 'ci/cd', 'cicd', 'kubernetes', 'terraform', 'docker', 'jenkins', 'ansible']) and \
                    _has_keyword(combined, ['aws', 'azure', 'gcp', 'linux', 'shell', 'bash', 'infrastructure'])

    # QA / Testing
    is_qa = _has_keyword(role_lower, ['qa', 'quality assurance', 'tester', 'testing', 'sdet', 'test engineer', 'test analyst'])
    if not is_qa:
        is_qa = _has_keyword(combined, ['manual testing', 'automation testing', 'selenium', 'test case', 'bug reporting',
                                         'stlc', 'sdlc', 'defect tracking', 'test plan', 'cypress', 'playwright'])

    # HR / Recruitment
    is_hr = _has_keyword(role_lower, ['hr', 'human resource', 'recruiter', 'recruiting', 'recruitment', 'talent acquisition',
                                       'people operations', 'hr intern', 'hr executive'])

    # Business / Marketing / Sales / Non-Tech
    is_biz = _has_keyword(role_lower, ['business development', 'bde', 'marketing', 'sales', 'growth', 'operations',
                                        'e-commerce', 'ecommerce', 'digital marketing', 'content', 'seo',
                                        'social media', 'account manager', 'client'])

    # Data / Analytics
    is_data = _has_keyword(role_lower, ['data analyst', 'data scientist', 'data engineer', 'analytics', 'bi analyst',
                                         'business analyst', 'data intern'])

    # --- 2. Check skill-based tech domains (only if no role-title match above) ---

    # AI / ML (use word boundaries to avoid 'ai' matching in random words)
    is_ai = _has_keyword(combined, ['artificial intelligence', 'machine learning', 'deep learning',
                                     'nlp', 'natural language processing', 'llm', 'generative ai',
                                     'computer vision', 'pytorch', 'tensorflow', 'transformers', 'neural network'])
    # Only match 'ai' and 'ml' in role titles (more reliable context)
    if not is_ai:
        is_ai = _has_keyword(role_lower, ['ai', 'ml', 'machine learning', 'data science'])

    # Frontend / Mobile
    is_frontend = _has_keyword(combined, ['react', 'react native', 'frontend', 'front-end', 'vue', 'angular',
                                           'flutter', 'swift', 'kotlin', 'ios developer', 'android developer'])
    if not is_frontend:
        is_frontend = _has_keyword(role_lower, ['ui', 'ux', 'web developer', 'mobile developer', 'frontend', 'front-end'])

    # Backend / API
    is_backend = _has_keyword(combined, ['backend', 'back-end', 'node.js', 'express', 'django', 'fastapi',
                                          'flask', 'spring boot', 'microservices', 'rest api', 'graphql'])
    if not is_backend:
        is_backend = _has_keyword(role_lower, ['backend', 'back-end', 'server', 'api developer'])

    # --- 3. Priority-based domain resolution ---

    # Specific non-tech roles take priority (avoids misclassifying HR/BDE as tech roles)
    if is_hr:
        return "HR_RECRUITMENT"
    if is_biz:
        return "BUSINESS_MARKETING"
    if is_data:
        return "DATA_ANALYTICS"
    if is_devops:
        return "DEVOPS_CLOUD"
    if is_qa:
        return "QA_TESTING"

    # Tech domains
    if is_ai and is_frontend:
        return "AI_FRONTEND"
    elif is_ai:
        return "AI_ML"
    elif is_frontend:
        return "FRONTEND_MOBILE"
    elif is_backend:
        return "BACKEND_API"
    else:
        return "GENERAL"

def generate_email_content(job: ExtractedJob, candidate_profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Advanced Job Profile-Aware LLM Engine for Application Email Generation.
    Dynamically customizes email paragraphs, skill highlights, and project alignment
    strictly based on the target Job Profile & Candidate Profile.
    """
    cand_name = sanitize_text(candidate_profile.get("name") or "Candidate")
    cand_email = sanitize_text(candidate_profile.get("email") or "")
    cand_phone = sanitize_text(candidate_profile.get("phone") or "")
    
    degree = sanitize_text(candidate_profile.get("degree") or "")
    college = sanitize_text(candidate_profile.get("college") or "")
    grad_year = sanitize_text(candidate_profile.get("graduation_year") or "")
    
    linkedin = candidate_profile.get("linkedin_url") or ""
    github = candidate_profile.get("github_url") or ""
    portfolio = candidate_profile.get("portfolio_url") or ""
    
    raw_skills = candidate_profile.get("skills", [])
    if isinstance(raw_skills, str):
        cand_skills = [s.strip() for s in raw_skills.split(',') if s.strip()]
    else:
        cand_skills = list(raw_skills) if raw_skills else []
        
    raw_projects = candidate_profile.get("projects", [])
    if isinstance(raw_projects, str):
        projects = [p.strip() for p in raw_projects.split(',') if p.strip()]
    else:
        projects = list(raw_projects) if raw_projects else []

    # Clean Company Name & Role
    company = sanitize_text(job.company_name or "").strip()
    company = re.sub(r'(?i)^(?:Company|🏢)\s*[:\-]*\s*', '', company).strip()
    if not company or company.lower() == "company" or company == "Unknown Company":
        company = "your company"

    role = sanitize_text(job.role or "").strip()
    role = re.sub(r'(?i)^(?:Role|Position|👤)\s*[:\-]*\s*', '', role).strip()
    if not role:
        role = "Software Developer"

    job_desc = job.job_description or ""
    req_skills_str = job.skills or ""

    # Subject Selection — personalize explicit subjects containing placeholder patterns
    if job.explicit_subject and job.explicit_subject.strip():
        subject = sanitize_text(job.explicit_subject.strip())
        # Replace common placeholders like "(Your Name)", "[Your Name]", "- Name" with candidate name
        subject = re.sub(r'(?i)\(?your\s*name\)?', cand_name, subject)
        subject = re.sub(r'(?i)\[your\s*name\]', cand_name, subject)
        # Replace "- Name" at the end with "- CandidateName"
        subject = re.sub(r'(?i)\b-\s*name\s*$', f'- {cand_name}', subject)
        # Replace "- Position" with actual role
        subject = re.sub(r'(?i)\b-\s*position\b', f'- {role}', subject)
    else:
        subject = f"Application for {role} Position - {cand_name}"

    # Detect Job Domain
    domain = detect_job_domain(role, job_desc, req_skills_str)

    # Filter candidate skills matching job profile
    job_desc_lower = (job_desc + " " + req_skills_str + " " + role).lower()
    matched_skills = []
    other_skills = []

    for s in cand_skills:
        if s.lower() in job_desc_lower:
            matched_skills.append(s)
        else:
            other_skills.append(s)

    # Combine matched skills first, then fill with general skills
    selected_skills = matched_skills + [s for s in other_skills if s not in matched_skills]
    if not selected_skills:
        selected_skills = ["React.js", "JavaScript", "Node.js", "REST APIs", "Python", "SQL"]
    
    skills_formatted = ", ".join(selected_skills[:8])

    # Qualification Sentence
    if degree and grad_year and any(y in grad_year for y in ["2025", "2026", "2027", "final"]):
        qual = f"I am a final-year {degree} student"
        if college:
            qual += f" at {college}"
    elif degree:
        qual = f"I am a {degree} graduate"
        if college:
            qual += f" from {college}"
    elif college:
        qual = f"I am a Computer Science Engineering student at {college}"
    else:
        qual = "I am a software engineering candidate"

    # Domain-Specific Experience & Project Paragraph Customization
    if domain == "AI_FRONTEND":
        body_para2 = (
            f"{qual} with hands-on experience in software development and full-stack application development. "
            f"I have experience working with {skills_formatted}. "
            "I also have experience working on AI-integrated applications and am interested in building practical AI-powered solutions."
        )
        body_para3 = (
            "Through my internships and academic projects, I have gained practical experience in developing responsive web and mobile applications, "
            "integrating AI model APIs, working with databases, and implementing modern development workflows."
        )
    elif domain == "AI_ML":
        body_para2 = (
            f"{qual} specializing in artificial intelligence and software engineering. "
            f"My technical toolkit includes {skills_formatted}. "
            "I have practical experience building AI-driven applications, implementing intelligent automation, and processing data pipelines."
        )
        body_para3 = (
            "Through my academic projects and practical research, I have developed machine learning workflows, integrated intelligent API endpoints, "
            "and built scalable solutions that turn data into actionable intelligence."
        )
    elif domain == "FRONTEND_MOBILE":
        body_para2 = (
            f"{qual} with strong expertise in frontend software engineering and mobile application development. "
            f"I have extensive hands-on experience working with {skills_formatted}."
        )
        body_para3 = (
            "Through my development experience and projects, I have focused on building responsive, high-performance user interfaces, "
            "managing complex state, integrating RESTful web APIs, and delivering seamless user experiences across web and mobile platforms."
        )
    elif domain == "BACKEND_API":
        body_para2 = (
            f"{qual} focusing on backend system architecture and database development. "
            f"My core tech stack includes {skills_formatted}."
        )
        body_para3 = (
            "I have hands-on experience designing robust RESTful APIs, engineering efficient server-side architecture, managing relational and NoSQL databases, "
            "and implementing secure backend workflows."
        )
    elif domain == "DEVOPS_CLOUD":
        body_para2 = (
            f"{qual} with a strong interest in DevOps practices, cloud infrastructure, and automation. "
            f"I have hands-on experience with {skills_formatted}."
        )
        body_para3 = (
            "Through my projects and coursework, I have worked on setting up CI/CD pipelines, containerizing applications, "
            "managing cloud deployments, and automating infrastructure workflows to improve reliability and deployment speed."
        )
    elif domain == "QA_TESTING":
        body_para2 = (
            f"{qual} with a keen eye for quality and detail in software development. "
            f"I have experience with {skills_formatted} and a strong understanding of software testing methodologies."
        )
        body_para3 = (
            "Through my academic work and projects, I have gained practical experience in writing test cases, performing manual and automated testing, "
            "tracking defects, and ensuring software quality throughout the development lifecycle."
        )
    elif domain == "HR_RECRUITMENT":
        body_para2 = (
            f"{qual} with strong interpersonal and organizational skills. "
            "I am enthusiastic about human resources, talent acquisition, and people management, "
            "and I am eager to contribute to your team's recruitment and HR operations."
        )
        body_para3 = (
            "I bring excellent communication skills, a proactive approach to problem-solving, "
            "and the ability to manage multiple tasks efficiently. I am excited about the opportunity to learn and grow in a professional HR environment."
        )
    elif domain == "BUSINESS_MARKETING":
        body_para2 = (
            f"{qual} with strong communication, analytical, and problem-solving skills. "
            "I am passionate about business growth, client relationships, and strategic marketing, "
            "and I am eager to contribute meaningfully to your team."
        )
        body_para3 = (
            "Through my academic experience and extracurricular activities, I have developed skills in market research, stakeholder communication, "
            "data-driven decision making, and driving results in collaborative team environments."
        )
    elif domain == "DATA_ANALYTICS":
        body_para2 = (
            f"{qual} with a strong foundation in data analysis and problem-solving. "
            f"I have experience working with {skills_formatted} and am adept at deriving insights from complex datasets."
        )
        body_para3 = (
            "Through my academic projects and practical work, I have gained experience in data collection, cleaning, visualization, "
            "and statistical analysis, enabling data-driven decisions and actionable business insights."
        )
    else:  # GENERAL
        body_para2 = (
            f"{qual} with hands-on experience in software development and a passion for technology. "
            f"I have experience working with {skills_formatted}."
        )
        body_para3 = (
            "Through my internships and academic projects, I have gained practical experience in developing applications, "
            "collaborating with teams, solving real-world problems, and adapting quickly to new technologies and workflows."
        )

    # Highlight Projects if relevant
    project_mention = ""
    if projects:
        proj_str = ", ".join(projects[:2])
        project_mention = f" My practical work includes projects such as {proj_str}."

    # Build Signature
    sig_lines = ["Best regards,", cand_name]
    if cand_phone:
        sig_lines.append(cand_phone)
    if cand_email:
        sig_lines.append(cand_email)
    if linkedin:
        sig_lines.append(f"LinkedIn: {clean_url(linkedin)}")
    if github:
        sig_lines.append(f"GitHub: {clean_url(github)}")
    if portfolio:
        sig_lines.append(f"Portfolio: {clean_url(portfolio)}")

    signature_block = "\n".join(sig_lines)

    email_body = f"""Dear Hiring Team,

I am writing to express my interest in the {role} position at {company}.

{body_para2}

{body_para3}{project_mention}

I have attached my resume for your consideration. I would appreciate the opportunity to discuss how my skills and experience could contribute to {company}.

Thank you for your time and consideration. I look forward to hearing from you.

{signature_block}"""

    return {"subject": subject, "body": sanitize_email_body(email_body)}

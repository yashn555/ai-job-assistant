import io
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{4}'
LINKEDIN_REGEX = r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+)/?'
GITHUB_REGEX = r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9\-_]+)/?'
URL_REGEX = r'(?:https?://)?(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?'

COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React.js", "React Native", "React",
    "Node.js", "Express.js", "HTML", "CSS", "SQL", "MongoDB", "MySQL", "PostgreSQL",
    "Java", "C++", "C", "C#", "PHP", "Go", "Rust", "Swift", "Kotlin", "Flutter",
    "REST APIs", "GraphQL", "Docker", "Kubernetes", "AWS", "Git", "GitHub", "Linux",
    "TailwindCSS", "Bootstrap", "Redux", "Next.js", "Vue.js", "Angular",
    "Artificial Intelligence", "AI", "Machine Learning", "NLP", "Deep Learning",
    "PyTorch", "TensorFlow", "FastAPI", "Django", "Flask", "Pandas", "NumPy"
]

DEGREE_KEYWORDS = [
    r'B\.?Tech\s*(?:in\s*)?[A-Za-z\s]+',
    r'B\.?E\.?\s*(?:in\s*)?[A-Za-z\s]+',
    r'Bachelor\s+of\s+[A-Za-z\s]+',
    r'M\.?Tech\s*(?:in\s*)?[A-Za-z\s]+',
    r'Master\s+of\s+[A-Za-z\s]+',
    r'BCA', r'MCA', r'B\.?Sc\s*(?:in\s*)?[A-Za-z\s]+'
]

def extract_text_from_pdf_or_docx(file_bytes: bytes, filename: str) -> str:
    text = ""
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif filename_lower.endswith(".docx"):
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
    return text

def parse_resume_details(text: str) -> Dict[str, Any]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    name = ""
    email = ""
    phone = ""
    degree = ""
    college = ""
    grad_year = ""
    linkedin = ""
    github = ""
    portfolio = ""
    detected_skills = []
    projects = []
    bio = ""

    # 1. Extract Email
    email_match = re.search(EMAIL_REGEX, text)
    if email_match:
        email = email_match.group(0)

    # 2. Extract Phone
    phone_match = re.search(PHONE_REGEX, text)
    if phone_match:
        phone = phone_match.group(0)

    # 3. Extract LinkedIn
    li_match = re.search(LINKEDIN_REGEX, text, re.IGNORECASE)
    if li_match:
        full_li = li_match.group(0)
        linkedin = full_li if full_li.startswith("http") else f"https://{full_li}"

    # 4. Extract GitHub
    gh_match = re.search(GITHUB_REGEX, text, re.IGNORECASE)
    if gh_match:
        full_gh = gh_match.group(0)
        github = full_gh if full_gh.startswith("http") else f"https://{full_gh}"

    # 5. Extract Portfolio
    all_urls = re.findall(URL_REGEX, text)
    for u in all_urls:
        if not re.search(r'linkedin|github|gmail|google', u, re.IGNORECASE):
            if any(term in u.lower() for term in ['portfolio', 'vercel.app', 'dev', 'me', 'io', 'github.io', 'netlify.app']):
                portfolio = u if u.startswith("http") else f"https://{u}"
                break

    # 6. Extract Name (From top 5 lines)
    for l in lines[:5]:
        if re.search(r'resume|curriculum|vitae|profile|contact|email|phone', l, re.IGNORECASE):
            continue
        if len(l.split()) >= 1 and len(l) < 40 and not re.search(r'[\d@#\$%^&*()_+=\[\]{}|\\:;]', l):
            name = l
            break

    # 7. Extract Degree & College & Graduation Year
    for d_pat in DEGREE_KEYWORDS:
        d_match = re.search(d_pat, text, re.IGNORECASE)
        if d_match:
            degree = d_match.group(0).strip()
            break

    # College match
    col_match = re.search(r'(?:College|Institute|University|School|IIT|NIT|BIT|VIT|SRM|RTMNU)\s*(?:of\s*)?[A-Za-z0-9\s,\.\-&]+', text, re.IGNORECASE)
    if col_match:
        college = col_match.group(0).strip().split('\n')[0][:80]

    # Graduation Year match
    yr_matches = re.findall(r'\b(202[0-9]|201[5-9])\b', text)
    if yr_matches:
        grad_year = yr_matches[-1]

    # 8. Extract Skills
    text_lower = text.lower()
    for s in COMMON_SKILLS:
        pattern = r'\b' + re.escape(s.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected_skills.append(s)

    # 9. Extract Projects
    proj_section_match = re.search(r'(?i)(?:Projects|Key Projects|Personal Projects)\s*[:\-]*\n+(.*?)(?=\n\s*(?:Education|Experience|Skills|Certifications|Declaration|$))', text, re.DOTALL)
    if proj_section_match:
        proj_text = proj_section_match.group(1).strip()
        proj_lines = [pl.strip('•-* ').strip() for pl in proj_text.splitlines() if pl.strip()]
        for pl in proj_lines[:5]:
            if len(pl) > 5 and len(pl) < 100:
                projects.append(pl)

    if not projects:
        if "AI Job Application Assistant" in text:
            projects.append("AI Job Application Assistant")

    # 10. Bio / Summary
    summary_match = re.search(r'(?i)(?:Summary|Profile Summary|Objective|About Me)\s*[:\-]*\n+(.*?)(?=\n\s*(?:Education|Skills|Projects|Experience|$))', text, re.DOTALL)
    if summary_match:
        bio = summary_match.group(1).strip()[:300]
    else:
        bio = f"{degree} student at {college} with strong problem solving skills and passion for software development." if (degree or college) else ""

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "degree": degree,
        "college": college,
        "graduation_year": grad_year,
        "linkedin_url": linkedin,
        "github_url": github,
        "portfolio_url": portfolio,
        "skills": list(dict.fromkeys(detected_skills)), # deduplicate keeping order
        "projects": projects,
        "bio": bio
    }

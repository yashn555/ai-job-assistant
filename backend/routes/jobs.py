import json
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.db import get_db
from backend.models.models import Application, CandidateProfile, AppSettings, User
from backend.models.schemas import (
    JobParseRequest, ExtractedJob, EmailGenerateRequest, ApplicationResponse
)
from backend.services.parser_service import parse_job_text
from backend.services.nemotron_service import generate_email_content
from backend.routes.auth import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("/parse", response_model=List[ApplicationResponse])
def parse_jobs(
    payload: JobParseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts raw text with 1 or 10+ job postings, parses all jobs concurrently,
    generates personalized emails for all detected jobs in parallel, and returns created application records.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()
    active_resume = settings.active_resume if settings else ""

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()

    profile_dict = {
        "name": profile.name if (profile and profile.name) else current_user.name,
        "email": profile.email if (profile and profile.email) else current_user.email,
        "degree": profile.degree if profile else "",
        "college": profile.college if profile else "",
        "graduation_year": profile.graduation_year if profile else "",
        "linkedin_url": profile.linkedin_url if profile else "",
        "github_url": profile.github_url if profile else "",
        "portfolio_url": profile.portfolio_url if profile else "",
        "skills": json.loads(profile.skills_json) if (profile and profile.skills_json) else [],
        "projects": json.loads(profile.projects_json) if (profile and profile.projects_json) else []
    }

    extracted_jobs = parse_job_text(payload.text)

    def process_single_job(job: ExtractedJob):
        gen_res = generate_email_content(job, profile_dict)
        return {
            "user_id": current_user.id,
            "company_name": job.company_name,
            "role": job.role,
            "experience": job.experience or "Fresher",
            "recipient_email": job.recipient_email,
            "job_description": job.job_description,
            "explicit_subject": job.explicit_subject,
            "generated_subject": gen_res["subject"],
            "generated_email": gen_res["body"],
            "skills": job.skills,
            "location": job.location,
            "source_text": job.source_text,
            "resume_filename": active_resume,
            "status": "GENERATED"
        }

    with ThreadPoolExecutor(max_workers=min(10, max(1, len(extracted_jobs)))) as executor:
        processed_results = list(executor.map(process_single_job, extracted_jobs))

    created_apps = []
    for res_dict in processed_results:
        app = Application(**res_dict)
        db.add(app)
        db.commit()
        db.refresh(app)
        created_apps.append(app)

    return created_apps


@router.post("/upload-parse", response_model=List[ApplicationResponse])
async def parse_jobs_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = ""
    filename = file.filename.lower()
    file_bytes = await file.read()

    if filename.endswith(".txt"):
        content = file_bytes.decode("utf-8", errors="ignore")
    elif filename.endswith(".pdf"):
        import io, pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            content += page.extract_text() + "\n"
    elif filename.endswith(".docx"):
        import io, docx
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            content += para.text + "\n"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    return parse_jobs(JobParseRequest(text=content), db=db, current_user=current_user)


@router.post("/generate-email", response_model=ApplicationResponse)
def generate_job_email(
    payload: EmailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not payload.application_id:
        raise HTTPException(status_code=400, detail="application_id is required.")

    app = db.query(Application).filter(Application.id == payload.application_id, Application.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()

    profile_dict = {
        "name": profile.name if (profile and profile.name) else current_user.name,
        "email": profile.email if (profile and profile.email) else current_user.email,
        "degree": profile.degree if profile else "",
        "college": profile.college if profile else "",
        "graduation_year": profile.graduation_year if profile else "",
        "linkedin_url": profile.linkedin_url if profile else "",
        "github_url": profile.github_url if profile else "",
        "portfolio_url": profile.portfolio_url if profile else "",
        "skills": json.loads(profile.skills_json) if (profile and profile.skills_json) else [],
        "projects": json.loads(profile.projects_json) if (profile and profile.projects_json) else []
    }

    job_obj = ExtractedJob(
        company_name=app.company_name,
        role=app.role,
        experience=app.experience,
        recipient_email=app.recipient_email,
        job_description=app.job_description,
        explicit_subject=app.explicit_subject,
        skills=app.skills,
        location=app.location,
        source_text=app.source_text
    )

    gen_res = generate_email_content(job_obj, profile_dict)

    app.generated_subject = gen_res["subject"]
    app.generated_email = gen_res["body"]
    app.status = "GENERATED"
    db.commit()
    db.refresh(app)

    return app

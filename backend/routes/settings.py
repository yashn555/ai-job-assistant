import json
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from backend.database.db import get_db
from backend.models.models import CandidateProfile, AppSettings
from backend.models.schemas import ProfileSchema, SettingsSchema, TestEmailRequest
from backend.services.resume_service import save_resume_file, list_uploaded_resumes, remove_resume_file
from backend.services.email_service import send_application_email

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("/profile", response_model=ProfileSchema)
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == 1).first()
    if not profile:
        profile = CandidateProfile(id=1)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileSchema(
        name=profile.name,
        email=profile.email or "yashnagapure25@gmail.com",
        degree=profile.degree,
        college=profile.college,
        graduation_year=profile.graduation_year,
        linkedin_url=profile.linkedin_url or "",
        github_url=profile.github_url or "",
        portfolio_url=profile.portfolio_url or "",
        skills=json.loads(profile.skills_json) if profile.skills_json else [],
        projects=json.loads(profile.projects_json) if profile.projects_json else [],
        bio=profile.bio or ""
    )


@router.put("/profile", response_model=ProfileSchema)
def update_profile(payload: ProfileSchema, db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == 1).first()
    if not profile:
        profile = CandidateProfile(id=1)
        db.add(profile)

    profile.name = payload.name
    if payload.email:
        profile.email = payload.email
    profile.degree = payload.degree
    profile.college = payload.college
    profile.graduation_year = payload.graduation_year
    profile.linkedin_url = payload.linkedin_url
    profile.github_url = payload.github_url
    profile.portfolio_url = payload.portfolio_url
    profile.skills_json = json.dumps(payload.skills)
    profile.projects_json = json.dumps(payload.projects)
    profile.bio = payload.bio

    db.commit()
    db.refresh(profile)
    return get_profile(db=db)


@router.get("/app", response_model=SettingsSchema)
def get_app_settings(db: Session = Depends(get_db)):
    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if not settings:
        settings = AppSettings(
            id=1,
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
            smtp_username=os.getenv("SMTP_USERNAME", "yashnagapure25@gmail.com"),
            smtp_password=os.getenv("SMTP_PASSWORD", "awmtyyfozljwmbvu"),
            sender_email=os.getenv("SENDER_EMAIL", "yashnagapure25@gmail.com")
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return SettingsSchema(
        auto_send=settings.auto_send,
        smtp_host=settings.smtp_host or "smtp.gmail.com",
        smtp_port=settings.smtp_port or 587,
        smtp_username=settings.smtp_username or "yashnagapure25@gmail.com",
        smtp_password=settings.smtp_password or "awmtyyfozljwmbvu",
        sender_email=settings.sender_email or "yashnagapure25@gmail.com",
        active_resume=settings.active_resume or "Yash_Nagapure_Resume.pdf"
    )


@router.put("/app", response_model=SettingsSchema)
def update_app_settings(payload: SettingsSchema, db: Session = Depends(get_db)):
    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if not settings:
        settings = AppSettings(id=1)
        db.add(settings)

    settings.auto_send = payload.auto_send
    settings.smtp_host = payload.smtp_host
    settings.smtp_port = payload.smtp_port
    settings.smtp_username = payload.smtp_username
    settings.smtp_password = payload.smtp_password
    settings.sender_email = payload.sender_email
    if payload.active_resume:
        settings.active_resume = payload.active_resume

    db.commit()
    db.refresh(settings)
    return get_app_settings(db=db)


@router.post("/resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resume formats are supported.")

    bytes_data = await file.read()
    filename = save_resume_file(bytes_data, file.filename)

    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if not settings:
        settings = AppSettings(id=1)
        db.add(settings)

    settings.active_resume = filename
    db.commit()

    return {"message": "Resume uploaded successfully.", "filename": filename}


@router.get("/resume")
def get_resumes():
    return list_uploaded_resumes()


@router.delete("/resume/{filename}")
def delete_resume(filename: str, db: Session = Depends(get_db)):
    success = remove_resume_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found.")

    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if settings and settings.active_resume == filename:
        settings.active_resume = ""
        db.commit()

    return {"message": "Resume file removed successfully."}


@router.post("/test-email")
def test_email(payload: TestEmailRequest, db: Session = Depends(get_db)):
    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    smtp_dict = {
        "smtp_host": settings.smtp_host if settings else "smtp.gmail.com",
        "smtp_port": settings.smtp_port if settings else 587,
        "smtp_username": settings.smtp_username if settings else "yashnagapure25@gmail.com",
        "smtp_password": settings.smtp_password if settings else "awmtyyfozljwmbvu",
        "sender_email": settings.sender_email if settings else "yashnagapure25@gmail.com",
    }

    success, msg = send_application_email(
        recipient_email=payload.recipient_email,
        subject="AI Job Application Assistant - Test Email",
        body="Congratulations! Your Gmail SMTP email setup (yashnagapure25@gmail.com) for AI Job Application Assistant is working correctly.",
        smtp_settings=smtp_dict
    )

    if not success:
        raise HTTPException(status_code=400, detail=msg)

    return {"message": "Test email sent successfully!", "recipient": payload.recipient_email}

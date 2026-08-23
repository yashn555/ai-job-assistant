import json
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.db import get_db
from backend.models.models import CandidateProfile, AppSettings, User
from backend.models.schemas import ProfileSchema, SettingsSchema, TestEmailRequest
from backend.services.resume_service import save_resume_file, list_uploaded_resumes, remove_resume_file
from backend.services.email_service import send_application_email
from backend.routes.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("/profile", response_model=ProfileSchema)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()

    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            name=current_user.name,
            email=current_user.email
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileSchema(
        name=profile.name or current_user.name,
        email=profile.email or current_user.email,
        degree=profile.degree or "",
        college=profile.college or "",
        graduation_year=profile.graduation_year or "",
        linkedin_url=profile.linkedin_url or "",
        github_url=profile.github_url or "",
        portfolio_url=profile.portfolio_url or "",
        skills=json.loads(profile.skills_json) if profile.skills_json else [],
        projects=json.loads(profile.projects_json) if profile.projects_json else [],
        bio=profile.bio or ""
    )


@router.put("/profile", response_model=ProfileSchema)
def update_profile(
    payload: ProfileSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()

    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    profile.name = payload.name
    profile.email = payload.email if payload.email else current_user.email
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
    return get_profile(db=db, current_user=current_user)


@router.get("/app", response_model=SettingsSchema)
def get_app_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()

    if not settings:
        settings = AppSettings(
            user_id=current_user.id,
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_username=current_user.email,
            smtp_password=current_user.app_password or "",
            sender_email=current_user.email
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return SettingsSchema(
        auto_send=settings.auto_send,
        smtp_host=settings.smtp_host or "smtp.gmail.com",
        smtp_port=settings.smtp_port or 587,
        smtp_username=settings.smtp_username or current_user.email,
        smtp_password=settings.smtp_password or (current_user.app_password or ""),
        sender_email=settings.sender_email or current_user.email,
        active_resume=settings.active_resume or ""
    )


@router.put("/app", response_model=SettingsSchema)
def update_app_settings(
    payload: SettingsSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()

    if not settings:
        settings = AppSettings(user_id=current_user.id)
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
    return get_app_settings(db=db, current_user=current_user)


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resume formats are supported.")

    bytes_data = await file.read()
    filename = save_resume_file(bytes_data, file.filename)

    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()
    if not settings:
        settings = AppSettings(user_id=current_user.id)
        db.add(settings)

    settings.active_resume = filename
    db.commit()

    return {"message": "Resume uploaded successfully.", "filename": filename}


@router.get("/resume")
def get_resumes(current_user: User = Depends(get_current_user)):
    return list_uploaded_resumes()


@router.delete("/resume/{filename}")
def delete_resume(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = remove_resume_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found.")

    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()
    if settings and settings.active_resume == filename:
        settings.active_resume = ""
        db.commit()

    return {"message": "Resume file removed successfully."}


@router.post("/test-email")
def test_email(
    payload: TestEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()

    smtp_username = settings.smtp_username if (settings and settings.smtp_username) else current_user.email
    smtp_password = settings.smtp_password if (settings and settings.smtp_password) else (current_user.app_password or "")
    sender_email = settings.sender_email if (settings and settings.sender_email) else current_user.email

    if not smtp_username or not smtp_password:
        raise HTTPException(status_code=400, detail="Gmail App Password is not configured for your account. Please update App Settings.")

    smtp_dict = {
        "smtp_host": settings.smtp_host if (settings and settings.smtp_host) else "smtp.gmail.com",
        "smtp_port": settings.smtp_port if (settings and settings.smtp_port) else 587,
        "smtp_username": smtp_username,
        "smtp_password": smtp_password,
        "sender_email": sender_email,
    }

    success, msg = send_application_email(
        recipient_email=payload.recipient_email,
        subject="AI Job Application Assistant - Test Email",
        body=f"Hello {current_user.name}!\n\nCongratulations! Your Gmail SMTP email setup ({sender_email}) for AI Job Application Assistant is working correctly.",
        smtp_settings=smtp_dict
    )

    if not success:
        raise HTTPException(status_code=400, detail=msg)

    return {"message": "Test email sent successfully!", "recipient": payload.recipient_email}

import json
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from backend.database.db import get_db
from backend.models.models import CandidateProfile, AppSettings, User
from backend.models.schemas import ProfileSchema, SettingsSchema, TestEmailRequest, ResumeExtractResponse
from backend.services.resume_service import (
    save_resume_file,
    list_uploaded_resumes,
    remove_resume_file,
    ensure_resume_on_disk
)
from backend.services.email_service import send_application_email
from backend.services.resume_extractor_service import extract_text_from_pdf_or_docx, parse_resume_details
from backend.services.crypto_service import encrypt_secret, decrypt_secret, mask_secret, is_masked
from backend.routes.auth import get_current_user, get_optional_user

logger = logging.getLogger("backend.routes.settings")
router = APIRouter(prefix="/api/settings", tags=["Settings"])


def safe_json_list(val: Any) -> List[Any]:
    if not val:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return [v.strip() for v in val.split(",") if v.strip()]
    return []


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
            email=current_user.email,
            phone=current_user.phone or ""
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileSchema(
        name=profile.name or current_user.name,
        email=profile.email or current_user.email,
        phone=profile.phone or current_user.phone or "",
        degree=profile.degree or "",
        college=profile.college or "",
        graduation_year=profile.graduation_year or "",
        linkedin_url=profile.linkedin_url or "",
        github_url=profile.github_url or "",
        portfolio_url=profile.portfolio_url or "",
        skills=safe_json_list(profile.skills_json),
        projects=safe_json_list(profile.projects_json),
        bio=profile.bio or "",
        is_profile_complete=bool(profile.is_profile_complete)
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

    if payload.name is not None and payload.name != "":
        profile.name = payload.name
        current_user.name = payload.name
    if payload.email is not None and payload.email != "":
        profile.email = payload.email
    if payload.phone is not None:
        profile.phone = payload.phone
        current_user.phone = payload.phone
    if payload.degree is not None:
        profile.degree = payload.degree
    if payload.college is not None:
        profile.college = payload.college
    if payload.graduation_year is not None:
        profile.graduation_year = payload.graduation_year
    if payload.linkedin_url is not None:
        profile.linkedin_url = payload.linkedin_url
    if payload.github_url is not None:
        profile.github_url = payload.github_url
    if payload.portfolio_url is not None:
        profile.portfolio_url = payload.portfolio_url
    if payload.skills is not None:
        profile.skills_json = json.dumps(payload.skills) if isinstance(payload.skills, list) else str(payload.skills)
    if payload.projects is not None:
        profile.projects_json = json.dumps(payload.projects) if isinstance(payload.projects, list) else str(payload.projects)
    if payload.bio is not None:
        profile.bio = payload.bio

    profile.is_profile_complete = bool(profile.name and profile.email and profile.degree)

    db.commit()
    db.refresh(profile)
    return get_profile(db=db, current_user=current_user)


@router.post("/extract-resume-profile", response_model=ResumeExtractResponse)
async def extract_resume_profile(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported for resume extraction.")

    bytes_data = await file.read()
    raw_text = extract_text_from_pdf_or_docx(bytes_data, file.filename)
    extracted = parse_resume_details(raw_text)

    # Save active resume file simultaneously
    filename = save_resume_file(bytes_data, file.filename)
    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()
    if not settings:
        settings = AppSettings(user_id=current_user.id)
        db.add(settings)

    import base64
    settings.active_resume = filename
    settings.resume_base64 = base64.b64encode(bytes_data).decode("utf-8")
    
    # Auto-populate CandidateProfile with extracted fields
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    if extracted.get("name") and (not profile.name or profile.name in ("User", "", current_user.email)):
        profile.name = extracted["name"]
        current_user.name = extracted["name"]
    if extracted.get("email") and not profile.email:
        profile.email = extracted["email"]
    if extracted.get("phone"):
        profile.phone = extracted["phone"]
        current_user.phone = extracted["phone"]
    if extracted.get("degree"):
        profile.degree = extracted["degree"]
    if extracted.get("college"):
        profile.college = extracted["college"]
    if extracted.get("graduation_year"):
        profile.graduation_year = extracted["graduation_year"]
    if extracted.get("linkedin_url"):
        profile.linkedin_url = extracted["linkedin_url"]
    if extracted.get("github_url"):
        profile.github_url = extracted["github_url"]
    if extracted.get("portfolio_url"):
        profile.portfolio_url = extracted["portfolio_url"]
    if extracted.get("skills"):
        profile.skills_json = json.dumps(extracted["skills"])
    if extracted.get("projects"):
        profile.projects_json = json.dumps(extracted["projects"])
    if extracted.get("bio"):
        profile.bio = extracted["bio"]

    profile.is_profile_complete = True
    db.commit()

    if not extracted.get("email"):
        extracted["email"] = current_user.email
    if not extracted.get("name"):
        extracted["name"] = current_user.name

    return ResumeExtractResponse(**extracted)


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

    stored_pass = settings.smtp_password or current_user.app_password or ""
    return SettingsSchema(
        auto_send=settings.auto_send,
        smtp_host=settings.smtp_host or "smtp.gmail.com",
        smtp_port=settings.smtp_port or 587,
        smtp_username=settings.smtp_username or current_user.email,
        smtp_password=mask_secret(stored_pass),
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

    if payload.auto_send is not None:
        settings.auto_send = payload.auto_send
    if payload.smtp_host is not None:
        settings.smtp_host = payload.smtp_host
    if payload.smtp_port is not None:
        settings.smtp_port = payload.smtp_port
    if payload.smtp_username is not None:
        settings.smtp_username = payload.smtp_username
    
    # Encrypt App Password when provided, without overwriting if client sends mask
    if payload.smtp_password is not None and not is_masked(payload.smtp_password) and payload.smtp_password.strip() != "":
        encrypted_pass = encrypt_secret(payload.smtp_password.strip())
        settings.smtp_password = encrypted_pass
        current_user.app_password = encrypted_pass

    if payload.sender_email is not None:
        settings.sender_email = payload.sender_email
    if payload.active_resume is not None and payload.active_resume != "":
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

    import base64
    settings.active_resume = filename
    settings.resume_base64 = base64.b64encode(bytes_data).decode("utf-8")
    db.commit()

    return {"message": "Resume uploaded successfully.", "filename": filename}


@router.get("/resume")
def get_resumes(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    if current_user:
        settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()
        if settings and settings.active_resume and settings.resume_base64:
            try:
                ensure_resume_on_disk(settings.active_resume, settings.resume_base64)
            except Exception as e:
                logger.warning(f"Error ensuring resume on disk: {e}")
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
    encrypted_pass = settings.smtp_password if (settings and settings.smtp_password) else (current_user.app_password or "")
    raw_smtp_password = decrypt_secret(encrypted_pass)
    sender_email = settings.sender_email if (settings and settings.sender_email) else current_user.email

    if not smtp_username or not raw_smtp_password:
        raise HTTPException(status_code=400, detail="Gmail App Password is not configured for your account. Please update App Settings.")

    smtp_dict = {
        "smtp_host": settings.smtp_host if (settings and settings.smtp_host) else "smtp.gmail.com",
        "smtp_port": settings.smtp_port if (settings and settings.smtp_port) else 587,
        "smtp_username": smtp_username,
        "smtp_password": raw_smtp_password,
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

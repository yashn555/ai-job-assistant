from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.models import Application, AppSettings, User
from backend.models.schemas import ApplicationResponse, ApplicationUpdate
from backend.services.email_service import validate_email_send_request, send_application_email
from backend.services.resume_service import ensure_resume_on_disk
from backend.routes.auth import get_current_user

router = APIRouter(prefix="/api/applications", tags=["Applications"])

@router.get("", response_model=List[ApplicationResponse])
def get_applications(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Application).filter(Application.user_id == current_user.id)
    if status:
        query = query.filter(Application.status == status.upper())
    return query.order_by(Application.created_at.desc()).all()


@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application_by_id(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        app = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.created_at.desc()).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application record not found. Please parse a job posting first.")
    return app


@router.put("/{app_id}", response_model=ApplicationResponse)
def update_application(
    app_id: str,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        app = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.created_at.desc()).first()

    if not app:
        settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()
        app = Application(
            id=app_id,
            user_id=current_user.id,
            company_name=payload.company_name or "Company",
            role=payload.role or "Software Engineer",
            recipient_email=payload.recipient_email or current_user.email,
            resume_filename=settings.active_resume if settings else "",
            status="DRAFT"
        )
        db.add(app)
        db.commit()
        db.refresh(app)

    if payload.company_name is not None:
        app.company_name = payload.company_name
    if payload.role is not None:
        app.role = payload.role
    if payload.experience is not None:
        app.experience = payload.experience
    if payload.recipient_email is not None:
        app.recipient_email = payload.recipient_email
    if payload.generated_subject is not None:
        app.generated_subject = payload.generated_subject
    if payload.generated_email is not None:
        app.generated_email = payload.generated_email
    if payload.status is not None:
        app.status = payload.status.upper()

    db.commit()
    db.refresh(app)
    return app


@router.post("/batch-send")
def batch_send_applications(
    app_ids: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()

    smtp_username = settings.smtp_username if (settings and settings.smtp_username) else current_user.email
    smtp_password = settings.smtp_password if (settings and settings.smtp_password) else (current_user.app_password or "")
    sender_email = settings.sender_email if (settings and settings.sender_email) else current_user.email

    if not smtp_username or not smtp_password:
        raise HTTPException(status_code=400, detail="Gmail App Password is not configured for your account. Please configure it in App Settings.")

    smtp_dict = {
        "smtp_host": settings.smtp_host if (settings and settings.smtp_host) else "smtp.gmail.com",
        "smtp_port": settings.smtp_port if (settings and settings.smtp_port) else 587,
        "smtp_username": smtp_username,
        "smtp_password": smtp_password,
        "sender_email": sender_email,
    }

    if app_ids and len(app_ids) > 0:
        apps = db.query(Application).filter(Application.id.in_(app_ids), Application.user_id == current_user.id).all()
    else:
        apps = db.query(Application).filter(Application.user_id == current_user.id, Application.status.in_(["GENERATED", "REVIEWED", "DRAFT"])).all()

    valid_apps = [a for a in apps if a.recipient_email]

    if not valid_apps:
        return {"sent_count": 0, "failed_count": 0, "message": "No applications with valid recipient emails were ready to send."}

    sent_count = 0
    failed_count = 0

    def send_single_app(app: Application):
        target_resume = app.resume_filename or (settings.active_resume if settings else None)
        if settings and target_resume:
            ensure_resume_on_disk(target_resume, settings.resume_base64)

        subject = app.generated_subject or app.explicit_subject or f"Application for {app.role}"
        success, send_err = send_application_email(
            recipient_email=app.recipient_email,
            subject=subject,
            body=app.generated_email,
            resume_filename=target_resume,
            smtp_settings=smtp_dict
        )
        return app.id, success, send_err

    with ThreadPoolExecutor(max_workers=min(5, len(valid_apps))) as executor:
        results = list(executor.map(send_single_app, valid_apps))

    for app_id, success, send_err in results:
        app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
        if app:
            if success:
                app.status = "SENT"
                app.sent_at = datetime.utcnow()
                app.error_message = None
                sent_count += 1
            else:
                app.status = "FAILED"
                app.error_message = send_err
                failed_count += 1
            db.commit()

    return {
        "sent_count": sent_count,
        "failed_count": failed_count,
        "message": f"Batch process complete: {sent_count} email(s) sent successfully, {failed_count} failed."
    }


@router.post("/{app_id}/send", response_model=ApplicationResponse)
def send_application(
    app_id: str,
    payload: Optional[ApplicationUpdate] = None,
    override_duplicate: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        app = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.created_at.desc()).first()

    if not app:
        settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()
        comp_name = (payload.company_name if payload and payload.company_name else None) or "Company"
        role_title = (payload.role if payload and payload.role else None) or "Software Engineer"
        recip_email = (payload.recipient_email if payload and payload.recipient_email else None) or current_user.email
        app = Application(
            id=app_id,
            user_id=current_user.id,
            company_name=comp_name,
            role=role_title,
            recipient_email=recip_email,
            generated_subject=payload.generated_subject if payload else None,
            generated_email=payload.generated_email if payload else None,
            resume_filename=settings.active_resume if settings else "",
            status="DRAFT"
        )
        db.add(app)
        db.commit()
        db.refresh(app)

    if payload:
        if payload.company_name:
            app.company_name = payload.company_name
        if payload.role:
            app.role = payload.role
        if payload.recipient_email:
            app.recipient_email = payload.recipient_email
        if payload.generated_subject:
            app.generated_subject = payload.generated_subject
        if payload.generated_email:
            app.generated_email = payload.generated_email

    settings = db.query(AppSettings).filter(AppSettings.user_id == current_user.id).first()

    target_resume = app.resume_filename or (settings.active_resume if settings else None)
    if settings and target_resume:
        ensure_resume_on_disk(target_resume, settings.resume_base64)

    valid, err_msg = validate_email_send_request(
        recipient_email=app.recipient_email,
        company_name=app.company_name,
        role=app.role,
        subject=app.generated_subject or app.explicit_subject,
        body=app.generated_email,
        resume_filename=target_resume
    )

    if not valid:
        app.status = "FAILED"
        app.error_message = err_msg
        db.commit()
        db.refresh(app)
        raise HTTPException(status_code=400, detail=err_msg)

    if not override_duplicate:
        duplicate = db.query(Application).filter(
            Application.user_id == current_user.id,
            Application.recipient_email == app.recipient_email,
            Application.company_name == app.company_name,
            Application.role == app.role,
            Application.status == "SENT",
            Application.id != app.id
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=f"Application already sent to {app.company_name} ({app.recipient_email}) for role '{app.role}'."
            )

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

    subject = app.generated_subject or app.explicit_subject or f"Application for {app.role}"

    success, send_err = send_application_email(
        recipient_email=app.recipient_email,
        subject=subject,
        body=app.generated_email,
        resume_filename=target_resume,
        smtp_settings=smtp_dict
    )

    if success:
        app.status = "SENT"
        app.sent_at = datetime.utcnow()
        app.error_message = None
    else:
        app.status = "FAILED"
        app.error_message = send_err

    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}")
def delete_application(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        app = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.created_at.desc()).first()

    if app:
        db.delete(app)
        db.commit()

    return {"message": "Application deleted successfully."}

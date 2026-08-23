import sys
import os

# Add root directory to sys.path so backend package imports work in all execution modes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database.db import engine, Base, SessionLocal, apply_migrations
from backend.models.models import CandidateProfile, AppSettings, Application, User
from backend.routes import jobs, applications, settings, auth, support
from backend.routes.auth import hash_password


# Initialize DB tables & migrations
Base.metadata.create_all(bind=engine)
apply_migrations()


app = FastAPI(
    title="AI Job Application Assistant API",
    version="1.0.0",
    description="Backend service for job description parsing, Nemotron AI email generation, and SMTP application sending."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.services.resume_service import get_upload_dir

# Mount Uploads directory
uploads_dir = get_upload_dir()
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# Include Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(settings.router)
app.include_router(support.router)


@app.on_event("startup")
def seed_initial_data():
    """
    Seeds initial candidate profile (Yash Nagapure), default user account, and settings if missing.
    Does NOT create any mock job applications so the dashboard starts completely clean.
    """
    db = SessionLocal()
    try:
        # Seed default user account (Yash Nagapure)
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = db.query(User).filter(User.email == "yashnagapure25@gmail.com").first()
        if not user:
            user = User(
                id=1,
                name="Yash Nagapure",
                email="yashnagapure25@gmail.com",
                password_hash=hash_password("yash1234"),
                app_password="awmtyyfozljwmbvu"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        profile = db.query(CandidateProfile).filter(CandidateProfile.id == 1).first()
        if not profile:
            initial_profile = CandidateProfile(
                id=1,
                user_id=user.id,
                name="Yash Nagapure",
                email="yashnagapure25@gmail.com",
                degree="B.Tech Computer Science Engineering",
                college="AISSMS IOIT, Pune",
                graduation_year="2027",
                linkedin_url="https://linkedin.com/in/yashnagapure",
                github_url="https://github.com/yashnagapure",
                portfolio_url="https://yashnagapure.dev",
                skills_json=json.dumps([
                    "Java", "C++", "JavaScript", "HTML", "CSS", "React.js",
                    "Node.js", "Express.js", "TypeScript", "Python", "SQL",
                    "MySQL", "MongoDB", "REST APIs", "Git", "GitHub",
                    "DSA", "OOP", "DBMS", "OS", "Computer Networks"
                ]),
                projects_json=json.dumps([
                    "Travel-Friend", "Hotel Mitraya", "DocuForge AI", "Face Recognition Attendance System"
                ]),
                bio="Final-year Computer Science Engineering student passionate about software development, AI automation, and full-stack web applications."
            )
            db.add(initial_profile)
        elif not profile.user_id:
            profile.user_id = user.id

        app_setting = db.query(AppSettings).filter(AppSettings.id == 1).first()
        if not app_setting:
            initial_setting = AppSettings(
                id=1,
                user_id=user.id,
                auto_send=False,
                smtp_host="smtp.gmail.com",
                smtp_port=587,
                smtp_username="yashnagapure25@gmail.com",
                smtp_password="awmtyyfozljwmbvu",
                sender_email="yashnagapure25@gmail.com",
                active_resume="Yash_Nagapure_Resume.pdf"
            )
            db.add(initial_setting)
        elif not app_setting.user_id:
            app_setting.user_id = user.id

        db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Job Application Assistant Backend",
        "nemotron_key_configured": bool(os.getenv("NVIDIA_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


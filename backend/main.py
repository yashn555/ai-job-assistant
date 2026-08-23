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


# Initialize DB tables & migrations directly on module load
try:
    Base.metadata.create_all(bind=engine)
    apply_migrations()
except Exception as e:
    print(f"DB Init Exception: {e}")


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


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Job Application Assistant Backend",
        "llm_engine": "Custom Local Deterministic LLM Engine Ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)



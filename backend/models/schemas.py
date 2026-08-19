from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class JobParseRequest(BaseModel):
    text: str

class ExtractedJob(BaseModel):
    company_name: str
    role: str
    experience: Optional[str] = "Fresher"
    recipient_email: Optional[str] = None
    job_description: Optional[str] = ""
    explicit_subject: Optional[str] = None
    skills: Optional[str] = ""
    location: Optional[str] = ""
    source_text: Optional[str] = ""

class JobParseResponse(BaseModel):
    jobs: List[ExtractedJob]

class EmailGenerateRequest(BaseModel):
    application_id: Optional[str] = None
    job_data: Optional[ExtractedJob] = None

class EmailGenerateResponse(BaseModel):
    application_id: str
    subject: str
    body: str

class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    role: Optional[str] = None
    experience: Optional[str] = None
    recipient_email: Optional[str] = None
    generated_subject: Optional[str] = None
    generated_email: Optional[str] = None
    status: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    company_name: str
    role: str
    experience: Optional[str] = "Fresher"
    recipient_email: Optional[str] = None
    job_description: Optional[str] = ""
    explicit_subject: Optional[str] = None
    generated_subject: Optional[str] = None
    generated_email: Optional[str] = None
    skills: Optional[str] = ""
    location: Optional[str] = ""
    resume_filename: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProfileSchema(BaseModel):
    name: str
    email: Optional[str] = "yashnagapure25@gmail.com"
    degree: str
    college: str
    graduation_year: str
    linkedin_url: Optional[str] = ""
    github_url: Optional[str] = ""
    portfolio_url: Optional[str] = ""
    skills: List[str]
    projects: List[str]
    bio: Optional[str] = ""

class SettingsSchema(BaseModel):
    auto_send: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender_email: str
    active_resume: Optional[str] = ""

class TestEmailRequest(BaseModel):
    recipient_email: str

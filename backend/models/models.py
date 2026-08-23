import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from backend.database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    app_password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), default=1, nullable=True)
    company_name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    experience = Column(String(100), default="Fresher")
    recipient_email = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=True)
    explicit_subject = Column(String(255), nullable=True)
    generated_subject = Column(String(255), nullable=True)
    generated_email = Column(Text, nullable=True)
    skills = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    source_text = Column(Text, nullable=True)
    resume_filename = Column(String(255), nullable=True)
    status = Column(String(50), default="DRAFT") # DRAFT, GENERATED, REVIEWED, SENT, FAILED, SKIPPED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

class CandidateProfile(Base):
    __tablename__ = "candidate_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1, nullable=True)
    name = Column(String(255), default="Yash Nagapure")
    email = Column(String(255), default="yashnagapure25@gmail.com")
    degree = Column(String(255), default="B.Tech Computer Science Engineering")
    college = Column(String(255), default="AISSMS IOIT, Pune")
    graduation_year = Column(String(50), default="2027")
    linkedin_url = Column(String(500), default="https://linkedin.com/in/yashnagapure")
    github_url = Column(String(500), default="https://github.com/yashnagapure")
    portfolio_url = Column(String(500), default="https://yashnagapure.dev")
    skills_json = Column(Text, default='["Java", "C++", "JavaScript", "HTML", "CSS", "React.js", "Node.js", "Express.js", "TypeScript", "Python", "SQL", "MySQL", "MongoDB", "REST APIs", "Git", "GitHub", "DSA", "OOP", "DBMS", "OS", "Computer Networks"]')
    projects_json = Column(Text, default='["Travel-Friend", "Hotel Mitraya", "DocuForge AI", "Face Recognition Attendance System"]')
    bio = Column(Text, default="Final-year Computer Science Engineering student passionate about software development, AI automation, and web technologies.")

class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1, nullable=True)

    auto_send = Column(Boolean, default=False)
    smtp_host = Column(String(255), default="smtp.gmail.com")
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String(255), default="yashnagapure25@gmail.com")
    smtp_password = Column(String(255), default="awmtyyfozljwmbvu")
    sender_email = Column(String(255), default="yashnagapure25@gmail.com")
    active_resume = Column(String(255), default="Yash_Nagapure_Resume.pdf")

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN") # OPEN, IN_PROGRESS, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)


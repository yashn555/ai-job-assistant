import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Detect Vercel serverless environment or local
is_vercel = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None

if is_vercel:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/job_assistant.db")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./job_assistant.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

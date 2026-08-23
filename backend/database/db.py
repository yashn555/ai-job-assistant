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

def apply_migrations():
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        with engine.connect() as conn:
            for table, col in [("candidate_profile", "user_id"), ("app_settings", "user_id"), ("applications", "user_id")]:
                if table in table_names:
                    columns = [c["name"] for c in inspector.get_columns(table)]
                    if col not in columns:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} INTEGER DEFAULT 1"))
                        conn.commit()
    except Exception as e:
        print(f"Migration notice: {e}")


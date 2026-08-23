import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.db import get_db
from backend.models.models import User, CandidateProfile, AppSettings
from backend.models.schemas import UserSignup, UserLogin, AuthResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])

SALT = b"ai_job_assistant_secure_salt_2026"

def hash_password(password: str) -> str:
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT, 100000)
    return key.hex()

def create_token(user_id: int) -> str:
    token_data = f"token_{user_id}_{hash_password(str(user_id))[:12]}"
    return token_data

def decode_token(token: str) -> Optional[int]:
    if not token:
        return None
    token_clean = token.strip().strip('"').strip("'")
    if not token_clean.startswith("token_"):
        return None
    try:
        parts = token_clean.split("_")
        user_id = int(parts[1])
        expected = f"token_{user_id}_{hash_password(str(user_id))[:12]}"
        if token_clean == expected:
            return user_id
    except Exception:
        return None
    return None

def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    token = None
    if authorization:
        token = authorization.replace("Bearer ", "").strip().strip('"').strip("'")
    elif x_user_token:
        token = x_user_token.strip().strip('"').strip("'")

    user_id = decode_token(token) if token else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again."
        )
    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    x_user_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    try:
        return get_current_user(authorization=authorization, x_user_token=x_user_token, db=db)
    except HTTPException:
        return None



@router.post("/signup", response_model=AuthResponse)
def signup(payload: UserSignup, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = User(
        name=payload.name.strip(),
        email=email_clean,
        password_hash=hash_password(payload.password),
        app_password=payload.app_password.strip() if payload.app_password else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize candidate profile for new user
    profile = CandidateProfile(
        user_id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        degree="B.Tech / Bachelor Degree",
        college="University",
        graduation_year="2026",
        skills_json=json.dumps(["JavaScript", "Python", "React", "HTML", "CSS"]),
        projects_json=json.dumps(["AI Job Assistant"]),
        bio=f"Passionate candidate interested in technology and software engineering opportunities."
    )
    db.add(profile)

    # Initialize App Settings with provided Email and App Password
    app_settings = AppSettings(
        user_id=new_user.id,
        auto_send=False,
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_username=new_user.email,
        smtp_password=payload.app_password.strip() if payload.app_password else "",
        sender_email=new_user.email,
        active_resume=""
    )
    db.add(app_settings)
    db.commit()

    token = create_token(new_user.id)
    return AuthResponse(
        token=token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or user.password_hash != hash_password(payload.password):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    token = create_token(user.id)
    return AuthResponse(
        token=token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

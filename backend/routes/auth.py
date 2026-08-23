import base64
import hashlib
import hmac
import json
import time
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.db import get_db
from backend.models.models import User, CandidateProfile, AppSettings
from backend.models.schemas import UserSignup, UserLogin, AuthResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])

SALT = b"ai_job_assistant_secure_salt_2026_stateless_v2"

def hash_password(password: str) -> str:
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT, 100000)
    return key.hex()

def create_token(user: User) -> str:
    payload = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "app_pass": user.app_password or "",
        "ts": int(time.time())
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    signature = hmac.new(SALT, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()[:16]
    return f"token_{payload_b64}_{signature}"

def decode_token(token: str) -> Optional[dict]:
    if not token:
        return None
    token_clean = token.strip().strip('"').strip("'")
    if not token_clean.startswith("token_"):
        return None
    try:
        parts = token_clean.split("_")
        if len(parts) < 3:
            return None
        payload_b64 = parts[1]
        signature = parts[2]

        expected_sig = hmac.new(SALT, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(signature, expected_sig):
            return None

        padding = "=" * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode((payload_b64 + padding).encode("utf-8")).decode("utf-8")
        return json.loads(payload_json)
    except Exception:
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

    payload = decode_token(token) if token else None
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in."
        )

    user_id = payload["id"]
    email = payload["email"]
    name = payload["name"]
    app_password = payload.get("app_pass")

    # Fetch user from current instance database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()

    # Re-provision user record on cold start Vercel instance if needed
    if not user:
        try:
            user = User(
                id=user_id,
                name=name,
                email=email,
                password_hash="stateless_session",
                app_password=app_password
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            user = db.query(User).filter(User.email == email).first()

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
        degree="",
        college="",
        graduation_year="",
        skills_json=json.dumps([]),
        projects_json=json.dumps([]),
        bio=""
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

    token = create_token(new_user)
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

    token = create_token(user)
    return AuthResponse(
        token=token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

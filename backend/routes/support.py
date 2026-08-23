from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.db import get_db
from backend.models.models import SupportTicket, User
from backend.models.schemas import SupportTicketCreate, SupportTicketResponse
from backend.routes.auth import get_optional_user

router = APIRouter(prefix="/api/support", tags=["Support"])

@router.post("/submit", response_model=SupportTicketResponse)
def submit_support_ticket(
    payload: SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    ticket = SupportTicket(
        user_id=current_user.id if current_user else None,
        name=current_user.name if current_user else "Guest User",
        email=current_user.email if current_user else "guest@example.com",
        subject=payload.subject.strip(),
        message=payload.message.strip(),
        status="OPEN"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return SupportTicketResponse.model_validate(ticket)


@router.get("/my-tickets", response_model=List[SupportTicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    if not current_user:
        return []
    tickets = db.query(SupportTicket).filter(SupportTicket.user_id == current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return [SupportTicketResponse.model_validate(t) for t in tickets]

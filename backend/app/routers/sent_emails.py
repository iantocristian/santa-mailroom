from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user
from app.models import User, SentEmail, Child
from app.schemas import SentEmailWithChild

router = APIRouter(prefix="/api/sent-emails", tags=["sent-emails"])


def get_family_child_ids(user: User, db: Session) -> List[int]:
    """Get all child IDs for the user's family."""
    if not user.family:
        return []
    return [c.id for c in user.family.children]


@router.get("", response_model=List[SentEmailWithChild])
def list_sent_emails(
    child_id: Optional[int] = Query(None, description="Filter by child ID"),
    email_type: Optional[str] = Query(None, description="Filter by type: letter_reply, deed_suggestion, deed_congrats"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List sent emails with optional filtering."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return []
    
    query = db.query(SentEmail).filter(SentEmail.child_id.in_(child_ids))
    
    if child_id is not None:
        if child_id not in child_ids:
            return []
        query = query.filter(SentEmail.child_id == child_id)
    
    if email_type is not None:
        query = query.filter(SentEmail.email_type == email_type)
    
    emails = query.order_by(SentEmail.sent_at.desc()).limit(limit).all()
    
    result = []
    for email in emails:
        child = db.query(Child).filter(Child.id == email.child_id).first()
        result.append(SentEmailWithChild(
            id=email.id,
            child_id=email.child_id,
            email_type=email.email_type,
            subject=email.subject,
            body_text=email.body_text,
            letter_id=email.letter_id,
            santa_reply_id=email.santa_reply_id,
            deed_id=email.deed_id,
            sent_at=email.sent_at,
            delivery_status=email.delivery_status,
            child_name=child.name if child else "Unknown"
        ))
    
    return result


@router.get("/{email_id}", response_model=SentEmailWithChild)
def get_sent_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific sent email."""
    child_ids = get_family_child_ids(current_user, db)
    
    email = db.query(SentEmail).filter(
        SentEmail.id == email_id,
        SentEmail.child_id.in_(child_ids)
    ).first()
    
    if not email:
        return None
    
    child = db.query(Child).filter(Child.id == email.child_id).first()
    
    return SentEmailWithChild(
        id=email.id,
        child_id=email.child_id,
        email_type=email.email_type,
        subject=email.subject,
        body_text=email.body_text,
        letter_id=email.letter_id,
        santa_reply_id=email.santa_reply_id,
        deed_id=email.deed_id,
        sent_at=email.sent_at,
        delivery_status=email.delivery_status,
        child_name=child.name if child else "Unknown"
    )

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models import User, ModerationFlag, Letter, Child
from app.schemas import ModerationFlagResponse, ModerationFlagUpdate, ModerationFlagWithContext

router = APIRouter(prefix="/api/moderation", tags=["moderation"])


def get_family_child_ids(user: User, db: Session) -> List[int]:
    """Get all child IDs for the user's family."""
    if not user.family:
        return []
    return [c.id for c in user.family.children]


@router.get("/flags", response_model=List[ModerationFlagWithContext])
def list_moderation_flags(
    reviewed: Optional[bool] = Query(None, description="Filter by review status"),
    severity: Optional[str] = Query(None, description="Filter by severity (low/medium/high)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List moderation flags with optional filtering."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return []
    
    query = db.query(ModerationFlag).join(Letter).filter(Letter.child_id.in_(child_ids))
    
    if reviewed is not None:
        query = query.filter(ModerationFlag.reviewed == reviewed)
    
    if severity is not None:
        query = query.filter(ModerationFlag.severity == severity)
    
    flags = query.order_by(ModerationFlag.created_at.desc()).all()
    
    result = []
    for flag in flags:
        letter = db.query(Letter).filter(Letter.id == flag.letter_id).first()
        child = db.query(Child).filter(Child.id == letter.child_id).first() if letter else None
        
        result.append(ModerationFlagWithContext(
            id=flag.id,
            letter_id=flag.letter_id,
            flag_type=flag.flag_type,
            severity=flag.severity,
            excerpt=flag.excerpt,
            ai_confidence=flag.ai_confidence,
            ai_explanation=flag.ai_explanation,
            reviewed=flag.reviewed,
            reviewed_at=flag.reviewed_at,
            action_taken=flag.action_taken,
            reviewer_note=flag.reviewer_note,
            created_at=flag.created_at,
            child_name=child.name if child else "Unknown",
            letter_subject=letter.subject if letter else None,
            letter_received_at=letter.received_at if letter else datetime.utcnow()
        ))
    
    return result


@router.get("/flags/{flag_id}", response_model=ModerationFlagWithContext)
def get_moderation_flag(
    flag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific moderation flag."""
    child_ids = get_family_child_ids(current_user, db)
    
    flag = db.query(ModerationFlag).join(Letter).filter(
        ModerationFlag.id == flag_id,
        Letter.child_id.in_(child_ids)
    ).first()
    
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moderation flag not found")
    
    letter = db.query(Letter).filter(Letter.id == flag.letter_id).first()
    child = db.query(Child).filter(Child.id == letter.child_id).first() if letter else None
    
    return ModerationFlagWithContext(
        id=flag.id,
        letter_id=flag.letter_id,
        flag_type=flag.flag_type,
        severity=flag.severity,
        excerpt=flag.excerpt,
        ai_confidence=flag.ai_confidence,
        ai_explanation=flag.ai_explanation,
        reviewed=flag.reviewed,
        reviewed_at=flag.reviewed_at,
        action_taken=flag.action_taken,
        reviewer_note=flag.reviewer_note,
        created_at=flag.created_at,
        child_name=child.name if child else "Unknown",
        letter_subject=letter.subject if letter else None,
        letter_received_at=letter.received_at if letter else datetime.utcnow()
    )


@router.put("/flags/{flag_id}", response_model=ModerationFlagResponse)
def resolve_moderation_flag(
    flag_id: int,
    flag_update: ModerationFlagUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a moderation flag."""
    child_ids = get_family_child_ids(current_user, db)
    
    flag = db.query(ModerationFlag).join(Letter).filter(
        ModerationFlag.id == flag_id,
        Letter.child_id.in_(child_ids)
    ).first()
    
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moderation flag not found")
    
    # Validate action_taken
    if flag_update.action_taken not in ["dismissed", "escalated", "noted"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action_taken must be 'dismissed', 'escalated', or 'noted'"
        )
    
    flag.reviewed = True
    flag.reviewed_at = datetime.utcnow()
    flag.action_taken = flag_update.action_taken
    if flag_update.reviewer_note:
        flag.reviewer_note = flag_update.reviewer_note
    
    db.commit()
    db.refresh(flag)
    
    return flag


@router.get("/stats")
def get_moderation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get moderation statistics."""
    from sqlalchemy import func
    
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return {
            "total_flags": 0,
            "pending_review": 0,
            "by_type": {},
            "by_severity": {}
        }
    
    base_query = db.query(ModerationFlag).join(Letter).filter(Letter.child_id.in_(child_ids))
    
    total_flags = base_query.count()
    pending_review = base_query.filter(ModerationFlag.reviewed == False).count()
    
    by_type = dict(
        base_query.with_entities(
            ModerationFlag.flag_type, func.count(ModerationFlag.id)
        ).group_by(ModerationFlag.flag_type).all()
    )
    
    by_severity = dict(
        base_query.with_entities(
            ModerationFlag.severity, func.count(ModerationFlag.id)
        ).group_by(ModerationFlag.severity).all()
    )
    
    return {
        "total_flags": total_flags,
        "pending_review": pending_review,
        "by_type": by_type,
        "by_severity": by_severity
    }

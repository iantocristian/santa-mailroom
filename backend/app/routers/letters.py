from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from collections import defaultdict

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Letter, WishItem, SantaReply, ModerationFlag, Child
from app.schemas import LetterResponse, LetterWithDetails, LetterTimeline, WishItemResponse, SantaReplyResponse, ModerationFlagResponse

router = APIRouter(prefix="/api/letters", tags=["letters"])


def get_family_child_ids(user: User, db: Session) -> List[int]:
    """Get all child IDs for the user's family."""
    if not user.family:
        return []
    return [c.id for c in user.family.children]


@router.get("", response_model=List[LetterWithDetails])
def list_letters(
    child_id: Optional[int] = Query(None, description="Filter by child ID"),
    year: Optional[int] = Query(None, description="Filter by Christmas year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List letters with optional filtering."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return []
    
    query = db.query(Letter).filter(Letter.child_id.in_(child_ids))
    
    if child_id is not None:
        if child_id not in child_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child not in your family")
        query = query.filter(Letter.child_id == child_id)
    
    if year is not None:
        query = query.filter(Letter.year == year)
    
    letters = query.order_by(Letter.received_at.desc()).all()
    
    # Build response with details
    result = []
    for letter in letters:
        child = db.query(Child).filter(Child.id == letter.child_id).first()
        result.append(LetterWithDetails(
            id=letter.id,
            child_id=letter.child_id,
            year=letter.year,
            subject=letter.subject,
            body_text=letter.body_text,
            received_at=letter.received_at,
            status=letter.status,
            processed_at=letter.processed_at,
            created_at=letter.created_at,
            child_name=child.name if child else None,
            wish_items=[WishItemResponse.model_validate(item) for item in letter.wish_items],
            santa_reply=SantaReplyResponse.model_validate(letter.santa_reply) if letter.santa_reply else None,
            moderation_flags=[ModerationFlagResponse.model_validate(flag) for flag in letter.moderation_flags]
        ))
    
    return result


@router.get("/timeline", response_model=List[LetterTimeline])
def get_timeline(
    child_id: Optional[int] = Query(None, description="Filter by child ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get timeline/scrapbook view grouped by year."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return []
    
    query = db.query(Letter).filter(Letter.child_id.in_(child_ids))
    
    if child_id is not None:
        if child_id not in child_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child not in your family")
        query = query.filter(Letter.child_id == child_id)
    
    letters = query.order_by(Letter.year.desc(), Letter.received_at.desc()).all()
    
    # Group by year
    by_year = defaultdict(list)
    for letter in letters:
        child = db.query(Child).filter(Child.id == letter.child_id).first()
        letter_detail = LetterWithDetails(
            id=letter.id,
            child_id=letter.child_id,
            year=letter.year,
            subject=letter.subject,
            body_text=letter.body_text,
            received_at=letter.received_at,
            status=letter.status,
            processed_at=letter.processed_at,
            created_at=letter.created_at,
            child_name=child.name if child else None,
            wish_items=[WishItemResponse.model_validate(item) for item in letter.wish_items],
            santa_reply=SantaReplyResponse.model_validate(letter.santa_reply) if letter.santa_reply else None,
            moderation_flags=[ModerationFlagResponse.model_validate(flag) for flag in letter.moderation_flags]
        )
        by_year[letter.year].append(letter_detail)
    
    return [
        LetterTimeline(year=year, letters=letters_list)
        for year, letters_list in sorted(by_year.items(), reverse=True)
    ]


@router.get("/{letter_id}", response_model=LetterWithDetails)
def get_letter(
    letter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific letter with all details."""
    child_ids = get_family_child_ids(current_user, db)
    
    letter = db.query(Letter).filter(
        Letter.id == letter_id,
        Letter.child_id.in_(child_ids)
    ).first()
    
    if not letter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Letter not found")
    
    child = db.query(Child).filter(Child.id == letter.child_id).first()
    
    return LetterWithDetails(
        id=letter.id,
        child_id=letter.child_id,
        year=letter.year,
        subject=letter.subject,
        body_text=letter.body_text,
        received_at=letter.received_at,
        status=letter.status,
        processed_at=letter.processed_at,
        created_at=letter.created_at,
        child_name=child.name if child else None,
        wish_items=[WishItemResponse.model_validate(item) for item in letter.wish_items],
        santa_reply=SantaReplyResponse.model_validate(letter.santa_reply) if letter.santa_reply else None,
        moderation_flags=[ModerationFlagResponse.model_validate(flag) for flag in letter.moderation_flags]
    )


@router.get("/years/available")
def get_available_years(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of years that have letters."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return {"years": []}
    
    years = db.query(Letter.year).filter(
        Letter.child_id.in_(child_ids)
    ).distinct().order_by(Letter.year.desc()).all()
    
    return {"years": [y[0] for y in years]}

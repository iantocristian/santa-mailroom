from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user, require_write_access
from app.models import User, GoodDeed, Child
from app.schemas import GoodDeedCreate, GoodDeedUpdate, GoodDeedResponse, GoodDeedWithChild
from app.job_queue import Job

router = APIRouter(prefix="/api/deeds", tags=["good-deeds"])


def get_family_child_ids(user: User, db: Session) -> List[int]:
    """Get all child IDs for the user's family."""
    if not user.family:
        return []
    return [c.id for c in user.family.children]


@router.get("", response_model=List[GoodDeedWithChild])
def list_good_deeds(
    child_id: Optional[int] = Query(None, description="Filter by child ID"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List good deeds with optional filtering."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return []
    
    query = db.query(GoodDeed).filter(GoodDeed.child_id.in_(child_ids))
    
    if child_id is not None:
        if child_id not in child_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child not in your family")
        query = query.filter(GoodDeed.child_id == child_id)
    
    if completed is not None:
        query = query.filter(GoodDeed.completed == completed)
    
    deeds = query.order_by(GoodDeed.suggested_at.desc()).all()
    
    result = []
    for deed in deeds:
        child = db.query(Child).filter(Child.id == deed.child_id).first()
        result.append(GoodDeedWithChild(
            id=deed.id,
            child_id=deed.child_id,
            description=deed.description,
            suggested_at=deed.suggested_at,
            completed=deed.completed,
            completed_at=deed.completed_at,
            parent_note=deed.parent_note,
            child_name=child.name if child else "Unknown"
        ))
    
    return result


@router.post("", response_model=GoodDeedResponse, status_code=status.HTTP_201_CREATED)
def create_good_deed(
    deed_data: GoodDeedCreate,
    send_email: bool = Query(True, description="Send notification email to child"),
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Suggest a new good deed for a child."""
    child_ids = get_family_child_ids(current_user, db)
    
    if deed_data.child_id not in child_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Child not in your family"
        )
    
    deed = GoodDeed(
        child_id=deed_data.child_id,
        description=deed_data.description
    )
    
    db.add(deed)
    db.commit()
    db.refresh(deed)
    
    # Queue email notification if requested
    if send_email:
        job = Job(
            task_type="send_deed_email",
            payload={"deed_id": deed.id},
            priority=1
        )
        db.add(job)
        db.commit()
    
    return deed


@router.get("/{deed_id}", response_model=GoodDeedWithChild)
def get_good_deed(
    deed_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific good deed."""
    child_ids = get_family_child_ids(current_user, db)
    
    deed = db.query(GoodDeed).filter(
        GoodDeed.id == deed_id,
        GoodDeed.child_id.in_(child_ids)
    ).first()
    
    if not deed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Good deed not found")
    
    child = db.query(Child).filter(Child.id == deed.child_id).first()
    
    return GoodDeedWithChild(
        id=deed.id,
        child_id=deed.child_id,
        description=deed.description,
        suggested_at=deed.suggested_at,
        completed=deed.completed,
        completed_at=deed.completed_at,
        parent_note=deed.parent_note,
        child_name=child.name if child else "Unknown"
    )


@router.put("/{deed_id}", response_model=GoodDeedResponse)
def update_good_deed(
    deed_id: int,
    deed_update: GoodDeedUpdate,
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Update a good deed (mark as completed, add note)."""
    child_ids = get_family_child_ids(current_user, db)
    
    deed = db.query(GoodDeed).filter(
        GoodDeed.id == deed_id,
        GoodDeed.child_id.in_(child_ids)
    ).first()
    
    if not deed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Good deed not found")
    
    update_data = deed_update.model_dump(exclude_unset=True)
    
    # Set completed_at timestamp when marking as completed
    if "completed" in update_data and update_data["completed"] and not deed.completed:
        deed.completed_at = datetime.utcnow()
    elif "completed" in update_data and not update_data["completed"]:
        deed.completed_at = None
    
    for field, value in update_data.items():
        setattr(deed, field, value)
    
    db.commit()
    db.refresh(deed)
    
    return deed


@router.post("/{deed_id}/complete", response_model=GoodDeedResponse)
def complete_good_deed(
    deed_id: int,
    body: Optional[dict] = None,
    send_email: bool = Query(True, description="Send congratulations email to child"),
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Mark a good deed as completed."""
    child_ids = get_family_child_ids(current_user, db)
    
    deed = db.query(GoodDeed).filter(
        GoodDeed.id == deed_id,
        GoodDeed.child_id.in_(child_ids)
    ).first()
    
    if not deed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Good deed not found")
    
    deed.completed = True
    deed.completed_at = datetime.utcnow()
    
    # Extract parent_note from body if provided
    parent_note = body.get("parent_note") if body else None
    if parent_note:
        deed.parent_note = parent_note
    
    db.commit()
    db.refresh(deed)
    
    # Queue congratulations email if requested
    if send_email:
        job = Job(
            task_type="send_deed_congrats",
            payload={"deed_id": deed.id},
            priority=1
        )
        db.add(job)
        db.commit()
    
    return deed


@router.delete("/{deed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_good_deed(
    deed_id: int,
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Delete a good deed."""
    child_ids = get_family_child_ids(current_user, db)
    
    deed = db.query(GoodDeed).filter(
        GoodDeed.id == deed_id,
        GoodDeed.child_id.in_(child_ids)
    ).first()
    
    if not deed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Good deed not found")
    
    db.delete(deed)
    db.commit()

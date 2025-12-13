from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user, require_write_access
from app.models import User, Notification
from app.schemas import NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationResponse])
def list_notifications(
    unread_only: bool = Query(False, description="Only show unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notifications for the current user's family."""
    if not current_user.family:
        return []
    
    query = db.query(Notification).filter(Notification.family_id == current_user.family.id)
    
    if unread_only:
        query = query.filter(Notification.read == False)
    
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


@router.get("/count")
def get_notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications."""
    if not current_user.family:
        return {"unread_count": 0}
    
    count = db.query(Notification).filter(
        Notification.family_id == current_user.family.id,
        Notification.read == False
    ).count()
    
    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification."""
    if not current_user.family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.family_id == current_user.family.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    return notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    if not current_user.family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.family_id == current_user.family.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    notification.read = True
    db.commit()
    db.refresh(notification)
    
    return notification


@router.post("/read-all")
def mark_all_read(
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read."""
    if not current_user.family:
        return {"updated_count": 0}
    
    updated = db.query(Notification).filter(
        Notification.family_id == current_user.family.id,
        Notification.read == False
    ).update({"read": True})
    
    db.commit()
    
    return {"updated_count": updated}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Delete a notification."""
    if not current_user.family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.family_id == current_user.family.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    db.delete(notification)
    db.commit()

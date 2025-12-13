from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth import get_current_user, require_write_access
from app.models import User, Family
from app.schemas import FamilyResponse, FamilyUpdate, FamilyStats, FamilyCreate
from app.config import get_settings
from app.rate_limit import limiter, RATE_LIMITS

router = APIRouter(prefix="/api/family", tags=["family"])
settings = get_settings()


def build_santa_email(santa_code: str) -> str:
    """Build the full Santa email address for a family code."""
    base_email = settings.santa_email_address or "santaclausgotmail@gmail.com"
    local, domain = base_email.split("@")
    return f"{local}+{santa_code}@{domain}"


@router.get("", response_model=FamilyResponse)
@limiter.limit(RATE_LIMITS["default"])
def get_family(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's family."""
    if not current_user.family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found. Please create a family first."
        )
    family = current_user.family
    # Add computed santa_email
    response = FamilyResponse.model_validate(family)
    response.santa_email = build_santa_email(family.santa_code)
    return response


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(
    family_data: FamilyCreate,
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Create a family for the current user."""
    if current_user.family:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a family"
        )
    
    family = Family(
        owner_id=current_user.id,
        name=family_data.name or f"{current_user.name or 'My'} Family"
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


@router.put("", response_model=FamilyResponse)
def update_family(
    family_update: FamilyUpdate,
    current_user: User = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    """Update family settings."""
    if not current_user.family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    family = current_user.family
    update_data = family_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(family, field, value)
    
    db.commit()
    db.refresh(family)
    return family


@router.get("/stats", response_model=FamilyStats)
@limiter.limit(RATE_LIMITS["default"])
def get_family_stats(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the family."""
    from app.models import Child, Letter, WishItem, Notification, ModerationFlag, GoodDeed
    from sqlalchemy import func
    
    # Return empty stats if no family yet
    if not current_user.family:
        return FamilyStats(
            total_children=0, total_letters=0, total_wish_items=0,
            pending_wish_items=0, approved_wish_items=0, denied_wish_items=0,
            total_estimated_budget=None, unread_notifications=0,
            pending_moderation_flags=0, completed_deeds=0, pending_deeds=0
        )
    
    family_id = current_user.family.id
    
    # Get child IDs for this family
    child_ids = [c.id for c in current_user.family.children]
    
    # Count children
    total_children = len(child_ids)
    
    # Count letters
    total_letters = db.query(Letter).filter(Letter.child_id.in_(child_ids)).count() if child_ids else 0
    
    # Count wish items by status
    wish_items_query = db.query(WishItem).join(Letter).filter(Letter.child_id.in_(child_ids)) if child_ids else None
    
    if wish_items_query:
        total_wish_items = wish_items_query.count()
        pending_wish_items = wish_items_query.filter(WishItem.status == "pending").count()
        approved_wish_items = wish_items_query.filter(WishItem.status == "approved").count()
        denied_wish_items = wish_items_query.filter(WishItem.status == "denied").count()
        
        # Calculate total estimated budget for approved items
        total_budget = db.query(func.sum(WishItem.estimated_price)).join(Letter).filter(
            Letter.child_id.in_(child_ids),
            WishItem.status == "approved",
            WishItem.estimated_price.isnot(None)
        ).scalar()
    else:
        total_wish_items = pending_wish_items = approved_wish_items = denied_wish_items = 0
        total_budget = None
    
    # Count unread notifications
    unread_notifications = db.query(Notification).filter(
        Notification.family_id == family_id,
        Notification.read == False
    ).count()
    
    # Count pending moderation flags
    pending_flags = db.query(ModerationFlag).join(Letter).filter(
        Letter.child_id.in_(child_ids),
        ModerationFlag.reviewed == False
    ).count() if child_ids else 0
    
    # Count good deeds
    if child_ids:
        completed_deeds = db.query(GoodDeed).filter(
            GoodDeed.child_id.in_(child_ids),
            GoodDeed.completed == True
        ).count()
        pending_deeds = db.query(GoodDeed).filter(
            GoodDeed.child_id.in_(child_ids),
            GoodDeed.completed == False
        ).count()
    else:
        completed_deeds = pending_deeds = 0
    
    return FamilyStats(
        total_children=total_children,
        total_letters=total_letters,
        total_wish_items=total_wish_items,
        pending_wish_items=pending_wish_items,
        approved_wish_items=approved_wish_items,
        denied_wish_items=denied_wish_items,
        total_estimated_budget=total_budget,
        unread_notifications=unread_notifications,
        pending_moderation_flags=pending_flags,
        completed_deeds=completed_deeds,
        pending_deeds=pending_deeds
    )

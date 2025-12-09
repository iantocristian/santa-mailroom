from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from app.database import get_db
from app.auth import get_current_user
from app.models import User, WishItem, Letter, Child
from app.schemas import WishItemResponse, WishItemUpdate, WishlistSummary

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


def get_family_child_ids(user: User, db: Session) -> List[int]:
    """Get all child IDs for the user's family."""
    if not user.family:
        return []
    return [c.id for c in user.family.children]


@router.get("", response_model=List[WishItemResponse])
def list_wish_items(
    child_id: Optional[int] = Query(None, description="Filter by child ID"),
    year: Optional[int] = Query(None, description="Filter by Christmas year"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (pending/approved/denied)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List wish items with optional filtering."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return []
    
    query = db.query(WishItem).join(Letter).filter(Letter.child_id.in_(child_ids))
    
    if child_id is not None:
        if child_id not in child_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child not in your family")
        query = query.filter(Letter.child_id == child_id)
    
    if year is not None:
        query = query.filter(Letter.year == year)
    
    if category is not None:
        query = query.filter(WishItem.category == category)
    
    if status is not None:
        query = query.filter(WishItem.status == status)
    
    return query.order_by(WishItem.created_at.desc()).all()


@router.get("/summary", response_model=WishlistSummary)
def get_wishlist_summary(
    child_id: Optional[int] = Query(None, description="Filter by child ID"),
    year: Optional[int] = Query(None, description="Filter by Christmas year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wishlist summary statistics."""
    child_ids = get_family_child_ids(current_user, db)
    
    if not child_ids:
        return WishlistSummary(
            total_items=0,
            by_status={},
            by_category={},
            total_estimated_cost=None,
            by_child={}
        )
    
    base_query = db.query(WishItem).join(Letter).filter(Letter.child_id.in_(child_ids))
    
    if child_id is not None:
        if child_id not in child_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child not in your family")
        base_query = base_query.filter(Letter.child_id == child_id)
    
    if year is not None:
        base_query = base_query.filter(Letter.year == year)
    
    # Total items
    total_items = base_query.count()
    
    # By status
    status_counts = db.query(
        WishItem.status, func.count(WishItem.id)
    ).join(Letter).filter(
        Letter.child_id.in_(child_ids)
    )
    if year is not None:
        status_counts = status_counts.filter(Letter.year == year)
    status_counts = status_counts.group_by(WishItem.status).all()
    by_status = {s: c for s, c in status_counts}
    
    # By category
    category_counts = db.query(
        WishItem.category, func.count(WishItem.id)
    ).join(Letter).filter(
        Letter.child_id.in_(child_ids),
        WishItem.category.isnot(None)
    )
    if year is not None:
        category_counts = category_counts.filter(Letter.year == year)
    category_counts = category_counts.group_by(WishItem.category).all()
    by_category = {c or "uncategorized": count for c, count in category_counts}
    
    # Total estimated cost (for approved items)
    total_cost_query = db.query(func.sum(WishItem.estimated_price)).join(Letter).filter(
        Letter.child_id.in_(child_ids),
        WishItem.status == "approved",
        WishItem.estimated_price.isnot(None)
    )
    if year is not None:
        total_cost_query = total_cost_query.filter(Letter.year == year)
    total_estimated_cost = total_cost_query.scalar()
    
    # By child
    child_counts = db.query(
        Child.name, func.count(WishItem.id)
    ).join(Letter, Letter.child_id == Child.id).join(
        WishItem, WishItem.letter_id == Letter.id
    ).filter(Child.id.in_(child_ids))
    if year is not None:
        child_counts = child_counts.filter(Letter.year == year)
    child_counts = child_counts.group_by(Child.name).all()
    by_child = {name: count for name, count in child_counts}
    
    return WishlistSummary(
        total_items=total_items,
        by_status=by_status,
        by_category=by_category,
        total_estimated_cost=total_estimated_cost,
        by_child=by_child
    )


@router.get("/{item_id}", response_model=WishItemResponse)
def get_wish_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific wish item."""
    child_ids = get_family_child_ids(current_user, db)
    
    item = db.query(WishItem).join(Letter).filter(
        WishItem.id == item_id,
        Letter.child_id.in_(child_ids)
    ).first()
    
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish item not found")
    
    return item


@router.put("/{item_id}", response_model=WishItemResponse)
def update_wish_item(
    item_id: int,
    item_update: WishItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a wish item (approve/deny - reality filter)."""
    child_ids = get_family_child_ids(current_user, db)
    
    item = db.query(WishItem).join(Letter).filter(
        WishItem.id == item_id,
        Letter.child_id.in_(child_ids)
    ).first()
    
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish item not found")
    
    update_data = item_update.model_dump(exclude_unset=True)
    
    # Validate status
    if "status" in update_data:
        if update_data["status"] not in ["pending", "approved", "denied"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'pending', 'approved', or 'denied'"
            )
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item

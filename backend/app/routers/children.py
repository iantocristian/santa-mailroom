from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import hashlib

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Child, Letter, WishItem, GoodDeed
from app.schemas import ChildCreate, ChildUpdate, ChildResponse, ChildWithStats

router = APIRouter(prefix="/api/children", tags=["children"])


def hash_email(email: str) -> str:
    """Hash an email address using SHA-256."""
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()


@router.get("", response_model=List[ChildWithStats])
def list_children(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all children in the current user's family."""
    if not current_user.family:
        return []  # No family yet, return empty list
    
    children = current_user.family.children
    result = []
    
    for child in children:
        letter_count = db.query(Letter).filter(Letter.child_id == child.id).count()
        wish_item_count = db.query(WishItem).join(Letter).filter(Letter.child_id == child.id).count()
        pending_deeds = db.query(GoodDeed).filter(
            GoodDeed.child_id == child.id,
            GoodDeed.completed == False
        ).count()
        completed_deeds = db.query(GoodDeed).filter(
            GoodDeed.child_id == child.id,
            GoodDeed.completed == True
        ).count()
        
        result.append(ChildWithStats(
            id=child.id,
            name=child.name,
            country=child.country,
            birth_year=child.birth_year,
            avatar_url=child.avatar_url,
            created_at=child.created_at,
            letter_count=letter_count,
            wish_item_count=wish_item_count,
            pending_deeds=pending_deeds,
            completed_deeds=completed_deeds
        ))
    
    return result


@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(
    child_data: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a new child."""
    if not current_user.family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found. Please create a family first."
        )
    
    email_hash = hash_email(child_data.email)
    
    # Check if child with this email already exists in this family
    existing = db.query(Child).filter(
        Child.family_id == current_user.family.id,
        Child.email_hash == email_hash
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A child with this email is already registered"
        )
    
    child = Child(
        family_id=current_user.family.id,
        name=child_data.name,
        email_hash=email_hash,
        country=child_data.country,
        birth_year=child_data.birth_year,
        avatar_url=child_data.avatar_url
    )
    
    db.add(child)
    db.commit()
    db.refresh(child)
    
    return child


@router.get("/{child_id}", response_model=ChildWithStats)
def get_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific child's details."""
    if not current_user.family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.family_id == current_user.family.id
    ).first()
    
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    
    letter_count = db.query(Letter).filter(Letter.child_id == child.id).count()
    wish_item_count = db.query(WishItem).join(Letter).filter(Letter.child_id == child.id).count()
    pending_deeds = db.query(GoodDeed).filter(
        GoodDeed.child_id == child.id,
        GoodDeed.completed == False
    ).count()
    completed_deeds = db.query(GoodDeed).filter(
        GoodDeed.child_id == child.id,
        GoodDeed.completed == True
    ).count()
    
    return ChildWithStats(
        id=child.id,
        name=child.name,
        country=child.country,
        birth_year=child.birth_year,
        avatar_url=child.avatar_url,
        created_at=child.created_at,
        letter_count=letter_count,
        wish_item_count=wish_item_count,
        pending_deeds=pending_deeds,
        completed_deeds=completed_deeds
    )


@router.put("/{child_id}", response_model=ChildResponse)
def update_child(
    child_id: int,
    child_update: ChildUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a child's details."""
    if not current_user.family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.family_id == current_user.family.id
    ).first()
    
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    
    update_data = child_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(child, field, value)
    
    db.commit()
    db.refresh(child)
    
    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a child and all their data."""
    if not current_user.family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.family_id == current_user.family.id
    ).first()
    
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    
    db.delete(child)
    db.commit()

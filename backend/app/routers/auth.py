from datetime import datetime, timedelta
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Family, InviteCode
from app.schemas import UserCreate, UserResponse, Token
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()

# Word lists for friendly family codes
ADJECTIVES = [
    "Snow", "Frost", "Jolly", "Merry", "Cozy", "Bright", "Sparkle", "Twinkle",
    "Golden", "Silver", "Crystal", "Velvet", "Rosy", "Starry", "Candy", "Ginger",
    "Holly", "Ivy", "Cocoa", "Maple", "Winter", "Arctic", "Nordic", "Alpine",
    "Sugar", "Plum", "Cherry", "Mint", "Snowy"
]

ANIMALS = [
    "Polar", "Owl", "Fox", "Bear", "Bunny", "Panda", "Koala", "Otter",
    "Seal", "Husky", "Wolf", "Dove", "Robin", "Finch", "Swan", "Deer",
    "Elk", "Moose", "Beaver", "Lynx", "Hare"
]


def generate_santa_code(db: Session) -> str:
    """Generate a unique friendly word code for a family (e.g., SnowPanda)."""
    while True:
        adjective = secrets.choice(ADJECTIVES)
        animal = secrets.choice(ANIMALS)
        code = f"{adjective}{animal}"
        # Check uniqueness
        existing = db.query(Family).filter(Family.santa_code == code).first()
        if not existing:
            return code


def validate_invite_code(db: Session, code: str) -> InviteCode:
    """Validate an invite code and return the InviteCode object if valid."""
    invite = db.query(InviteCode).filter(InviteCode.code == code).first()
    
    if not invite:
        return None
    
    # Check if already used
    if invite.used_at:
        return None
    
    # Check if active
    if not invite.is_active:
        return None
    
    # Check expiry
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        return None
    
    return invite


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Validate invite code
    invite = validate_invite_code(db, user.invite_token)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invite code"
        )
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    password_bytes = user.password.encode("utf-8")
    # Create new user
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 72 bytes or fewer"
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        invite_code_id=invite.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Mark invite code as used
    invite.used_at = datetime.utcnow()
    db.add(invite)
    db.commit()
    
    # Auto-create a family for the new user with unique santa code
    santa_code = generate_santa_code(db)
    family = Family(
        owner_id=db_user.id,
        name=f"{db_user.name or 'My'} Family",
        santa_code=santa_code
    )
    db.add(family)
    db.commit()
    
    return db_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


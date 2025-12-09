from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from app.database import get_db
from app.models import User
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


def verify_invite_token(token: str) -> bool:
    """Verify the invite token signature using Ed25519 public key."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Verifying invite token: {token[:50]}...")
    logger.info(f"Public key configured: {bool(settings.invite_public_key)}")
    
    if not settings.invite_public_key:
        logger.error("Invite public key not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invite system not configured"
        )
    try:
        # Load the public key (handle escaped newlines from .env)
        key_pem = settings.invite_public_key.replace("\\n", "\n")
        logger.info(f"Key PEM starts with: {key_pem[:50]}")
        
        public_key = serialization.load_pem_public_key(key_pem.encode())
        logger.info(f"Public key type: {type(public_key)}")
        
        if not isinstance(public_key, Ed25519PublicKey):
            logger.error(f"Wrong key type: {type(public_key)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid public key type"
            )
        # Decode and verify the JWT with EdDSA algorithm
        jwt.decode(token, public_key, algorithms=["EdDSA"])
        logger.info("Token verified successfully")
        return True
    except InvalidTokenError as e:
        logger.error(f"Invalid token error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        return False


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verify invite token signature
    if not verify_invite_token(user.invite_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite token"
        )
    
    # Check if invite token already used
    existing_token = db.query(User).filter(User.invite_token == user.invite_token).first()
    if existing_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite token already used"
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
        invite_token=user.invite_token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
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


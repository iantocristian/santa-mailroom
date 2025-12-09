from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    Boolean, Numeric, Float, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# Enums
class LetterStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    PROCESSED = "processed"
    FAILED = "failed"


class WishItemStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class DenialReason(str, enum.Enum):
    TOO_EXPENSIVE = "too_expensive"
    VIOLENT = "violent"
    AGE_INAPPROPRIATE = "age_inappropriate"
    NOT_AVAILABLE = "not_available"
    OTHER = "other"


class ModerationSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NotificationType(str, enum.Enum):
    NEW_LETTER = "new_letter"
    BUDGET_ALERT = "budget_alert"
    MODERATION_FLAG = "moderation_flag"
    DEED_COMPLETED = "deed_completed"


# Models

class User(Base):
    """Parent account - manages a family"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100))
    invite_token = Column(String(512), unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to family
    family = relationship("Family", back_populates="owner", uselist=False)


class Family(Base):
    """Tenant/family unit with settings"""
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String(100))  # e.g., "The Smith Family"
    
    # Settings
    language = Column(String(10), default="en")
    budget_alert_threshold = Column(Numeric(10, 2), nullable=True)
    moderation_strictness = Column(String(20), default="medium")  # low/medium/high
    data_retention_years = Column(Integer, default=5)
    timezone = Column(String(50), default="UTC")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="family")
    children = relationship("Child", back_populates="family", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="family", cascade="all, delete-orphan")


class Child(Base):
    """Registered child who can email Santa"""
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Display name/nickname
    email_hash = Column(String(64), nullable=False, index=True)  # SHA-256 of lowercase email
    country = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2 country code
    birth_year = Column(Integer, nullable=True)  # For age-appropriate filtering
    avatar_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    family = relationship("Family", back_populates="children")
    letters = relationship("Letter", back_populates="child", cascade="all, delete-orphan")
    good_deeds = relationship("GoodDeed", back_populates="child", cascade="all, delete-orphan")


class Letter(Base):
    """Incoming email from a child to Santa"""
    __tablename__ = "letters"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    year = Column(Integer, nullable=False)  # Christmas year this letter is for
    
    # Email content
    subject = Column(String(500), nullable=True)
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=False)
    message_id = Column(String(200), unique=True, nullable=True)  # Email Message-ID header
    from_email = Column(String(255), nullable=True)  # Original sender (for reference)
    
    # Processing status
    status = Column(String(20), default=LetterStatus.PENDING.value)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)  # If processing failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    child = relationship("Child", back_populates="letters")
    wish_items = relationship("WishItem", back_populates="letter", cascade="all, delete-orphan")
    santa_reply = relationship("SantaReply", back_populates="letter", uselist=False, cascade="all, delete-orphan")
    moderation_flags = relationship("ModerationFlag", back_populates="letter", cascade="all, delete-orphan")


class WishItem(Base):
    """Extracted wish item from a letter"""
    __tablename__ = "wish_items"

    id = Column(Integer, primary_key=True, index=True)
    letter_id = Column(Integer, ForeignKey("letters.id"), nullable=False)
    
    # Extracted info
    raw_text = Column(String(500), nullable=False)  # Original mention from letter
    normalized_name = Column(String(200), nullable=True)  # Cleaned up name
    category = Column(String(50), nullable=True)  # toys, books, clothes, electronics, games, etc.
    
    # Parent filtering (reality filter)
    status = Column(String(20), default=WishItemStatus.PENDING.value)
    denial_reason = Column(String(50), nullable=True)
    denial_note = Column(String(500), nullable=True)  # Parent's note about why denied
    
    # Product search results (via OpenAI web search)
    estimated_price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD")
    product_url = Column(String(1000), nullable=True)
    product_image_url = Column(String(1000), nullable=True)
    product_description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    letter = relationship("Letter", back_populates="wish_items")


class SantaReply(Base):
    """Generated reply from Santa to a child"""
    __tablename__ = "santa_replies"

    id = Column(Integer, primary_key=True, index=True)
    letter_id = Column(Integer, ForeignKey("letters.id"), nullable=False, unique=True)
    
    # Content
    body_text = Column(Text, nullable=False)  # Plain text version
    body_html = Column(Text, nullable=True)  # Rendered HTML with template
    
    # Suggested good deed for this reply
    suggested_deed = Column(String(500), nullable=True)
    
    # Delivery status
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivery_status = Column(String(20), default="pending")  # pending/sent/failed
    delivery_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    letter = relationship("Letter", back_populates="santa_reply")


class GoodDeed(Base):
    """Kindness mechanic - suggested and tracked good deeds"""
    __tablename__ = "good_deeds"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    
    description = Column(String(500), nullable=False)
    suggested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Completion tracking
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    parent_note = Column(String(500), nullable=True)  # Parent's note when marking complete
    
    # Link to the reply where it was suggested
    suggested_in_reply_id = Column(Integer, ForeignKey("santa_replies.id"), nullable=True)
    # Link to the reply where Santa acknowledged completion
    acknowledged_in_reply_id = Column(Integer, ForeignKey("santa_replies.id"), nullable=True)

    # Relationships
    child = relationship("Child", back_populates="good_deeds")


class ModerationFlag(Base):
    """Content moderation flags for concerning content"""
    __tablename__ = "moderation_flags"

    id = Column(Integer, primary_key=True, index=True)
    letter_id = Column(Integer, ForeignKey("letters.id"), nullable=False)
    
    # Flag details
    flag_type = Column(String(50), nullable=False)  # self_harm, bullying, abuse, sad, anxious, violence
    severity = Column(String(20), default=ModerationSeverity.MEDIUM.value)
    excerpt = Column(Text, nullable=True)  # The concerning snippet from the letter
    ai_confidence = Column(Float, nullable=True)  # Confidence score from classifier (0-1)
    ai_explanation = Column(Text, nullable=True)  # AI's reasoning
    
    # Resolution by parent
    reviewed = Column(Boolean, default=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    action_taken = Column(String(50), nullable=True)  # dismissed/escalated/noted
    reviewer_note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    letter = relationship("Letter", back_populates="moderation_flags")


class Notification(Base):
    """Parent notifications"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    
    type = Column(String(50), nullable=False)  # new_letter, budget_alert, moderation_flag, deed_completed
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=True)
    read = Column(Boolean, default=False)
    
    # Links to related entities
    related_letter_id = Column(Integer, ForeignKey("letters.id"), nullable=True)
    related_child_id = Column(Integer, ForeignKey("children.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    family = relationship("Family", back_populates="notifications")

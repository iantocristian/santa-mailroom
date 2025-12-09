from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# ============== Auth Schemas ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    invite_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ============== Family Schemas ==============

class FamilyCreate(BaseModel):
    name: Optional[str] = None


class FamilyUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    budget_alert_threshold: Optional[Decimal] = None
    moderation_strictness: Optional[str] = None  # low/medium/high
    data_retention_years: Optional[int] = None
    timezone: Optional[str] = None


class FamilyResponse(BaseModel):
    id: int
    name: Optional[str] = None
    language: str = "en"
    budget_alert_threshold: Optional[Decimal] = None
    moderation_strictness: str = "medium"
    data_retention_years: int = 5
    timezone: str = "UTC"
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyStats(BaseModel):
    total_children: int
    total_letters: int
    total_wish_items: int
    pending_wish_items: int
    approved_wish_items: int
    denied_wish_items: int
    total_estimated_budget: Optional[Decimal]
    unread_notifications: int
    pending_moderation_flags: int
    completed_deeds: int
    pending_deeds: int


# ============== Child Schemas ==============

class ChildCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Will be hashed before storage
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    avatar_url: Optional[str] = None


class ChildUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    avatar_url: Optional[str] = None


class ChildResponse(BaseModel):
    id: int
    name: str
    country: Optional[str]
    birth_year: Optional[int]
    avatar_url: Optional[str]
    created_at: datetime
    letter_count: Optional[int] = None  # Computed field

    class Config:
        from_attributes = True


class ChildWithStats(ChildResponse):
    letter_count: int
    wish_item_count: int
    pending_deeds: int
    completed_deeds: int


# ============== Letter Schemas ==============

class LetterResponse(BaseModel):
    id: int
    child_id: int
    year: int
    subject: Optional[str]
    body_text: str
    received_at: datetime
    status: str
    processed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class LetterWithDetails(LetterResponse):
    child_name: Optional[str] = None
    wish_items: List["WishItemResponse"] = []
    santa_reply: Optional["SantaReplyResponse"] = None
    moderation_flags: List["ModerationFlagResponse"] = []


class LetterTimeline(BaseModel):
    """For scrapbook/timeline view"""
    year: int
    letters: List[LetterWithDetails]


# ============== WishItem Schemas ==============

class WishItemResponse(BaseModel):
    id: int
    letter_id: int
    raw_text: str
    normalized_name: Optional[str]
    category: Optional[str]
    status: str
    denial_reason: Optional[str]
    denial_note: Optional[str]
    estimated_price: Optional[Decimal]
    currency: str
    product_url: Optional[str]
    product_image_url: Optional[str]
    product_description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WishItemUpdate(BaseModel):
    status: Optional[str] = None  # pending/approved/denied
    denial_reason: Optional[str] = None
    denial_note: Optional[str] = None


class WishlistFilter(BaseModel):
    child_id: Optional[int] = None
    year: Optional[int] = None
    category: Optional[str] = None
    status: Optional[str] = None


class WishlistSummary(BaseModel):
    total_items: int
    by_status: dict[str, int]  # pending: 5, approved: 10, denied: 2
    by_category: dict[str, int]  # toys: 8, books: 3, clothes: 2
    total_estimated_cost: Optional[Decimal]
    by_child: dict[str, int]  # child_name: item_count


# ============== SantaReply Schemas ==============

class SantaReplyResponse(BaseModel):
    id: int
    letter_id: int
    body_text: str
    suggested_deed: Optional[str]
    sent_at: Optional[datetime]
    delivery_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============== GoodDeed Schemas ==============

class GoodDeedCreate(BaseModel):
    child_id: int
    description: str = Field(..., min_length=1, max_length=500)


class GoodDeedUpdate(BaseModel):
    completed: Optional[bool] = None
    parent_note: Optional[str] = None


class GoodDeedResponse(BaseModel):
    id: int
    child_id: int
    description: str
    suggested_at: datetime
    completed: bool
    completed_at: Optional[datetime]
    parent_note: Optional[str]

    class Config:
        from_attributes = True


class GoodDeedWithChild(GoodDeedResponse):
    child_name: str


# ============== ModerationFlag Schemas ==============

class ModerationFlagResponse(BaseModel):
    id: int
    letter_id: int
    flag_type: str
    severity: str
    excerpt: Optional[str]
    ai_confidence: Optional[float]
    ai_explanation: Optional[str]
    reviewed: bool
    reviewed_at: Optional[datetime]
    action_taken: Optional[str]
    reviewer_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ModerationFlagUpdate(BaseModel):
    action_taken: str  # dismissed/escalated/noted
    reviewer_note: Optional[str] = None


class ModerationFlagWithContext(ModerationFlagResponse):
    child_name: str
    letter_subject: Optional[str]
    letter_received_at: datetime


# ============== Notification Schemas ==============

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: Optional[str]
    read: bool
    related_letter_id: Optional[int]
    related_child_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Export Schemas ==============

class ExportRequest(BaseModel):
    include_letters: bool = True
    include_replies: bool = True
    include_wish_items: bool = True
    years: Optional[List[int]] = None  # Filter by years, None = all
    child_ids: Optional[List[int]] = None  # Filter by children, None = all


class ExportResponse(BaseModel):
    status: str  # pending/ready/failed
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


# Forward references for nested models
LetterWithDetails.model_rebuild()

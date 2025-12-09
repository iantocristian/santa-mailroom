"""
Test fixtures and configuration for Santa Wishlist API tests.
Uses SQLite in-memory database for fast, isolated testing.
"""
import pytest
from datetime import datetime, timedelta
from typing import Generator, Tuple
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User, Family, Child, Letter, WishItem, GoodDeed, SantaReply
from app.auth import get_password_hash, create_access_token
from app.services.email_service import EmailService


# SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create fresh database tables for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create test client with database override."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user with a family."""
    user = User(
        email="parent@test.com",
        hashed_password=get_password_hash("testpass123"),
        name="Test Parent",
        invite_token="valid-invite-token-1"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create family for user
    family = Family(
        owner_id=user.id,
        name="Test Family"
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    
    # Refresh user to get family relationship
    db.refresh(user)
    return user


@pytest.fixture
def test_user_2(db: Session) -> User:
    """Create a second test user for IDOR tests."""
    user = User(
        email="parent2@test.com",
        hashed_password=get_password_hash("testpass456"),
        name="Other Parent",
        invite_token="valid-invite-token-2"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create family for user
    family = Family(
        owner_id=user.id,
        name="Other Family"
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    
    # Refresh user to get family relationship
    db.refresh(user)
    return user


@pytest.fixture
def test_child(db: Session, test_user: User) -> Child:
    """Create a test child for the test user's family."""
    child = Child(
        family_id=test_user.family.id,
        name="Tommy",
        email_hash=EmailService.hash_email("tommy@test.com"),
        country="US",
        birth_year=2015
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@pytest.fixture
def test_child_user2(db: Session, test_user_2: User) -> Child:
    """Create a test child for user 2's family (for IDOR tests)."""
    child = Child(
        family_id=test_user_2.family.id,
        name="Sarah",
        email_hash=EmailService.hash_email("sarah@test.com"),
        country="UK",
        birth_year=2016
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@pytest.fixture
def test_letter(db: Session, test_child: Child) -> Letter:
    """Create a test letter from the test child."""
    letter = Letter(
        child_id=test_child.id,
        year=2024,
        subject="Dear Santa",
        body_text="I would like a bicycle please!",
        received_at=datetime.utcnow(),
        message_id="<test-message-id@test.com>",
        from_email="tommy@test.com",
        status="processed"
    )
    db.add(letter)
    db.commit()
    db.refresh(letter)
    return letter


@pytest.fixture
def test_letter_user2(db: Session, test_child_user2: Child) -> Letter:
    """Create a test letter for user 2's child (for IDOR tests)."""
    letter = Letter(
        child_id=test_child_user2.id,
        year=2024,
        subject="Hello Santa",
        body_text="I want a doll please!",
        received_at=datetime.utcnow(),
        message_id="<test-message-id-2@test.com>",
        from_email="sarah@test.com",
        status="processed"
    )
    db.add(letter)
    db.commit()
    db.refresh(letter)
    return letter


@pytest.fixture
def test_wish_item(db: Session, test_letter: Letter) -> WishItem:
    """Create a test wish item."""
    item = WishItem(
        letter_id=test_letter.id,
        raw_text="a bicycle",
        normalized_name="Kids Bicycle",
        category="sports",
        status="pending"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def test_wish_item_user2(db: Session, test_letter_user2: Letter) -> WishItem:
    """Create a test wish item for user 2 (for IDOR tests)."""
    item = WishItem(
        letter_id=test_letter_user2.id,
        raw_text="a doll",
        normalized_name="Fashion Doll",
        category="toys",
        status="pending"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def test_deed(db: Session, test_child: Child) -> GoodDeed:
    """Create a test good deed."""
    deed = GoodDeed(
        child_id=test_child.id,
        description="Help set the dinner table"
    )
    db.add(deed)
    db.commit()
    db.refresh(deed)
    return deed


@pytest.fixture
def test_deed_user2(db: Session, test_child_user2: Child) -> GoodDeed:
    """Create a test good deed for user 2 (for IDOR tests)."""
    deed = GoodDeed(
        child_id=test_child_user2.id,
        description="Clean your room"
    )
    db.add(deed)
    db.commit()
    db.refresh(deed)
    return deed


def get_auth_header(user: User) -> dict:
    """Generate an authorization header with a valid JWT token."""
    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(hours=1)
    )
    return {"Authorization": f"Bearer {token}"}


def get_expired_auth_header(user: User) -> dict:
    """Generate an authorization header with an expired JWT token."""
    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )
    return {"Authorization": f"Bearer {token}"}


def get_invalid_auth_header() -> dict:
    """Generate an authorization header with an invalid token."""
    return {"Authorization": "Bearer invalid.token.here"}


def get_malformed_auth_header() -> dict:
    """Generate a malformed authorization header."""
    return {"Authorization": "NotBearer somejunk"}

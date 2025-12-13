"""
Read-Only User Tests

Tests to verify:
- Read-only users can still access all GET endpoints (read data)
- Read-only users are blocked from all POST/PUT/DELETE endpoints (modify data)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import get_auth_header
from app.models import User, Child, GoodDeed, Notification, ModerationFlag, Letter, WishItem


class TestReadOnlyUserBlocksWrites:
    """Test that read-only users cannot modify any data."""
    
    def test_readonly_user_blocked_from_create_child(
        self,
        client: TestClient,
        test_user: User,
        db: Session
    ):
        """Read-only user cannot create a child."""
        # Mark user as readonly
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.post(
            "/api/children",
            headers=headers,
            json={"name": "New Child", "email": "newchild@test.com"}
        )
        
        assert response.status_code == 403
        assert "read-only" in response.json()["detail"].lower()
    
    def test_readonly_user_blocked_from_update_child(
        self,
        client: TestClient,
        test_user: User,
        test_child: Child,
        db: Session
    ):
        """Read-only user cannot update a child."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.put(
            f"/api/children/{test_child.id}",
            headers=headers,
            json={"name": "Updated Name"}
        )
        
        assert response.status_code == 403
    
    def test_readonly_user_blocked_from_delete_child(
        self,
        client: TestClient,
        test_user: User,
        test_child: Child,
        db: Session
    ):
        """Read-only user cannot delete a child."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.delete(f"/api/children/{test_child.id}", headers=headers)
        
        assert response.status_code == 403
        
        # Verify child still exists
        child = db.query(Child).filter(Child.id == test_child.id).first()
        assert child is not None
    
    def test_readonly_user_blocked_from_update_family(
        self,
        client: TestClient,
        test_user: User,
        db: Session
    ):
        """Read-only user cannot update family settings."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.put(
            "/api/family",
            headers=headers,
            json={"name": "Hacked Family Name"}
        )
        
        assert response.status_code == 403
    
    def test_readonly_user_blocked_from_create_deed(
        self,
        client: TestClient,
        test_user: User,
        test_child: Child,
        db: Session
    ):
        """Read-only user cannot create a good deed."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.post(
            "/api/deeds?send_email=false",
            headers=headers,
            json={"child_id": test_child.id, "description": "Test deed"}
        )
        
        assert response.status_code == 403
    
    def test_readonly_user_blocked_from_complete_deed(
        self,
        client: TestClient,
        test_user: User,
        test_deed: GoodDeed,
        db: Session
    ):
        """Read-only user cannot complete a good deed."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.post(
            f"/api/deeds/{test_deed.id}/complete?send_email=false",
            headers=headers
        )
        
        assert response.status_code == 403
    
    def test_readonly_user_blocked_from_update_wish_item(
        self,
        client: TestClient,
        test_user: User,
        test_wish_item: WishItem,
        db: Session
    ):
        """Read-only user cannot update a wish item."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.put(
            f"/api/wishlist/{test_wish_item.id}",
            headers=headers,
            json={"status": "approved"}
        )
        
        assert response.status_code == 403


class TestReadOnlyUserCanRead:
    """Test that read-only users can still read all data."""
    
    def test_readonly_user_can_list_children(
        self,
        client: TestClient,
        test_user: User,
        test_child: Child,
        db: Session
    ):
        """Read-only user can list children."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.get("/api/children", headers=headers)
        
        assert response.status_code == 200
        assert len(response.json()) >= 1
    
    def test_readonly_user_can_get_child(
        self,
        client: TestClient,
        test_user: User,
        test_child: Child,
        db: Session
    ):
        """Read-only user can get a specific child."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.get(f"/api/children/{test_child.id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["name"] == test_child.name
    
    def test_readonly_user_can_get_family(
        self,
        client: TestClient,
        test_user: User,
        db: Session
    ):
        """Read-only user can get family info."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.get("/api/family", headers=headers)
        
        assert response.status_code == 200
    
    def test_readonly_user_can_get_family_stats(
        self,
        client: TestClient,
        test_user: User,
        db: Session
    ):
        """Read-only user can get family stats."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.get("/api/family/stats", headers=headers)
        
        assert response.status_code == 200
    
    def test_readonly_user_can_list_letters(
        self,
        client: TestClient,
        test_user: User,
        test_letter: Letter,
        db: Session
    ):
        """Read-only user can list letters."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.get("/api/letters", headers=headers)
        
        assert response.status_code == 200
    
    def test_readonly_user_can_list_wishlist(
        self,
        client: TestClient,
        test_user: User,
        test_wish_item: WishItem,
        db: Session
    ):
        """Read-only user can list wish items."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.get("/api/wishlist", headers=headers)
        
        assert response.status_code == 200
    
    def test_readonly_user_can_list_deeds(
        self,
        client: TestClient,
        test_user: User,
        test_deed: GoodDeed,
        db: Session
    ):
        """Read-only user can list good deeds."""
        test_user.is_readonly = True
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.get("/api/deeds", headers=headers)
        
        assert response.status_code == 200


class TestNonReadOnlyUserUnaffected:
    """Test that normal users are not affected by the read-only feature."""
    
    def test_normal_user_can_create_child(
        self,
        client: TestClient,
        test_user: User,
        db: Session
    ):
        """Normal user (is_readonly=False) can create a child."""
        # Explicitly ensure user is not readonly
        test_user.is_readonly = False
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.post(
            "/api/children",
            headers=headers,
            json={"name": "Normal Child", "email": "normalchild@test.com"}
        )
        
        assert response.status_code == 201
    
    def test_normal_user_can_update_family(
        self,
        client: TestClient,
        test_user: User,
        db: Session
    ):
        """Normal user can update family settings."""
        test_user.is_readonly = False
        db.commit()
        
        headers = get_auth_header(test_user)
        response = client.put(
            "/api/family",
            headers=headers,
            json={"name": "Updated Family Name"}
        )
        
        assert response.status_code == 200

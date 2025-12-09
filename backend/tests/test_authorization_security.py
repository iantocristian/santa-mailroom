"""
Authorization Security Tests (IDOR - Insecure Direct Object Reference)

Tests to verify:
- User A cannot access User B's family data
- User A cannot access User B's children
- User A cannot access User B's wish items
- User A cannot access User B's letters/deeds
- User A cannot modify User B's resources
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import get_auth_header
from app.models import User, Child, Letter, WishItem, GoodDeed


class TestChildrenIDOR:
    """Test that users can only access their own family's children."""
    
    def test_user_can_list_own_children(
        self, client: TestClient, test_user: User, test_child: Child
    ):
        """User can list their own family's children."""
        headers = get_auth_header(test_user)
        response = client.get("/api/children", headers=headers)
        
        assert response.status_code == 200
        children = response.json()
        assert len(children) == 1
        assert children[0]["name"] == test_child.name
    
    def test_user_cannot_see_other_family_children_in_list(
        self,
        client: TestClient,
        test_user: User,
        test_child: Child,
        test_user_2: User,
        test_child_user2: Child
    ):
        """User only sees their own children, not other users' children."""
        headers = get_auth_header(test_user)
        response = client.get("/api/children", headers=headers)
        
        assert response.status_code == 200
        children = response.json()
        
        # Should only see own child
        child_names = [c["name"] for c in children]
        assert test_child.name in child_names
        assert test_child_user2.name not in child_names
    
    def test_user_cannot_get_other_family_child_by_id(
        self,
        client: TestClient,
        test_user: User,
        test_child_user2: Child
    ):
        """User cannot access another user's child by ID."""
        headers = get_auth_header(test_user)
        response = client.get(f"/api/children/{test_child_user2.id}", headers=headers)
        
        assert response.status_code == 404
    
    def test_user_cannot_update_other_family_child(
        self,
        client: TestClient,
        test_user: User,
        test_child_user2: Child
    ):
        """User cannot update another user's child."""
        headers = get_auth_header(test_user)
        response = client.put(
            f"/api/children/{test_child_user2.id}",
            headers=headers,
            json={"name": "Hacked Name"}
        )
        
        assert response.status_code == 404
    
    def test_user_cannot_delete_other_family_child(
        self,
        client: TestClient,
        test_user: User,
        test_child_user2: Child,
        db: Session
    ):
        """User cannot delete another user's child."""
        headers = get_auth_header(test_user)
        response = client.delete(f"/api/children/{test_child_user2.id}", headers=headers)
        
        assert response.status_code == 404
        
        # Verify child still exists
        child = db.query(Child).filter(Child.id == test_child_user2.id).first()
        assert child is not None


class TestWishlistIDOR:
    """Test that users can only access their own family's wishlist items."""
    
    def test_user_can_list_own_wish_items(
        self, client: TestClient, test_user: User, test_wish_item: WishItem
    ):
        """User can list their own family's wish items."""
        headers = get_auth_header(test_user)
        response = client.get("/api/wishlist", headers=headers)
        
        assert response.status_code == 200
        items = response.json()
        assert len(items) >= 1
        assert any(i["id"] == test_wish_item.id for i in items)
    
    def test_user_cannot_see_other_family_wish_items_in_list(
        self,
        client: TestClient,
        test_user: User,
        test_wish_item: WishItem,
        test_wish_item_user2: WishItem
    ):
        """User only sees their own family's wish items."""
        headers = get_auth_header(test_user)
        response = client.get("/api/wishlist", headers=headers)
        
        assert response.status_code == 200
        items = response.json()
        
        item_ids = [i["id"] for i in items]
        assert test_wish_item.id in item_ids
        assert test_wish_item_user2.id not in item_ids
    
    def test_user_cannot_get_other_family_wish_item_by_id(
        self,
        client: TestClient,
        test_user: User,
        test_wish_item_user2: WishItem
    ):
        """User cannot access another family's wish item by ID."""
        headers = get_auth_header(test_user)
        response = client.get(f"/api/wishlist/{test_wish_item_user2.id}", headers=headers)
        
        assert response.status_code == 404
    
    def test_user_cannot_update_other_family_wish_item(
        self,
        client: TestClient,
        test_user: User,
        test_wish_item_user2: WishItem
    ):
        """User cannot update another family's wish item."""
        headers = get_auth_header(test_user)
        response = client.put(
            f"/api/wishlist/{test_wish_item_user2.id}",
            headers=headers,
            json={"status": "approved"}
        )
        
        assert response.status_code == 404
    
    def test_cannot_filter_by_other_family_child_id(
        self,
        client: TestClient,
        test_user: User,
        test_child: Child,  # Need this so test_user has children
        test_child_user2: Child
    ):
        """User cannot filter wishlist by another family's child ID.
        
        The API returns 403 Forbidden when attempting to filter by
        a child_id that doesn't belong to the user's family.
        """
        headers = get_auth_header(test_user)
        response = client.get(
            f"/api/wishlist?child_id={test_child_user2.id}",
            headers=headers
        )
        
        # Should return 403 Forbidden - child not in user's family
        assert response.status_code == 403


class TestLettersIDOR:
    """Test that users can only access their own family's letters."""
    
    def test_user_can_list_own_letters(
        self, client: TestClient, test_user: User, test_letter: Letter
    ):
        """User can list their own family's letters."""
        headers = get_auth_header(test_user)
        response = client.get("/api/letters", headers=headers)
        
        assert response.status_code == 200
        letters = response.json()
        assert len(letters) >= 1
        assert any(l["id"] == test_letter.id for l in letters)
    
    def test_user_cannot_see_other_family_letters(
        self,
        client: TestClient,
        test_user: User,
        test_letter: Letter,
        test_letter_user2: Letter
    ):
        """User only sees their own family's letters."""
        headers = get_auth_header(test_user)
        response = client.get("/api/letters", headers=headers)
        
        assert response.status_code == 200
        letters = response.json()
        
        letter_ids = [l["id"] for l in letters]
        assert test_letter.id in letter_ids
        assert test_letter_user2.id not in letter_ids
    
    def test_user_cannot_get_other_family_letter_by_id(
        self,
        client: TestClient,
        test_user: User,
        test_letter_user2: Letter
    ):
        """User cannot access another family's letter by ID."""
        headers = get_auth_header(test_user)
        response = client.get(f"/api/letters/{test_letter_user2.id}", headers=headers)
        
        assert response.status_code == 404


class TestDeedsIDOR:
    """Test that users can only access their own family's good deeds."""
    
    def test_user_can_list_own_deeds(
        self, client: TestClient, test_user: User, test_deed: GoodDeed
    ):
        """User can list their own family's good deeds."""
        headers = get_auth_header(test_user)
        response = client.get("/api/deeds", headers=headers)
        
        assert response.status_code == 200
        deeds = response.json()
        assert len(deeds) >= 1
        assert any(d["id"] == test_deed.id for d in deeds)
    
    def test_user_cannot_see_other_family_deeds(
        self,
        client: TestClient,
        test_user: User,
        test_deed: GoodDeed,
        test_deed_user2: GoodDeed
    ):
        """User only sees their own family's deeds."""
        headers = get_auth_header(test_user)
        response = client.get("/api/deeds", headers=headers)
        
        assert response.status_code == 200
        deeds = response.json()
        
        deed_ids = [d["id"] for d in deeds]
        assert test_deed.id in deed_ids
        assert test_deed_user2.id not in deed_ids
    
    def test_user_cannot_update_other_family_deed(
        self,
        client: TestClient,
        test_user: User,
        test_deed_user2: GoodDeed
    ):
        """User cannot update another family's deed."""
        headers = get_auth_header(test_user)
        response = client.put(
            f"/api/deeds/{test_deed_user2.id}",
            headers=headers,
            json={"completed": True}
        )
        
        assert response.status_code == 404
    
    def test_user_cannot_delete_other_family_deed(
        self,
        client: TestClient,
        test_user: User,
        test_deed_user2: GoodDeed,
        db: Session
    ):
        """User cannot delete another family's deed."""
        headers = get_auth_header(test_user)
        response = client.delete(f"/api/deeds/{test_deed_user2.id}", headers=headers)
        
        assert response.status_code == 404
        
        # Verify deed still exists
        deed = db.query(GoodDeed).filter(GoodDeed.id == test_deed_user2.id).first()
        assert deed is not None


class TestCrossFamilyCreation:
    """Test that users cannot create resources in other families."""
    
    def test_cannot_create_child_for_other_family(
        self,
        client: TestClient,
        test_user: User,
        test_user_2: User,
        db: Session
    ):
        """User cannot create a child specifying another family's ID.
        
        Note: The API doesn't accept family_id in the request body,
        so this tests that the system uses the authenticated user's family.
        """
        headers = get_auth_header(test_user)
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": "Injected Child",
                "email": "injected@test.com",
                "country": "US"
            }
        )
        
        # Should succeed but use the authenticated user's family
        if response.status_code == 201:
            child_id = response.json()["id"]
            child = db.query(Child).filter(Child.id == child_id).first()
            assert child.family_id == test_user.family.id
            assert child.family_id != test_user_2.family.id
    
    def test_cannot_create_deed_for_other_family_child(
        self,
        client: TestClient,
        test_user: User,
        test_child_user2: Child
    ):
        """User cannot create a deed for another family's child."""
        headers = get_auth_header(test_user)
        response = client.post(
            "/api/deeds",
            headers=headers,
            json={
                "child_id": test_child_user2.id,
                "description": "Sneaky deed for wrong child"
            }
        )
        
        # Should fail - child not in user's family
        assert response.status_code in [403, 404]


class TestIDEnumeration:
    """Test that sequential ID enumeration doesn't leak data."""
    
    def test_sequential_child_id_probe_returns_404(
        self,
        client: TestClient,
        test_user: User
    ):
        """Probing sequential child IDs returns 404, not different errors."""
        headers = get_auth_header(test_user)
        
        # Try a bunch of IDs that might or might not exist
        for child_id in range(1, 20):
            response = client.get(f"/api/children/{child_id}", headers=headers)
            # Should either be 200 (own child) or 404 (not found/not accessible)
            # Never 403 which would confirm existence
            assert response.status_code in [200, 404]
    
    def test_negative_id_handled_gracefully(
        self,
        client: TestClient,
        test_user: User
    ):
        """Negative IDs are handled gracefully."""
        headers = get_auth_header(test_user)
        response = client.get("/api/children/-1", headers=headers)
        
        # Should return 404 or 422 (validation error), not 500
        assert response.status_code in [404, 422]
    
    def test_very_large_id_handled_gracefully(
        self,
        client: TestClient,
        test_user: User
    ):
        """Very large IDs are handled gracefully."""
        headers = get_auth_header(test_user)
        response = client.get("/api/children/999999999", headers=headers)
        
        assert response.status_code == 404

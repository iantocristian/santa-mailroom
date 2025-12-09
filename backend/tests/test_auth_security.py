"""
Authentication Security Tests

Tests to verify:
- Protected endpoints require authentication
- Invalid/expired/malformed tokens are rejected
- Token-based attacks are prevented
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import (
    get_auth_header,
    get_expired_auth_header,
    get_invalid_auth_header,
    get_malformed_auth_header,
)
from app.models import User


class TestUnauthorizedAccess:
    """Test that endpoints require valid authentication."""
    
    PROTECTED_ENDPOINTS = [
        ("GET", "/api/children"),
        ("POST", "/api/children"),
        ("GET", "/api/wishlist"),
        ("GET", "/api/wishlist/summary"),
        ("GET", "/api/letters"),
        ("GET", "/api/deeds"),
        ("GET", "/api/family"),
        ("GET", "/api/notifications"),
        ("GET", "/api/auth/me"),
    ]
    
    @pytest.mark.parametrize("method,endpoint", PROTECTED_ENDPOINTS)
    def test_no_token_returns_401(self, client: TestClient, method: str, endpoint: str):
        """Accessing protected endpoints without a token returns 401."""
        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json={})
        elif method == "PUT":
            response = client.put(endpoint, json={})
        elif method == "DELETE":
            response = client.delete(endpoint)
        
        assert response.status_code == 401
        assert "detail" in response.json()


class TestInvalidTokens:
    """Test that various invalid tokens are properly rejected."""
    
    def test_invalid_token_rejected(self, client: TestClient, db: Session):
        """Invalid JWT tokens are rejected with 401."""
        headers = get_invalid_auth_header()
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_expired_token_rejected(self, client: TestClient, test_user: User):
        """Expired JWT tokens are rejected with 401."""
        headers = get_expired_auth_header(test_user)
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_malformed_auth_header_rejected(self, client: TestClient, db: Session):
        """Malformed Authorization headers are rejected."""
        headers = get_malformed_auth_header()
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_empty_bearer_rejected(self, client: TestClient, db: Session):
        """Empty bearer token is rejected."""
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_none_token_value_rejected(self, client: TestClient, db: Session):
        """Token with 'None' or 'null' value is rejected."""
        headers = {"Authorization": "Bearer None"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401
        
        headers = {"Authorization": "Bearer null"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401


class TestTokenTampering:
    """Test that tampered tokens are detected and rejected."""
    
    def test_modified_signature_rejected(self, client: TestClient, test_user: User):
        """Token with modified signature is rejected."""
        headers = get_auth_header(test_user)
        token = headers["Authorization"].split(" ")[1]
        
        # Modify the last character of the signature
        if token[-1] == "a":
            tampered_token = token[:-1] + "b"
        else:
            tampered_token = token[:-1] + "a"
        
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_token_with_wrong_algorithm_rejected(self, client: TestClient, db: Session):
        """Token signed with wrong algorithm is rejected."""
        # Create a token with a different algorithm claim
        import jwt
        fake_token = jwt.encode(
            {"sub": "fake@test.com", "exp": 9999999999},
            "wrong-secret",
            algorithm="HS512"
        )
        headers = {"Authorization": f"Bearer {fake_token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401


class TestValidAuthentication:
    """Test that valid authentication works correctly."""
    
    def test_valid_token_accepted(self, client: TestClient, test_user: User):
        """Valid JWT token grants access."""
        headers = get_auth_header(test_user)
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == test_user.email
    
    def test_user_info_in_token_matches_response(self, client: TestClient, test_user: User):
        """User info from token matches the returned user data."""
        headers = get_auth_header(test_user)
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["id"] == test_user.id


class TestLoginSecurity:
    """Test login endpoint security."""
    
    def test_wrong_password_rejected(self, client: TestClient, test_user: User):
        """Wrong password returns 401."""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    def test_nonexistent_user_rejected(self, client: TestClient, db: Session):
        """Non-existent user returns 401."""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistent@test.com", "password": "anypassword"}
        )
        assert response.status_code == 401
    
    def test_same_error_for_wrong_user_and_wrong_password(
        self, client: TestClient, test_user: User, db: Session
    ):
        """Same error message for wrong user and wrong password (prevent enumeration)."""
        # Wrong password
        response1 = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "wrongpassword"}
        )
        
        # Non-existent user
        response2 = client.post(
            "/api/auth/login",
            data={"username": "nonexistent@test.com", "password": "anypassword"}
        )
        
        # Both should return same error to prevent user enumeration
        assert response1.status_code == response2.status_code == 401
        assert response1.json()["detail"] == response2.json()["detail"]


class TestInviteTokenSecurity:
    """Test invite code security."""
    
    def test_invite_code_cannot_be_reused(self, client: TestClient, db: Session, test_user: User):
        """Invite codes cannot be used twice."""
        from app.models import InviteCode
        from datetime import datetime
        
        # Create an invite code and mark it as used
        used_invite = InviteCode(
            code="SANTA-USED01",
            used_at=datetime.utcnow()
        )
        db.add(used_invite)
        db.commit()
        
        # Try to register with an already-used invite code
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "newpassword123",
                "name": "New User",
                "invite_token": "SANTA-USED01"
            }
        )
        # Code is rejected as invalid/used
        assert response.status_code == 400
    
    def test_invalid_invite_token_rejected(self, client: TestClient, db: Session):
        """Invalid invite tokens are rejected."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "attacker@test.com",
                "password": "password123",
                "name": "Attacker",
                "invite_token": "totally-fake-invalid-token"
            }
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    def test_empty_invite_token_rejected(self, client: TestClient, db: Session):
        """Empty invite token is rejected."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "name": "New User",
                "invite_token": ""
            }
        )
        # Should fail validation or return error
        assert response.status_code in [400, 422]

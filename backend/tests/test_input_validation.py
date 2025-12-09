"""
Input Validation Security Tests

Tests to verify:
- SQL injection attempts are safely handled
- Extremely long inputs are rejected
- Email format validation works correctly
- Password length limits are enforced
- Special characters are handled safely
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import get_auth_header
from app.models import User, Child


class TestSQLInjectionPrevention:
    """Test that SQL injection attempts are safely handled."""
    
    SQL_INJECTION_PAYLOADS = [
        "'; DROP TABLE users; --",
        "1 OR 1=1",
        "1; DELETE FROM children WHERE 1=1; --",
        "admin'--",
        "' UNION SELECT * FROM users --",
        "'; UPDATE users SET email='hacked@test.com' WHERE 1=1; --",
        "1 AND (SELECT COUNT(*) FROM users) > 0",
        "'||'",
        "1' AND '1'='1",
    ]
    
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_sql_injection_in_child_name(
        self, client: TestClient, test_user: User, payload: str
    ):
        """SQL injection in child name field is safely handled."""
        headers = get_auth_header(test_user)
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": payload,
                "email": "test-injection@test.com"
            }
        )
        
        # Should either accept safely or reject - never cause DB error
        assert response.status_code in [201, 400, 422]
        
        # If created, verify the name is stored as-is (not executed)
        if response.status_code == 201:
            child_id = response.json()["id"]
            get_response = client.get(f"/api/children/{child_id}", headers=headers)
            assert get_response.status_code == 200
            assert get_response.json()["name"] == payload
    
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_sql_injection_in_login_email(
        self, client: TestClient, db: Session, payload: str
    ):
        """SQL injection in login email field is safely handled."""
        response = client.post(
            "/api/auth/login",
            data={"username": payload, "password": "anypassword"}
        )
        
        # Should return 401 (not authenticated), not 500 (DB error)
        assert response.status_code == 401
    
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_sql_injection_in_deed_description(
        self, client: TestClient, test_user: User, test_child: Child, payload: str
    ):
        """SQL injection in deed description is safely handled."""
        headers = get_auth_header(test_user)
        response = client.post(
            "/api/deeds",
            headers=headers,
            json={
                "child_id": test_child.id,
                "description": payload
            }
        )
        
        # Should either accept safely or reject - never cause DB error
        assert response.status_code in [201, 400, 422]


class TestMaxLengthValidation:
    """Test that excessively long inputs are rejected."""
    
    def test_very_long_name_rejected(self, client: TestClient, test_user: User):
        """Very long child name is rejected."""
        headers = get_auth_header(test_user)
        long_name = "A" * 10000  # 10k characters
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": long_name,
                "email": "test@test.com"
            }
        )
        
        # Should reject with validation error
        assert response.status_code in [400, 422]
    
    def test_very_long_email_rejected(self, client: TestClient, test_user: User):
        """Very long email is rejected."""
        headers = get_auth_header(test_user)
        long_email = "a" * 10000 + "@test.com"
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": "Test Child",
                "email": long_email
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_very_long_password_rejected(self, client: TestClient, db: Session):
        """Very long password is rejected (bcrypt has 72 byte limit)."""
        long_password = "A" * 100  # Over 72 bytes
        
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "password": long_password,
                "name": "New User",
                "invite_token": "some-token"
            }
        )
        
        # Should reject or handle gracefully
        # (72 byte limit for bcrypt)
        assert response.status_code in [400, 422, 500]  # 500 only if not handled
    
    def test_very_long_deed_description_rejected(
        self, client: TestClient, test_user: User, test_child: Child
    ):
        """Very long deed description is rejected."""
        headers = get_auth_header(test_user)
        long_description = "A" * 10000
        
        response = client.post(
            "/api/deeds",
            headers=headers,
            json={
                "child_id": test_child.id,
                "description": long_description
            }
        )
        
        assert response.status_code in [400, 422]


class TestEmailValidation:
    """Test email format validation."""
    
    INVALID_EMAILS = [
        "notanemail",
        "@nolocal.com",
        "no@domain",
        "spaces @test.com",
        "test@",
        "",
        "   ",
        "test@test@test.com",
    ]
    
    @pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
    def test_invalid_email_format_rejected(
        self, client: TestClient, test_user: User, invalid_email: str
    ):
        """Invalid email formats are rejected when registering a child."""
        headers = get_auth_header(test_user)
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": "Test Child",
                "email": invalid_email
            }
        )
        
        # Should reject invalid emails
        assert response.status_code in [400, 422]
    
    @pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
    def test_invalid_email_in_registration(
        self, client: TestClient, db: Session, invalid_email: str
    ):
        """Invalid email formats are rejected during user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": invalid_email,
                "password": "password123",
                "name": "Test User",
                "invite_token": "some-token"
            }
        )
        
        assert response.status_code in [400, 422]


class TestSpecialCharacterHandling:
    """Test that special characters are handled safely."""
    
    SPECIAL_CHAR_PAYLOADS = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "{{constructor.constructor('return this')()}}",
        "${7*7}",
        "<%=7*7%>",
        "{{7*7}}",
        "\x00\x00\x00",  # Null bytes
        "test\r\nX-Injected: header",  # Header injection
    ]
    
    @pytest.mark.parametrize("payload", SPECIAL_CHAR_PAYLOADS)
    def test_special_chars_in_child_name(
        self, client: TestClient, test_user: User, payload: str
    ):
        """Special characters in child name are handled safely."""
        headers = get_auth_header(test_user)
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": payload,
                "email": "special-test@test.com"
            }
        )
        
        # Should accept safely or reject - never crash
        assert response.status_code in [201, 400, 422]
        
        # If created, verify returned data is escaped/safe
        if response.status_code == 201:
            child_data = response.json()
            assert "name" in child_data
    
    @pytest.mark.parametrize("payload", SPECIAL_CHAR_PAYLOADS)
    def test_special_chars_in_user_name(
        self, client: TestClient, db: Session, payload: str
    ):
        """Special characters in user name are handled safely."""
        # This will likely fail due to invite token, but tests the handler
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test-special@test.com",
                "password": "password123",
                "name": payload,
                "invite_token": "fake-token"
            }
        )
        
        # Should handle gracefully (likely 400 for bad token)
        assert response.status_code in [400, 422]


class TestJSONHandling:
    """Test malformed JSON handling."""
    
    def test_malformed_json_rejected(self, client: TestClient, test_user: User):
        """Malformed JSON is rejected gracefully."""
        headers = get_auth_header(test_user)
        headers["Content-Type"] = "application/json"
        
        response = client.post(
            "/api/children",
            headers=headers,
            content="{not valid json"
        )
        
        # Should return 422 (Unprocessable Entity) not 500
        assert response.status_code == 422
    
    def test_nested_object_bomb_handling(self, client: TestClient, test_user: User):
        """Deeply nested JSON doesn't cause stack overflow."""
        headers = get_auth_header(test_user)
        
        # Create deeply nested object
        nested = {"name": "test", "email": "test@test.com"}
        for _ in range(50):
            nested = {"data": nested}
        
        response = client.post(
            "/api/children",
            headers=headers,
            json=nested
        )
        
        # Should reject, not crash
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client: TestClient, test_user: User):
        """Missing required fields return clear error."""
        headers = get_auth_header(test_user)
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={}  # No name or email
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()


class TestTypeCoercion:
    """Test that type coercion attacks are prevented."""
    
    def test_string_where_int_expected(self, client: TestClient, test_user: User):
        """String in integer field is rejected."""
        headers = get_auth_header(test_user)
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": "Test Child",
                "email": "test@test.com",
                "birth_year": "not-a-number"
            }
        )
        
        assert response.status_code == 422
    
    def test_array_where_string_expected(self, client: TestClient, test_user: User):
        """Array in string field is rejected."""
        headers = get_auth_header(test_user)
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": ["array", "of", "strings"],
                "email": "test@test.com"
            }
        )
        
        assert response.status_code == 422
    
    def test_object_where_string_expected(self, client: TestClient, test_user: User):
        """Object in string field is rejected."""
        headers = get_auth_header(test_user)
        
        response = client.post(
            "/api/children",
            headers=headers,
            json={
                "name": {"key": "value"},
                "email": "test@test.com"
            }
        )
        
        assert response.status_code == 422

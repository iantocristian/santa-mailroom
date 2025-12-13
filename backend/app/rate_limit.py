"""
Rate limiting configuration for the Santa Wishlist API.

Uses slowapi to provide per-user and per-IP rate limiting.
"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from typing import Optional


def get_user_identifier(request: Request) -> str:
    """
    Get rate limit key based on authenticated user or IP address.
    
    For authenticated requests, uses user email from JWT.
    For unauthenticated requests, falls back to IP address.
    """
    # Check if we have an authenticated user in request state
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.email}"
    
    # Check authorization header for JWT to extract email
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from jose import jwt
            from app.config import get_settings
            settings = get_settings()
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            email = payload.get("sub")
            if email:
                return f"user:{email}"
        except Exception:
            pass  # Fall through to IP-based limiting
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def get_ip_identifier(request: Request) -> str:
    """Get rate limit key based on IP address only."""
    return f"ip:{get_remote_address(request)}"


# Check if rate limiting should be enabled (disabled during tests)
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() != "false"

# Main limiter for authenticated endpoints (per-user)
limiter = Limiter(
    key_func=get_user_identifier,
    enabled=RATE_LIMIT_ENABLED
)

# Stricter limiter for auth endpoints (per-IP)
auth_limiter = Limiter(
    key_func=get_ip_identifier,
    enabled=RATE_LIMIT_ENABLED
)

# Rate limit configurations
RATE_LIMITS = {
    # General API rate limits (per user)
    "default": "600/minute",
    
    # Auth endpoints (per IP) - stricter
    "login": "5/minute",
    "register": "3/minute",
    
    # Resource-intensive endpoints
    "ai_generation": "10/minute",
}

"""Unit tests for JWT utilities."""
import time
from datetime import timedelta
from uuid import uuid4

import jwt
import pytest

from src.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    encode_jwt,
    verify_token,
)


def test_encode_jwt():
    """Test JWT encoding with RS256."""
    payload = {"sub": "test-user-id", "role": "student"}
    token = encode_jwt(payload, expires_delta=timedelta(minutes=15))

    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0

    # Token should have 3 parts (header.payload.signature)
    assert token.count(".") == 2


def test_decode_jwt():
    """Test JWT decoding with RS256."""
    user_id = str(uuid4())
    payload = {"sub": user_id, "role": "student", "type": "access"}
    token = encode_jwt(payload, expires_delta=timedelta(minutes=15))

    # Decode token
    decoded = decode_jwt(token)

    # Verify payload
    assert decoded["sub"] == user_id
    assert decoded["role"] == "student"
    assert decoded["type"] == "access"
    assert "exp" in decoded
    assert "iat" in decoded


def test_decode_jwt_expired():
    """Test JWT decoding with expired token."""
    payload = {"sub": "test-user-id", "role": "student"}
    token = encode_jwt(payload, expires_delta=timedelta(seconds=-1))  # Already expired

    # Should raise ExpiredSignatureError
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_jwt(token)


def test_decode_jwt_invalid():
    """Test JWT decoding with invalid token."""
    invalid_token = "invalid.token.here"

    # Should raise InvalidTokenError
    with pytest.raises(jwt.InvalidTokenError):
        decode_jwt(invalid_token)


def test_create_access_token():
    """Test access token creation."""
    user_id = uuid4()
    role = "teacher"
    email = "teacher@example.com"

    token = create_access_token(user_id, role, email)

    # Decode and verify
    decoded = decode_jwt(token)
    assert decoded["sub"] == str(user_id)
    assert decoded["role"] == role
    assert decoded["email"] == email
    assert decoded["type"] == "access"


def test_create_refresh_token():
    """Test refresh token creation."""
    user_id = uuid4()

    token = create_refresh_token(user_id)

    # Decode and verify
    decoded = decode_jwt(token)
    assert decoded["sub"] == str(user_id)
    assert decoded["type"] == "refresh"
    assert "role" not in decoded  # Refresh tokens don't include role
    assert "email" not in decoded  # Refresh tokens don't include email


def test_verify_token_access():
    """Test token verification for access tokens."""
    user_id = uuid4()
    token = create_access_token(user_id, "student", "student@example.com")

    # Verify as access token
    payload = verify_token(token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_verify_token_refresh():
    """Test token verification for refresh tokens."""
    user_id = uuid4()
    token = create_refresh_token(user_id)

    # Verify as refresh token
    payload = verify_token(token, expected_type="refresh")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_verify_token_wrong_type():
    """Test token verification with wrong expected type."""
    user_id = uuid4()
    access_token = create_access_token(user_id, "student", "student@example.com")

    # Try to verify access token as refresh token
    with pytest.raises(ValueError, match="Invalid token type"):
        verify_token(access_token, expected_type="refresh")

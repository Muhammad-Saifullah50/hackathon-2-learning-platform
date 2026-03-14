"""JWT token utilities for encoding and decoding tokens."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

import jwt

from src.config import settings


def encode_jwt(
    payload: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Encode a JWT token using RS256 algorithm.

    Args:
        payload: Dictionary containing JWT claims
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string

    Raises:
        Exception: If private key cannot be loaded or encoding fails
    """
    to_encode = payload.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    private_key = settings.get_private_key()
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token using RS256 algorithm.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary containing decoded JWT claims

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    public_key = settings.get_public_key()
    decoded = jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])

    return decoded


def create_access_token(user_id: UUID, role: str, email: str, session_id: Optional[UUID] = None) -> str:
    """
    Create an access token for a user.

    Args:
        user_id: User's UUID
        role: User's role (student, teacher, admin)
        email: User's email address
        session_id: Optional session UUID for session tracking

    Returns:
        Encoded JWT access token
    """
    payload = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "type": "access",
    }

    if session_id:
        payload["session_id"] = str(session_id)

    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return encode_jwt(payload, expires_delta)


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a refresh token for a user.

    Args:
        user_id: User's UUID

    Returns:
        Encoded JWT refresh token
    """
    payload = {
        "sub": str(user_id),
        "type": "refresh",
    }

    expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    return encode_jwt(payload, expires_delta)


def verify_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """
    Verify a JWT token and check its type.

    Args:
        token: JWT token string to verify
        expected_type: Expected token type ('access' or 'refresh')

    Returns:
        Dictionary containing decoded JWT claims

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
        ValueError: If token type doesn't match expected type
    """
    payload = decode_jwt(token)

    token_type = payload.get("type")
    if token_type != expected_type:
        raise ValueError(f"Invalid token type. Expected {expected_type}, got {token_type}")

    return payload

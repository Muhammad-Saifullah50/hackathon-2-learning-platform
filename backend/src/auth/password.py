"""Password utilities for hashing and breach checking."""
import hashlib
from typing import Tuple

import bcrypt
import httpx

from src.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


async def check_password_breach(password: str) -> Tuple[bool, int]:
    """
    Check if password has been breached using HaveIBeenPwned API.

    Uses k-anonymity model: only first 5 characters of SHA-1 hash are sent.

    Args:
        password: Plain text password to check

    Returns:
        Tuple of (is_breached, breach_count)
        - is_breached: True if password found in breach database
        - breach_count: Number of times password appears in breaches (0 if not breached)

    Raises:
        httpx.HTTPError: If API request fails
    """
    # Generate SHA-1 hash of password
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    # Query HaveIBeenPwned API with first 5 characters
    url = f"{settings.HIBP_API_URL}{prefix}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()

    # Parse response to find matching hash suffix
    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return True, int(count)

    return False, 0


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets strength requirements.

    Requirements:
    - At least 8 characters
    - At most 128 characters
    - At least one non-alphanumeric character

    Args:
        password: Plain text password to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if password meets requirements
        - error_message: Empty string if valid, error description otherwise
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 128:
        return False, "Password must be at most 128 characters long"

    if not any(not c.isalnum() for c in password):
        return False, "Password must contain at least one non-alphanumeric character"

    return True, ""

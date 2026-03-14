"""Unit tests for password utilities."""
import pytest

from src.auth.password import hash_password, validate_password_strength, verify_password


def test_hash_password():
    """Test password hashing with bcrypt."""
    password = "Test@1234"
    hashed = hash_password(password)

    # Hash should be different from plain password
    assert hashed != password

    # Hash should be bcrypt format (starts with $2b$)
    assert hashed.startswith("$2b$")

    # Hash should be consistent length
    assert len(hashed) == 60


def test_verify_password():
    """Test password verification."""
    password = "Test@1234"
    hashed = hash_password(password)

    # Correct password should verify
    assert verify_password(password, hashed) is True

    # Incorrect password should not verify
    assert verify_password("WrongPassword", hashed) is False


def test_validate_password_strength_valid():
    """Test password strength validation with valid passwords."""
    # Valid password with special character
    is_valid, error = validate_password_strength("Test@1234")
    assert is_valid is True
    assert error == ""

    # Valid password with different special character
    is_valid, error = validate_password_strength("MyPass!word123")
    assert is_valid is True
    assert error == ""


def test_validate_password_strength_too_short():
    """Test password strength validation with too short password."""
    is_valid, error = validate_password_strength("Test@12")
    assert is_valid is False
    assert "at least 8 characters" in error


def test_validate_password_strength_too_long():
    """Test password strength validation with too long password."""
    long_password = "A" * 129 + "@"
    is_valid, error = validate_password_strength(long_password)
    assert is_valid is False
    assert "at most 128 characters" in error


def test_validate_password_strength_no_special_char():
    """Test password strength validation without special character."""
    is_valid, error = validate_password_strength("TestPassword123")
    assert is_valid is False
    assert "non-alphanumeric character" in error


@pytest.mark.asyncio
async def test_check_password_breach():
    """Test password breach checking with HaveIBeenPwned API."""
    from src.auth.password import check_password_breach

    # Test with known breached password
    is_breached, count = await check_password_breach("password123")
    assert is_breached is True
    assert count > 0

    # Test with likely non-breached password (random string)
    is_breached, count = await check_password_breach("X9z#mK2$pQ7!vL4@wN8")
    # This might be breached or not, but should not raise error
    assert isinstance(is_breached, bool)
    assert isinstance(count, int)

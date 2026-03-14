"""Database models for authentication and authorization."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.database import Base
from src.database_types import GUID, JSONType


class UserRole(str, PyEnum):
    """User role enumeration."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class IdentifierType(str, PyEnum):
    """Rate limit identifier type enumeration."""

    IP = "ip"
    EMAIL = "email"


class User(Base):
    """User model representing platform users."""

    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)
    permissions = Column(JSONType, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    email_verification_tokens = relationship(
        "EmailVerificationToken", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'teacher', 'admin')",
            name="check_user_role"
        ),
    )


class Session(Base):
    """Session model for refresh token management."""

    __tablename__ = "sessions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="check_session_expiry"
        ),
    )


class PasswordResetToken(Base):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")

    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="check_password_reset_token_expiry"
        ),
    )


class EmailVerificationToken(Base):
    """Email verification token model."""

    __tablename__ = "email_verification_tokens"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="email_verification_tokens")

    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="check_email_verification_token_expiry"
        ),
    )


class RateLimitCounter(Base):
    """Rate limit counter model for tracking failed login attempts."""

    __tablename__ = "rate_limit_counters"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    identifier = Column(String(255), unique=True, nullable=False, index=True)
    identifier_type = Column(Enum(IdentifierType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    attempt_count = Column(Integer, nullable=False, default=0)
    lockout_until = Column(DateTime, nullable=True, index=True)
    last_attempt_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "identifier_type IN ('ip', 'email')",
            name="check_identifier_type"
        ),
        CheckConstraint(
            "attempt_count >= 0",
            name="check_attempt_count_positive"
        ),
    )

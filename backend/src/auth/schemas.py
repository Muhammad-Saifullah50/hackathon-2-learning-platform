"""Pydantic schemas for authentication requests and responses."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRole:
    """User role constants."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


# Request Schemas


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    display_name: str = Field(..., min_length=1, max_length=100, description="User display name")
    role: str = Field(..., description="User role: student, teacher, or admin")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is one of the allowed values."""
        if v not in [UserRole.STUDENT, UserRole.TEACHER, UserRole.ADMIN]:
            raise ValueError("Role must be one of: student, teacher, admin")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password has at least one non-alphanumeric character."""
        if not any(not c.isalnum() for c in v):
            raise ValueError("Password must contain at least one non-alphanumeric character")
        return v


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request."""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password has at least one non-alphanumeric character."""
        if not any(not c.isalnum() for c in v):
            raise ValueError("Password must contain at least one non-alphanumeric character")
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request."""

    token: str = Field(..., description="Email verification token")


class ResendVerificationRequest(BaseModel):
    """Resend verification email request."""

    email: EmailStr = Field(..., description="User email address")


# Response Schemas


class UserResponse(BaseModel):
    """User response model."""

    id: UUID
    email: str
    role: str
    display_name: str
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str = Field(..., description="JWT access token (15 minutes)")
    refresh_token: str = Field(..., description="Refresh token (7 days)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")


class LoginResponse(BaseModel):
    """Login response model."""

    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")

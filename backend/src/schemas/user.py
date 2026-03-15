"""User schemas for validation."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    role: str = Field(default="student", pattern="^(student|teacher|admin)$")
    display_name: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    preferences: Optional[Dict[str, Any]] = None


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    preferences: Dict[str, Any]


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    email_verified_at: Optional[datetime] = None
    mfa_enabled: bool
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfileBase(BaseModel):
    """Base user profile schema."""
    bio: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserProfileCreate(UserProfileBase):
    """Schema for creating a user profile."""
    user_id: UUID


class UserProfileUpdate(BaseModel):
    """Schema for updating a user profile."""
    bio: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UserProfileResponse(UserProfileBase):
    """Schema for user profile response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStreakResponse(BaseModel):
    """Schema for user streak response."""
    id: UUID
    user_id: UUID
    current_streak: int
    longest_streak: int
    last_activity_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

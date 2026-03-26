"""User profile management schemas for F04."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LearningPace(str, Enum):
    """Learning pace preference enum."""

    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


class DifficultyLevel(str, Enum):
    """Difficulty level preference enum."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Theme(str, Enum):
    """Theme preference enum (MVP: dark only)."""

    DARK = "dark"


class ProfileUpdateRequest(BaseModel):
    """Request schema for updating user profile."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: Optional[str]) -> Optional[str]:
        """Trim whitespace from display name."""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: Optional[str]) -> Optional[str]:
        """Validate bio length."""
        if v is not None and len(v) > 500:
            raise ValueError("Bio must be 500 characters or less")
        return v


class PreferencesUpdateRequest(BaseModel):
    """Request schema for updating learning preferences."""

    learning_pace: Optional[LearningPace] = None
    difficulty_level: Optional[DifficultyLevel] = None
    theme: Optional[Theme] = None


class AccountDeleteRequest(BaseModel):
    """Request schema for account deletion with password confirmation."""

    password: str = Field(min_length=8)


class ProfileResponse(BaseModel):
    """Response schema for user profile (combined User + UserProfile)."""

    id: UUID
    email: str
    display_name: str
    role: str
    bio: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserListItem(BaseModel):
    """Response schema for admin user list item."""

    id: UUID
    email: str
    display_name: str
    role: str
    email_verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    """Response schema for paginated admin user list."""

    users: list[AdminUserListItem]
    total: int
    page: int
    page_size: int
    total_pages: int

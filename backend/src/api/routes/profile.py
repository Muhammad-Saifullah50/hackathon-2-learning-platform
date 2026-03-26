"""FastAPI routes for user profile management."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.user_profile import (
    AccountDeleteRequest,
    PreferencesUpdateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from src.services.user_profile_service import UserProfileService

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's profile.

    Returns combined User and UserProfile data including:
    - Basic user info (email, display_name, role)
    - Bio from UserProfile
    - Learning preferences
    - Email verification status

    Requires: JWT authentication
    """
    service = UserProfileService(db)
    profile = await service.get_profile(current_user.id)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return profile


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    update_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile.

    Updates:
    - display_name: User's display name (1-100 chars, fallback to email if empty)
    - bio: User biography (max 500 chars)

    Business rules:
    - Empty display_name defaults to email
    - Creates UserProfile if it doesn't exist

    Requires: JWT authentication
    """
    service = UserProfileService(db)

    try:
        profile = await service.update_profile(current_user.id, update_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/preferences", response_model=ProfileResponse)
async def update_preferences(
    preferences_data: PreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's learning preferences.

    Updates:
    - learning_pace: slow, normal, or fast
    - difficulty_level: beginner, intermediate, or advanced
    - theme: dark (MVP scope)

    Preferences affect AI tutor behavior and content difficulty.

    Requires: JWT authentication
    """
    service = UserProfileService(db)

    try:
        profile = await service.update_preferences(current_user.id, preferences_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    delete_data: AccountDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently delete current user's account (GDPR compliance).

    Requires password confirmation for security.

    Hard deletion removes ALL user data:
    - User account
    - UserProfile
    - UserStreak
    - UserExerciseProgress
    - UserQuizAttempt
    - UserModuleMastery
    - CodeSubmission
    - Sessions

    This action is IRREVERSIBLE.

    Requires: JWT authentication + password confirmation
    """
    service = UserProfileService(db)

    try:
        await service.hard_delete_account(current_user.id, delete_data.password)
        return None
    except ValueError as e:
        if "Incorrect password" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

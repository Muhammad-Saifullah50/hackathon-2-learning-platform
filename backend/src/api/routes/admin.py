"""FastAPI routes for admin user management."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, require_role
from src.database import get_db
from src.models.user import User
from src.schemas.user_profile import AdminUserListResponse
from src.services.user_profile_service import UserProfileService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Users per page (max 100)"),
    role: Optional[str] = Query(
        None, pattern="^(student|teacher|admin)$", description="Filter by role"
    ),
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users with pagination and optional role filtering.

    Query parameters:
    - page: Page number (default: 1)
    - page_size: Users per page (default: 50, max: 100)
    - role: Filter by role (student, teacher, admin)

    Returns paginated list with:
    - users: List of user items
    - total: Total user count
    - page: Current page
    - page_size: Users per page
    - total_pages: Total pages

    Requires: JWT authentication + admin role
    """
    service = UserProfileService(db)
    result = await service.list_users(page=page, page_size=page_size, role=role)
    return result

"""FastAPI dependencies for database sessions and repositories."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_db
from src.repositories import (
    UserRepository,
    UserProfileRepository,
    UserStreakRepository,
    CurriculumRepository,
    ProgressRepository,
    SubmissionRepository,
    CacheRepository,
)


# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get async database session.

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async for session in get_async_db():
        yield session


# Repository dependencies
async def get_user_repository(db: AsyncSession = None) -> UserRepository:
    """Get UserRepository instance."""
    if db is None:
        async for session in get_async_db():
            return UserRepository(session)
    return UserRepository(db)


async def get_user_profile_repository(db: AsyncSession = None) -> UserProfileRepository:
    """Get UserProfileRepository instance."""
    if db is None:
        async for session in get_async_db():
            return UserProfileRepository(session)
    return UserProfileRepository(db)


async def get_user_streak_repository(db: AsyncSession = None) -> UserStreakRepository:
    """Get UserStreakRepository instance."""
    if db is None:
        async for session in get_async_db():
            return UserStreakRepository(session)
    return UserStreakRepository(db)


async def get_curriculum_repository(db: AsyncSession = None) -> CurriculumRepository:
    """Get CurriculumRepository instance."""
    if db is None:
        async for session in get_async_db():
            return CurriculumRepository(session)
    return CurriculumRepository(db)


async def get_progress_repository(db: AsyncSession = None) -> ProgressRepository:
    """Get ProgressRepository instance."""
    if db is None:
        async for session in get_async_db():
            return ProgressRepository(session)
    return ProgressRepository(db)


async def get_submission_repository(db: AsyncSession = None) -> SubmissionRepository:
    """Get SubmissionRepository instance."""
    if db is None:
        async for session in get_async_db():
            return SubmissionRepository(session)
    return SubmissionRepository(db)


async def get_cache_repository(db: AsyncSession = None) -> CacheRepository:
    """Get CacheRepository instance."""
    if db is None:
        async for session in get_async_db():
            return CacheRepository(session)
    return CacheRepository(db)

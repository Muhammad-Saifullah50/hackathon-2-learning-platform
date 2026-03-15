"""Submission repository - operations for CodeSubmission."""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.submission import CodeSubmission


class SubmissionRepository:
    """Repository for code submission operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_submission(
        self,
        user_id: str,
        exercise_id: int,
        code_text: str,
        result: dict,
        quality_rating: Optional[float] = None
    ) -> CodeSubmission:
        """Create a new code submission."""
        submission = CodeSubmission(
            user_id=user_id,
            exercise_id=exercise_id,
            code_text=code_text,
            result=result,
            quality_rating=quality_rating
        )
        self.session.add(submission)
        await self.session.commit()
        await self.session.refresh(submission)
        return submission

    async def get_submission_history(
        self,
        user_id: str,
        exercise_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[CodeSubmission]:
        """Get submission history for a user and exercise with pagination."""
        stmt = (
            select(CodeSubmission)
            .where(
                CodeSubmission.user_id == user_id,
                CodeSubmission.exercise_id == exercise_id
            )
            .order_by(CodeSubmission.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_failed_attempts_count(
        self,
        user_id: str,
        exercise_id: int
    ) -> int:
        """
        Get count of failed attempts for struggle detection.

        Counts submissions where result->>'success' = 'false'
        """
        stmt = (
            select(func.count(CodeSubmission.id))
            .where(
                CodeSubmission.user_id == user_id,
                CodeSubmission.exercise_id == exercise_id,
                CodeSubmission.result['success'].astext == 'false'
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def detect_error_patterns(
        self,
        user_id: str,
        exercise_id: int,
        min_occurrences: int = 3
    ) -> List[dict]:
        """
        Detect repeated error patterns for struggle detection.

        Returns list of error types that occurred >= min_occurrences times.
        """
        # Get all failed submissions
        stmt = (
            select(CodeSubmission)
            .where(
                CodeSubmission.user_id == user_id,
                CodeSubmission.exercise_id == exercise_id,
                CodeSubmission.result['success'].astext == 'false'
            )
            .order_by(CodeSubmission.created_at.desc())
        )
        result = await self.session.execute(stmt)
        submissions = list(result.scalars().all())

        # Count error patterns
        error_counts = {}
        for submission in submissions:
            stderr = submission.result.get('stderr', '')
            if stderr:
                # Extract error type (first line of stderr)
                error_type = stderr.split('\n')[0][:100]  # First 100 chars
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

        # Filter patterns that meet threshold
        patterns = [
            {'error_type': error_type, 'count': count}
            for error_type, count in error_counts.items()
            if count >= min_occurrences
        ]

        return patterns

    async def get_recent_submissions(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[CodeSubmission]:
        """Get recent submissions for a user across all exercises."""
        stmt = (
            select(CodeSubmission)
            .where(CodeSubmission.user_id == user_id)
            .order_by(CodeSubmission.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

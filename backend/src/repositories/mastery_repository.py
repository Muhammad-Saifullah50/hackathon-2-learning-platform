"""Mastery repository.

CRUD operations for mastery records.
"""

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.agent_exercise import MasteryRecord


class MasteryRepository:
    """Repository for mastery record operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_mastery(self, user_id: uuid.UUID, topic: str) -> MasteryRecord:
        """
        Get an existing mastery record or create a new one.

        Args:
            user_id: UUID of the user
            topic: Curriculum topic

        Returns:
            Existing or newly created MasteryRecord
        """
        stmt = select(MasteryRecord).where(
            MasteryRecord.user_id == user_id,
            MasteryRecord.topic == topic,
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            record = MasteryRecord(
                user_id=user_id,
                topic=topic,
                score=0.0,
                level="Beginner",
                component_breakdown={
                    "exercises": 0.0,
                    "quizzes": 0.0,
                    "code_quality": 0.0,
                    "streak": 0.0,
                    "missing_components": [
                        "exercises",
                        "quizzes",
                        "code_quality",
                        "streak",
                    ],
                },
            )
            self.session.add(record)
            await self.session.commit()
            await self.session.refresh(record)

        return record

    async def update_mastery(
        self,
        user_id: uuid.UUID,
        topic: str,
        score: float,
        level: str,
        component_breakdown: dict[str, Any],
    ) -> Optional[MasteryRecord]:
        """
        Update a mastery record.

        Args:
            user_id: UUID of the user
            topic: Curriculum topic
            score: Overall mastery score (0-100)
            level: Mapped mastery level
            component_breakdown: Breakdown of component scores

        Returns:
            Updated MasteryRecord if found, None otherwise
        """
        record = await self.get_or_create_mastery(user_id, topic)
        record.score = score
        record.level = level
        record.component_breakdown = component_breakdown

        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_user_mastery_records(self, user_id: uuid.UUID) -> list[MasteryRecord]:
        """
        Get all mastery records for a user.

        Args:
            user_id: UUID of the user

        Returns:
            List of MasteryRecord objects
        """
        stmt = (
            select(MasteryRecord)
            .where(MasteryRecord.user_id == user_id)
            .order_by(MasteryRecord.topic)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_mastery_by_topic(self, user_id: uuid.UUID, topic: str) -> Optional[MasteryRecord]:
        """
        Get mastery record for a specific topic.

        Args:
            user_id: UUID of the user
            topic: Curriculum topic

        Returns:
            MasteryRecord if found, None otherwise
        """
        stmt = select(MasteryRecord).where(
            MasteryRecord.user_id == user_id,
            MasteryRecord.topic == topic,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

"""Curriculum repository - operations for Module, Lesson, Exercise, Quiz."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.curriculum import Module, Lesson, Exercise, Quiz


class CurriculumRepository:
    """Repository for curriculum model operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Module operations
    async def get_all_modules(self) -> List[Module]:
        """Get all modules ordered by order field."""
        stmt = select(Module).where(Module.deleted_at.is_(None)).order_by(Module.order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_module_by_id(self, module_id: int) -> Optional[Module]:
        """Get module by ID."""
        stmt = select(Module).where(Module.id == module_id, Module.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Lesson operations
    async def get_lessons_by_module(self, module_id: int) -> List[Lesson]:
        """Get all lessons for a module ordered by order field."""
        stmt = (
            select(Lesson)
            .where(Lesson.module_id == module_id, Lesson.deleted_at.is_(None))
            .order_by(Lesson.order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """Get lesson by ID."""
        stmt = select(Lesson).where(Lesson.id == lesson_id, Lesson.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Exercise operations
    async def get_exercises_by_lesson(self, lesson_id: int) -> List[Exercise]:
        """Get all exercises for a lesson ordered by order field."""
        stmt = (
            select(Exercise)
            .where(Exercise.lesson_id == lesson_id, Exercise.deleted_at.is_(None))
            .order_by(Exercise.order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_exercise_by_id(self, exercise_id: int) -> Optional[Exercise]:
        """Get exercise by ID."""
        stmt = select(Exercise).where(Exercise.id == exercise_id, Exercise.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Quiz operations
    async def get_quizzes_by_lesson(self, lesson_id: int) -> List[Quiz]:
        """Get all quizzes for a lesson."""
        stmt = select(Quiz).where(Quiz.lesson_id == lesson_id, Quiz.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_quiz_by_id(self, quiz_id: int) -> Optional[Quiz]:
        """Get quiz by ID."""
        stmt = select(Quiz).where(Quiz.id == quiz_id, Quiz.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

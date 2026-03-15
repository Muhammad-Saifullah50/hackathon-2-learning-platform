"""Curriculum-related models: Module, Lesson, Exercise, Quiz."""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.database import Base
from src.models.base import SoftDeleteMixin, TimestampMixin


class Module(Base, TimestampMixin, SoftDeleteMixin):
    """
    Module model - represents the 8 Python curriculum modules.

    Each module contains multiple lessons and represents a major topic area.
    """
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, unique=True)

    # Relationships
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")
    user_mastery = relationship("UserModuleMastery", back_populates="module")


class Lesson(Base, TimestampMixin, SoftDeleteMixin):
    """
    Lesson model - represents learning units within modules.

    Each lesson contains exercises and quizzes.
    """
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey('modules.id', ondelete='RESTRICT'), nullable=False)
    title = Column(String(200), nullable=False)
    order = Column(Integer, nullable=False)
    content_ref = Column(String(500), nullable=False)

    # Relationships
    module = relationship("Module", back_populates="lessons")
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")


class Exercise(Base, TimestampMixin, SoftDeleteMixin):
    """
    Exercise model - represents coding challenges within lessons.

    Students write and execute code to complete exercises.
    """
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='RESTRICT'), nullable=False)
    title = Column(String(200), nullable=False)
    order = Column(Integer, nullable=False)
    starter_code = Column(Text, nullable=True)
    content_ref = Column(String(500), nullable=False)

    # Relationships
    lesson = relationship("Lesson", back_populates="exercises")
    user_progress = relationship("UserExerciseProgress", back_populates="exercise")
    code_submissions = relationship("CodeSubmission", back_populates="exercise")


class Quiz(Base, TimestampMixin, SoftDeleteMixin):
    """
    Quiz model - represents assessments for lessons or modules.

    Contains questions in JSONB format with expected answers.
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='RESTRICT'), nullable=True)
    title = Column(String(200), nullable=False)
    questions = Column(JSONB, nullable=False)

    # Relationships
    lesson = relationship("Lesson", back_populates="quizzes")
    user_attempts = relationship("UserQuizAttempt", back_populates="quiz")

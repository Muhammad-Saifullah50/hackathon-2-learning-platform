"""Progress tracking models: UserExerciseProgress, UserQuizAttempt, UserModuleMastery."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from src.database import Base
from src.models.base import TimestampMixin


class UserExerciseProgress(Base, TimestampMixin):
    """
    User exercise progress model - tracks student progress on exercises.

    Records status, score, attempts, and completion timestamp.
    """
    __tablename__ = "user_exercise_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id', ondelete='RESTRICT'), nullable=False)
    status = Column(String(20), nullable=False, server_default='not_started')
    score = Column(Float, nullable=True)
    attempts = Column(Integer, nullable=False, server_default='0')
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="exercise_progress")
    exercise = relationship("Exercise", back_populates="user_progress")

    __table_args__ = (
        CheckConstraint("status IN ('not_started', 'in_progress', 'completed')", name='check_exercise_status'),
        CheckConstraint('score >= 0 AND score <= 100', name='check_exercise_score_range'),
    )


class UserQuizAttempt(Base):
    """
    User quiz attempt model - tracks student quiz submissions.

    Stores score and answers for each quiz attempt.
    """
    __tablename__ = "user_quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='RESTRICT'), nullable=False)
    score = Column(Float, nullable=False)
    answers = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default='NOW()')

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="user_attempts")

    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 100', name='check_quiz_score_range'),
    )


class UserModuleMastery(Base, TimestampMixin):
    """
    User module mastery model - stores computed mastery scores.

    Uses optimistic locking (version column) for concurrent updates.
    Formula: 40% exercises + 30% quizzes + 20% code quality + 10% streak
    """
    __tablename__ = "user_module_mastery"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id', ondelete='RESTRICT'), nullable=False)
    score = Column(Float, nullable=False, server_default='0')
    version = Column(Integer, nullable=False, server_default='1')

    # Relationships
    user = relationship("User", back_populates="module_mastery")
    module = relationship("Module", back_populates="user_mastery")

    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 100', name='check_mastery_score_range'),
    )

    __mapper_args__ = {
        "version_id_col": version
    }

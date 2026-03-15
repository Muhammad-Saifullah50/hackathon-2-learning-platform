"""Models package - exports all SQLAlchemy models."""
from src.models.base import SoftDeleteMixin, TimestampMixin
from src.models.user import User, UserProfile, UserStreak
from src.models.curriculum import Module, Lesson, Exercise, Quiz
from src.models.progress import UserExerciseProgress, UserQuizAttempt, UserModuleMastery
from src.models.submission import CodeSubmission
from src.models.cache import LLMCache

__all__ = [
    # Base mixins
    "SoftDeleteMixin",
    "TimestampMixin",
    # User models
    "User",
    "UserProfile",
    "UserStreak",
    # Curriculum models
    "Module",
    "Lesson",
    "Exercise",
    "Quiz",
    # Progress models
    "UserExerciseProgress",
    "UserQuizAttempt",
    "UserModuleMastery",
    # Submission model
    "CodeSubmission",
    # Cache model
    "LLMCache",
]

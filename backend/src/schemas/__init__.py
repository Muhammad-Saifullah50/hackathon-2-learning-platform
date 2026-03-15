"""Schemas package - exports all Pydantic schemas."""
from src.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserPreferencesUpdate,
    UserResponse,
    UserProfileBase,
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserStreakResponse,
)
from src.schemas.curriculum import (
    ModuleBase,
    ModuleResponse,
    LessonBase,
    LessonResponse,
    ExerciseBase,
    ExerciseResponse,
    QuizQuestionSchema,
    QuizBase,
    QuizResponse,
)
from src.schemas.progress import (
    UserExerciseProgressBase,
    UserExerciseProgressCreate,
    UserExerciseProgressResponse,
    UserQuizAttemptBase,
    UserQuizAttemptCreate,
    UserQuizAttemptResponse,
    UserModuleMasteryBase,
    UserModuleMasteryResponse,
    MasteryCalculationRequest,
)
from src.schemas.submission import (
    CodeExecutionResult,
    CodeSubmissionBase,
    CodeSubmissionCreate,
    CodeSubmissionResponse,
    ErrorPattern,
)
from src.schemas.cache import (
    LLMCacheCreate,
    LLMCacheResponse,
    CacheLookupRequest,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPreferencesUpdate",
    "UserResponse",
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileResponse",
    "UserStreakResponse",
    # Curriculum schemas
    "ModuleBase",
    "ModuleResponse",
    "LessonBase",
    "LessonResponse",
    "ExerciseBase",
    "ExerciseResponse",
    "QuizQuestionSchema",
    "QuizBase",
    "QuizResponse",
    # Progress schemas
    "UserExerciseProgressBase",
    "UserExerciseProgressCreate",
    "UserExerciseProgressResponse",
    "UserQuizAttemptBase",
    "UserQuizAttemptCreate",
    "UserQuizAttemptResponse",
    "UserModuleMasteryBase",
    "UserModuleMasteryResponse",
    "MasteryCalculationRequest",
    # Submission schemas
    "CodeExecutionResult",
    "CodeSubmissionBase",
    "CodeSubmissionCreate",
    "CodeSubmissionResponse",
    "ErrorPattern",
    # Cache schemas
    "LLMCacheCreate",
    "LLMCacheResponse",
    "CacheLookupRequest",
]

"""Progress schemas for validation."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class UserExerciseProgressBase(BaseModel):
    """Base user exercise progress schema."""
    user_id: UUID
    exercise_id: int
    status: str = Field(default="not_started", pattern="^(not_started|in_progress|completed)$")
    score: Optional[float] = Field(None, ge=0, le=100)
    attempts: int = Field(default=0, ge=0)


class UserExerciseProgressCreate(BaseModel):
    """Schema for creating exercise progress."""
    exercise_id: int
    status: str = Field(pattern="^(not_started|in_progress|completed)$")
    score: Optional[float] = Field(None, ge=0, le=100)


class UserExerciseProgressResponse(UserExerciseProgressBase):
    """Schema for exercise progress response."""
    id: UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserQuizAttemptBase(BaseModel):
    """Base user quiz attempt schema."""
    quiz_id: int
    score: float = Field(ge=0, le=100)
    answers: Dict[str, Any]


class UserQuizAttemptCreate(UserQuizAttemptBase):
    """Schema for creating quiz attempt."""
    pass


class UserQuizAttemptResponse(UserQuizAttemptBase):
    """Schema for quiz attempt response."""
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserModuleMasteryBase(BaseModel):
    """Base user module mastery schema."""
    module_id: int
    score: float = Field(ge=0, le=100)


class UserModuleMasteryResponse(UserModuleMasteryBase):
    """Schema for module mastery response."""
    id: UUID
    user_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MasteryCalculationRequest(BaseModel):
    """Schema for mastery calculation request."""
    user_id: UUID
    module_id: int
    exercise_score: float = Field(ge=0, le=100)
    quiz_score: float = Field(ge=0, le=100)
    code_quality_score: float = Field(ge=0, le=100)
    streak_score: float = Field(ge=0, le=100)

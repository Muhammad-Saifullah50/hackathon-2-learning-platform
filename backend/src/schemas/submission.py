"""Submission schemas for validation."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class CodeExecutionResult(BaseModel):
    """Schema for code execution result."""
    stdout: str
    stderr: str
    execution_time_ms: int = Field(ge=0)
    success: bool


class CodeSubmissionBase(BaseModel):
    """Base code submission schema."""
    exercise_id: int
    code_text: str = Field(min_length=1, max_length=50000)
    result: CodeExecutionResult
    quality_rating: Optional[float] = Field(None, ge=0, le=100)


class CodeSubmissionCreate(CodeSubmissionBase):
    """Schema for creating code submission."""
    pass


class CodeSubmissionResponse(BaseModel):
    """Schema for code submission response."""
    id: UUID
    user_id: UUID
    exercise_id: int
    code_text: str
    result: Dict[str, Any]
    quality_rating: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorPattern(BaseModel):
    """Schema for detected error pattern."""
    error_type: str
    count: int

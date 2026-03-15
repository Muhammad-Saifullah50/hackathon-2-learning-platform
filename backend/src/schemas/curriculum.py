"""Curriculum schemas for validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ModuleBase(BaseModel):
    """Base module schema."""
    title: str = Field(min_length=1, max_length=100)
    description: str
    order: int = Field(ge=1, le=8)


class ModuleResponse(ModuleBase):
    """Schema for module response."""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LessonBase(BaseModel):
    """Base lesson schema."""
    module_id: int
    title: str = Field(min_length=1, max_length=200)
    order: int = Field(ge=1)
    content_ref: str = Field(min_length=1, max_length=500)


class LessonResponse(LessonBase):
    """Schema for lesson response."""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExerciseBase(BaseModel):
    """Base exercise schema."""
    lesson_id: int
    title: str = Field(min_length=1, max_length=200)
    order: int = Field(ge=1)
    starter_code: Optional[str] = None
    content_ref: str = Field(min_length=1, max_length=500)


class ExerciseResponse(ExerciseBase):
    """Schema for exercise response."""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuizQuestionSchema(BaseModel):
    """Schema for a single quiz question."""
    question: str
    type: str = Field(pattern="^(multiple_choice|true_false|short_answer)$")
    options: Optional[List[str]] = None
    correct_answer: str


class QuizBase(BaseModel):
    """Base quiz schema."""
    lesson_id: Optional[int] = None
    title: str = Field(min_length=1, max_length=200)
    questions: List[QuizQuestionSchema]


class QuizResponse(BaseModel):
    """Schema for quiz response."""
    id: int
    lesson_id: Optional[int] = None
    title: str
    questions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

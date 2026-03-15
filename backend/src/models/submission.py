"""Code submission model."""
from sqlalchemy import Column, Text, Float, ForeignKey, DateTime, CheckConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from src.database import Base


class CodeSubmission(Base):
    """
    Code submission model - stores all student code attempts.

    Records code text, execution results, and optional quality ratings.
    """
    __tablename__ = "code_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id', ondelete='RESTRICT'), nullable=False)
    code_text = Column(Text, nullable=False)
    result = Column(JSONB, nullable=False)
    quality_rating = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default='NOW()')

    # Relationships
    user = relationship("User", back_populates="code_submissions")
    exercise = relationship("Exercise", back_populates="code_submissions")

    __table_args__ = (
        CheckConstraint('quality_rating >= 0 AND quality_rating <= 100', name='check_quality_rating_range'),
    )

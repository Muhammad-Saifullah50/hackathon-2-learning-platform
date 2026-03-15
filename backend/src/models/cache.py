"""LLM cache model."""
from sqlalchemy import Column, String, Text, Integer, DateTime, CheckConstraint

from src.database import Base


class LLMCache(Base):
    """
    LLM cache model - caches LLM responses to reduce API costs.

    Uses SHA-256 hash as primary key for O(1) lookups.
    TTL strategy: curriculum content (indefinite), exercises (7-30 days).
    """
    __tablename__ = "llm_cache"

    cache_key_hash = Column(String(64), primary_key=True)
    prompt_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    model = Column(String(100), nullable=False)
    token_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default='NOW()')
    last_accessed_at = Column(DateTime(timezone=True), nullable=False, server_default='NOW()')
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint('token_count > 0', name='check_token_count_positive'),
    )

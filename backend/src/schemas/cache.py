"""Cache schemas for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LLMCacheCreate(BaseModel):
    """Schema for creating LLM cache entry."""
    prompt: str = Field(min_length=1)
    response: str = Field(min_length=1, max_length=50000)
    model: str = Field(min_length=1, max_length=100)
    token_count: int = Field(gt=0)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=600, gt=0)
    ttl_days: Optional[int] = Field(None, gt=0)


class LLMCacheResponse(BaseModel):
    """Schema for LLM cache response."""
    cache_key_hash: str
    prompt_text: str
    response_text: str
    model: str
    token_count: int
    created_at: datetime
    last_accessed_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CacheLookupRequest(BaseModel):
    """Schema for cache lookup request."""
    prompt: str
    model: str
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=600, gt=0)

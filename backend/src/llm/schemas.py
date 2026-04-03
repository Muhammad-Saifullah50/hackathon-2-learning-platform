"""Pydantic schemas for LLM provider API requests and responses."""

from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat message in a conversation."""

    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content text")


class LlmChatRequest(BaseModel):
    """Request body for the streaming chat endpoint."""

    system_prompt: str = Field(..., description="System prompt defining agent behavior")
    messages: list[ChatMessage] = Field(..., description="Conversation messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=600, gt=0, le=4096, description="Maximum output tokens")


class TokenUsage(BaseModel):
    """Token usage breakdown from LLM response."""

    input: int = Field(..., description="Input/prompt tokens")
    output: int = Field(..., description="Output/completion tokens")
    total: int = Field(..., description="Total tokens used")


class LlmStreamResponse(BaseModel):
    """Single SSE event from streaming response."""

    token: Optional[str] = Field(default=None, description="Single token chunk (streaming events)")
    index: Optional[int] = Field(default=None, description="Token index in response")
    done: Optional[bool] = Field(
        default=None, description="Whether streaming is complete (final event only)"
    )
    model: Optional[str] = Field(default=None, description="Model used (final event only)")
    tokens: Optional[TokenUsage] = Field(default=None, description="Token usage (final event only)")


class LlmErrorResponse(BaseModel):
    """Structured error response from LLM endpoints."""

    error: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message")
    detail: str = Field(..., description="Additional context (never includes sensitive data)")

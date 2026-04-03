"""LLM provider API routes - streaming chat and cache lookup."""

import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.auth.dependencies import get_current_user
from src.dependencies import get_cache_repository, get_llm_service
from src.llm.schemas import LlmChatRequest, LlmErrorResponse
from src.llm.service import LlmService
from src.repositories.cache_repository import CacheRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])


async def _stream_generator(
    request: LlmChatRequest,
    llm_service: LlmService,
) -> AsyncGenerator[str, None]:
    """
    Generate SSE events from the LLM service.

    Args:
        request: The chat request
        llm_service: LLM service instance

    Yields:
        SSE-formatted event strings
    """
    async for event in llm_service.stream_chat(request):
        yield event


@router.post(
    "/chat",
    summary="Send a chat request and receive a streaming response",
    description=(
        "Sends a prompt to the configured LLM provider and streams the response token-by-token "
        "via Server-Sent Events (SSE). Checks the PostgreSQL cache first — if an identical prompt "
        "has been seen before, returns the cached response immediately without calling the provider."
    ),
    responses={
        200: {
            "description": "Streaming response via Server-Sent Events",
            "content": {"text/event-stream": {}},
        },
        400: {
            "model": LlmErrorResponse,
            "description": "Invalid request (e.g., prompt exceeds token limit)",
        },
        401: {"description": "Unauthorized — missing or invalid JWT"},
        502: {"model": LlmErrorResponse, "description": "LLM provider error"},
        504: {"model": LlmErrorResponse, "description": "LLM provider timeout"},
    },
)
async def stream_chat(
    request: LlmChatRequest,
    llm_service: LlmService = Depends(get_llm_service),
    current_user=Depends(get_current_user),
):
    """
    Stream a chat response from the LLM provider.

    Args:
        request: Chat request with system prompt and messages
        llm_service: Injected LLM service
        current_user: Authenticated user

    Returns:
        StreamingResponse with SSE events
    """
    logger.debug("LLM chat request from user=%s", current_user.email)

    return StreamingResponse(
        _stream_generator(request, llm_service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/cache/lookup",
    summary="Check if a prompt response is cached",
    description=(
        "Checks whether an identical prompt (same system prompt, messages, temperature, and max_tokens) "
        "has been previously answered and cached. Returns the cached response if available, or 404 if not."
    ),
    responses={
        200: {"description": "Cached response found"},
        404: {"description": "No cached response found"},
        401: {"description": "Unauthorized — missing or invalid JWT"},
    },
)
async def lookup_cache(
    request: LlmChatRequest,
    llm_service: LlmService = Depends(get_llm_service),
    current_user=Depends(get_current_user),
):
    """
    Check if a prompt response is cached.

    Args:
        request: Chat request to check cache for
        llm_service: Injected LLM service
        current_user: Authenticated user

    Returns:
        Dict with cached response info or cache miss indicator

    Raises:
        HTTPException: 404 if not cached
    """
    logger.debug("Cache lookup request from user=%s", current_user.email)

    result = await llm_service.lookup_cache(request)

    if result:
        return result

    raise HTTPException(status_code=404, detail={"cached": False})

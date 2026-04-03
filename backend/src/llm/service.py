"""LLM service layer - orchestrates cache check, LLM call, cache write, and streaming."""

import json
import logging
from typing import AsyncGenerator, Optional

from src.config import settings
from src.llm.client import LlmClient
from src.llm.schemas import LlmChatRequest, TokenUsage

logger = logging.getLogger(__name__)


def _estimate_tokens(text: str) -> int:
    """
    Estimate token count using character-based heuristic.

    Uses ~4 characters per token as a fast approximation for English text.

    Args:
        text: Input text to estimate

    Returns:
        Estimated token count
    """
    return max(1, len(text) // 4)


def _build_messages(system_prompt: str, messages: list) -> list[dict]:
    """
    Build the messages list for the LLM API call.

    Args:
        system_prompt: System prompt text
        messages: List of ChatMessage objects

    Returns:
        List of message dicts with 'role' and 'content' keys
    """
    return [{"role": "system", "content": system_prompt}] + [
        {"role": msg.role, "content": msg.content} for msg in messages
    ]


def _build_prompt_hash(system_prompt: str, messages: list) -> str:
    """
    Build a hashable prompt string for cache key generation.

    Args:
        system_prompt: System prompt text
        messages: List of ChatMessage objects

    Returns:
        Combined prompt string for cache hashing
    """
    parts = [system_prompt]
    for msg in messages:
        parts.append(f"{msg.role}: {msg.content}")
    return "\n".join(parts)


class LlmService:
    """
    Service layer for LLM operations.

    Orchestrates:
    1. Cache check before LLM call
    2. LLM streaming completion
    3. Cache write after successful completion
    4. Streaming response to client
    """

    def __init__(
        self,
        client: LlmClient,
        cache_repository=None,
    ):
        """
        Initialize the LLM service.

        Args:
            client: LlmClient instance for making LLM API calls
            cache_repository: CacheRepository for prompt/response caching
        """
        self.client = client
        self.cache_repository = cache_repository

    def _validate_input_tokens(self, request: LlmChatRequest) -> Optional[str]:
        """
        Validate that input prompt does not exceed maximum token limit.

        Args:
            request: The chat request to validate

        Returns:
            Error message if validation fails, None if valid
        """
        full_prompt = _build_prompt_hash(request.system_prompt, request.messages)
        estimated_tokens = _estimate_tokens(full_prompt)

        if estimated_tokens > settings.LLM_MAX_INPUT_TOKENS:
            return (
                f"Prompt exceeds maximum input token limit of {settings.LLM_MAX_INPUT_TOKENS} tokens. "
                f"Estimated {estimated_tokens:,} tokens in input."
            )
        return None

    async def stream_chat(
        self,
        request: LlmChatRequest,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat response, checking cache first.

        Flow:
        1. Validate input tokens
        2. Check cache for existing response
        3. If cache hit: return cached response as stream
        4. If cache miss: call LLM, stream tokens, cache result
        5. Yield SSE-formatted events

        Args:
            request: The chat request with system prompt and messages

        Yields:
            SSE-formatted event strings

        Raises:
            ValueError: If input validation fails
        """
        # Validate input tokens
        validation_error = self._validate_input_tokens(request)
        if validation_error:
            error_event = (
                f'data: {{"error": "invalid_request", "message": "{validation_error}"}}\n\n'
            )
            yield error_event
            return

        # Build messages for LLM
        messages = _build_messages(request.system_prompt, request.messages)
        prompt_for_cache = _build_prompt_hash(request.system_prompt, request.messages)

        # Check cache
        if self.cache_repository:
            try:
                cache_key = self.cache_repository.generate_cache_key(
                    prompt=prompt_for_cache,
                    model=settings.LLM_MODEL,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )
                cached_response = await self.cache_repository.get_cached_response(cache_key)

                if cached_response:
                    logger.debug("Cache hit for prompt hash (key=%s...)", cache_key[:8])
                    # Stream cached response as single event
                    yield f'data: {{"token": {json.dumps(cached_response)}, "index": 0}}\n\n'
                    yield f'data: {{"done": true, "model": "{settings.LLM_MODEL}", "tokens": {{"input": 0, "output": 0, "total": 0}}}}\n\n'
                    return
            except Exception as e:
                # If cache is unavailable, proceed to LLM call
                logger.warning("Cache unavailable, proceeding to LLM: %s", str(e))

        # Cache miss - call LLM
        logger.debug("Cache miss, calling LLM provider")
        full_response = []
        index = 0
        usage = None

        try:
            async for token_content, token_usage in self.client.stream_completion(
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            ):
                if token_content:
                    full_response.append(token_content)
                    escaped_token = json.dumps(token_content)
                    yield f'data: {{"token": {escaped_token}, "index": {index}}}\n\n'
                    index += 1

                if token_usage:
                    usage = token_usage

        except Exception as e:
            # Mid-stream failure - do NOT cache partial response
            logger.error("Streaming error: %s", str(e))
            error_type = "timeout" if "timed out" in str(e).lower() else "provider_error"
            yield f'data: {{"error": "{error_type}", "message": "LLM provider returned an error"}}\n\n'
            return

        # Cache the full response
        if self.cache_repository and full_response and usage:
            try:
                await self.cache_repository.set_cached_response(
                    prompt=prompt_for_cache,
                    response="".join(full_response),
                    model=settings.LLM_MODEL,
                    token_count=usage.get("total", 0),
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    ttl_days=settings.LLM_CACHE_TTL_DAYS,
                )
                logger.debug("Cached LLM response (key=%s...)", cache_key[:8])
            except Exception as e:
                logger.warning("Failed to cache response: %s", str(e))

        # Send final event with usage
        final_tokens = usage if usage else {"input": 0, "output": 0, "total": 0}
        yield f'data: {{"done": true, "model": "{settings.LLM_MODEL}", "tokens": {{"input": {final_tokens["input"]}, "output": {final_tokens["output"]}, "total": {final_tokens["total"]}}}}}\n\n'

    async def lookup_cache(
        self,
        request: LlmChatRequest,
    ) -> Optional[dict]:
        """
        Check if a prompt response is cached.

        Args:
            request: The chat request to check

        Returns:
            Dict with cached response info if found, None if not cached
        """
        if not self.cache_repository:
            return None

        prompt_for_cache = _build_prompt_hash(request.system_prompt, request.messages)

        try:
            cache_key = self.cache_repository.generate_cache_key(
                prompt=prompt_for_cache,
                model=settings.LLM_MODEL,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            cached_response = await self.cache_repository.get_cached_response(cache_key)

            if cached_response:
                return {
                    "cached": True,
                    "response": cached_response,
                    "model": settings.LLM_MODEL,
                }
        except Exception as e:
            logger.warning("Cache lookup error: %s", str(e))

        return None

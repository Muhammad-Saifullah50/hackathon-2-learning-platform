"""LiteLLM client wrapper with streaming, timeout, and error handling."""

import json
import logging
from typing import AsyncGenerator, Optional

import litellm
from litellm import APIError, AuthenticationError, RateLimitError, Timeout

from src.config import settings

logger = logging.getLogger(__name__)


def _redact_api_key(api_key: str) -> str:
    """Redact API key for logging, showing only first/last 4 characters."""
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:4]}...{api_key[-4:]}"


class LlmClient:
    """Async LiteLLM client wrapper with streaming, timeout, and error handling."""

    def __init__(
        self,
        model: str = None,
        api_key: str = None,
        api_base: str = None,
        timeout: int = None,
    ):
        """
        Initialize the LLM client.

        Args:
            model: LiteLLM model identifier (e.g., 'openrouter/qwen-3.6')
            api_key: API key for the provider
            api_base: Base URL for the provider API
            timeout: Request timeout in seconds
        """
        self.model = model or settings.LLM_MODEL
        self.api_key = api_key or settings.LLM_API_KEY
        self.api_base = api_base or settings.LLM_BASE_URL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

        logger.debug(
            "LLM client initialized - model=%s, api_base=%s, api_key=%s",
            self.model,
            self.api_base,
            _redact_api_key(self.api_key),
        )

    async def stream_completion(
        self,
        messages: list[dict],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[tuple[str, Optional[dict]], None]:
        """
        Stream completion tokens from the LLM provider.

        Yields tuples of (token_content, usage_metadata).
        usage_metadata is None for streaming chunks, populated on the final chunk.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Yields:
            Tuple of (token_string, usage_dict_or_None)

        Raises:
            AuthenticationError: If API key is invalid
            Timeout: If request exceeds configured timeout
            APIError: If provider returns an error
        """
        max_tokens = max_tokens or settings.LLM_MAX_OUTPUT_TOKENS
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE

        logger.debug(
            "Streaming completion - model=%s, messages=%d, max_tokens=%d, temperature=%.2f",
            self.model,
            len(messages),
            max_tokens,
            temperature,
        )

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                api_base=self.api_base,
                stream=True,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout,
            )

            async for chunk in response:
                delta = chunk.choices[0].delta
                usage = None

                # Extract token usage from final chunk if available
                if hasattr(chunk, "usage") and chunk.usage:
                    usage = {
                        "input": getattr(chunk.usage, "prompt_tokens", 0),
                        "output": getattr(chunk.usage, "completion_tokens", 0),
                        "total": getattr(chunk.usage, "total_tokens", 0),
                    }

                token_content = delta.content if delta and delta.content else ""
                yield token_content, usage

                if usage:
                    logger.debug(
                        "LLM token usage - input=%d, output=%d, total=%d",
                        usage["input"],
                        usage["output"],
                        usage["total"],
                    )

        except AuthenticationError as e:
            logger.error("LLM authentication failed: %s", str(e))
            raise
        except Timeout as e:
            logger.error("LLM request timed out after %ds: %s", self.timeout, str(e))
            raise
        except RateLimitError as e:
            logger.error("LLM rate limit exceeded: %s", str(e))
            raise
        except APIError as e:
            logger.error("LLM API error: %s", str(e))
            raise
        except Exception as e:
            logger.error("Unexpected LLM client error: %s", str(e))
            raise

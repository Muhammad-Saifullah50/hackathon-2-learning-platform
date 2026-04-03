"""Unit tests for LLM service layer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.llm.schemas import ChatMessage, LlmChatRequest
from src.llm.service import LlmService, _build_messages, _build_prompt_hash, _estimate_tokens


class TestEstimateTokens:
    """Tests for token estimation utility."""

    def test_estimates_short_text(self):
        tokens = _estimate_tokens("Hello world")
        assert tokens > 0

    def test_estimates_longer_text(self):
        tokens = _estimate_tokens("This is a longer piece of text for testing purposes")
        assert tokens > 0

    def test_returns_at_least_one(self):
        tokens = _estimate_tokens("a")
        assert tokens >= 1


class TestBuildMessages:
    """Tests for message building utility."""

    def test_builds_system_and_user_messages(self):
        messages = [ChatMessage(role="user", content="What is Python?")]
        result = _build_messages("You are a tutor.", messages)

        assert len(result) == 2
        assert result[0] == {"role": "system", "content": "You are a tutor."}
        assert result[1] == {"role": "user", "content": "What is Python?"}

    def test_builds_multiple_messages(self):
        messages = [
            ChatMessage(role="user", content="Hi"),
            ChatMessage(role="assistant", content="Hello!"),
        ]
        result = _build_messages("System", messages)

        assert len(result) == 3
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"
        assert result[2]["role"] == "assistant"


class TestBuildPromptHash:
    """Tests for prompt hash building utility."""

    def test_combines_system_and_messages(self):
        messages = [ChatMessage(role="user", content="Hello")]
        result = _build_prompt_hash("You are helpful", messages)

        assert "You are helpful" in result
        assert "user: Hello" in result


class TestLlmServiceValidateInput:
    """Tests for LlmService input validation."""

    def test_rejects_oversized_prompt(self):
        client = MagicMock()
        service = LlmService(client=client)

        long_content = "x" * 10000
        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content=long_content)],
        )

        error = service._validate_input_tokens(request)
        assert error is not None
        assert "exceeds maximum" in error

    def test_accepts_normal_prompt(self):
        client = MagicMock()
        service = LlmService(client=client)

        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content="What is a variable?")],
        )

        error = service._validate_input_tokens(request)
        assert error is None


class TestLlmServiceStreamChat:
    """Tests for LlmService streaming chat."""

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_response(self):
        client = MagicMock()
        cache_repo = AsyncMock()
        cache_repo.generate_cache_key.return_value = "abc123"
        cache_repo.get_cached_response.return_value = "Cached answer"

        service = LlmService(client=client, cache_repository=cache_repo)

        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content="What is Python?")],
        )

        events = []
        async for event in service.stream_chat(request):
            events.append(event)

        assert len(events) == 2
        assert "Cached answer" in events[0]
        assert "done" in events[1]

    @pytest.mark.asyncio
    @patch("src.llm.client.settings")
    async def test_cache_miss_calls_llm_and_streams(self, mock_settings):
        mock_settings.LLM_MODEL = "test/model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "https://test.api"
        mock_settings.LLM_TIMEOUT_SECONDS = 30
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_OUTPUT_TOKENS = 600
        mock_settings.LLM_CACHE_TTL_DAYS = 30
        mock_settings.LLM_MAX_INPUT_TOKENS = 1200

        client = MagicMock()

        async def mock_stream(messages, **kwargs):
            yield "Hello", None
            yield " world", {"input": 5, "output": 3, "total": 8}

        client.stream_completion = mock_stream

        cache_repo = AsyncMock()
        cache_repo.generate_cache_key.return_value = "abc123"
        cache_repo.get_cached_response.return_value = None
        cache_repo.set_cached_response.return_value = MagicMock()

        service = LlmService(client=client, cache_repository=cache_repo)

        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content="Hi")],
        )

        events = []
        async for event in service.stream_chat(request):
            events.append(event)

        assert len(events) >= 3
        assert '"done": true' in events[-1]
        assert '"model": "test/model"' in events[-1]
        cache_repo.set_cached_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_unavailable_proceeds_to_llm(self):
        client = MagicMock()

        async def mock_stream(messages, **kwargs):
            yield "Response", {"input": 1, "output": 1, "total": 2}

        client.stream_completion = mock_stream

        cache_repo = AsyncMock()
        cache_repo.generate_cache_key.side_effect = Exception("Cache down")

        service = LlmService(client=client, cache_repository=cache_repo)

        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content="Hi")],
        )

        events = []
        async for event in service.stream_chat(request):
            events.append(event)

        assert len(events) >= 1
        assert "Response" in events[0] or "done" in events[-1]


class TestLlmServiceLookupCache:
    """Tests for LlmService cache lookup."""

    @pytest.mark.asyncio
    async def test_returns_cached_response_when_found(self):
        client = MagicMock()
        cache_repo = AsyncMock()
        cache_repo.generate_cache_key.return_value = "abc123"
        cache_repo.get_cached_response.return_value = "Cached answer"

        service = LlmService(client=client, cache_repository=cache_repo)

        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content="What is Python?")],
        )

        result = await service.lookup_cache(request)

        assert result is not None
        assert result["cached"] is True
        assert result["response"] == "Cached answer"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_cached(self):
        client = MagicMock()
        cache_repo = AsyncMock()
        cache_repo.generate_cache_key.return_value = "abc123"
        cache_repo.get_cached_response.return_value = None

        service = LlmService(client=client, cache_repository=cache_repo)

        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content="What is Python?")],
        )

        result = await service.lookup_cache(request)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_no_cache_repo(self):
        client = MagicMock()
        service = LlmService(client=client, cache_repository=None)

        request = LlmChatRequest(
            system_prompt="You are a tutor.",
            messages=[ChatMessage(role="user", content="What is Python?")],
        )

        result = await service.lookup_cache(request)

        assert result is None

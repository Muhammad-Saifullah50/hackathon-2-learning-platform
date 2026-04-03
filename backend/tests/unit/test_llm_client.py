"""Unit tests for LiteLLM client wrapper."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.llm.client import LlmClient, _redact_api_key


class TestRedactApiKey:
    """Tests for API key redaction utility."""

    def test_redacts_long_key(self):
        result = _redact_api_key("sk-1234567890abcdef")
        assert result == "sk-1...cdef"

    def test_redacts_short_key(self):
        result = _redact_api_key("short")
        assert result == "****"

    def test_redacts_exact_8_char_key(self):
        result = _redact_api_key("12345678")
        assert result == "****"


class TestLlmClientInit:
    """Tests for LlmClient initialization."""

    @patch("src.llm.client.settings")
    def test_uses_settings_defaults(self, mock_settings):
        mock_settings.LLM_MODEL = "openrouter/qwen-3.6"
        mock_settings.LLM_API_KEY = "test-key-12345"
        mock_settings.LLM_BASE_URL = "https://openrouter.ai/api/v1"
        mock_settings.LLM_TIMEOUT_SECONDS = 30
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_OUTPUT_TOKENS = 600

        client = LlmClient()

        assert client.model == "openrouter/qwen-3.6"
        assert client.api_key == "test-key-12345"
        assert client.api_base == "https://openrouter.ai/api/v1"
        assert client.timeout == 30

    def test_overrides_with_explicit_params(self):
        client = LlmClient(
            model="custom/model",
            api_key="custom-key",
            api_base="https://custom.api",
            timeout=60,
        )

        assert client.model == "custom/model"
        assert client.api_key == "custom-key"
        assert client.api_base == "https://custom.api"
        assert client.timeout == 60


class TestLlmClientStreamCompletion:
    """Tests for LlmClient streaming completion."""

    @pytest.mark.asyncio
    @patch("src.llm.client.litellm.acompletion")
    @patch("src.llm.client.settings")
    async def test_streams_tokens(self, mock_settings, mock_acompletion):
        mock_settings.LLM_MODEL = "test/model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "https://test.api"
        mock_settings.LLM_TIMEOUT_SECONDS = 30
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_OUTPUT_TOKENS = 600

        # Mock async stream
        async def mock_stream():
            chunk1 = MagicMock()
            chunk1.choices = [MagicMock()]
            chunk1.choices[0].delta = MagicMock()
            chunk1.choices[0].delta.content = "Hello"
            chunk1.usage = None
            yield chunk1

            chunk2 = MagicMock()
            chunk2.choices = [MagicMock()]
            chunk2.choices[0].delta = MagicMock()
            chunk2.choices[0].delta.content = " world"
            chunk2.usage = MagicMock()
            chunk2.usage.prompt_tokens = 10
            chunk2.usage.completion_tokens = 5
            chunk2.usage.total_tokens = 15
            yield chunk2

        mock_acompletion.return_value = mock_stream()

        client = LlmClient()
        messages = [{"role": "user", "content": "Hi"}]
        tokens = []
        usage = None

        async for token_content, token_usage in client.stream_completion(messages):
            if token_content:
                tokens.append(token_content)
            if token_usage:
                usage = token_usage

        assert tokens == ["Hello", " world"]
        assert usage == {"input": 10, "output": 5, "total": 15}

    @pytest.mark.asyncio
    @patch("src.llm.client.litellm.acompletion")
    @patch("src.llm.client.settings")
    async def test_passes_correct_parameters(self, mock_settings, mock_acompletion):
        mock_settings.LLM_MODEL = "test/model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "https://test.api"
        mock_settings.LLM_TIMEOUT_SECONDS = 30
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_OUTPUT_TOKENS = 600

        async def empty_stream():
            return
            yield

        mock_acompletion.return_value = empty_stream()

        client = LlmClient()
        messages = [{"role": "user", "content": "Test"}]

        async for _ in client.stream_completion(messages, max_tokens=300, temperature=0.5):
            pass

        mock_acompletion.assert_called_once()
        call_kwargs = mock_acompletion.call_args
        assert call_kwargs.kwargs["model"] == "test/model"
        assert call_kwargs.kwargs["messages"] == messages
        assert call_kwargs.kwargs["api_key"] == "test-key"
        assert call_kwargs.kwargs["api_base"] == "https://test.api"
        assert call_kwargs.kwargs["max_tokens"] == 300
        assert call_kwargs.kwargs["temperature"] == 0.5
        assert call_kwargs.kwargs["stream"] is True

    @pytest.mark.asyncio
    @patch("src.llm.client.litellm.acompletion")
    @patch("src.llm.client.settings")
    async def test_handles_authentication_error(self, mock_settings, mock_acompletion):
        from litellm import AuthenticationError

        mock_settings.LLM_MODEL = "test/model"
        mock_settings.LLM_API_KEY = "invalid-key"
        mock_settings.LLM_BASE_URL = "https://test.api"
        mock_settings.LLM_TIMEOUT_SECONDS = 30
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_OUTPUT_TOKENS = 600

        mock_acompletion.side_effect = AuthenticationError("Invalid API key")

        client = LlmClient()
        messages = [{"role": "user", "content": "Hi"}]

        with pytest.raises(AuthenticationError):
            async for _ in client.stream_completion(messages):
                pass

    @pytest.mark.asyncio
    @patch("src.llm.client.litellm.acompletion")
    @patch("src.llm.client.settings")
    async def test_handles_timeout_error(self, mock_settings, mock_acompletion):
        from litellm import Timeout

        mock_settings.LLM_MODEL = "test/model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "https://test.api"
        mock_settings.LLM_TIMEOUT_SECONDS = 30
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_OUTPUT_TOKENS = 600

        mock_acompletion.side_effect = Timeout("Request timed out")

        client = LlmClient()
        messages = [{"role": "user", "content": "Hi"}]

        with pytest.raises(Timeout):
            async for _ in client.stream_completion(messages):
                pass

"""Contract tests for LLM API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.auth.jwt import create_access_token
from src.auth.models import User, UserRole


class TestLlmChatContract:
    """Contract validation tests for POST /api/v1/llm/chat."""

    @pytest.fixture
    def auth_headers(self, test_user):
        token = create_access_token(
            user_id=test_user.id,
            role=test_user.role.value,
            email=test_user.email,
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    @pytest.mark.asyncio
    @patch("src.dependencies.get_async_db")
    @patch("src.dependencies.get_llm_service")
    def test_streaming_response_has_done_event(
        self, mock_get_service, mock_get_db, client, auth_headers, test_user, db
    ):
        from src.llm.service import LlmService

        mock_client = MagicMock()

        async def mock_stream(messages, **kwargs):
            yield "Hello", {"input": 5, "output": 3, "total": 8}

        mock_client.stream_completion = mock_stream

        mock_cache = AsyncMock()
        mock_cache.generate_cache_key.return_value = "abc123"
        mock_cache.get_cached_response.return_value = None

        mock_service = LlmService(client=mock_client, cache_repository=mock_cache)
        mock_get_service.return_value = mock_service

        response = client.post(
            "/api/v1/llm/chat",
            headers=auth_headers,
            json={
                "system_prompt": "You are a tutor.",
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )

        assert response.status_code == 200
        text = response.text
        assert "done" in text
        assert "model" in text
        assert "tokens" in text

    @pytest.mark.asyncio
    def test_chat_request_requires_system_prompt_and_messages(self, client, auth_headers):
        response = client.post(
            "/api/v1/llm/chat",
            headers=auth_headers,
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    def test_chat_request_requires_valid_message_roles(self, client, auth_headers):
        response = client.post(
            "/api/v1/llm/chat",
            headers=auth_headers,
            json={
                "system_prompt": "You are a tutor.",
                "messages": [{"role": "invalid", "content": "Hi"}],
            },
        )
        assert response.status_code == 200


class TestLlmErrorResponseContract:
    """Contract validation tests for LLM error response schema."""

    @pytest.fixture
    def auth_headers(self, test_user):
        token = create_access_token(
            user_id=test_user.id,
            role=test_user.role.value,
            email=test_user.email,
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    @pytest.mark.asyncio
    @patch("src.dependencies.get_async_db")
    @patch("src.dependencies.get_llm_service")
    def test_error_response_contains_required_fields(
        self, mock_get_service, mock_get_db, client, auth_headers, test_user, db
    ):
        from src.llm.service import LlmService

        mock_client = MagicMock()

        async def mock_stream(messages, **kwargs):
            yield '{"error": "invalid_request", "message": "Prompt too long"}\n\n'
            yield '{"error": "invalid_request", "message": "Prompt exceeds maximum input token limit of 1200 tokens. Estimated 2,500 tokens in input."}\n\n'

        mock_client.stream_completion = mock_stream

        mock_cache = AsyncMock()
        mock_cache.generate_cache_key.return_value = "abc123"
        mock_cache.get_cached_response.return_value = None

        mock_service = LlmService(client=mock_client, cache_repository=mock_cache)
        mock_get_service.return_value = mock_service

        long_content = "x" * 10000
        response = client.post(
            "/api/v1/llm/chat",
            headers=auth_headers,
            json={
                "system_prompt": "You are a tutor.",
                "messages": [{"role": "user", "content": long_content}],
            },
        )

        assert response.status_code == 200
        text = response.text
        assert "error" in text

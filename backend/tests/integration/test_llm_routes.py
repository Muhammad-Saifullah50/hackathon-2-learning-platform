"""Integration tests for LLM routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.auth.jwt import create_access_token
from src.auth.models import User, UserRole


class TestLlmChatEndpoint:
    """Integration tests for POST /api/v1/llm/chat."""

    @pytest.fixture
    def auth_headers(self, test_user):
        token = create_access_token(
            user_id=test_user.id,
            role=test_user.role.value,
            email=test_user.email,
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    @pytest.mark.asyncio
    def test_streaming_chat_requires_auth(self, client):
        response = client.post(
            "/api/v1/llm/chat",
            json={
                "system_prompt": "You are a tutor.",
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("src.dependencies.get_async_db")
    @patch("src.dependencies.get_llm_service")
    def test_streaming_chat_returns_sse_events(
        self, mock_get_service, mock_get_db, client, auth_headers, test_user, db
    ):
        from src.llm.schemas import ChatMessage, LlmChatRequest
        from src.llm.service import LlmService

        mock_client = MagicMock()

        async def mock_stream(messages, **kwargs):
            yield "Hello", None
            yield " world", {"input": 5, "output": 3, "total": 8}

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
        assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    @patch("src.dependencies.get_async_db")
    @patch("src.dependencies.get_llm_service")
    def test_streaming_chat_rejects_oversized_prompt(
        self, mock_get_service, mock_get_db, client, auth_headers, test_user, db
    ):
        from src.llm.service import LlmService

        mock_service = MagicMock(spec=LlmService)
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
        content = response.text
        assert "error" in content or "exceeds" in content.lower()


class TestLlmCacheLookupEndpoint:
    """Integration tests for POST /api/v1/llm/cache/lookup."""

    @pytest.fixture
    def auth_headers(self, test_user):
        token = create_access_token(
            user_id=test_user.id,
            role=test_user.role.value,
            email=test_user.email,
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    @pytest.mark.asyncio
    def test_cache_lookup_requires_auth(self, client):
        response = client.post(
            "/api/v1/llm/cache/lookup",
            json={
                "system_prompt": "You are a tutor.",
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("src.dependencies.get_async_db")
    @patch("src.dependencies.get_llm_service")
    def test_cache_lookup_returns_404_when_not_cached(
        self, mock_get_service, mock_get_db, client, auth_headers, test_user, db
    ):
        from src.llm.service import LlmService

        mock_service = MagicMock(spec=LlmService)

        async def mock_lookup(request):
            return None

        mock_service.lookup_cache = mock_lookup
        mock_get_service.return_value = mock_service

        response = client.post(
            "/api/v1/llm/cache/lookup",
            headers=auth_headers,
            json={
                "system_prompt": "You are a tutor.",
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch("src.dependencies.get_async_db")
    @patch("src.dependencies.get_llm_service")
    def test_cache_lookup_returns_200_when_cached(
        self, mock_get_service, mock_get_db, client, auth_headers, test_user, db
    ):
        from src.llm.service import LlmService

        mock_service = MagicMock(spec=LlmService)

        async def mock_lookup(request):
            return {
                "cached": True,
                "response": "Cached answer",
                "model": "test/model",
            }

        mock_service.lookup_cache = mock_lookup
        mock_get_service.return_value = mock_service

        response = client.post(
            "/api/v1/llm/cache/lookup",
            headers=auth_headers,
            json={
                "system_prompt": "You are a tutor.",
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True
        assert data["response"] == "Cached answer"

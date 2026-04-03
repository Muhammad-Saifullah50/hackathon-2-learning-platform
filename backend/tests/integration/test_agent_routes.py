"""Integration tests for agent routes."""

import pytest

from src.main import app


class TestAgentRoutes:
    """Integration tests for agent API endpoints."""

    def test_chat_requires_auth(self, client, setup_test_database):
        response = client.post(
            "/api/v1/agents/chat",
            json={"message": "What is a list?"},
        )
        assert response.status_code in [401, 403]

    def test_get_session_requires_auth(self, client, setup_test_database):
        response = client.get("/api/v1/agents/sessions/fake-id")
        assert response.status_code in [401, 403]

    def test_generate_exercise_requires_auth(self, client, setup_test_database):
        response = client.post(
            "/api/v1/agents/exercises",
            json={"topic": "loops", "difficulty": "beginner"},
        )
        assert response.status_code in [401, 403]

    def test_submit_exercise_requires_auth(self, client, setup_test_database):
        response = client.post(
            "/api/v1/agents/exercises/fake-id/submit",
            json={"code": "print('hello')"},
        )
        assert response.status_code in [401, 403]

    def test_advance_hint_requires_auth(self, client, setup_test_database):
        response = client.post(
            "/api/v1/agents/hints/advance",
            json={"session_id": "fake-id"},
        )
        assert response.status_code in [401, 403]

    def test_progress_requires_auth(self, client, setup_test_database):
        response = client.get("/api/v1/agents/progress")
        assert response.status_code in [401, 403]

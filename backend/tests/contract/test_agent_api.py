"""Contract tests for agent API against OpenAPI spec."""

import pytest


class TestAgentAPIContracts:
    """Contract tests validating agent endpoints against expected API shape."""

    def test_chat_endpoint_exists(self, client, setup_test_database):
        response = client.post("/api/v1/agents/chat", json={"message": "test"})
        assert response.status_code != 404

    def test_sessions_endpoint_exists(self, client, setup_test_database):
        response = client.get("/api/v1/agents/sessions/fake-id")
        assert response.status_code != 404

    def test_exercises_endpoint_exists(self, client, setup_test_database):
        response = client.post(
            "/api/v1/agents/exercises",
            json={"topic": "test", "difficulty": "beginner"},
        )
        assert response.status_code != 404

    def test_submit_exercise_endpoint_exists(self, client, setup_test_database):
        response = client.post("/api/v1/agents/exercises/fake-id/submit", json={"code": "test"})
        assert response.status_code != 404

    def test_hints_advance_endpoint_exists(self, client, setup_test_database):
        response = client.post("/api/v1/agents/hints/advance", json={"session_id": "fake"})
        assert response.status_code != 404

    def test_progress_endpoint_exists(self, client, setup_test_database):
        response = client.get("/api/v1/agents/progress")
        assert response.status_code != 404

    def test_chat_request_validation(self, client, setup_test_database):
        response = client.post("/api/v1/agents/chat", json={})
        assert response.status_code in [401, 403, 422]

    def test_exercise_request_validation(self, client, setup_test_database):
        response = client.post("/api/v1/agents/exercises", json={})
        assert response.status_code in [401, 403, 422]

    def test_hint_advance_request_validation(self, client, setup_test_database):
        response = client.post("/api/v1/agents/hints/advance", json={})
        assert response.status_code in [401, 403, 422]

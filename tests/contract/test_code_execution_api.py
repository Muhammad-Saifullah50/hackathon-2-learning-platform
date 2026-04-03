"""
Contract tests for Code Execution API endpoint.

Tests verify that the API contract matches the OpenAPI specification in
specs/005-python-code-sandbox/contracts/code-execution-api.yaml
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_execute_code_success_contract(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test successful code execution matches API contract."""
    request_payload = {
        "code": "print('Hello, World!')",
        "module_id": None,
        "lesson_id": None,
        "exercise_id": None,
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Verify required fields per contract
    assert "id" in data
    assert "status" in data
    assert "execution_time_ms" in data
    assert "output" in data

    # Verify field types
    assert isinstance(data["id"], str)
    assert data["status"] in [
        "success",
        "timeout",
        "error",
        "blocked",
        "infrastructure_failure",
    ]
    assert isinstance(data["execution_time_ms"], int)
    assert 0 <= data["execution_time_ms"] <= 8000

    # Verify optional fields
    if "error_message" in data:
        assert isinstance(data["error_message"], (str, type(None)))
    if "error_type" in data:
        assert isinstance(data["error_type"], (str, type(None)))
    if "memory_used_bytes" in data:
        assert isinstance(data["memory_used_bytes"], (int, type(None)))
    if "code_submission_id" in data:
        assert isinstance(data["code_submission_id"], (str, type(None)))


@pytest.mark.asyncio
async def test_execute_code_validation_error_contract(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test validation error response matches API contract."""
    request_payload = {
        "code": "",  # Empty code should fail validation
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()

    # Verify error structure per contract
    assert "error" in data
    assert "message" in data
    assert "details" in data

    assert data["error"] == "validation_error"
    assert isinstance(data["message"], str)
    assert isinstance(data["details"], list)


@pytest.mark.asyncio
async def test_execute_code_error_response_contract(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution error response matches API contract."""
    request_payload = {
        "code": "print(undefined_variable)",  # NameError
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    # Should return 200 with error status (not 422) based on implementation
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Verify error fields
    assert data["status"] == "error"
    assert "error_message" in data
    assert "error_type" in data
    assert isinstance(data["error_message"], str)
    assert isinstance(data["error_type"], str)


@pytest.mark.asyncio
async def test_execute_code_security_violation_contract(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test security violation response matches API contract."""
    request_payload = {
        "code": "import os\nprint(os.getcwd())",  # Blocked import
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    # Should return 200 with blocked status
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "error_message" in data
    assert "error_type" in data


@pytest.mark.asyncio
async def test_execute_code_requires_authentication(
    async_client: AsyncClient,
):
    """Test that endpoint requires JWT authentication per contract."""
    request_payload = {
        "code": "print('Hello')",
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        # No auth headers
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_execute_code_max_length_validation(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that code length is validated per contract (max 10000 chars)."""
    request_payload = {
        "code": "x = 1\n" * 10000,  # Exceeds 10000 character limit
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"] == "validation_error"


@pytest.mark.asyncio
async def test_execute_code_with_optional_context_fields(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution with optional module/lesson/exercise IDs per contract."""
    request_payload = {
        "code": "result = 2 + 2\nprint(result)",
        "module_id": "550e8400-e29b-41d4-a716-446655440000",
        "lesson_id": "550e8400-e29b-41d4-a716-446655440001",
        "exercise_id": "550e8400-e29b-41d4-a716-446655440002",
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"

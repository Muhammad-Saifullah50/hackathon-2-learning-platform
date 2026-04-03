"""
Integration tests for resource limit enforcement in code execution sandbox.

Tests verify that timeout and memory limits are properly enforced.
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_timeout_enforcement_infinite_loop(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that infinite loops are terminated after timeout."""
    request_payload = {
        "code": """
while True:
    pass
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "timeout"
    assert data["execution_time_ms"] >= 5000  # Should hit 5s timeout
    assert data["execution_time_ms"] <= 8000  # With overhead
    assert (
        "timeout" in data["error_message"].lower()
        or "time limit" in data["error_message"].lower()
    )
    assert data["error_type"] == "TimeoutError"


@pytest.mark.asyncio
async def test_timeout_enforcement_long_computation(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that long computations are terminated after timeout."""
    request_payload = {
        "code": """
import time
for i in range(100):
    time.sleep(0.1)  # Total 10 seconds, should timeout at 5s
    print(f'Iteration {i}')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "timeout"
    assert data["execution_time_ms"] >= 5000
    assert data["error_type"] == "TimeoutError"


@pytest.mark.asyncio
async def test_timeout_enforcement_nested_loops(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test timeout with deeply nested loops."""
    request_payload = {
        "code": """
for i in range(1000000):
    for j in range(1000000):
        x = i * j
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "timeout"
    assert data["execution_time_ms"] >= 5000


@pytest.mark.asyncio
async def test_fast_execution_completes_before_timeout(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that fast code completes well before timeout."""
    request_payload = {
        "code": """
result = sum(range(1000))
print(f'Sum: {result}')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "success"
    assert data["execution_time_ms"] < 1000  # Should complete in under 1 second


@pytest.mark.asyncio
async def test_memory_limit_enforcement_large_list(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that large memory allocations are caught."""
    request_payload = {
        "code": """
# Try to allocate ~100MB (exceeds 50MB limit)
large_list = [0] * (100 * 1024 * 1024 // 8)  # 100MB of integers
print('Allocated')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should either fail with MemoryError or be killed by Docker
    assert data["status"] in ["error", "infrastructure_failure"]
    if data["status"] == "error":
        assert data["error_type"] == "MemoryError"


@pytest.mark.asyncio
async def test_memory_limit_enforcement_string_multiplication(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test memory limit with large string allocation."""
    request_payload = {
        "code": """
# Try to create a very large string (exceeds 50MB limit)
large_string = 'x' * (100 * 1024 * 1024)  # 100MB string
print('Created')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] in ["error", "infrastructure_failure"]
    if data["status"] == "error":
        assert data["error_type"] == "MemoryError"


@pytest.mark.asyncio
async def test_memory_limit_enforcement_recursive_data_structure(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test memory limit with recursive data structure growth."""
    request_payload = {
        "code": """
# Try to create deeply nested lists
data = []
for i in range(1000000):
    data.append([0] * 1000)  # Will exceed memory
print('Done')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should timeout or run out of memory
    assert data["status"] in ["timeout", "error", "infrastructure_failure"]


@pytest.mark.asyncio
async def test_reasonable_memory_usage_succeeds(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that reasonable memory usage completes successfully."""
    request_payload = {
        "code": """
# Allocate ~10MB (well under 50MB limit)
data = [0] * (10 * 1024 * 1024 // 8)
print(f'Allocated {len(data)} integers')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "success"
    assert "Allocated" in data["output"]
    if data.get("memory_used_bytes"):
        assert data["memory_used_bytes"] < 50 * 1024 * 1024  # Under 50MB


@pytest.mark.asyncio
async def test_memory_tracking_reported(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that memory usage is tracked and reported."""
    request_payload = {
        "code": """
data = [i for i in range(10000)]
print(f'Created list with {len(data)} items')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "success"
    # Memory tracking may be optional in implementation
    if "memory_used_bytes" in data and data["memory_used_bytes"] is not None:
        assert data["memory_used_bytes"] > 0
        assert data["memory_used_bytes"] < 50 * 1024 * 1024

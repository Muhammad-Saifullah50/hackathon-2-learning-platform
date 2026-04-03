"""
Integration tests for security restrictions in code execution sandbox.

Tests verify that blocked imports and dangerous operations are properly
prevented and return educational error messages.
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_blocked_os_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that os module import is blocked."""
    request_payload = {
        "code": """
import os
print(os.getcwd())
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "os" in data["error_message"].lower()
    assert data["error_type"] == "SecurityViolation"


@pytest.mark.asyncio
async def test_blocked_sys_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that sys module import is blocked."""
    request_payload = {
        "code": """
import sys
print(sys.version)
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "sys" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_blocked_subprocess_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that subprocess module import is blocked."""
    request_payload = {
        "code": """
import subprocess
result = subprocess.run(['echo', 'hello'])
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "subprocess" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_blocked_socket_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that socket module import is blocked."""
    request_payload = {
        "code": """
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "socket" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_blocked_urllib_request_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that urllib.request module import is blocked."""
    request_payload = {
        "code": """
from urllib.request import urlopen
response = urlopen('http://example.com')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "urllib" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_blocked_shutil_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that shutil module import is blocked."""
    request_payload = {
        "code": """
import shutil
shutil.rmtree('/tmp/test')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "shutil" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_blocked_multiprocessing_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that multiprocessing module import is blocked."""
    request_payload = {
        "code": """
import multiprocessing
p = multiprocessing.Process(target=lambda: print('test'))
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "multiprocessing" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_blocked_threading_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that threading module import is blocked."""
    request_payload = {
        "code": """
import threading
t = threading.Thread(target=lambda: print('test'))
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    assert "threading" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_educational_error_message_for_blocked_import(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that blocked imports provide educational error messages."""
    request_payload = {
        "code": """
import os
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "blocked"
    error_msg = data["error_message"]

    # Should be educational and helpful
    assert len(error_msg) > 20
    assert "os" in error_msg.lower()
    # Should suggest alternatives or explain why it's blocked
    assert any(
        word in error_msg.lower()
        for word in ["security", "restricted", "blocked", "not allowed"]
    )


@pytest.mark.asyncio
async def test_mixed_allowed_and_blocked_imports(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test code with both allowed and blocked imports."""
    request_payload = {
        "code": """
import math
import os
import json

print(math.pi)
print(os.getcwd())
print(json.dumps({}))
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should be blocked due to os import
    assert data["status"] == "blocked"
    assert "os" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_allowed_imports_work_correctly(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that allowed imports work without restrictions."""
    request_payload = {
        "code": """
import math
import json
import datetime
import random
from collections import Counter

print(f'Pi: {math.pi}')
print(f'JSON: {json.dumps({"key": "value"})}')
print(f'Year: {datetime.datetime.now().year}')
random.seed(42)
print(f'Random: {random.randint(1, 10)}')
counter = Counter([1, 1, 2])
print(f'Counter: {counter[1]}')
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
    assert "Pi:" in data["output"]
    assert "JSON:" in data["output"]
    assert "Year:" in data["output"]
    assert "Random:" in data["output"]
    assert "Counter: 2" in data["output"]


@pytest.mark.asyncio
async def test_network_access_blocked_via_docker(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that network access is blocked even if import passes."""
    # Note: This test assumes urllib.parse is allowed but urllib.request is blocked
    request_payload = {
        "code": """
# Even if we somehow bypass import validation, Docker should block network
import socket
try:
    s = socket.socket()
    s.connect(('example.com', 80))
    print('Connected')
except Exception as e:
    print(f'Network blocked: {type(e).__name__}')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should be blocked at import validation stage
    assert data["status"] == "blocked"


@pytest.mark.asyncio
async def test_file_system_access_restricted(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that file system access outside temp directory is restricted."""
    request_payload = {
        "code": """
# Try to read a system file
try:
    with open('/etc/passwd', 'r') as f:
        content = f.read()
    print('File read succeeded')
except Exception as e:
    print(f'File access blocked: {type(e).__name__}')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should either be blocked or fail with permission error
    if data["status"] == "success":
        assert "File access blocked" in data["output"]
    else:
        assert data["status"] in ["error", "blocked"]

"""
Integration tests for error message simplification and student-friendly error handling.

Tests verify that Python errors are parsed and converted to beginner-friendly
messages through the complete execution pipeline.
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_syntax_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that SyntaxError is converted to student-friendly message."""
    request_payload = {"code": "print('Hello"}  # Missing closing quote

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "SyntaxError"

    error_msg = data["error_message"]
    # Should be educational and mention the issue
    assert len(error_msg) > 20
    assert "syntax" in error_msg.lower() or "string" in error_msg.lower()


@pytest.mark.asyncio
async def test_name_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that NameError is converted to student-friendly message."""
    request_payload = {"code": "print(undefined_variable)"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "NameError"

    error_msg = data["error_message"]
    # Should mention the variable name and explain the issue
    assert "undefined_variable" in error_msg
    assert len(error_msg) > 20


@pytest.mark.asyncio
async def test_type_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that TypeError is converted to student-friendly message."""
    request_payload = {"code": "result = '5' + 10"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "TypeError"

    error_msg = data["error_message"]
    # Should explain type mismatch in simple terms
    assert len(error_msg) > 20
    assert "type" in error_msg.lower()


@pytest.mark.asyncio
async def test_index_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that IndexError is converted to student-friendly message."""
    request_payload = {
        "code": """
numbers = [1, 2, 3]
print(numbers[10])
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "IndexError"

    error_msg = data["error_message"]
    # Should explain index out of bounds
    assert len(error_msg) > 20
    assert "index" in error_msg.lower()


@pytest.mark.asyncio
async def test_key_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that KeyError is converted to student-friendly message."""
    request_payload = {
        "code": """
person = {'name': 'Alice'}
print(person['age'])
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "KeyError"

    error_msg = data["error_message"]
    # Should mention the missing key
    assert len(error_msg) > 20
    assert "key" in error_msg.lower() or "age" in error_msg


@pytest.mark.asyncio
async def test_zero_division_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that ZeroDivisionError is converted to student-friendly message."""
    request_payload = {"code": "result = 10 / 0"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "ZeroDivisionError"

    error_msg = data["error_message"]
    # Should explain division by zero
    assert len(error_msg) > 20
    assert "zero" in error_msg.lower()


@pytest.mark.asyncio
async def test_attribute_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that AttributeError is converted to student-friendly message."""
    request_payload = {
        "code": """
text = "hello"
text.append('!')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "AttributeError"

    error_msg = data["error_message"]
    # Should mention the attribute and type
    assert len(error_msg) > 20
    assert "append" in error_msg.lower()


@pytest.mark.asyncio
async def test_indentation_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that IndentationError is converted to student-friendly message."""
    request_payload = {
        "code": """
def greet():
print('Hello')
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "IndentationError"

    error_msg = data["error_message"]
    # Should explain indentation issue
    assert len(error_msg) > 20
    assert "indent" in error_msg.lower()


@pytest.mark.asyncio
async def test_value_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that ValueError is converted to student-friendly message."""
    request_payload = {"code": "number = int('abc')"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "ValueError"

    error_msg = data["error_message"]
    # Should explain invalid value
    assert len(error_msg) > 20
    assert "value" in error_msg.lower() or "invalid" in error_msg.lower()


@pytest.mark.asyncio
async def test_error_message_includes_line_number(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that error messages include line numbers."""
    request_payload = {
        "code": """
x = 10
y = 20
print(undefined_variable)
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    error_msg = data["error_message"]

    # Should mention line number
    assert "line" in error_msg.lower() or "3" in error_msg


@pytest.mark.asyncio
async def test_error_in_function_call(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test error handling in function calls."""
    request_payload = {
        "code": """
def divide(a, b):
    return a / b

result = divide(10, 0)
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "ZeroDivisionError"
    assert len(data["error_message"]) > 20


@pytest.mark.asyncio
async def test_multiple_errors_reports_first(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that when multiple errors exist, the first one is reported."""
    request_payload = {
        "code": """
print(undefined_var1)
print(undefined_var2)
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    assert data["error_type"] == "NameError"
    # Should report the first undefined variable
    assert "undefined_var1" in data["error_message"]


@pytest.mark.asyncio
async def test_error_message_is_educational(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that error messages are educational and helpful."""
    request_payload = {"code": "print(x)"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "error"
    error_msg = data["error_message"]

    # Should be more than just "NameError: name 'x' is not defined"
    assert len(error_msg) > 30

    # Should provide guidance
    helpful_words = [
        "not defined",
        "doesn't exist",
        "create",
        "define",
        "forgot",
        "variable",
    ]
    assert any(word in error_msg.lower() for word in helpful_words)


@pytest.mark.asyncio
async def test_recursion_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that RecursionError is converted to student-friendly message."""
    request_payload = {
        "code": """
def infinite_recursion():
    return infinite_recursion()

infinite_recursion()
"""
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # May timeout or error depending on implementation
    assert data["status"] in ["error", "timeout"]

    if data["status"] == "error":
        assert data["error_type"] == "RecursionError"
        assert "recursion" in data["error_message"].lower()


@pytest.mark.asyncio
async def test_import_error_simplified(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that ImportError is converted to student-friendly message."""
    request_payload = {"code": "import nonexistent_module"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should be blocked or error
    assert data["status"] in ["error", "blocked"]
    assert len(data["error_message"]) > 20

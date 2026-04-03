"""
Integration tests for Code Execution API endpoint.

Tests verify end-to-end functionality of code execution including
sandbox interaction, database persistence, and error handling.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.code_submission import CodeSubmission


@pytest.mark.asyncio
async def test_execute_simple_code_success(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test successful execution of simple Python code."""
    request_payload = {
        "code": "print('Hello, World!')\nresult = 2 + 2\nprint(f'Result: {result}')"
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "success"
    assert "Hello, World!" in data["output"]
    assert "Result: 4" in data["output"]
    assert data["execution_time_ms"] > 0
    assert data["execution_time_ms"] < 5000
    assert data["code_submission_id"] is not None

    # Verify database persistence
    submission_id = data["code_submission_id"]
    result = await db_session.execute(
        select(CodeSubmission).where(CodeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    assert submission is not None
    assert submission.status == "success"
    assert submission.code_content == request_payload["code"]
    assert "Hello, World!" in submission.execution_output


@pytest.mark.asyncio
async def test_execute_code_with_math_operations(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution with mathematical operations."""
    request_payload = {
        "code": """
import math

radius = 5
area = math.pi * radius ** 2
print(f'Area: {area:.2f}')
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
    assert "Area: 78.54" in data["output"]


@pytest.mark.asyncio
async def test_execute_code_with_data_structures(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution with lists and dictionaries."""
    request_payload = {
        "code": """
numbers = [1, 2, 3, 4, 5]
squared = [n**2 for n in numbers]
print(f'Squared: {squared}')

person = {'name': 'Alice', 'age': 25}
print(f"Name: {person['name']}")
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
    assert "Squared: [1, 4, 9, 16, 25]" in data["output"]
    assert "Name: Alice" in data["output"]


@pytest.mark.asyncio
async def test_execute_code_with_functions(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution with function definitions."""
    request_payload = {
        "code": """
def greet(name):
    return f'Hello, {name}!'

def add(a, b):
    return a + b

print(greet('World'))
print(f'Sum: {add(10, 20)}')
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
    assert "Hello, World!" in data["output"]
    assert "Sum: 30" in data["output"]


@pytest.mark.asyncio
async def test_execute_code_with_loops(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution with for and while loops."""
    request_payload = {
        "code": """
# For loop
for i in range(3):
    print(f'Count: {i}')

# While loop
x = 0
while x < 2:
    print(f'X: {x}')
    x += 1
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
    assert "Count: 0" in data["output"]
    assert "Count: 1" in data["output"]
    assert "Count: 2" in data["output"]
    assert "X: 0" in data["output"]
    assert "X: 1" in data["output"]


@pytest.mark.asyncio
async def test_execute_code_with_conditionals(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution with if/elif/else statements."""
    request_payload = {
        "code": """
score = 85

if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
else:
    grade = 'C'

print(f'Grade: {grade}')
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
    assert "Grade: B" in data["output"]


@pytest.mark.asyncio
async def test_execute_code_with_context_fields(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test execution with module/lesson/exercise context."""
    module_id = "550e8400-e29b-41d4-a716-446655440000"
    lesson_id = "550e8400-e29b-41d4-a716-446655440001"
    exercise_id = "550e8400-e29b-41d4-a716-446655440002"

    request_payload = {
        "code": "print('Context test')",
        "module_id": module_id,
        "lesson_id": lesson_id,
        "exercise_id": exercise_id,
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "success"

    # Verify context is stored in database
    submission_id = data["code_submission_id"]
    result = await db_session.execute(
        select(CodeSubmission).where(CodeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    assert submission is not None
    assert str(submission.module_id) == module_id
    assert str(submission.lesson_id) == lesson_id
    assert str(submission.exercise_id) == exercise_id


@pytest.mark.asyncio
async def test_execute_code_with_allowed_imports(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test execution with various allowed standard library imports."""
    request_payload = {
        "code": """
import math
import json
import datetime
import random
from collections import Counter

# Math
print(f'Pi: {math.pi:.2f}')

# JSON
data = json.dumps({'key': 'value'})
print(f'JSON: {data}')

# Datetime
now = datetime.datetime.now()
print(f'Year: {now.year}')

# Random
random.seed(42)
print(f'Random: {random.randint(1, 10)}')

# Collections
counter = Counter([1, 1, 2, 3])
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
    assert "Pi: 3.14" in data["output"]
    assert "JSON:" in data["output"]
    assert "Year:" in data["output"]
    assert "Random:" in data["output"]
    assert "Counter: 2" in data["output"]

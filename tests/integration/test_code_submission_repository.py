"""
Integration tests for code submission repository persistence.

Tests verify that successful code executions are persisted to the database
and failed executions are not persisted.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.code_submission import CodeSubmission


@pytest.mark.asyncio
async def test_successful_execution_persisted(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that successful code execution is persisted to database."""
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
    assert data["code_submission_id"] is not None

    # Verify record exists in database
    submission_id = data["code_submission_id"]
    result = await db_session.execute(
        select(CodeSubmission).where(CodeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    assert submission is not None
    assert submission.status == "success"
    assert submission.code_content == request_payload["code"]
    assert "Hello, World!" in submission.execution_output
    assert "Result: 4" in submission.execution_output
    assert submission.execution_time_ms > 0
    assert submission.error_message is None
    assert submission.error_type is None


@pytest.mark.asyncio
async def test_successful_execution_with_context_persisted(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that successful execution with context fields is persisted."""
    module_id = "550e8400-e29b-41d4-a716-446655440000"
    lesson_id = "550e8400-e29b-41d4-a716-446655440001"
    exercise_id = "550e8400-e29b-41d4-a716-446655440002"

    request_payload = {
        "code": "x = 10\nprint(f'Value: {x}')",
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

    # Verify context fields are persisted
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
async def test_failed_execution_not_persisted(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that failed code execution is NOT persisted to database."""
    # Get initial count of submissions
    result = await db_session.execute(select(func.count(CodeSubmission.id)))
    initial_count = result.scalar()

    request_payload = {"code": "print(undefined_variable)"}  # NameError

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "error"
    assert data["code_submission_id"] is None  # Should not have submission ID

    # Verify no new record was created
    result = await db_session.execute(select(func.count(CodeSubmission.id)))
    final_count = result.scalar()

    assert final_count == initial_count  # Count should not increase


@pytest.mark.asyncio
async def test_timeout_execution_not_persisted(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that timed-out execution is NOT persisted to database."""
    # Get initial count
    result = await db_session.execute(select(func.count(CodeSubmission.id)))
    initial_count = result.scalar()

    request_payload = {"code": "while True:\n    pass"}  # Infinite loop

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "timeout"
    assert data["code_submission_id"] is None

    # Verify no new record was created
    result = await db_session.execute(select(func.count(CodeSubmission.id)))
    final_count = result.scalar()

    assert final_count == initial_count


@pytest.mark.asyncio
async def test_blocked_execution_not_persisted(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that blocked execution is NOT persisted to database."""
    # Get initial count
    result = await db_session.execute(select(func.count(CodeSubmission.id)))
    initial_count = result.scalar()

    request_payload = {"code": "import os\nprint(os.getcwd())"}  # Blocked import

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "blocked"
    assert data["code_submission_id"] is None

    # Verify no new record was created
    result = await db_session.execute(select(func.count(CodeSubmission.id)))
    final_count = result.scalar()

    assert final_count == initial_count


@pytest.mark.asyncio
async def test_multiple_successful_executions_all_persisted(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that multiple successful executions are all persisted."""
    codes = [
        "print('First')",
        "print('Second')",
        "print('Third')",
    ]

    submission_ids = []

    for code in codes:
        response = await async_client.post(
            "/api/v1/code-execution",
            json={"code": code},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        submission_ids.append(data["code_submission_id"])

    # Verify all records exist
    for submission_id in submission_ids:
        result = await db_session.execute(
            select(CodeSubmission).where(CodeSubmission.id == submission_id)
        )
        submission = result.scalar_one_or_none()
        assert submission is not None
        assert submission.status == "success"


@pytest.mark.asyncio
async def test_user_id_associated_with_submission(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_user,
):
    """Test that code submission is associated with the authenticated user."""
    request_payload = {"code": "print('User test')"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"

    # Verify user_id is set correctly
    submission_id = data["code_submission_id"]
    result = await db_session.execute(
        select(CodeSubmission).where(CodeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    assert submission is not None
    assert submission.user_id == test_user.id


@pytest.mark.asyncio
async def test_execution_metadata_persisted(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that execution metadata (time, memory) is persisted."""
    request_payload = {
        "code": "data = [i for i in range(1000)]\nprint(f'Created {len(data)} items')"
    }

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"

    # Verify metadata is persisted
    submission_id = data["code_submission_id"]
    result = await db_session.execute(
        select(CodeSubmission).where(CodeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    assert submission is not None
    assert submission.execution_time_ms > 0
    assert submission.execution_time_ms < 5000
    # Memory tracking may be optional
    if submission.memory_used_bytes is not None:
        assert submission.memory_used_bytes > 0


@pytest.mark.asyncio
async def test_timestamps_set_on_persistence(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that created_at and updated_at timestamps are set."""
    request_payload = {"code": "print('Timestamp test')"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"

    # Verify timestamps are set
    submission_id = data["code_submission_id"]
    result = await db_session.execute(
        select(CodeSubmission).where(CodeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    assert submission is not None
    assert submission.created_at is not None
    assert submission.updated_at is not None
    # Timestamps should be recent (within last minute)
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    assert (now - submission.created_at) < timedelta(minutes=1)
    assert (now - submission.updated_at) < timedelta(minutes=1)


@pytest.mark.asyncio
async def test_language_field_set_to_python(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test that language field is set to 'python'."""
    request_payload = {"code": "print('Language test')"}

    response = await async_client.post(
        "/api/v1/code-execution",
        json=request_payload,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"

    # Verify language field
    submission_id = data["code_submission_id"]
    result = await db_session.execute(
        select(CodeSubmission).where(CodeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    assert submission is not None
    assert submission.language == "python"

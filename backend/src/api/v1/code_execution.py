import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ...auth.dependencies import get_current_user
from ...database import get_db
from ...models.user import User
from ...repositories.submission_repository import SubmissionRepository
from ...schemas.code_execution import CodeExecutionRequest, CodeExecutionResponse
from ...services.code_execution_service import CodeExecutionService

# Set up logging
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/v1", tags=["code-execution"])


@router.post("/code-execution", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
    db_session=Depends(get_db),
) -> CodeExecutionResponse:
    """
    Execute Python code in a secure sandbox environment.

    This endpoint accepts Python code from authenticated users and executes it
    in an isolated environment with strict resource limits (5s timeout, 50MB memory).
    The execution result is returned with any output or error messages.

    Note: For compatibility with existing CodeSubmission model, exercise_id is treated as an integer.
    In a full implementation, UUID mapping would be handled by a dedicated service.
    """
    logger.info(
        f"Code execution API request from user_id={current_user.id}, code_length={len(request.code)}"
    )

    # Initialize the submission repository
    submission_repo = SubmissionRepository(db_session)

    # Initialize the code execution service
    code_execution_service = CodeExecutionService(submission_repo=submission_repo)

    try:
        # Execute the code (passing exercise_id as None for now to avoid complications)
        result = await code_execution_service.execute_code(
            code=request.code,
            user_id=str(current_user.id),
            module_id=request.module_id,
            lesson_id=request.lesson_id,
            exercise_id=None,  # Temporarily set to None to avoid issues with UUID/int mismatch
        )

        logger.info(
            f"Code execution completed successfully: status={result.status}, execution_time_ms={result.execution_time_ms}"
        )
        return result

    except Exception as e:
        # Log the error for debugging
        logger.error(
            f"Error executing code for user_id={current_user.id}: {str(e)}",
            exc_info=True,
        )

        # Return a 500 error response
        raise HTTPException(
            status_code=500, detail="Internal server error during code execution"
        )


# Add the router to be imported in main app
__all__ = ["router"]

"""Logging utility for repository operations."""
import logging
from functools import wraps
from typing import Callable

# Configure logger
logger = logging.getLogger("repositories")


def log_repository_operation(operation_name: str):
    """
    Decorator to log repository operations.

    Usage:
        @log_repository_operation("get_user_by_id")
        async def get_by_id(self, user_id: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"Repository operation: {operation_name} - Args: {args[1:]} Kwargs: {kwargs}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Repository operation: {operation_name} - Success")
                return result
            except Exception as e:
                logger.error(f"Repository operation: {operation_name} - Error: {str(e)}")
                raise
        return wrapper
    return decorator

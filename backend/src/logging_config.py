"""Logging configuration for the application."""
import logging
import sys
from typing import Any, Dict

from src.config import settings


def setup_logging() -> None:
    """Configure application-wide logging."""
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Set log level based on environment
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Set specific log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Set our application loggers to appropriate levels
    logging.getLogger("src.auth").setLevel(log_level)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - level: {logging.getLevelName(log_level)}, environment: {settings.ENVIRONMENT}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ExecutionResult:
    """Represents the result of code execution."""

    success: bool
    output: str
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    execution_time_ms: int = 0
    memory_used_bytes: Optional[int] = None
    status: str = "success"  # success, timeout, error, blocked, infrastructure_failure


class SandboxInterface(ABC):
    """Abstract interface for code execution sandbox implementations."""

    @abstractmethod
    async def execute_code(
        self, code: str, timeout_seconds: int = 5, memory_limit: str = "50MB"
    ) -> ExecutionResult:
        """Execute Python code in a sandboxed environment.

        Args:
            code: The Python code to execute
            timeout_seconds: Maximum execution time in seconds
            memory_limit: Maximum memory limit (e.g., "50MB")

        Returns:
            ExecutionResult containing output, errors, and metadata
        """
        pass

    @abstractmethod
    async def validate_imports(self, code: str) -> tuple[bool, Optional[str]]:
        """Validate that the code only imports allowed modules.

        Args:
            code: The Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

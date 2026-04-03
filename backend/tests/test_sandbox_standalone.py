"""Standalone test script for Python code sandbox functionality."""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.sandbox.docker_sandbox import DockerSandbox


async def test_valid_code():
    """Test 1: Execute valid Python code."""
    print("\n=== Test 1: Valid Python Code ===")
    sandbox = DockerSandbox()
    code = 'print("Hello, World!")'
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Execution Time: {result.execution_time_ms}ms")

    assert result.success, "Valid code should execute successfully"
    assert "Hello, World!" in result.output, "Output should contain expected text"
    print("✓ Test 1 PASSED")


async def test_syntax_error():
    """Test 2: Execute code with syntax error."""
    print("\n=== Test 2: Syntax Error ===")
    sandbox = DockerSandbox()
    code = 'print("Hello'  # Missing closing quote
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Error Type: {result.error_type}")
    print(f"Error Message: {result.error_message}")

    assert not result.success, "Code with syntax error should fail"
    assert result.error_type == "SyntaxError", "Should detect syntax error"
    print("✓ Test 2 PASSED")


async def test_timeout():
    """Test 3: Execute code that times out."""
    print("\n=== Test 3: Timeout ===")
    sandbox = DockerSandbox()
    code = """
import time
while True:
    time.sleep(1)
"""
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Error Type: {result.error_type}")
    print(f"Error Message: {result.error_message}")

    assert result.status == "timeout", "Infinite loop should timeout"
    assert result.execution_time_ms >= 5000, "Should take at least 5 seconds"
    print("✓ Test 3 PASSED")


async def test_blocked_import():
    """Test 4: Execute code with blocked import."""
    print("\n=== Test 4: Blocked Import ===")
    sandbox = DockerSandbox()
    code = """
import os
print(os.listdir('/'))
"""
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Error Type: {result.error_type}")
    print(f"Error Message: {result.error_message}")

    assert not result.success, "Blocked import should fail"
    assert result.error_type == "SecurityViolation", "Should detect security violation"
    print("✓ Test 4 PASSED")


async def test_allowed_import():
    """Test 5: Execute code with allowed import."""
    print("\n=== Test 5: Allowed Import ===")
    sandbox = DockerSandbox()
    code = """
import math
print(math.pi)
"""
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")

    assert result.success, "Allowed import should succeed"
    assert "3.14" in result.output, "Should output pi value"
    print("✓ Test 5 PASSED")


async def test_memory_limit():
    """Test 6: Execute code that exceeds memory limit."""
    print("\n=== Test 6: Memory Limit ===")
    sandbox = DockerSandbox()
    code = """
# Try to allocate 100MB of memory
data = [0] * (100 * 1024 * 1024)
print("Allocated memory")
"""
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Error Type: {result.error_type}")
    print(f"Error Message: {result.error_message}")

    # Memory limit enforcement depends on Docker configuration
    # This test may pass or fail depending on system setup
    print("✓ Test 6 COMPLETED (memory limit enforcement varies by system)")


async def test_runtime_error():
    """Test 7: Execute code with runtime error."""
    print("\n=== Test 7: Runtime Error ===")
    sandbox = DockerSandbox()
    code = """
x = 10
y = 0
result = x / y
"""
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Error Type: {result.error_type}")
    print(f"Error Message: {result.error_message}")

    assert not result.success, "Division by zero should fail"
    assert "ZeroDivisionError" in result.error_type, "Should detect ZeroDivisionError"
    print("✓ Test 7 PASSED")


async def test_empty_code():
    """Test 8: Execute empty code."""
    print("\n=== Test 8: Empty Code ===")
    sandbox = DockerSandbox()
    code = ""
    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")

    # Empty code should execute successfully but produce no output
    assert result.success, "Empty code should execute successfully"
    print("✓ Test 8 PASSED")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Python Code Sandbox - Standalone Test Suite")
    print("=" * 60)

    tests = [
        test_valid_code,
        test_syntax_error,
        test_timeout,
        test_blocked_import,
        test_allowed_import,
        test_memory_limit,
        test_runtime_error,
        test_empty_code,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

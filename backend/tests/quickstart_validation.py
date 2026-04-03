"""
Quickstart validation script for Python Code Sandbox.

This script validates the core functionality described in quickstart.md:
1. Simple code execution
2. Error handling
3. Blocked imports
4. Resource limits
"""

import asyncio
import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from services.sandbox.docker_sandbox import DockerSandbox
from services.sandbox.error_parser import ErrorParser
from services.sandbox.import_validator import ImportValidator


async def test_simple_execution():
    """Test 1: Simple code execution (from quickstart.md example 1)"""
    print("\n=== Test 1: Simple Code Execution ===")
    sandbox = DockerSandbox()
    code = "print('Hello, World!')\nresult = 2 + 2\nprint(f'Result: {result}')"

    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    assert result.success, f"Expected success, got {result.status}"
    assert (
        "Hello, World!" in result.output
    ), f"Expected 'Hello, World!' in output, got: {result.output}"
    assert (
        "Result: 4" in result.output
    ), f"Expected 'Result: 4' in output, got: {result.output}"
    assert (
        result.execution_time_ms < 5000
    ), f"Execution took too long: {result.execution_time_ms}ms"

    print(f"✓ Status: {result.status}")
    print(f"✓ Output: {result.output}")
    print(f"✓ Execution time: {result.execution_time_ms}ms")


async def test_error_handling():
    """Test 2: Error handling (from quickstart.md example 2)"""
    print("\n=== Test 2: Error Handling ===")
    sandbox = DockerSandbox()
    code = "print(undefined_variable)"

    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    assert not result.success, f"Expected failure, got success"
    assert result.status == "error", f"Expected status 'error', got {result.status}"
    assert (
        result.error_type == "NameError"
    ), f"Expected NameError, got {result.error_type}"
    assert result.error_message is not None, "Expected error message"

    print(f"✓ Status: {result.status}")
    print(f"✓ Error type: {result.error_type}")
    print(f"✓ Error message: {result.error_message[:100]}...")


async def test_blocked_imports():
    """Test 3: Blocked imports (from quickstart.md example 3)"""
    print("\n=== Test 3: Blocked Imports ===")
    sandbox = DockerSandbox()
    code = "import os\nprint(os.getcwd())"

    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    assert not result.success, f"Expected failure, got success"
    assert result.status == "blocked", f"Expected status 'blocked', got {result.status}"
    assert (
        result.error_type == "SecurityViolation"
    ), f"Expected SecurityViolation, got {result.error_type}"
    assert (
        "os" in result.error_message
    ), f"Expected 'os' in error message, got: {result.error_message}"

    print(f"✓ Status: {result.status}")
    print(f"✓ Error type: {result.error_type}")
    print(f"✓ Error message: {result.error_message}")


async def test_allowed_imports():
    """Test 4: Allowed imports (math, json, datetime)"""
    print("\n=== Test 4: Allowed Imports ===")
    sandbox = DockerSandbox()
    code = """
import math
import json
from datetime import datetime

result = math.sqrt(16)
data = json.dumps({"value": result})
print(f"Result: {result}")
print(f"JSON: {data}")
"""

    result = await sandbox.execute_code(code, timeout_seconds=5, memory_limit="50MB")

    assert result.success, f"Expected success, got {result.status}"
    assert (
        "Result: 4.0" in result.output
    ), f"Expected 'Result: 4.0' in output, got: {result.output}"

    print(f"✓ Status: {result.status}")
    print(f"✓ Output: {result.output}")


async def test_timeout():
    """Test 5: Timeout enforcement"""
    print("\n=== Test 5: Timeout Enforcement ===")
    sandbox = DockerSandbox()
    code = "import time\nwhile True:\n    pass"

    result = await sandbox.execute_code(code, timeout_seconds=2, memory_limit="50MB")

    assert not result.success, f"Expected failure, got success"
    assert result.status == "timeout", f"Expected status 'timeout', got {result.status}"

    print(f"✓ Status: {result.status}")
    print(f"✓ Timeout enforced correctly")


async def test_error_parser():
    """Test 6: Error parser functionality"""
    print("\n=== Test 6: Error Parser ===")
    parser = ErrorParser()

    # Test SyntaxError
    error_msg = parser.parse_error("SyntaxError: invalid syntax", "SyntaxError")
    assert (
        "Syntax Error" in error_msg
    ), f"Expected 'Syntax Error' in message, got: {error_msg}"

    # Test NameError
    error_msg = parser.parse_error("NameError: name 'x' is not defined", "NameError")
    assert (
        "Name Error" in error_msg
    ), f"Expected 'Name Error' in message, got: {error_msg}"

    print(f"✓ Error parser working correctly")


async def test_import_validator():
    """Test 7: Import validator functionality"""
    print("\n=== Test 7: Import Validator ===")
    validator = ImportValidator()

    # Test allowed import
    is_valid, error = validator.validate_imports("import math")
    assert is_valid, f"Expected math to be allowed, got error: {error}"

    # Test blocked import
    is_valid, error = validator.validate_imports("import os")
    assert not is_valid, f"Expected os to be blocked"
    assert "os" in error, f"Expected 'os' in error message, got: {error}"

    print(f"✓ Import validator working correctly")


async def main():
    """Run all validation tests"""
    print("=" * 60)
    print("Python Code Sandbox - Quickstart Validation")
    print("=" * 60)

    tests = [
        ("Simple Execution", test_simple_execution),
        ("Error Handling", test_error_handling),
        ("Blocked Imports", test_blocked_imports),
        ("Allowed Imports", test_allowed_imports),
        ("Timeout Enforcement", test_timeout),
        ("Error Parser", test_error_parser),
        ("Import Validator", test_import_validator),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {str(e)}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All quickstart validation tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

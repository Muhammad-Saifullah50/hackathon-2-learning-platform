import pytest

from backend.src.services.sandbox.import_validator import ImportValidator


class TestImportValidator:
    """Test cases for ImportValidator class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.validator = ImportValidator()

    def test_valid_imports(self):
        """Test that allowed imports are accepted."""
        valid_codes = [
            "import math",
            "import json",
            "import datetime",
            "import collections",
            "from math import sqrt",
            "from collections import defaultdict",
            "from datetime import datetime",
            "import os.path",  # This is allowed (but not os directly)
        ]

        for code in valid_codes:
            is_valid, error_msg = self.validator.validate_imports(code)
            assert is_valid, f"Expected {code} to be valid, but got error: {error_msg}"

    def test_invalid_imports(self):
        """Test that blocked imports are rejected."""
        invalid_codes = [
            "import os",
            "import subprocess",
            "import sys",
            "import socket",
            "from os import getcwd",
            "from subprocess import run",
            "import shutil",
            "import threading",
        ]

        for code in invalid_codes:
            is_valid, error_msg = self.validator.validate_imports(code)
            assert not is_valid, f"Expected {code} to be invalid, but it was accepted"
            assert error_msg is not None
            assert "blocked for security" in error_msg

    def test_mixed_imports(self):
        """Test code with both valid and invalid imports."""
        mixed_code = """
import math
import os
import json
"""
        is_valid, error_msg = self.validator.validate_imports(mixed_code)
        assert not is_valid
        assert error_msg is not None

    def test_get_disallowed_imports(self):
        """Test getting specific disallowed imports."""
        code = """
import os
import math
from subprocess import run
import json
"""
        disallowed = self.validator.get_disallowed_imports(code)
        assert "os" in disallowed
        assert "subprocess" in disallowed
        assert "math" not in disallowed
        assert "json" not in disallowed

    def test_no_imports(self):
        """Test code with no imports."""
        code = "x = 5\nprint(x)"
        is_valid, error_msg = self.validator.validate_imports(code)
        assert is_valid
        assert error_msg is None


if __name__ == "__main__":
    pytest.main([__file__])

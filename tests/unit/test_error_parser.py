import pytest

from backend.src.services.sandbox.error_parser import ErrorParser


class TestErrorParser:
    """Test cases for ErrorParser class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.parser = ErrorParser()

    def test_parse_syntax_error(self):
        """Test parsing of syntax errors."""
        error_msg = "SyntaxError: invalid syntax"
        result = self.parser.parse_error(error_msg, "SyntaxError")

        assert "Syntax Error" in result
        assert "missing colons" in result or "parentheses" in result

    def test_parse_name_error(self):
        """Test parsing of name errors."""
        error_msg = "NameError: name 'variable' is not defined"
        result = self.parser.parse_error(error_msg, "NameError")

        assert "Variable 'variable' is not defined" in result
        assert "Did you forget to create it" in result

    def test_parse_type_error(self):
        """Test parsing of type errors."""
        error_msg = "TypeError: unsupported operand type(s)"
        result = self.parser.parse_error(error_msg, "TypeError")

        assert "Type Error" in result
        assert "incompatible types" in result

    def test_enhanced_error_message(self):
        """Test enhanced error message with suggestions."""
        error_msg = "NameError: name 'x' is not defined"
        result = self.parser.enhance_error_message(
            error_message=error_msg, error_type="NameError", line_number=5
        )

        assert "around line 5" in result
        assert "💡 Suggestion" in result
        assert "defined the variable before using it" in result

    def test_extract_line_number(self):
        """Test extraction of line numbers from error messages."""
        error_msg = "Traceback (most recent call last):\n  File \"<stdin>\", line 3, in <module>\nNameError: name 'x' is not defined"
        line_num = self.parser.extract_line_number(error_msg)

        assert line_num == 3

    def test_classify_error_type(self):
        """Test classification of error types."""
        error_msg = "SyntaxError: invalid syntax"
        error_type = self.parser.classify_error_type(error_msg)

        assert error_type == "SyntaxError"


if __name__ == "__main__":
    pytest.main([__file__])

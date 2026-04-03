import ast
from typing import Optional, Set, Tuple


class ImportValidator:
    """Validates Python imports against a whitelist of allowed modules."""

    def __init__(self):
        # Define the whitelist of allowed standard library modules
        self.allowed_modules = {
            # Core Language
            "__future__",
            "keyword",
            "token",
            "tokenize",
            # Mathematics
            "math",
            "cmath",
            "decimal",
            "fractions",
            "random",
            "statistics",
            "numbers",
            # Collections
            "collections",
            "collections.abc",
            "heapq",
            "bisect",
            "array",
            # Text Processing
            "string",
            "re",
            "difflib",
            "stringprep",
            "textwrap",
            "unicodedata",
            # Data Formats
            "json",
            "marshal",
            "csv",
            "xml.etree.ElementTree",
            # Date/Time
            "datetime",
            "calendar",
            "time",
            # Algorithms
            "hashlib",
            "hmac",
            "copy",
            "pprint",
            "reprlib",
            # File Formats
            "configparser",
            "urllib.parse",
            # Generic OS Services
            "os.path",
            "tempfile",
            # Data Persistence
            "sqlite3",
            # Structural Patterns
            "enum",
            "dataclasses",
            "types",
            # Functional Programming
            "functools",
            "operator",
            "itertools",
            # Error Handling
            "warnings",
            "traceback",
            "logging",
            # Internationalization
            "locale",
            "gettext",
            # Binary Data
            "struct",
            "codecs",
            "encodings",
            # File Handling
            "io",
            "pathlib",
            "linecache",
        }

    def validate_imports(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate that the code only imports allowed modules.

        Args:
            code: The Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse the code as an AST
            tree = ast.parse(code)

            # Find all import statements
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Handle 'import module' statements
                    for alias in node.names:
                        module_name = alias.name
                        if not self._is_allowed_module(module_name):
                            return (
                                False,
                                f"Import blocked for security: '{module_name}' module is restricted. Use allowed modules like 'math', 'json', 'datetime' instead.",
                            )

                elif isinstance(node, ast.ImportFrom):
                    # Handle 'from module import ...' statements
                    module_name = node.module
                    if module_name and not self._is_allowed_module(module_name):
                        return (
                            False,
                            f"Import blocked for security: '{module_name}' module is restricted. Use allowed modules like 'math', 'json', 'datetime' instead.",
                        )

        except SyntaxError:
            # If there's a syntax error, let it be caught during execution
            pass

        return True, None

    def _is_allowed_module(self, module_name: str) -> bool:
        """Check if a module is in the allowed list."""
        # Handle both direct imports and submodules (e.g., 'collections.abc')
        parts = module_name.split(".")
        for i in range(len(parts), 0, -1):
            check_module = ".".join(parts[:i])
            if check_module in self.allowed_modules:
                return True
        return False

    def get_disallowed_imports(self, code: str) -> Set[str]:
        """Get a set of disallowed imports in the code.

        Args:
            code: The Python code to analyze

        Returns:
            Set of disallowed module names
        """
        disallowed = set()

        try:
            # Parse the code as an AST
            tree = ast.parse(code)

            # Find all import statements
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Handle 'import module' statements
                    for alias in node.names:
                        module_name = alias.name
                        if not self._is_allowed_module(module_name):
                            disallowed.add(module_name)

                elif isinstance(node, ast.ImportFrom):
                    # Handle 'from module import ...' statements
                    module_name = node.module
                    if module_name and not self._is_allowed_module(module_name):
                        disallowed.add(module_name)

        except SyntaxError:
            # If there's a syntax error, return empty set to let it be caught during execution
            pass

        return disallowed

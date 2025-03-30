"""
Error handling module for the Logo compiler.

This module defines a comprehensive set of exceptions used by the Logo compiler
with improved error reporting capabilities and type safety.
"""

from typing import List, Optional, TextIO, Dict, Any


class CompilerError(Exception):
    """Base class for all compiler exceptions."""

    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
        source_snippet: Optional[str] = None,
    ) -> None:
        """
        Initialize a new compiler exception with improved error context.

        Args:
            message: Descriptive error message.
            line: Line number where the error occurred. Defaults to 0.
            column: Column number where the error occurred. Defaults to 0.
            source_snippet: Snippet of source code where the error occurred.
        """
        self.message: str = message
        self.line: int = line
        self.column: int = column
        self.source_snippet: Optional[str] = source_snippet

        # Build the complete message with position information
        full_message: str = message
        if line > 0:
            position_info: str = f"line {line}"
            if column > 0:
                position_info += f", column {column}"
            full_message = f"{position_info}: {message}"

        super().__init__(full_message)

    def with_source_context(
        self, source_lines: List[str], context_lines: int = 2
    ) -> "CompilerError":
        """
        Add source code context to the error.

        Args:
            source_lines: List of all source code lines.
            context_lines: Number of lines to include before and after the error.

        Returns:
            Self with updated source context.
        """
        if self.line <= 0 or not source_lines:
            return self

        start: int = max(0, self.line - context_lines - 1)
        end: int = min(len(source_lines), self.line + context_lines)

        context: List[str] = []
        for i in range(start, end):
            line_number: int = i + 1
            prefix: str = "  "
            if line_number == self.line:
                prefix = "> "
            context.append(f"{prefix}{line_number:4d}: {source_lines[i]}")

            # Add pointer to the column if this is the error line
            if line_number == self.line and self.column > 0:
                context.append(" " * (len(prefix) + 6 + self.column - 1) + "^")

        self.source_snippet = "\n".join(context)
        return self

    def get_formatted_message(self) -> str:
        """
        Get a nicely formatted error message with source context if available.

        Returns:
            Formatted error message.
        """
        parts: List[str] = [str(self)]
        if self.source_snippet:
            parts.extend(["", "Source context:", self.source_snippet])
        return "\n".join(parts)


class LexerError(CompilerError):
    """Exception for errors during lexical analysis."""

    ERROR_CODE = "E001"

    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
        source_snippet: Optional[str] = None,
        error_code: Optional[str] = None,
    ) -> None:
        """
        Initialize a lexer error with optional error code.

        Args:
            message: Error message.
            line: Line where the error occurred. Defaults to 0.
            column: Column where the error occurred. Defaults to 0.
            source_snippet: Source code snippet. Defaults to None.
            error_code: Specific error code. Defaults to None.
        """
        self.error_code: str = error_code or self.ERROR_CODE
        full_message: str = f"[{self.error_code}] {message}"
        super().__init__(full_message, line, column, source_snippet)


class InvalidCharacterError(LexerError):
    """Exception for unexpected or invalid characters in the source code."""

    ERROR_CODE = "E101"


class StringLiteralError(LexerError):
    """Exception for errors in string literals (unclosed, too long, etc.)."""

    ERROR_CODE = "E102"


class NumberLiteralError(LexerError):
    """Exception for errors in numeric literals (invalid format, too long, etc.)."""

    ERROR_CODE = "E103"


class IdentifierError(LexerError):
    """Exception for errors in identifiers (invalid format, too long, etc.)."""

    ERROR_CODE = "E104"


class SyntaxError(CompilerError):
    """Exception for syntax errors during parsing."""

    ERROR_CODE = "E201"

    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
        source_snippet: Optional[str] = None,
        expected: Optional[str] = None,
        found: Optional[str] = None,
    ) -> None:
        """
        Initialize a syntax error with expected/found tokens.

        Args:
            message: Error message.
            line: Line where the error occurred. Defaults to 0.
            column: Column where the error occurred. Defaults to 0.
            source_snippet: Source code snippet. Defaults to None.
            expected: Expected token(s). Defaults to None.
            found: Found token. Defaults to None.
        """
        self.expected: Optional[str] = expected
        self.found: Optional[str] = found

        details: List[str] = []
        if expected:
            details.append(f"expected: {expected}")
        if found:
            details.append(f"found: {found}")

        full_message: str = message
        if details:
            full_message = f"{message} ({', '.join(details)})"

        super().__init__(
            f"[{self.ERROR_CODE}] {full_message}", line, column, source_snippet
        )


class SemanticError(CompilerError):
    """Exception for semantic errors during semantic analysis."""

    ERROR_CODE = "E301"


class NameError(SemanticError):
    """Exception for undefined or duplicate identifiers."""

    ERROR_CODE = "E302"


class TypeError(SemanticError):
    """Exception for type errors."""

    ERROR_CODE = "E303"


class CodeGenerationError(CompilerError):
    """Exception for errors during code generation."""

    ERROR_CODE = "E401"


class FileError(CompilerError):
    """Exception for file-related errors."""

    ERROR_CODE = "E501"


class IOError(FileError):
    """Exception for input/output errors."""

    ERROR_CODE = "E502"


class ErrorReporter:
    """
    Helper class to generate and format error messages.
    """

    @staticmethod
    def report_error(
        error: CompilerError,
        source_lines: Optional[List[str]] = None,
        output: Optional[TextIO] = None,
    ) -> str:
        """
        Report an error with optional source context.

        Args:
            error: The error to report.
            source_lines: List of source code lines. Defaults to None.
            output: Output file object. Defaults to None.

        Returns:
            Formatted error message.
        """
        if source_lines:
            error.with_source_context(source_lines)

        formatted: str = error.get_formatted_message()

        if output:
            print(formatted, file=output)

        return formatted

    @staticmethod
    def load_source_file(file_path: str) -> List[str]:
        """
        Load a source file and return its lines.

        Args:
            file_path: Path to the source file.

        Returns:
            List of source code lines.

        Raises:
            FileError: If the file cannot be opened or read.
        """
        try:
            with open(file_path, "r") as file:
                return file.read().splitlines()
        except Exception as e:
            raise FileError(f"Failed to load source file: {str(e)}")

    @staticmethod
    def format_json_error(error: CompilerError) -> Dict[str, Any]:
        """
        Format an error as a JSON-serializable dictionary.

        Args:
            error: The error to format.

        Returns:
            Dictionary representation of the error.
        """
        result: Dict[str, Any] = {
            "type": error.__class__.__name__,
            "message": error.message,
            "line": error.line,
            "column": error.column,
        }

        if hasattr(error, "error_code"):
            result["code"] = error.error_code

        if hasattr(error, "expected"):
            result["expected"] = error.expected

        if hasattr(error, "found"):
            result["found"] = error.found

        if error.source_snippet:
            result["source_context"] = error.source_snippet

        return result

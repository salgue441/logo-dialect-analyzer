"""
Error module for the Logo compiler.

This module defines the exceptions used by the Logo compiler
"""


class CompilerError(Exception):
    """
    Base class for all compiler exceptions
    """

    def __init__(self, message: str, line: int = 0, column: int = 0):
        """
        Initialize a new compiler exception.

        Args:
            message (str): Descriptive error message.
            line (int, optional): Line number where the error occurred. Defaults to 0.
            column (int, optional): Column number where the error occurred. Defaults to 0.
        """

        self.message = message
        self.line = line
        self.column = column

        full_message = message
        if line > 0:
            position_info = f"line {line}"

            if column > 0:
                position_info += f", column {column}"

            full_message = f"{position_info}: {message}"

        super().__init__(full_message)


class LexerError(CompilerError):
    """Exception for errors during lexical analysis"""

    pass


class SyntaxError(CompilerError):
    """Exception for syntax errors during parsing."""

    pass


class SemanticError(CompilerError):
    """Exception for semantic errors during semantic analysis."""

    pass


class CodeGenerationError(CompilerError):
    """Exception for errors during code generation."""

    pass


class FileError(CompilerError):
    """Exception for file-related errors."""

    pass

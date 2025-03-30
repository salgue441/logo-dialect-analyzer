"""
Module for lexical and syntactic analysis of the Logo dialect.

This module provides the necessary classes to perform
lexical and syntactic analysis of the Logo dialect.
"""

from .logo_tokens import Token, Tag
from .logo_errors import (
    LexerError,
    SyntaxError,
    SemanticError,
    CodeGenerationError,
    FileError,
    CompilerError,
)
from .logo_lexer import Lexer

__all__ = [
    "Token",
    "Tag",
    "Lexer",
    "LexerError",
    "SyntaxError",
    "SemanticError",
    "CodeGenerationError",
    "FileError",
    "CompilerError",
]

__version__ = "1.0.0"

"""
Logo Compiler Package.

A modular compiler for the Logo dialect with lexical analysis, syntax parsing,
and semantic analysis components.
"""

__version__ = "1.0.0"
__author__ = "Logo Compiler Team"

from logo.lexical.lexer import Lexer
from logo.utils.error import CompilerError, LexerError, FileError

__all__ = ["Lexer", "CompilerError", "LexerError", "FileError"]

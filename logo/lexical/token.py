"""
Token module for the Logo compiler.

This module defines token types and the Token class used by the lexical analyzer,
with memory optimization and type safety.
"""

from enum import IntEnum
from typing import Optional, Union, Dict, List, Set, TypeVar, Generic, Tuple, Any, cast


class Tag(IntEnum):
    """
    Enumeration of token types available in the Logo dialect.

    This enum defines all token types recognized by the lexer, including
    special tokens, operators, regular expressions, and reserved words.
    """

    # Special tokens
    EOF = 65535
    ERROR = 65534

    # Operators
    GEQ = 258  # >=
    LEQ = 259  # <=
    NEQ = 260  # <>
    ASSIGN = 261  # :=
    AND = 262
    OR = 263
    MOD = 264

    # Regular expressions
    ID = 358  # Identifier
    NUMBER = 359  # Numeric literal
    STRING = 360  # String literal
    TRUE = 361  # #t
    FALSE = 362  # #f

    # Reserved words
    VAR = 457
    FORWARD = 458
    BACKWARD = 459
    RIGHT = 460
    LEFT = 461
    SETX = 462
    SETY = 463
    SETXY = 464
    HOME = 465
    CLEAR = 466
    CIRCLE = 467
    ARC = 468
    PENUP = 469
    PENDOWN = 470
    COLOR = 471
    PENWIDTH = 472
    PRINT = 473
    WHILE = 474
    IF = 475
    IFELSE = 476


# Type definition for token values
TokenValue = Optional[Union[str, int, float]]


class Token:
    """
    Represents a token recognized by the lexer.

    Attributes:
        tag: The token type.
        value: The value associated with the token, if any.
    """

    __slots__ = ("tag", "value")  # Memory optimization

    def __init__(self, tag: Union[Tag, int], value: TokenValue = None) -> None:
        """
        Initialize a new token.

        Args:
            tag: The token type.
            value: The value associated with the token. Defaults to None.
        """
        self.tag: Union[Tag, int] = tag
        self.value: TokenValue = value

    def __str__(self) -> str:
        """
        Return a string representation of the token.

        Returns:
            The token representation.
        """
        if self.tag == Tag.GEQ:
            return "'>='"
        elif self.tag == Tag.LEQ:
            return "'<='"
        elif self.tag == Tag.NEQ:
            return "'<>'"
        elif self.tag == Tag.ASSIGN:
            return "':='"
        elif self.tag == Tag.TRUE:
            return "'#T'"
        elif self.tag == Tag.FALSE:
            return "'#F'"
        elif self.tag == Tag.NUMBER:
            return f"NUMBER = {self.value}"
        elif self.tag == Tag.ID:
            return f"ID = '{self.value}'"
        elif self.tag == Tag.AND:
            return "'AND'"
        elif self.tag == Tag.OR:
            return "'OR'"
        elif self.tag == Tag.MOD:
            return "'MOD'"
        elif self.tag == Tag.STRING:
            return f"STRING = {self.value}"
        elif isinstance(self.tag, Tag) and Tag.VAR <= self.tag <= Tag.IFELSE:
            return f"'{self.value}'"
        else:
            # Handle ASCII character tokens
            try:
                return f"'{chr(self.tag)}'"
            except (ValueError, TypeError, OverflowError):
                return f"UNKNOWN({self.tag})"

    def __repr__(self) -> str:
        """
        Return a detailed representation of the token for debugging.

        Returns:
            The detailed token representation.
        """
        tag_repr = (
            self.tag.name if isinstance(self.tag, Tag) else f"ASCII_{chr(self.tag)}"
        )
        return f"Token(tag={tag_repr}, value={repr(self.value)})"

    def __eq__(self, other: object) -> bool:
        """
        Compare this token to another for equality.

        Args:
            other: The other token to compare with.

        Returns:
            True if the tokens are equal, False otherwise.
        """
        if not isinstance(other, Token):
            return False
        return self.tag == other.tag and self.value == other.value


class ReservedWords:
    """
    Manages the dictionary of reserved words and previously found tokens.
    Optimized for faster lookups and reduced memory usage.
    """

    def __init__(self) -> None:
        """
        Initialize the reserved words dictionary with optimized data structures.
        """
        # Main dictionary mapping word to token
        self.words: Dict[str, Token] = {}

        # Cache of known identifiers for faster lookups
        self._identifier_cache: Set[str] = set()

        # Initialize with all reserved words
        self._init_reserved_words()

    def _init_reserved_words(self) -> None:
        """
        Initialize the dictionary with all reserved words of the Logo language.
        Uses optimized batch initialization for better performance.
        """
        # Reserved words
        self.words["VAR"] = Token(Tag.VAR, "VAR")

        # Movement commands - using batch initialization
        movement_commands = [
            (["FORWARD", "FD"], Tag.FORWARD, "FORWARD"),
            (["BACKWARD", "BK"], Tag.BACKWARD, "BACKWARD"),
            (["RIGHT", "RT"], Tag.RIGHT, "RIGHT"),
            (["LEFT", "LT"], Tag.LEFT, "LEFT"),
        ]

        for lexemes, tag, value in movement_commands:
            for lexeme in lexemes:
                self.words[lexeme] = Token(tag, value)

        # Individual commands
        single_commands = [
            ("SETX", Tag.SETX),
            ("SETY", Tag.SETY),
            ("SETXY", Tag.SETXY),
            ("HOME", Tag.HOME),
            ("CIRCLE", Tag.CIRCLE),
            ("ARC", Tag.ARC),
            ("COLOR", Tag.COLOR),
            ("PENWIDTH", Tag.PENWIDTH),
            ("PRINT", Tag.PRINT),
            ("WHILE", Tag.WHILE),
            ("IF", Tag.IF),
            ("IFELSE", Tag.IFELSE),
        ]

        for lexeme, tag in single_commands:
            self.words[lexeme] = Token(tag, lexeme)

        # Drawing commands with aliases
        self._add_reserved_word(["CLEAR", "CLS"], Tag.CLEAR, "CLEAR")
        self._add_reserved_word(["PENUP", "PU"], Tag.PENUP, "PENUP")
        self._add_reserved_word(["PENDOWN", "PD"], Tag.PENDOWN, "PENDOWN")

        # Operators
        operators = [("AND", Tag.AND), ("OR", Tag.OR), ("MOD", Tag.MOD)]

        for lexeme, tag in operators:
            self.words[lexeme] = Token(tag, lexeme)

    def _add_reserved_word(self, lexemes: List[str], tag: Tag, value: str) -> None:
        """
        Add a reserved word with multiple lexemes to the dictionary.

        Args:
            lexemes: List of lexemes for the same reserved word.
            tag: The tag associated with the reserved word.
            value: The value associated with the reserved word.
        """
        for lexeme in lexemes:
            self.words[lexeme] = Token(tag, value)

    def get(self, lexeme: str) -> Optional[Token]:
        """
        Get a token from the words dictionary with case-insensitive lookup.

        Args:
            lexeme: The lexeme to look for.

        Returns:
            The token associated with the lexeme, or None if it doesn't exist.
        """
        return self.words.get(lexeme.upper())

    def add(self, lexeme: str, token: Token) -> None:
        """
        Add a token to the words dictionary.

        Args:
            lexeme: The lexeme to add.
            token: The token associated with the lexeme.
        """
        upper_lexeme = lexeme.upper()
        self.words[upper_lexeme] = token
        self._identifier_cache.add(upper_lexeme)

    def contains(self, lexeme: str) -> bool:
        """
        Check if a lexeme exists in the words dictionary.

        Args:
            lexeme: The lexeme to check.

        Returns:
            True if the lexeme exists, False otherwise.
        """
        return lexeme.upper() in self.words

    def is_identifier(self, lexeme: str) -> bool:
        """
        Check if a lexeme is a known identifier (not a reserved word).

        Args:
            lexeme: The lexeme to check.

        Returns:
            True if the lexeme is a known identifier, False otherwise.
        """
        upper_lexeme = lexeme.upper()
        return upper_lexeme in self._identifier_cache


# Singleton instance for global use
DEFAULT_RESERVED_WORDS = ReservedWords()

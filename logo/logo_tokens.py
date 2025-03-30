"""
Token module for the Logo compiler

This module defines the token types and Token class used by the lexical analysis
"""

from enum import IntEnum
from typing import Optional, Union, Dict


class Tag(IntEnum):
    """
    Enumeration of token types available in the Logo dialect.
    """

    # Special tokens
    EOF = 65535
    ERROR = 65534

    # Operators
    GEQ = 258
    LEQ = 259
    NEQ = 260
    ASSIGN = 261
    AND = 262
    OR = 263
    MOD = 264

    # Regular expressions
    ID = 358
    NUMBER = 359
    STRING = 360
    TRUE = 361
    FALSE = 362

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


class Token:
    """
    Represents a token recognized by the lexer

    Attributes:
      tag (Tag): The token type.
      value (Optional[Union[str, int, float]]): The value associated with the token, if any.
    """

    def __init__(self, tag: Tag, value: Optional[Union[str, int, float]] = None):
        """
        Initializes a new token

        Args:
          tag (Tag): The token type.
          value (Optional[Union[str, int, float]], optional): The value associated with the token.Defaults to None.
        """

        self.tag = tag
        self.value = value

    def __str__(self) -> str:
        """
        Return a string representation of the token.

        Returns:
          str: The token representation
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

        elif Tag.VAR <= self.tag <= Tag.IFELSE:
            return f"'{self.value}'"

        else:
            return f"'{chr(self.tag)}'"

    def __repr__(self) -> str:
        """
        Return a detailed representation of the token for debugging

        Returns:
          str: The detailed token representation
        """

        return f"Token(tag={self.tag.name}, value={repr(self.value)})"


class ReservedWords:
    """
    Manages the dictionary of reserved words and previously found tokens
    """

    def __init__(self):
        """
        Initialize the reserved words dictionary
        """

        self.words: Dict[str, Token] = {}
        self._init_reserved_words()

    def _init_reserved_words(self) -> None:
        """
        Initialize the directory with all reserved words of the Logo Language.
        """

        # Reserved words
        self.words["VAR"] = Token(Tag.VAR, "VAR")

        # Movement commands
        self._add_reserved_word(["FORWARD", "FD"], Tag.FORWARD, "FORWARD")
        self._add_reserved_word(["BACKWARD", "BK"], Tag.BACKWARD, "BACKWARD")
        self._add_reserved_word(["RIGHT", "RT"], Tag.RIGHT, "RIGHT")
        self._add_reserved_word(["LEFT", "LT"], Tag.LEFT, "LEFT")
        self.words["SETX"] = Token(Tag.SETX, "SETX")
        self.words["SETY"] = Token(Tag.SETY, "SETY")
        self.words["SETXY"] = Token(Tag.SETXY, "SETXY")
        self.words["HOME"] = Token(Tag.HOME, "HOME")

        # Drawing commands
        self._add_reserved_word(["CLEAR", "CLS"], Tag.CLEAR, "CLEAR")
        self.words["CIRCLE"] = Token(Tag.CIRCLE, "CIRCLE")
        self.words["ARC"] = Token(Tag.ARC, "ARC")
        self._add_reserved_word(["PENUP", "PU"], Tag.PENUP, "PENUP")
        self._add_reserved_word(["PENDOWN", "PD"], Tag.PENDOWN, "PENDOWN")
        self.words["COLOR"] = Token(Tag.COLOR, "COLOR")
        self.words["PENWIDTH"] = Token(Tag.PENWIDTH, "PENWIDTH")

        # Text commands
        self.words["PRINT"] = Token(Tag.PRINT, "PRINT")

        # Control structures
        self.words["WHILE"] = Token(Tag.WHILE, "WHILE")
        self.words["IF"] = Token(Tag.IF, "IF")
        self.words["IFELSE"] = Token(Tag.IFELSE, "IFELSE")

        # Operators
        self.words["AND"] = Token(Tag.AND, "AND")
        self.words["OR"] = Token(Tag.OR, "OR")
        self.words["MOD"] = Token(Tag.MOD, "MOD")

    def _add_reserved_word(self, lexemes: list, tag: Tag, value: str) -> None:
        """
        Add a reserved word with multiple lexemes to the dictionary

        Args:
          lexemes (list): List of lexemes for the same reserved word.
          tag (Tag): The tag associated with the reserved word.
          value (str): The value associated with the reserved word.
        """

        for lexeme in lexemes:
            self.words[lexeme] = Token(tag, value)

    def get(self, lexeme: str) -> Optional[Token]:
        """
        Get a token from the words dictionary.

        Args:
          lexeme (str): The lexeme to look for.

        Returns:
          Optional[Token]: The token associated with the lexeme, or None if it doesn't exist.
        """

        return self.words.get(lexeme.upper())

    def add(self, lexeme: str, token: Token) -> None:
        """
        Add a token to the words dictionary

        Args:
          lexeme (str): The lexeme to add.
          token (Token): The token associated with the lexeme.
        """

        self.words[lexeme.upper()] = token

    def contains(self, lexeme: str) -> bool:
        """
        Check if a lexeme exists in the words dictionary

        Args:
          lexeme (str): The lexeme to check

        Returns:
          bool: True if the lexeme exists, false otherwise
        """

        return lexeme.upper() in self.words

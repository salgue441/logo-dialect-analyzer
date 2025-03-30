"""
Lexical analyzer module for the Logo compiler

This module provides the implementation of the lexical analyzer (Lexer)
for the Logo dialect
"""

import os
from typing import Optional, TextIO, Union, Tuple

from .logo_errors import LexerError, FileError
from .logo_tokens import Token, Tag, ReservedWords


class BufferManager:
    """
    Buffer manager for efficient file reading.

    This class implements a double buffer system for efficient source code file reading.
    """

    def __init__(self, file_path: str, buffer_size: int = 1024):
        """
        Initialize the buffer manager.

        Args:
          file_path (str): Path to the file to read.
          buffer_size (int, optional): Size of each buffer. Defaults to 1024.

        Raises:
          FileError: If there is a problem with the file.
        """

        if not os.path.exists(file_path):
            raise FileError(f"File {file_path} does not exist")

        self.file_path = file_path
        self.buffer_size = buffer_size
        self.position = 0
        self.current_buffer = ""
        self.next_buffer = ""

        try:
            self._refill_buffer()

        except Exception as e:
            raise FileError(f"Error reading file {file_path}: {str(e)}")

    def _refill_buffer(self) -> None:
        """
        Refill the next buffer.

        Raises:
          FileError: If there is a problem reading the file.
        """

        try:
            with open(self.file_path, "r") as file:
                file.seek(self.position)

                self.next_buffer = file.read(self.buffer_size)
                self.position += len(self.next_buffer)

        except Exception as e:
            raise FileError(f"Error reading file: {str(e)}")

    def get_next_char(self) -> Optional[str]:
        """
        Get the next character from the buffer

        Returns:
          Optional[str]: The next character, or None if the end of the file (EOF) has been reached.

        Raises:
          FileError: If there is a problem reading the file.
        """

        if not self.current_buffer:
            self.current_buffer = self.next_buffer
            self._refill_buffer()

            # If both buffers are empty, EOF has been reached
            if not self.current_buffer:
                return None

        char = self.current_buffer[0]
        self.current_buffer = self.current_buffer[1:]

        return char

    def push_back(self, char: Optional[str]) -> None:
        """
        Push a character back to the buffer

        Args:
          char (Optional[str]): The character to push back
        """

        if char is not None:
            self.current_buffer = char + self.current_buffer


class PositionTracker:
    """
    Tracks the current position in the source code
    """

    def __init__(self):
        """
        Initialize the position tracker
        """

        self.line = 1
        self.column = 0

    def update(self, char: str) -> None:
        """
        Update the position based on the read character

        Args:
          char (str): The read character
        """

        if char == "\n":
            self.line += 1
            self.column = 0

        else:
            self.column += 1

    def revert(self, char: str) -> None:
        """
        Revert the position based on the push back character

        Args:
          char (str): The pushed back character
        """

        if char == "\n":
            self.line -= 1

        else:
            self.column = max(0, self.column - 1)

    def get_position(self) -> Tuple[int, int]:
        """
        Get the current position

        Returns:
          Tuple[int, int]: A tuple containing (line, column).
        """

        return (self.line, self.column)


class Lexer:
    """
    Lexical analysis for the Logo dialect

    This class implements a lexical analyzer that recognizes tokens from the Logo dialect.
    """

    def __init__(self, file_path: str, buffer_size: int = 1024):
        """
        Initializes the lexical analyzer

        Args:
          file_path (str): Path to the file to analyze
          buffer_size (int, optional): Size of the read buffer. Default to 1024

        Raises:
          FileError: If there is a problem with the file.
        """

        self.buffer = BufferManager(file_path, buffer_size)
        self.position = PositionTracker()
        self.reserved_words = ReservedWords()

    @property
    def line(self) -> int:
        """
        Get the current line number.

        Returns:
          int: The current line number
        """

        return self.position.line

    @property
    def column(self) -> int:
        """
        Get the current column number.

        Returns:
          int: The current column number
        """

        return self.position.column

    def get_next_char(self) -> Optional[str]:
        """
        Get the next character from the input.

        Returns:
          Optional[str]: The next character, or None if end of file.

        Raises:
          LexerError: If there is a problem reading the file
        """

        try:
            char = self.buffer.get_next_char()
            if char is not None:
                self.position.update(char)

            return char

        except Exception as e:
            raise LexerError(str(e), self.line, self.column)

    def push_back(self, char: Optional[str]) -> None:
        """
        Push a character back to the input

        Args:
          char (Optional[str]): The character to push back
        """

        if char is not None:
            self.position.revert(char)
            self.buffer.push_back(char)

    def scan(self) -> Token:
        """
        Scan the next token from the source code

        Returns:
          Token: The next token found.

        Raises:
          LexerError: If there is an error during lexical analysis
        """

        try:
            return self._scan_impl()

        except Exception as e:
            if not isinstance(e, LexerError):
                line, column = self.position.get_position()

                raise LexerError(
                    f"Error during lexical analysis: {str(e)}", line, column
                )

            raise

    def _scan_impl(self) -> Token:
        """
        Implementation of the scan method

        Returns:
          Token: The next token found

        Raises:
          LexerError: If there is an error during lexical analysis
        """

        while True:
            char = self.get_next_char()
            if char is None:
                return Token(Tag.EOF)

            if char.isspace():
                continue

            # Handle comments
            if char == "%":
                self._skip_comment()
                continue

            # Comparison operators
            if char == "<":
                return self._handle_less_than()

            if char == ">":
                return self._handle_greater_than()

            # Boolean values
            if char == "#":
                return self._handle_hash()

            # Assignment operator
            if char == ":":
                return self._handle_colon()

            # String literals
            if char == '"':
                return self._handle_string()

            # Numbers
            if char.isdigit():
                return self._handle_number(char)

            # Identifiers and reserved words
            if char.isalpha():
                return self._handle_identifier(char)

            # Any other
            return Token(ord(char))

    def _skip_comment(self) -> None:
        """
        Skip all characters until the end of line (comment).
        """

        while True:
            char = self.get_next_char()
            if char is None or char == "\n":
                break

    def _handle_less_than(self) -> Token:
        """
        Handles operators starting with '<'

        Returns:
          Token: The corresponding token
        """

        char = self.get_next_char()
        if char in ["=", ">"]:
            if char == "=":
                return Token(Tag.LEQ, "<=")

            else:
                return Token(Tag.NEQ, "<>")

        else:
            self.push_back(char)
            return Token(ord("<"))

    def _handle_greater_than(self) -> Token:
        """
        Handle operators starting with '>'

        Returns:
          Token: The corresponding token.
        """

        char = self.get_next_char()
        if char == "=":
            return Token(Tag.GEQ, ">=")

        else:
            self.push_back(char)
            return Token(ord(">"))

    def _handle_hash(self) -> Token:
        """
        Handles boolean values starting with '#'

        Returns:
          Token: The corresponding token
        """

        char = self.get_next_char()
        if char is not None:
            char_upper = char.upper()

            if char_upper in ["T", "F"]:
                if char_upper == "T":
                    return Token(Tag.TRUE, "#T")

                else:
                    return Token(Tag.FALSE, "#F")

            else:
                self.push_back(char)

        else:
            self.push_back(char)

        return Token(ord("#"))

    def _handle_colon(self) -> Token:
        """
        Handle operators starting with ':'.

        Returns:
            Token: The corresponding token.
        """

        char = self.get_next_char()
        if char == "=":
            return Token(Tag.ASSIGN, ":=")

        else:
            self.push_back(char)
            return Token(ord(":"))

    def _handle_string(self) -> Token:
        """
        Handle string literals

        Returns:
          Token: The corresponding token

        Raises:
          LexerError: If the string is not closed
        """

        text = '"'
        line_start = self.line

        while True:
            char = self.get_next_char()
            if char is None:
                raise LexerError(
                    f"Unclosed string literal, started at line {line_start}",
                    line_start,
                    0,
                )

            text += char
            if char == '"':
                break

        return Token(Tag.STRING, text)

    def _handle_number(self, first_digit: str) -> Token:
        """
        Handle numbers (integers and decimals).

        Args:
          first_digit (str): The first digit of the number

        Returns:
          Token: The corresponding token
        """

        value = 0.0
        is_integer = True
        char = first_digit

        while char is not None and char.isdigit():
            value = (value * 10) + int(char)
            char = self.get_next_char()

        # Decimals
        if char == ".":
            is_integer = False
            decimal_factor = 0.1
            char = self.get_next_char()

            # If there's a dot but no digit follows
            if char is None or not char.isdigit():
                self.push_back(char)
                self.push_back(".")

                return Token(Tag.NUMBER, int(value) if is_integer else value)

            # Process decimals
            while char is not None and char.isdigit():
                value += int(char) * decimal_factor
                decimal_factor *= 0.1

                char = self.get_next_char()

        self.push_back(char)
        return Token(Tag.NUMBER, int(value) if is_integer else value)

    def _handle_identifier(self, first_char: str) -> Token:
        """
        Handle identifiers and reserved words.

        Args:
          first_char (str): The first character of the identifier

        Returns:
          Token: The corresponding token
        """

        lexeme = ""
        char = first_char

        while char is not None and char.isalnum():
            lexeme += char.upper()
            char = self.get_next_char()

        self.push_back(char)

        token = self.reserved_words.get(lexeme)
        if token:
            return token

        token = Token(Tag.ID, lexeme)
        self.reserved_words.add(lexeme, token)

        return token

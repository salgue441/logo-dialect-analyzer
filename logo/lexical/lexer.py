"""
Lexical analyzer module for the Logo compiler

This module provides the implementation of the lexical analyzer (Lexer)
for the Logo dialect
"""

import os
import time
from typing import Optional, TextIO, Union, Tuple, Dict, List, Any, Set, cast
import io

from logo.utils.error import (
    LexerError,
    FileError,
    StringLiteralError,
    NumberLiteralError,
    IdentifierError,
    InvalidCharacterError,
)

from logo.lexical.token import (
    Token,
    Tag,
    ReservedWords,
    DEFAULT_RESERVED_WORDS,
)


class BufferManager:
    """
    Buffered Reading for file reading.

    Implements a double buffer system with memory-efficient operations
    and improved file handling for better performance
    """

    __slots__ = (
        "file_path",
        "buffer_size",
        "position",
        "current_buffer",
        "next_buffer",
        "_file",
        "_eof_reached",
    )

    def __init__(self, file_path: str, buffer_size: int = 4096) -> None:
        """
        Initialize the buffer manager with performance-optimized settings.

        Args:
            file_path: Path to the file to read.
            buffer_size: Size of each buffer. Defaults to 4096 for optimal I/O

        Raises:
            FileError: If there is a problem with the file
        """

        if not os.path.exists(file_path):
            raise FileError(f"File {file_path} does not exist")

        self.file_path: str = file_path
        self.buffer_size: int = buffer_size
        self.position: int = 0
        self.current_buffer: str = ""
        self.next_buffer: str = ""
        self._file: Optional[TextIO] = None
        self._eof_reached: bool = False

        try:
            self._file = open(file_path, "r", encoding="utf-8")
            self._refill_buffers()

        except Exception as e:
            if self._file:
                self._file.close()

            raise FileError(f"Error reading file {file_path}: {str(e)}")

    def __del__(self) -> None:
        """
        Ensure the file is closed when the object is garbage collected.
        """

        self.close()

    def _refill_buffers(self) -> None:
        """
        Refill buffers from the file with minimal memory allocation

        Raises:
          FileError: If there is a problem reading the file.
        """

        if self.next_buffer:
            self.current_buffer = self.next_buffer
            self.next_buffer = ""

        if not self._eof_reached and self._file:
            try:
                self.next_buffer = self._file.read(self.buffer_size)

                if not self.next_buffer:
                    self._eof_reached = True

            except Exception as e:
                raise FileError(f"Error reading file: {str(e)}")

    def get_next_char(self) -> Optional[str]:
        """
        Get the next character from the buffer with optimized checks.

        Returns:
          The next character, or None if EOF has been reached
        """

        if not self.current_buffer:
            self._refill_buffers()

            if not self.current_buffer:
                return None

        char: str = self.current_buffer[0]
        self.current_buffer = self.current_buffer[1:]

        return char

    def push_back(self, char: Optional[str]) -> None:
        """
        Push a character back to the buffer.

        Args:
          char (Optional[str]): The character to push back
        """

        if char is not None:
            self.current_buffer = char + self.current_buffer

    def close(self) -> None:
        """
        Close the file if it's open
        """

        if self._file:
            self._file.close()
            self._file = None


class PositionTracker:
    """
    Tracker for source code position with efficient line/column tracking
    """

    __slots__ = ("line", "column", "last_newline_column", "max_column")

    def __init__(self) -> None:
        """
        Initialize the position tracker with optimized data structures
        """

        self.line: int = 1
        self.column: int = 0
        self.last_newline_column: List[int] = []
        self.max_column: int = 0

    def update(self, char: str) -> None:
        """
        Update the position based on the read character.

        Args:
          char (str): The read character
        """

        if char == "\n":
            self.last_newline_column.append(self.column)

            self.line += 1
            self.column = 0

        else:
            self.column += 1

            if self.column > self.max_column:
                self.max_column = self.column

    def revert(self, char: str) -> None:
        """
        Revert the position based on the pushed back character.

        Args:
          char (str): The pushed back character
        """

        if char == "\n":
            self.line -= 1

            if self.last_newline_column:
                self.column = self.last_newline_column.pop()

            else:
                self.column = 0

        else:
            self.column = max(0, self.column - 1)

    def get_position(self) -> Tuple[int, int]:
        """
        Get the current position

        Returns:
          Tuple[int, int]: A tuple containing (line, column)
        """

        return (self.line, self.column)

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about tracked positions.

        Returns:
          Dict[str, int]: Dictionary with position statistics
        """

        return {"lines": self.line, "max_column": self.max_column}


class LexerStatistics:
    """
    Collects statistics about lexical analysis for performance monitoring.
    """

    __slots__ = (
        "start_time",
        "token_count",
        "token_types",
        "errors",
        "processing_time",
        "char_count",
        "line_count",
    )

    def __init__(self) -> None:
        """
        Initialize the statistics collector with zero values.
        """

        self.start_time: float = time.time()
        self.token_count: int = 0
        self.token_types: Dict[str, int] = {}
        self.errors: List[str] = []
        self.processing_time: float = 0
        self.char_count: int = 0
        self.line_count: int = 0

    def add_token(self, token: Token) -> None:
        """
        Record a token in the statistics

        Args:
          token (Token): The token to record
        """

        self.token_count += 1

        if isinstance(token.tag, int) and not isinstance(token.tag, Tag):
            tag_name = f"ASCII_{chr(token.tag)}"

        else:
            tag_name = token.tag.name if hasattr(token.tag, "name") else str(token.tag)

        if tag_name in self.token_types:
            self.token_types[tag_name] += 1

        else:
            self.token_types[tag_name] = 1

    def add_error(self, error: Exception) -> None:
        """
        Record an error in the statistics.

        Args:
            error: The error to record.
        """

        self.errors.append(str(error))

    def add_char(self) -> None:
        """
        Increment the character count.
        """

        self.char_count += 1

    def add_line(self) -> None:
        """
        Increment the line count.
        """

        self.line_count += 1

    def finish(self) -> None:
        """
        Finalize statistics collection.
        """

        self.processing_time = time.time() - self.start_time

    def get_report(self) -> Dict[str, Any]:
        """
        Get a complete statistics report.

        Returns:
            Dictionary with all statistics.
        """

        return {
            "token_count": self.token_count,
            "token_types": self.token_types,
            "error_count": len(self.errors),
            "errors": self.errors,
            "processing_time": self.processing_time,
            "char_count": self.char_count,
            "line_count": self.line_count,
            "tokens_per_second": self.token_count / max(0.001, self.processing_time),
            "chars_per_second": self.char_count / max(0.001, self.processing_time),
        }


class Lexer:
    """
    Lexical analyzer for the Logo dialect. This class implements a lexical analyzer with enhanced performance, memory efficiency, and comprehensive error handling.
    """

    __slots__ = (
        "buffer",
        "position",
        "reserved_words",
        "statistics",
        "max_identifier_length",
        "max_number_length",
        "max_string_length",
    )

    def __init__(self, file_path: str, buffer_size: int = 4096) -> None:
        """
        Initialize the lexical analyzer with performance-optimized settings.

        Args:
          file_path (str): Path to the file to analyze
          buffer_size (int): Size of the read buffer. Defaults to 4096

        Raises:
          FileError: If there is a problem with the file
        """

        self.buffer: BufferManager = BufferManager(file_path, buffer_size)
        self.position: PositionTracker = PositionTracker()
        self.reserved_words: ReservedWords = DEFAULT_RESERVED_WORDS
        self.statistics: LexerStatistics = LexerStatistics()

        # Configuration constants
        self.max_identifier_length: int = 255
        self.max_number_length: int = 100
        self.max_string_length: int = 10000

    def __del__(self) -> None:
        """
        Cleanup resources when the lexer is destroyed
        """

        if hasattr(self, "buffer"):
            self.buffer.close()

    @property
    def line(self) -> int:
        """
        Get the current line number.

        Returns:
            The current line number.
        """

        return self.position.line

    @property
    def column(self) -> int:
        """
        Get the current column number.

        Returns:
            The current column number.
        """

        return self.position.column

    def get_next_char(self) -> Optional[str]:
        """
        Get the next character from the input with position tracking

        Returns:
          The next character, or None if end of file (EOF)

        Raises:
          LexerError: If there is a problem reading the file
        """

        try:
            char = self.buffer.get_next_char()

            if char is not None:
                self.position.update(char)
                self.statistics.add_char()

                if char == "\n":
                    self.statistics.add_line()

            return char

        except FileError as e:
            line, column = self.position.get_position()
            raise LexerError(str(e), line, column)

    def push_back(self, char: Optional[str]) -> None:
        """
        Push a character back to the input.

        Args:
          char (Optional[str]): The character to push back
        """

        if char is not None:
            self.position.revert(char)
            self.buffer.push_back(char)

            if self.statistics.char_count > 0:
                self.statistics.char_count -= 1

            if char == "\n" and self.statistics.line_count > 0:
                self.statistics.line_count -= 1

    def scan(self) -> Token:
        """
        Scan the next token from the source code with enhanced error handling.

        Returns:
            The next token found.

        Raises:
            LexerError: If there is an error during lexical analysis.
        """

        try:
            token = self._scan_impl()
            self.statistics.add_token(token)

            return token

        except Exception as e:
            if not isinstance(e, LexerError):
                line, column = self.position.get_position()
                error = LexerError(
                    f"Error during lexical analysis: {str(e)}", line, column
                )

            else:
                error = e

            self.statistics.add_error(error)
            raise error

    def _scan_impl(self) -> Token:
        """
        Implementation of the scan method with optimized token recognition.

        Returns:
            The next token found.

        Raises:
            LexerError: If there is an error during lexical analysis.
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

            # Numbers (including decimals like .5)
            if char.isdigit() or char == ".":
                if char == ".":
                    next_char = self.get_next_char()
                    if next_char is not None and next_char.isdigit():
                        return self._handle_number(char, next_char)

                    else:
                        self.push_back(next_char)
                        return Token(ord("."))
                else:
                    return self._handle_number(char)

            # Identifiers and reserved words
            if char.isalpha() or char == "_":
                return self._handle_identifier(char)

            # Any other character
            return Token(ord(char))

    def _skip_comment(self) -> None:
        """
        Skip all characters until the end of line (comment)
        """

        while True:
            char = self.get_next_char()

            if char is None or char == "\n":
                break

    def _handle_less_than(self) -> Token:
        """
        Handle operators starting with '<'.

        Returns:
            The corresponding token.
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
        Handle operators starting with '>'.

        Returns:
            The corresponding token.
        """
        char = self.get_next_char()
        if char == "=":
            return Token(Tag.GEQ, ">=")

        else:
            self.push_back(char)
            return Token(ord(">"))

    def _handle_hash(self) -> Token:
        """
        Handle boolean values starting with '#'

        Returns:
          The corresponding token

        Raises:
          InvalidCharacterError: If the hash is followed by invalid character.
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
                line, column = self.position.get_position()
                raise InvalidCharacterError(
                    f"Invalid character after '#': '{char}'", line, column
                )

        else:
            line, column = self.position.get_position()
            raise InvalidCharacterError(
                "Unexpected end of file after '#'", line, column
            )

    def _handle_colon(self) -> Token:
        """
        Handle operators starting with ':'.

        Returns:
            The corresponding token.
        """
        char = self.get_next_char()
        if char == "=":
            return Token(Tag.ASSIGN, ":=")

        else:
            self.push_back(char)
            return Token(ord(":"))

    def _handle_string(self) -> Token:
        """
        Handle string literals with error handling and length limits.

        Returns:
          The corresponding tokens.

        Raises:
          StringLiteralError: If the string is not closed or exceeds max length
        """

        text = '"'
        line_start, column_start = self.position.get_position()
        column_start -= 1
        length = 1

        while length < self.max_string_length:
            char = self.get_next_char()
            if char is None:
                raise StringLiteralError(
                    f"Unclosed string literal, started at line {line_start}, column {column_start}",
                    line_start,
                    column_start,
                )

            text += char
            length += 1

            if char == '"':
                return Token(Tag.STRING, text)

        raise StringLiteralError(
            f"String literal exceeds maximum length of {self.max_string_length} characters",
            line_start,
            column_start,
        )

    def _handle_number(
        self, first_char: str, second_char: Optional[str] = None
    ) -> Token:
        """
        Handle numbers (integers and decimals).

        Args:
          first_char: The first character of the number
          second_char: Optional second character for decimals starting with '.'

        Returns:
          The corresponding token

        Raises:
          NumberLiteralError: If the number format is invalid or exceeds max length.
        """

        value = 0.0
        is_integer = True
        number_str = first_char
        length = 1
        line_start, column_start = self.position.get_position()
        column_start -= 1

        # Handle decimals starting with a dot
        if first_char == ".":
            is_integer = False
            decimal_factor = 0.1

            number_str += second_char
            value = int(second_char) * decimal_factor

            decimal_factor *= 0.1
            length += 1

            char = self.get_next_char()

        else:
            value = int(first_char)
            char = self.get_next_char()

            while (
                char is not None and char.isdigit() and length < self.max_number_length
            ):
                number_str += char
                value = (value * 10) + int(char)

                length += 1
                char = self.get_next_char()

            # Process decimal part if present
            if char == ".":
                number_str += char
                is_integer = False

                decimal_factor = 0.1
                length += 1

                char = self.get_next_char()

        # Continue processing decimal part
        if not is_integer:
            while (
                char is not None and char.isdigit() and length < self.max_number_length
            ):
                number_str += char
                value += int(char) * decimal_factor

                decimal_factor *= 0.1
                length += 1

                char = self.get_next_char()

        if (
            length >= self.max_number_length
            and char is not None
            and (char.isdigit() or char == ".")
        ):
            raise NumberLiteralError(
                f"Number literal exceeds maximum length of {self.max_number_length} characters",
                line_start,
                column_start,
            )

        self.push_back(char)
        return Token(Tag.NUMBER, int(value) if is_integer else value)

    def _handle_identifier(self, first_char: str) -> Token:
        """
        Handle identifiers and reserved words with length limit checking.

        Args:
            first_char: The first character of the identifier.

        Returns:
            The corresponding token.

        Raises:
            IdentifierError: If the identifier exceeds maximum length.
        """
        lexeme = first_char
        length = 1
        line_start, column_start = self.position.get_position()
        column_start -= 1

        while length < self.max_identifier_length:
            char = self.get_next_char()
            if char is None or not (char.isalnum() or char == "_"):
                self.push_back(char)
                break

            lexeme += char
            length += 1

        # Check if we hit the length limit
        if length >= self.max_identifier_length:
            next_char = self.get_next_char()
            if next_char is not None and (next_char.isalnum() or next_char == "_"):
                self.push_back(next_char)
                raise IdentifierError(
                    f"Identifier exceeds maximum length of {self.max_identifier_length} characters",
                    line_start,
                    column_start,
                )

            self.push_back(next_char)

        token = self.reserved_words.get(lexeme)
        if token:
            return token

        token = Token(Tag.ID, lexeme.upper())
        self.reserved_words.add(lexeme, token)
        return token

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the lexical analysis.

        Returns:
            Dictionary with lexical analysis statistics.
        """

        self.statistics.finish()
        stats = self.statistics.get_report()
        stats.update({"position": self.position.get_stats()})

        return stats

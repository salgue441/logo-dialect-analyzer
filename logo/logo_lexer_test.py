"""
Test script for the Logo dialect lexical analyzer

This script allows testing the functionality of the Logo dialect lexical analyzer. It reads a source code file and displays the recognized tokens
"""

import sys
import os
import argparse
from typing import List, Optional, TextIO

from .logo_tokens import Token, Tag
from .logo_lexer import Lexer
from .logo_errors import LexerError, FileError


class LexerTest:
    """
    Class for testing the Logo dialect lexical analyzer.
    """

    def __init__(
        self, file_path: str, verbose: bool = False, output_file: Optional[str] = None
    ):
        """
        Initialize the tester.

        Args:
          file_path (str): Path to the source code file to analyze
          verbose (bool, optional): If True, displays detailed information. Defaults to False.
          output_file (Optional[str], optional): Path to the output file. If None, output is displayed on the console. Defaults to None
        """

        self.file_path = file_path
        self.verbose = verbose
        self.output_file = output_file
        self.tokens: List[Token] = []

    def run(self) -> int:
        """
        Run the lexical analysis

        Returns:
          int: 0 if the analysis was successful, 1 if there was an error
        """

        output: Optional[TextIO] = None

        try:
            lexer = Lexer(self.file_path)
            output = open(self.output_file, "w") if self.output_file else sys.stdout

            self._print_header(output)
            self._analyze_tokens(lexer, output)

            if self.verbose:
                self._print_statistics(output)

            print("\nLexical analysis completed successfully", file=output)
            return 0

        except LexerError as e:
            print(f"Lexical error: {str(e)}", file=sys.stderr)
            return 1

        except FileError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1

        except IOError as e:
            print(f"I/O error: {str(e)}", file=sys.stderr)
            return 1

        except Exception as e:
            print(f"Unexpected error: {str(e)}", file=sys.stderr)
            return 1

        finally:
            if output and output != sys.stdout:
                output.close()

    def _print_header(self, output: TextIO) -> None:
        """
        Print the header information.

        Args:
          output (TextIO): The output file where to print the header
        """

        print(f"Analyzing file: {self.file_path}", file=output)
        print("-" * 60, file=output)

    def _analyze_tokens(self, lexer: Lexer, output: TextIO) -> None:
        """
        Analyze the tokens in the .logo files.

        Args:
            lexer (Lexer): Lexer to use for the analysis
            output (TextIO): output buffer (either a file or stddout)
        """

        while True:
            token = lexer.scan()
            self.tokens.append(token)

            if token.tag == Tag.EOF:
                print(f"Line {lexer.line}, Column {lexer.column}: EOF", file=output)
                break

            token_info = f"Line {lexer.line}, Column {lexer.column}: {token}"

            if self.verbose:
                if isinstance(token.tag, int) and not isinstance(token.tag, Tag):
                    # For ASCII characters
                    tag_name = f"ASCII '{chr(token.tag)}'"
                    tag_value = token.tag
                else:
                    # For Tag enum members
                    tag_name = token.tag.name
                    tag_value = token.tag.value

                token_info += f" (Tag: {tag_name} = {tag_value})"

            print(token_info, file=output)

    def _print_statistics(self, output: TextIO) -> None:
        """
        Print statistics about the found tokens.

        Args:
            output (TextIO): The output file where to print the statistics.
        """

        token_counts = {}
        for token in self.tokens:
            if isinstance(token.tag, int) and not isinstance(token.tag, Tag):
                tag_name = f"ASCII '{chr(token.tag)}'"

            else:
                tag_name = token.tag.name

            token_counts[tag_name] = token_counts.get(tag_name, 0) + 1

        # Print statistics
        print("\nStatistics:", file=output)
        print("-" * 30, file=output)
        print(f"Total tokens: {len(self.tokens)}", file=output)

        print("\nTokens by type:", file=output)
        for tag_name, count in sorted(
            token_counts.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {tag_name}: {count}", file=output)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments

    Returns:
      argparse.Namespace: The parsed arguments
    """

    parser = argparse.ArgumentParser(
        description="Test the Logo dialect lexical analyzer."
    )

    parser.add_argument("file", help="Source code file to analyze.")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed information."
    )
    parser.add_argument(
        "-o", "--output", help="File where to save the output (default: stddout)"
    )

    return parser.parse_args()


def main() -> int:
    """
    Main function.

    Returns:
      int: Exit code (0: success, 1: error)
    """

    args = parse_arguments()
    tester = LexerTest(args.file, args.verbose, args.output)

    return tester.run()


if __name__ == "__main__":
    main()

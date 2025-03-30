"""
Enhanced test script for the Logo dialect lexical analyzer.

This script provides a comprehensive testing framework for the Logo lexical analyzer
with improved output formatting, error handling, and performance monitoring.
"""

import sys
import os
import argparse
import time
import json
from typing import List, Optional, TextIO, Dict, Any, Set, Tuple, Union
import concurrent.futures
import re
from datetime import datetime

try:
    import colorama
    from colorama import Fore, Back, Style

    colorama.init()
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

    # Define color stubs if colorama is not available
    class ColorStub:
        def __getattr__(self, name):
            return ""

    Fore = ColorStub()
    Back = ColorStub()
    Style = ColorStub()

from logo.lexical.token import Token, Tag
from logo.lexical.lexer import Lexer
from logo.utils.error import (
    LexerError,
    FileError,
    ErrorReporter,
)


class TokenFormatter:
    """
    Formats tokens for display with optional coloring.
    """

    @staticmethod
    def token_to_str(token: Token, with_color: bool = False) -> str:
        """
        Convert a token to a string with optional coloring.

        Args:
            token: The token to convert.
            with_color: Whether to add color to the output.

        Returns:
            Formatted token string.
        """
        # Base string representation
        token_str = str(token)

        if not with_color or not COLORS_AVAILABLE:
            return token_str

        # Add color based on token type
        if isinstance(token.tag, Tag):
            if token.tag == Tag.ID:
                return f"{Fore.CYAN}{token_str}{Style.RESET_ALL}"
            elif token.tag == Tag.NUMBER:
                return f"{Fore.YELLOW}{token_str}{Style.RESET_ALL}"
            elif token.tag == Tag.STRING:
                return f"{Fore.GREEN}{token_str}{Style.RESET_ALL}"
            elif token.tag == Tag.TRUE or token.tag == Tag.FALSE:
                return f"{Fore.MAGENTA}{token_str}{Style.RESET_ALL}"
            elif token.tag >= Tag.VAR and token.tag <= Tag.IFELSE:
                return f"{Fore.BLUE}{Style.BRIGHT}{token_str}{Style.RESET_ALL}"
            elif token.tag == Tag.EOF:
                return f"{Fore.RED}{Style.BRIGHT}{token_str}{Style.RESET_ALL}"
            else:
                return f"{Fore.WHITE}{token_str}{Style.RESET_ALL}"
        else:
            # ASCII character tokens
            return f"{Fore.WHITE}{Style.DIM}{token_str}{Style.RESET_ALL}"

    @staticmethod
    def position_to_str(line: int, column: int, with_color: bool = False) -> str:
        """
        Format position information.

        Args:
            line: Line number.
            column: Column number.
            with_color: Whether to add color to the output.

        Returns:
            Formatted position string.
        """
        position_str = f"Line {line}, Column {column}"

        if not with_color or not COLORS_AVAILABLE:
            return position_str

        return f"{Fore.WHITE}{Style.DIM}{position_str}{Style.RESET_ALL}"


class LexerTester:
    """
    Enhanced class for testing the Logo dialect lexical analyzer.
    """

    def __init__(
        self,
        file_path: str,
        verbose: bool = False,
        output_file: Optional[str] = None,
        json_output: bool = False,
        max_tokens: int = 0,
        color: bool = True,
        benchmark: bool = False,
        stats_only: bool = False,
    ) -> None:
        """
        Initialize the tester with enhanced options.

        Args:
            file_path: Path to the source code file to analyze.
            verbose: If True, displays detailed information. Defaults to False.
            output_file: Path to the output file. If None, output is displayed on the console.
            json_output: If True, outputs in JSON format. Defaults to False.
            max_tokens: Maximum number of tokens to process. Defaults to 0 (no limit).
            color: If True, use colored output. Defaults to True.
            benchmark: If True, run performance benchmark. Defaults to False.
            stats_only: If True, only show statistics. Defaults to False.
        """
        self.file_path: str = file_path
        self.verbose: bool = verbose
        self.output_file: Optional[str] = output_file
        self.json_output: bool = json_output
        self.max_tokens: int = max_tokens
        self.color: bool = (
            color and COLORS_AVAILABLE and sys.stdout.isatty() and not output_file
        )
        self.benchmark: bool = benchmark
        self.stats_only: bool = stats_only
        self.tokens: List[Token] = []
        self.source_lines: List[str] = []
        self.benchmark_results: Dict[str, Any] = {}

        # Performance metrics
        self.start_time: float = 0
        self.end_time: float = 0
        self.processing_speed: float = 0  # tokens per second

    def load_source_file(self) -> None:
        """
        Load the source file into memory.

        Raises:
            FileError: If the file cannot be opened or read.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.source_lines = file.read().splitlines()
        except Exception as e:
            raise FileError(f"Failed to load source file: {str(e)}")

    def run(self) -> int:
        """
        Run the lexical analysis.

        Returns:
            0 if the analysis was successful, 1 if there was an error.
        """
        output: Optional[TextIO] = None
        lexer: Optional[Lexer] = None

        try:
            # Load source file for error reporting
            self.load_source_file()

            # Create lexer
            lexer = Lexer(self.file_path)

            # Create output file or use stdout
            output = open(self.output_file, "w") if self.output_file else sys.stdout

            # Print header if not in stats-only mode
            if not self.stats_only:
                self._print_header(output)

            # Analyze tokens
            if self.benchmark:
                self._run_benchmark(lexer, output)
            else:
                self._analyze_tokens(lexer, output)

            # Show statistics
            if self.verbose or self.stats_only:
                self._print_statistics(lexer, output)

            if not self.stats_only and not self.json_output:
                print("\nLexical analysis completed successfully.", file=output)

            return 0

        except LexerError as e:
            if not self.json_output:
                print(
                    f"Lexical error: {ErrorReporter.report_error(e, self.source_lines)}",
                    file=sys.stderr,
                )
            else:
                error_json = {
                    "success": False,
                    "error": ErrorReporter.format_json_error(e),
                }
                print(json.dumps(error_json, indent=2), file=output)
            return 1
        except FileError as e:
            if not self.json_output:
                print(f"File error: {str(e)}", file=sys.stderr)
            else:
                error_json = {
                    "success": False,
                    "error": {"type": "FileError", "message": str(e)},
                }
                print(json.dumps(error_json, indent=2), file=output)
            return 1
        except Exception as e:
            if not self.json_output:
                print(f"Unexpected error: {str(e)}", file=sys.stderr)
            else:
                error_json = {
                    "success": False,
                    "error": {"type": "UnexpectedError", "message": str(e)},
                }
                print(json.dumps(error_json, indent=2), file=output)
            return 1
        finally:
            # Close output file if not stdout
            if output and output != sys.stdout:
                output.close()

    def _print_header(self, output: TextIO) -> None:
        """
        Print the header information.

        Args:
            output: The output file where to print the header.
        """
        if self.json_output:
            # JSON output doesn't need a header
            return

        header = f"Analyzing file: {self.file_path}"
        if self.color:
            header = f"{Style.BRIGHT}{header}{Style.RESET_ALL}"
        print(header, file=output)
        print("-" * 60, file=output)

    def _analyze_tokens(self, lexer: Lexer, output: TextIO) -> None:
        """
        Analyze tokens and print them.

        Args:
            lexer: The lexical analyzer to use.
            output: The output file where to print the tokens.

        Raises:
            LexerError: If there is an error during lexical analysis.
        """
        self.start_time = time.time()
        token_count = 0

        # Prepare JSON output if needed
        json_result = {"success": True, "file": self.file_path, "tokens": []}

        while True:
            token = lexer.scan()
            self.tokens.append(token)
            token_count += 1

            # Process token based on output format
            if self.json_output:
                # Add token to JSON output
                token_data = {
                    "line": lexer.line,
                    "column": lexer.column,
                    "type": (
                        token.tag.name
                        if hasattr(token.tag, "name")
                        else f"ASCII {chr(token.tag)}"
                    ),
                    "value": token.value,
                }
                json_result["tokens"].append(token_data)
            elif not self.stats_only:
                # Print token info
                position = TokenFormatter.position_to_str(
                    lexer.line, lexer.column, self.color
                )
                token_str = TokenFormatter.token_to_str(token, self.color)

                # Additional information in verbose mode
                if self.verbose:
                    if isinstance(token.tag, int) and not isinstance(token.tag, Tag):
                        # For ASCII characters
                        tag_name = f"ASCII '{chr(token.tag)}'"
                        tag_value = token.tag
                    else:
                        # For Tag enum members
                        tag_name = (
                            token.tag.name
                            if hasattr(token.tag, "name")
                            else str(token.tag)
                        )
                        tag_value = token.tag

                    token_info = (
                        f"{position}: {token_str} (Tag: {tag_name} = {tag_value})"
                    )
                else:
                    token_info = f"{position}: {token_str}"

                print(token_info, file=output)

            # Check for EOF or max tokens limit
            if token.tag == Tag.EOF or (
                self.max_tokens > 0 and token_count >= self.max_tokens
            ):
                break

        self.end_time = time.time()
        self.processing_speed = token_count / max(
            0.001, self.end_time - self.start_time
        )

        # Output JSON if requested
        if self.json_output:
            json_result["token_count"] = token_count
            json_result["processing_time"] = self.end_time - self.start_time
            json_result["processing_speed"] = self.processing_speed
            print(json.dumps(json_result, indent=2), file=output)

    def _run_benchmark(self, lexer: Lexer, output: TextIO) -> None:
        """
        Run a benchmark of the lexer performance.

        Args:
            lexer: The lexical analyzer to benchmark.
            output: The output file where to print results.
        """
        iteration_count = 3  # Number of benchmark iterations
        total_tokens = 0
        total_times = []

        for i in range(iteration_count):
            if not self.json_output and not self.stats_only:
                print(f"Benchmark run {i+1}/{iteration_count}...", file=output)

            # Create a fresh lexer for each run
            bench_lexer = Lexer(self.file_path)

            # Run the benchmark
            start_time = time.time()
            token_count = 0

            while True:
                token = bench_lexer.scan()
                token_count += 1
                if token.tag == Tag.EOF:
                    break

            end_time = time.time()
            run_time = end_time - start_time

            total_tokens += token_count
            total_times.append(run_time)

        # Calculate statistics
        avg_time = sum(total_times) / len(total_times)
        avg_tokens = total_tokens / iteration_count
        avg_speed = avg_tokens / avg_time if avg_time > 0 else 0

        # Store benchmark results
        self.benchmark_results = {
            "iterations": iteration_count,
            "total_tokens": total_tokens,
            "avg_tokens_per_run": avg_tokens,
            "times": total_times,
            "avg_time": avg_time,
            "avg_speed": avg_speed,
        }

        # Print results
        if self.json_output:
            benchmark_json = {
                "success": True,
                "file": self.file_path,
                "benchmark": self.benchmark_results,
            }
            print(json.dumps(benchmark_json, indent=2), file=output)
        elif not self.stats_only:
            print("\nBenchmark Results:", file=output)
            print(f"  Iterations: {iteration_count}", file=output)
            print(f"  Average tokens: {avg_tokens:.0f}", file=output)
            print(f"  Average time: {avg_time:.6f} seconds", file=output)
            print(f"  Average speed: {avg_speed:.0f} tokens/second", file=output)

    def _print_statistics(self, lexer: Lexer, output: TextIO) -> None:
        """
        Print statistics about the found tokens and lexer performance.

        Args:
            lexer: The lexical analyzer.
            output: The output file where to print the statistics.
        """
        if self.json_output:
            # Statistics are already included in JSON output
            return

        # Get lexer statistics
        stats = lexer.get_statistics() if hasattr(lexer, "get_statistics") else {}

        # Count tokens by type if not already provided by lexer
        token_counts = {}
        if "token_types" not in stats and self.tokens:
            for token in self.tokens:
                if isinstance(token.tag, int) and not isinstance(token.tag, Tag):
                    tag_name = f"ASCII_{chr(token.tag)}"
                else:
                    tag_name = (
                        token.tag.name if hasattr(token.tag, "name") else str(token.tag)
                    )

                token_counts[tag_name] = token_counts.get(tag_name, 0) + 1
        else:
            token_counts = stats.get("token_types", {})

        # Print statistics
        header = "\nStatistics:"
        if self.color:
            header = f"{Style.BRIGHT}{header}{Style.RESET_ALL}"
        print(header, file=output)
        print("-" * 30, file=output)

        # Token count
        token_count = stats.get("token_count", len(self.tokens))
        print(f"Total tokens: {token_count}", file=output)

        # Performance metrics
        processing_time = stats.get("processing_time", self.end_time - self.start_time)
        if processing_time > 0:
            tokens_per_second = token_count / processing_time
            print(f"Processing time: {processing_time:.6f} seconds", file=output)
            print(
                f"Processing speed: {tokens_per_second:.0f} tokens/second", file=output
            )

        # Line and character counts
        if "char_count" in stats:
            print(f"Characters processed: {stats['char_count']}", file=output)
        if "line_count" in stats:
            print(f"Lines processed: {stats['line_count']}", file=output)

        # Error count
        if "error_count" in stats and stats["error_count"] > 0:
            print(f"Errors encountered: {stats['error_count']}", file=output)

        # Token distribution
        print("\nTokens by type:", file=output)
        for tag_name, count in sorted(
            token_counts.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {tag_name}: {count}", file=output)

        # Benchmark results
        if self.benchmark and self.benchmark_results:
            print("\nBenchmark Results:", file=output)
            print(f"  Iterations: {self.benchmark_results['iterations']}", file=output)
            print(
                f"  Average tokens: {self.benchmark_results['avg_tokens_per_run']:.0f}",
                file=output,
            )
            print(
                f"  Average time: {self.benchmark_results['avg_time']:.6f} seconds",
                file=output,
            )
            print(
                f"  Average speed: {self.benchmark_results['avg_speed']:.0f} tokens/second",
                file=output,
            )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments with enhanced options.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Enhanced test script for the Logo dialect lexical analyzer.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("file", help="Source code file to analyze.")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed information."
    )

    parser.add_argument(
        "-o", "--output", help="File where to save the output (default: stdout)."
    )

    parser.add_argument(
        "-j", "--json", action="store_true", help="Output in JSON format."
    )

    parser.add_argument(
        "-m",
        "--max-tokens",
        type=int,
        default=0,
        help="Maximum number of tokens to process (0 = no limit).",
    )

    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output."
    )

    parser.add_argument(
        "-b", "--benchmark", action="store_true", help="Run performance benchmark."
    )

    parser.add_argument(
        "-s", "--stats-only", action="store_true", help="Only show statistics."
    )

    return parser.parse_args()


def main() -> int:
    """
    Main function with enhanced error handling and options.

    Returns:
        Exit code (0: success, 1: error).
    """
    # Parse arguments
    args = parse_arguments()

    try:
        # Run tester
        tester = LexerTester(
            args.file,
            args.verbose,
            args.output,
            args.json,
            args.max_tokens,
            not args.no_color,
            args.benchmark,
            args.stats_only,
        )
        return tester.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

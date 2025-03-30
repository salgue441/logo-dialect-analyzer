# Logo Dialect Lexical Analyzer

This project implements a modular lexical analyzer for a Logo dialect with enhanced error handling and performance optimization. The lexer can recognize all tokens defined in the grammar, including reserved words, operators, numbers (integers and decimals), string literals, and comments.

## Features

- Complete recognition of all tokens defined in the Logo dialect grammar
- Support for all movement and drawing commands (FORWARD/FD, BACKWARD/BK, etc)
- Recognition of control structures (IF, IFELSE, WHILE)
- Support for comments (lines starting with '%')
- Decimal number recognition
- Robust error handling with detailed error reporting
- Performance monitoring and statistics
- Colorized output for better readability
- JSON output option for programmatic processing

## Project Structure

The project is organized in the following structure:

```bash
logo-compiler/
├── logo/
│   ├── __init__.py                # Package initialization
│   ├── lexical/                   # Lexical analysis components
│   │   ├── __init__.py
│   │   ├── token.py               # Token definitions
│   │   └── lexer.py               # Lexer implementation
│   ├── utils/                     # Utility modules
│   │   ├── __init__.py
│   │   └── error.py               # Error handling
│   └── cli/                       # Command-line interfaces
│       ├── __init__.py
│       └── lexer_test.py          # CLI for lexer testing
├── examples/                      # Example Logo code
│   └── example.logo
├── run_lexer.py                   # Convenience script
├── setup.py                       # Package setup
└── requirements.txt               # Dependencies
```

## Installation

### Using pip

```bash
# Install from project directory
pip install .
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/salgue441/logo-dialect-analyzer
cd logo-dialect-analyzer

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

### Command-Line Interface

```bash
# Using the command-line tool (after installation)
logo-lexer examples/example.logo

# Using the convenience script (without installation)
python run_lexer.py examples/example.logo

# Show detailed token information
logo-lexer examples/example.logo -v

# Save the output to a file
logo-lexer examples/example.logo -o output.txt

# Output in JSON format
logo-lexer examples/example.logo -j

# Only show statistics
logo-lexer examples/example.logo -s

# Run a performance benchmark
logo-lexer examples/example.logo -b
```

### Programmatic Usage

```python
from logo.lexical.lexer import Lexer
from logo.lexical.token import Tag
from logo.utils.error import LexerError, ErrorReporter

try:
    # Create a lexer for the source file
    lexer = Lexer("examples/example.logo")

    # Scan all tokens
    while True:
        token = lexer.scan()
        print(f"Line {lexer.line}, Column {lexer.column}: {token}")

        # Exit when EOF is reached
        if token.tag == Tag.EOF:
            break

    # Get lexer statistics
    stats = lexer.get_statistics()
    print(f"Processed {stats['token_count']} tokens in {stats['processing_time']:.6f} seconds")

except LexerError as e:
    # Load source file for error context
    source_lines = ErrorReporter.load_source_file("examples/example.logo")
    print(ErrorReporter.report_error(e, source_lines))
```

## Key Components

### Tokens

The lexer recognizes these token types:

- **Reserved words**: VAR, FORWARD/FWD, BACKWARD/BK, RIGHT/RT, LEFT/LT, etc.
- **Operators**: +,-,\*,/, MOD, etc.
- **Comparison operators**: <, <=, >, >=, =, <>
- **Logical operators**: AND, OR
- **Boolean literals**: #t, #f
- **Numbers**: Both integers (123) and decimals (3.14159)
- **String literals**: Enclosed in quotes ("Hello, world")
- **Comments**: Lines starting with '%'

## Error Handling

The lexer provides detailed error messages with line and column information. It can detect and report:

- Unclosed string literals
- Invalid characters after '#'
- Excessively long identifiers or numbers
- File not found or reading errors

## License

This project is licensed under the [License](./LICENSE).

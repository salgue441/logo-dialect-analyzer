# Logo Dialect Lexical Analyzer

This project implements a lexical analyzer for a Logo dialect. The lexer can recognize all tokens defined in the grammar, including reserved words, operators, numbers (integers and decimals), string literals, and comments.

## Features

- Complete recognition of all tokens defined in the Logo dialect grammar
- Support for all movement and drawing commands (FORWARD/FWD, BACKWARD/BK, etc.)
- Recognition of control structures (IF, IFELSE, WHILE)
- Support for comments (lines starting with '%')
- Decimal number recognition
- Error handling with detailed error reporting

## Project Structure

The project is organized into the following modules:

- `logo_tokens.py`: Defines the token types and the Token class
- `logo_errors.py`: Contains the exception hierarchy for error handling
- `logo_lexer.py`: Implements the lexical analyzer
- `logo_lexer_test.py`: Test script for the lexical analyzer
- `example.logo`: Example Logo code for testing

## Installation

### Using pip

```bash
# Install from project directory
pip install .
```

### Manual Installation

```bash
# Clone the repository
git clone {url}
cd logo-compiler

# Install dependencies
pip install -r requirements.txt

# Make the test script executable
chmod +x logo_lexer_test.py
```

## Usage

### Command-line Inteface

```bash
# Analyze a Logo source file
logo-lexer example.logo

# Show detailed token information
logo-lexer -v example.logo

# Save the output to a file
logo-lexer -o output.txt example.logo
```

### Programmatic Usage

```python
from logo_lexer import Lexer
from logo_tokens import Tag
from logo_errors import LexerError

try:
  # Create a lexer for the source file
  lexer = Lexer("example.logo")

  # Scan all tokens
  while True:
    token = lexer.scan()
    print(f"Line {lexer.line}, Column {lexer.column}: {token}")

    # Exit when EOF if reached
    if token.tag == Tag.EOF:
      break

except LexerError as e:
  print(f"Error: {str(e)}")
```

## Grammar

The lexical analyzer recognizes token according to the grammar defined for the Logo dialect. The grammar includes:

- Reserved words (VAR, FORWARD, BACKWARD, etc.)
- Operators (+, -, \*, /, MOD, etc.)
- Comparison operators (<, <=, >, >=, =, <>)
- Boolean literals (#t, #f)
- Numbers (integers and decimals)
- String literals (enclosed in quotes)
- Comments (lines starting with '%')

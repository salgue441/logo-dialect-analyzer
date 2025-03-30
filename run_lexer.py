#!/usr/bin/env python3
"""
Convenient script to run the Logo lexical analyzer from the project root.

This script allows running the lexical analyzer without installing the package.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from logo.cli.lexer_test import main


if __name__ == "__main__":
    sys.exit(main())

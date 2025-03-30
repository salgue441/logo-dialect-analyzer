"""
Setup script for the Logo compiler package.
"""

from setuptools import setup, find_packages

setup(
    name="logo-compiler",
    version="1.0.0",
    description="Lexical analyzer for the Logo dialect",
    author="Logo Compiler Team",
    author_email="contact@example.com",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "logo-lexer=logo_lexer_test:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="compiler, lexer, logo, programming language",
)

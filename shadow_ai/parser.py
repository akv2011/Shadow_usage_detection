"""
Multi-Language File Parser Module

This module provides functionality to parse various input sources (files, strings, directories)
and prepare them for analysis by the AI detection engine. It handles encoding detection,
file validation, and provides a unified interface for different input types.

Author: Shadow AI Detection Tool
Created: 2025-08-04
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Union


class ParserError(Exception):
    """Base exception for parser-related errors."""
    pass


class FileTooLargeError(ParserError):
    """Raised when a file exceeds the maximum allowed size."""
    pass


class InvalidInputError(ParserError):
    """Raised when input is invalid or cannot be processed."""
    pass


class UnsupportedFileTypeError(ParserError):
    """Raised when a file type is not supported for analysis."""
    pass


# Configuration constants
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_STRING_LENGTH = 1000000  # 1 million characters for raw strings


def validate_file_input(file_path: Path) -> None:
    """
    Validate file input for security and processing constraints.
    
    Args:
        file_path: Path to the file to validate
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IsADirectoryError: If the path points to a directory
        PermissionError: If the file cannot be read
        FileTooLargeError: If the file exceeds size limits
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
    
    if not file_path.is_file():
        raise InvalidInputError(f"Path exists but is not a regular file: {file_path}")
    
    # Check file permissions
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"File cannot be read (permission denied): {file_path}")
    
    # Check file size
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        raise FileTooLargeError(
            f"File too large: {size_mb:.1f}MB (max: {MAX_FILE_SIZE_MB}MB): {file_path}"
        )


def validate_string_input(text: str) -> None:
    """
    Validate raw string input for processing constraints.
    
    Args:
        text: Raw string to validate
        
    Raises:
        InvalidInputError: If the string is invalid for processing
    """
    if not isinstance(text, str):
        raise InvalidInputError(f"Input must be a string, got {type(text).__name__}")
    
    if len(text) == 0:
        raise InvalidInputError("Input string cannot be empty")
    
    if len(text) > MAX_STRING_LENGTH:
        raise InvalidInputError(
            f"Input string too long: {len(text)} characters (max: {MAX_STRING_LENGTH})"
        )
    
    # Check for null bytes or other problematic characters
    if '\x00' in text:
        raise InvalidInputError("Input string contains null bytes")


def read_source(source: Union[str, Path]) -> Tuple[str, str]:
    """
    Read content from a file path or treat as raw string input.
    
    This function is the foundation of the parser module, handling both file input
    and direct string input with robust encoding detection for files.
    
    Args:
        source: Either a file path (str/Path) or raw string content
        
    Returns:
        Tuple containing:
        - content (str): The text content
        - source_identifier (str): File path or 'raw_string'
        
    Raises:
        FileNotFoundError: If the file path doesn't exist
        PermissionError: If the file cannot be read due to permissions
        IsADirectoryError: If the path points to a directory
        FileTooLargeError: If the file exceeds size limits
        InvalidInputError: If the input is invalid
        UnicodeDecodeError: If the file cannot be decoded with common encodings
    """
    # Handle empty string case before Path creation
    if isinstance(source, str) and len(source) == 0:
        validate_string_input(source)  # This will raise InvalidInputError
        return source, 'raw_string'
    
    source_path = Path(source)
    
    # Check if source is a file path
    if source_path.exists():
        if source_path.is_file():
            # Validate file input
            validate_file_input(source_path)
            
            try:
                # First attempt: UTF-8 encoding (most common)
                with open(source_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                return content, str(source_path)
            except UnicodeDecodeError:
                try:
                    # Fallback: Latin-1 encoding (covers most edge cases)
                    with open(source_path, 'r', encoding='latin-1') as file:
                        content = file.read()
                    return content, str(source_path)
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(
                        f"Unable to decode file {source_path} with UTF-8 or Latin-1 encoding"
                    ) from e
        elif source_path.is_dir():
            raise IsADirectoryError(f"Path is a directory, not a file: {source_path}")
        else:
            # Path exists but is neither file nor directory (e.g., special file)
            raise InvalidInputError(f"Path exists but is not a regular file: {source_path}")
    else:
        # Path doesn't exist - treat as raw string input and validate it
        text = str(source)
        validate_string_input(text)
        return text, 'raw_string'


class LanguageMapper:
    """
    Maps file extensions to programming language names.
    
    This class provides a centralized way to identify programming languages
    based on file extensions, with easy extensibility for future language support.
    """
    
    # Common programming language extensions
    EXTENSION_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'JavaScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.cxx': 'C++',
        '.cc': 'C++',
        '.c': 'C',
        '.h': 'C/C++',
        '.hpp': 'C++',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.cs': 'C#',
        '.sh': 'Shell',
        '.bash': 'Bash',
        '.zsh': 'Zsh',
        '.ps1': 'PowerShell',
        '.r': 'R',
        '.m': 'MATLAB',
        '.pl': 'Perl',
        '.lua': 'Lua',
        '.dart': 'Dart',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.less': 'LESS',
        '.xml': 'XML',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.toml': 'TOML',
        '.sql': 'SQL',
    }
    
    @classmethod
    def get_language(cls, file_path: Union[str, Path]) -> str:
        """
        Identify the programming language based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Language name or 'plaintext' if unknown
        """
        extension = Path(file_path).suffix.lower()
        return cls.EXTENSION_MAP.get(extension, 'plaintext')
    
    @classmethod
    def is_code_file(cls, file_path: Union[str, Path]) -> bool:
        """
        Check if a file is likely a source code file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if it's a recognized code file extension
        """
        extension = Path(file_path).suffix.lower()
        return extension in cls.EXTENSION_MAP


def read_source_with_language(source: Union[str, Path]) -> Tuple[str, str, str]:
    """
    Read content from a source and identify the programming language.
    
    This enhanced version of read_source also determines the programming
    language based on file extension, with full validation.
    
    Args:
        source: Either a file path (str/Path) or raw string content
        
    Returns:
        Tuple containing:
        - content (str): The text content
        - language (str): Programming language name or 'plaintext'
        - source_identifier (str): File path or 'raw_string'
        
    Raises:
        All exceptions from read_source, plus language mapping errors
    """
    content, source_identifier = read_source(source)
    
    # Determine language
    if source_identifier == 'raw_string':
        language = 'plaintext'
    else:
        language = LanguageMapper.get_language(source_identifier)
    
    return content, language, source_identifier

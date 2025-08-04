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


def parse_directory(dir_path: Union[str, Path], max_files: int = 5) -> List[Dict[str, str]]:
    """
    Parse multiple files from a directory for batch analysis.
    
    Scans the given directory for source code files and processes up to max_files
    of them. Files are selected based on recognized code file extensions and
    processed in alphabetical order for consistency.
    
    Args:
        dir_path: Path to the directory to scan
        max_files: Maximum number of files to process (default: 5)
        
    Returns:
        List of dictionaries, each containing:
        - 'content': The file content as string
        - 'language': Programming language name  
        - 'source': File path
        
    Raises:
        FileNotFoundError: If the directory doesn't exist
        NotADirectoryError: If the path is not a directory
        PermissionError: If the directory cannot be accessed
        InvalidInputError: If max_files is invalid
    """
    if max_files <= 0:
        raise InvalidInputError(f"max_files must be positive, got {max_files}")
    
    directory = Path(dir_path)
    
    # Validate directory
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    
    # Check directory permissions
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"Directory cannot be read (permission denied): {directory}")
    
    results = []
    processed_count = 0
    
    try:
        # Get all files and sort them for consistent ordering
        all_files = sorted([f for f in directory.iterdir() if f.is_file()])
        
        for file_path in all_files:
            # Stop if we've reached the maximum number of files
            if processed_count >= max_files:
                break
            
            # Check if it's a recognized code file
            if LanguageMapper.is_code_file(file_path):
                try:
                    content, language, source = read_source_with_language(file_path)
                    results.append({
                        'content': content,
                        'language': language,
                        'source': source
                    })
                    processed_count += 1
                except (UnicodeDecodeError, FileTooLargeError, PermissionError) as e:
                    # Skip files that can't be processed, but continue with others
                    # In a production environment, you might want to log these errors
                    continue
    
    except PermissionError:
        # Re-raise directory permission errors
        raise PermissionError(f"Cannot list directory contents: {directory}")
    
    return results


def get_directory_stats(dir_path: Union[str, Path]) -> Dict[str, int]:
    """
    Get statistics about code files in a directory.
    
    Args:
        dir_path: Path to the directory to analyze
        
    Returns:
        Dictionary with statistics:
        - 'total_files': Total number of files
        - 'code_files': Number of recognized code files
        - 'languages': Dictionary mapping language names to file counts
        
    Raises:
        FileNotFoundError: If the directory doesn't exist
        NotADirectoryError: If the path is not a directory
        PermissionError: If the directory cannot be accessed
    """
    directory = Path(dir_path)
    
    # Validate directory
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"Directory cannot be read: {directory}")
    
    stats = {
        'total_files': 0,
        'code_files': 0,
        'languages': {}
    }
    
    try:
        for file_path in directory.iterdir():
            if file_path.is_file():
                stats['total_files'] += 1
                
                if LanguageMapper.is_code_file(file_path):
                    stats['code_files'] += 1
                    language = LanguageMapper.get_language(file_path)
                    stats['languages'][language] = stats['languages'].get(language, 0) + 1
    
    except PermissionError:
        raise PermissionError(f"Cannot list directory contents: {directory}")
    
    return stats


def parse(source: Union[str, Path], max_files: int = 5) -> List[Dict[str, str]]:
    """
    Unified parser interface for all input types.
    
    This is the main entry point for the parser module. It automatically detects
    the input type (file, directory, or raw string) and processes it accordingly,
    always returning a consistent list format for the detection engine.
    
    Args:
        source: Input source - can be:
            - File path (str/Path): Single file to process
            - Directory path (str/Path): Directory to batch process  
            - Raw string: Code content to analyze directly
        max_files: Maximum files to process for directories (default: 5)
        
    Returns:
        List of dictionaries, each containing:
        - 'content': The code content as string
        - 'language': Programming language name
        - 'source': Source identifier (file path or 'raw_string')
        - 'metadata': Additional metadata dictionary
        
    Raises:
        All exceptions from underlying functions (validation, file access, etc.)
        
    Examples:
        # Single file
        results = parse('app.py')
        
        # Directory batch processing
        results = parse('./src', max_files=10)
        
        # Raw code string
        results = parse('def hello(): print("world")')
    """
    # Handle empty string case before Path creation (empty string resolves to current directory)
    if isinstance(source, str) and len(source) == 0:
        # This will raise InvalidInputError for empty strings
        content, language, source_id = read_source_with_language(source)
        return [{
            'content': content,
            'language': language,
            'source': source_id,
            'metadata': {
                'input_type': 'raw_string',
                'content_length': len(content),
                'estimated_lines': content.count('\n') + 1 if content else 0
            }
        }]
    
    source_path = Path(source)
    
    # Detect input type and route to appropriate function
    if source_path.exists():
        if source_path.is_file():
            # Single file processing
            content, language, source_id = read_source_with_language(source_path)
            return [{
                'content': content,
                'language': language,
                'source': source_id,
                'metadata': {
                    'input_type': 'file',
                    'file_size': source_path.stat().st_size,
                    'file_extension': source_path.suffix
                }
            }]
        
        elif source_path.is_dir():
            # Directory batch processing
            directory_results = parse_directory(source_path, max_files=max_files)
            
            # Add metadata to each result
            for result in directory_results:
                file_path = Path(result['source'])
                result['metadata'] = {
                    'input_type': 'directory_batch',
                    'file_size': file_path.stat().st_size,
                    'file_extension': file_path.suffix,
                    'directory': str(source_path)
                }
            
            return directory_results
        
        else:
            # Path exists but is neither file nor directory
            raise InvalidInputError(f"Path exists but is not a file or directory: {source_path}")
    
    else:
        # Path doesn't exist - treat as raw string
        content, language, source_id = read_source_with_language(source)
        return [{
            'content': content,
            'language': language,
            'source': source_id,
            'metadata': {
                'input_type': 'raw_string',
                'content_length': len(content),
                'estimated_lines': content.count('\n') + 1 if content else 0
            }
        }]


def parse_with_stats(source: Union[str, Path], max_files: int = 5) -> Dict[str, any]:
    """
    Parse with additional statistics and metadata.
    
    This enhanced version of parse() provides additional context about the
    parsing operation, useful for debugging and user feedback.
    
    Args:
        source: Input source (file, directory, or raw string)
        max_files: Maximum files to process for directories
        
    Returns:
        Dictionary containing:
        - 'results': List of parsed results (same as parse())
        - 'stats': Statistics about the parsing operation
        - 'summary': Human-readable summary
        
    Raises:
        All exceptions from parse()
    """
    import time
    start_time = time.time()
    
    # Perform the parsing
    results = parse(source, max_files=max_files)
    
    # Calculate statistics
    end_time = time.time()
    processing_time = end_time - start_time
    
    total_content_length = sum(len(result['content']) for result in results)
    languages_found = set(result['language'] for result in results)
    
    # Determine input type for stats
    source_path = Path(source)
    if source_path.exists():
        if source_path.is_file():
            input_type = 'file'
            source_info = str(source_path)
        elif source_path.is_dir():
            input_type = 'directory'
            source_info = str(source_path)
        else:
            input_type = 'special_file'
            source_info = str(source_path)
    else:
        input_type = 'raw_string'
        source_info = f"string ({len(str(source))} chars)"
    
    stats = {
        'input_type': input_type,
        'source_info': source_info,
        'files_processed': len(results),
        'total_content_length': total_content_length,
        'languages_found': sorted(list(languages_found)),
        'processing_time_seconds': round(processing_time, 4),
        'max_files_limit': max_files
    }
    
    # Generate human-readable summary
    if input_type == 'directory':
        summary = f"Processed {len(results)} files from directory '{source}' in {processing_time:.3f}s"
    elif input_type == 'file':
        summary = f"Processed single file '{source}' ({total_content_length} characters) in {processing_time:.3f}s"
    else:
        summary = f"Processed raw string input ({total_content_length} characters) in {processing_time:.3f}s"
    
    if languages_found:
        summary += f". Languages: {', '.join(sorted(languages_found))}"
    
    return {
        'results': results,
        'stats': stats,
        'summary': summary
    }

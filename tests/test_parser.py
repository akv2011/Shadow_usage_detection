"""
Tests for the Multi-Language File Parser Module

This test suite validates the parser's ability to handle various input sources,
encoding detection, language identification, and error handling scenarios.

Author: Shadow AI Detection Tool
Created: 2025-08-04
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from shadow_ai.parser import (
    LanguageMapper, 
    read_source, 
    read_source_with_language,
    parse_directory,
    get_directory_stats,
    parse,
    parse_with_stats,
    validate_file_input,
    validate_string_input,
    ParserError,
    FileTooLargeError,
    InvalidInputError,
    UnsupportedFileTypeError,
    MAX_FILE_SIZE_BYTES,
    MAX_STRING_LENGTH
)


class TestCoreFileReading:
    """Test the core file and string reading functionality."""
    
    def test_read_source_with_utf8_file(self):
        """Test reading a file with UTF-8 encoding."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.py') as f:
            test_content = "# This is a test file with UTF-8 content\ndef hello():\n    print('Hello, 世界!')"
            f.write(test_content)
            temp_path = f.name
        
        try:
            content, source_id = read_source(temp_path)
            assert content == test_content
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_read_source_with_latin1_file(self):
        """Test reading a file with Latin-1 encoding (fallback scenario)."""
        # Create a file with Latin-1 specific characters that would fail UTF-8
        test_content = "# Test with Latin-1 characters: café, naïve, résumé"
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
            # Write in Latin-1 encoding to create a file that would fail UTF-8 reading
            f.write(test_content.encode('latin-1'))
            temp_path = f.name
        
        try:
            content, source_id = read_source(temp_path)
            assert isinstance(content, str)
            assert source_id == temp_path
            # Content should be readable (might have different characters due to encoding)
            assert len(content) > 0
        finally:
            os.unlink(temp_path)
    
    def test_read_source_with_raw_string(self):
        """Test reading raw string input."""
        test_string = "def example():\n    return 'This is raw code'"
        content, source_id = read_source(test_string)
        
        assert content == test_string
        assert source_id == 'raw_string'
    
    def test_read_source_with_empty_file(self):
        """Test reading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("")  # Empty file
            temp_path = f.name
        
        try:
            content, source_id = read_source(temp_path)
            assert content == ""
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_read_source_nonexistent_file_as_string(self):
        """Test that a non-existent file path is treated as raw string."""
        fake_path = "/this/path/does/not/exist.py"
        content, source_id = read_source(fake_path)
        
        assert content == fake_path
        assert source_id == 'raw_string'


class TestLanguageMapper:
    """Test the language identification functionality."""
    
    def test_get_language_python(self):
        """Test Python file extension detection."""
        assert LanguageMapper.get_language('script.py') == 'Python'
        assert LanguageMapper.get_language(Path('app.py')) == 'Python'
    
    def test_get_language_javascript(self):
        """Test JavaScript file extension detection."""
        assert LanguageMapper.get_language('app.js') == 'JavaScript'
        assert LanguageMapper.get_language('component.jsx') == 'JavaScript'
    
    def test_get_language_typescript(self):
        """Test TypeScript file extension detection."""
        assert LanguageMapper.get_language('app.ts') == 'TypeScript'
        assert LanguageMapper.get_language('component.tsx') == 'TypeScript'
    
    def test_get_language_various_extensions(self):
        """Test various programming language extensions."""
        test_cases = [
            ('server.go', 'Go'),
            ('main.rs', 'Rust'),
            ('App.java', 'Java'),
            ('main.cpp', 'C++'),
            ('header.h', 'C/C++'),
            ('script.php', 'PHP'),
            ('app.rb', 'Ruby'),
            ('Model.swift', 'Swift'),
            ('Main.kt', 'Kotlin'),
            ('Program.cs', 'C#'),
            ('script.sh', 'Shell'),
            ('config.json', 'JSON'),
            ('config.yaml', 'YAML'),
            ('query.sql', 'SQL'),
        ]
        
        for filename, expected_language in test_cases:
            assert LanguageMapper.get_language(filename) == expected_language
    
    def test_get_language_unknown_extension(self):
        """Test unknown file extension defaults to plaintext."""
        assert LanguageMapper.get_language('notes.txt') == 'plaintext'
        assert LanguageMapper.get_language('README.md') == 'plaintext'
        assert LanguageMapper.get_language('file.xyz') == 'plaintext'
    
    def test_get_language_no_extension(self):
        """Test file without extension defaults to plaintext."""
        assert LanguageMapper.get_language('Makefile') == 'plaintext'
        assert LanguageMapper.get_language('LICENSE') == 'plaintext'
    
    def test_get_language_case_insensitive(self):
        """Test that extension matching is case-insensitive."""
        assert LanguageMapper.get_language('Script.PY') == 'Python'
        assert LanguageMapper.get_language('App.JS') == 'JavaScript'
        assert LanguageMapper.get_language('Main.CPP') == 'C++'
    
    def test_is_code_file_positive(self):
        """Test is_code_file returns True for known code extensions."""
        code_files = [
            'app.py', 'server.js', 'main.cpp', 'lib.go', 
            'component.tsx', 'style.css', 'config.json'
        ]
        
        for filename in code_files:
            assert LanguageMapper.is_code_file(filename), f"{filename} should be recognized as code"
    
    def test_is_code_file_negative(self):
        """Test is_code_file returns False for non-code extensions."""
        non_code_files = [
            'README.md', 'notes.txt', 'image.png', 'document.pdf',
            'archive.zip', 'video.mp4', 'unknown.xyz'
        ]
        
        for filename in non_code_files:
            assert not LanguageMapper.is_code_file(filename), f"{filename} should not be recognized as code"


class TestSourceWithLanguage:
    """Test the combined source reading and language identification."""
    
    def test_read_source_with_language_file(self):
        """Test reading a file with language identification."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def test():\n    pass"
            f.write(test_content)
            temp_path = f.name
        
        try:
            content, language, source_id = read_source_with_language(temp_path)
            assert content == test_content
            assert language == 'Python'
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_read_source_with_language_raw_string(self):
        """Test reading raw string with language identification."""
        test_string = "function test() { return true; }"
        content, language, source_id = read_source_with_language(test_string)
        
        assert content == test_string
        assert language == 'plaintext'  # Raw strings default to plaintext
        assert source_id == 'raw_string'
    
    def test_read_source_with_language_unknown_extension(self):
        """Test reading file with unknown extension."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.unknown') as f:
            test_content = "Some content"
            f.write(test_content)
            temp_path = f.name
        
        try:
            content, language, source_id = read_source_with_language(temp_path)
            assert content == test_content
            assert language == 'plaintext'  # Unknown extensions default to plaintext
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_read_source_with_language_various_files(self):
        """Test reading various file types with correct language identification."""
        test_cases = [
            ('.js', 'console.log("Hello");', 'JavaScript'),
            ('.go', 'package main\nfunc main() {}', 'Go'),
            ('.rs', 'fn main() {\n    println!("Hello");\n}', 'Rust'),
            ('.java', 'public class Test {\n    public static void main(String[] args) {}\n}', 'Java'),
        ]
        
        for extension, content, expected_language in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=extension) as f:
                f.write(content)
                temp_path = f.name
            
            try:
                read_content, language, source_id = read_source_with_language(temp_path)
                assert read_content == content
                assert language == expected_language
                assert source_id == temp_path
            finally:
                os.unlink(temp_path)


class TestInputValidation:
    """Test input validation functionality."""
    
    def test_validate_file_input_success(self):
        """Test successful file validation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("print('hello')")
            temp_path = Path(f.name)
        
        try:
            # Should not raise any exception
            validate_file_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_input_not_found(self):
        """Test validation with non-existent file."""
        fake_path = Path("/this/path/does/not/exist.py")
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            validate_file_input(fake_path)
    
    def test_validate_file_input_directory(self):
        """Test validation with directory path."""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            with pytest.raises(IsADirectoryError, match="Path is a directory"):
                validate_file_input(temp_dir)
        finally:
            os.rmdir(temp_dir)
    
    def test_validate_file_input_permission_denied(self):
        """Test validation with permission-denied file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("print('hello')")
            temp_path = Path(f.name)
        
        try:
            # Mock os.access to return False (no read permission)
            with patch('os.access', return_value=False):
                with pytest.raises(PermissionError, match="permission denied"):
                    validate_file_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_input_too_large(self):
        """Test validation with file exceeding size limit."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_path = Path(f.name)
        
        try:
            # Mock the validate_file_input function's file size check
            with patch('shadow_ai.parser.MAX_FILE_SIZE_BYTES', 100):  # Very small limit
                # Write content that exceeds the mock limit
                with open(temp_path, 'w') as f:
                    f.write('x' * 200)  # Exceeds the 100-byte limit
                
                with pytest.raises(FileTooLargeError, match="File too large"):
                    validate_file_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_string_input_success(self):
        """Test successful string validation."""
        valid_strings = [
            "def hello(): pass",
            "print('Hello, world!')",
            "x" * 1000,  # Reasonable length
        ]
        
        for test_string in valid_strings:
            # Should not raise any exception
            validate_string_input(test_string)
    
    def test_validate_string_input_empty(self):
        """Test validation with empty string."""
        with pytest.raises(InvalidInputError, match="cannot be empty"):
            validate_string_input("")
    
    def test_validate_string_input_too_long(self):
        """Test validation with overly long string."""
        long_string = "x" * (MAX_STRING_LENGTH + 1)
        
        with pytest.raises(InvalidInputError, match="too long"):
            validate_string_input(long_string)
    
    def test_validate_string_input_null_bytes(self):
        """Test validation with null bytes in string."""
        string_with_null = "def hello():\x00 pass"
        
        with pytest.raises(InvalidInputError, match="null bytes"):
            validate_string_input(string_with_null)
    
    def test_validate_string_input_wrong_type(self):
        """Test validation with non-string input."""
        with pytest.raises(InvalidInputError, match="must be a string"):
            validate_string_input(123)
        
        with pytest.raises(InvalidInputError, match="must be a string"):
            validate_string_input(None)
        
        with pytest.raises(InvalidInputError, match="must be a string"):
            validate_string_input(['not', 'a', 'string'])


class TestEnhancedFileReading:
    """Test enhanced file reading with validation."""
    
    def test_read_source_with_validation_success(self):
        """Test that read_source now includes validation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def test(): return True"
            f.write(test_content)
            temp_path = f.name
        
        try:
            content, source_id = read_source(temp_path)
            assert content == test_content
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_read_source_directory_error(self):
        """Test that read_source rejects directory paths."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            with pytest.raises(IsADirectoryError):
                read_source(temp_dir)
        finally:
            os.rmdir(temp_dir)
    
    def test_read_source_file_too_large(self):
        """Test that read_source rejects overly large files."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_path = Path(f.name)
        
        try:
            # Mock the file size limit to be very small
            with patch('shadow_ai.parser.MAX_FILE_SIZE_BYTES', 100):
                # Write content that exceeds the mock limit
                with open(temp_path, 'w') as f:
                    f.write('x' * 200)  # Exceeds the 100-byte limit
                
                with pytest.raises(FileTooLargeError):
                    read_source(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_read_source_string_validation(self):
        """Test that read_source validates string input."""
        # Valid string should work
        valid_code = "def hello(): pass"
        content, source_id = read_source(valid_code)
        assert content == valid_code
        assert source_id == 'raw_string'
        
        # Empty string should fail
        with pytest.raises(InvalidInputError):
            read_source("")
        
        # String with null bytes should fail
        with pytest.raises(InvalidInputError):
            read_source("def hello():\x00 pass")
    
    def test_read_source_with_language_validation(self):
        """Test that read_source_with_language includes validation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def test(): return True"
            f.write(test_content)
            temp_path = f.name
        
        try:
            content, language, source_id = read_source_with_language(temp_path)
            assert content == test_content
            assert language == 'Python'
            assert source_id == temp_path
        finally:
            os.unlink(temp_path)
        
        # Test validation errors are propagated
        temp_dir = tempfile.mkdtemp()
        try:
            with pytest.raises(IsADirectoryError):
                read_source_with_language(temp_dir)
        finally:
            os.rmdir(temp_dir)


class TestParserExceptions:
    """Test custom parser exceptions."""
    
    def test_parser_error_hierarchy(self):
        """Test that custom exceptions inherit from ParserError."""
        assert issubclass(FileTooLargeError, ParserError)
        assert issubclass(InvalidInputError, ParserError)
        assert issubclass(UnsupportedFileTypeError, ParserError)
    
    def test_file_too_large_error_message(self):
        """Test FileTooLargeError message formatting."""
        error = FileTooLargeError("Test file too large")
        assert "Test file too large" in str(error)
    
    def test_invalid_input_error_message(self):
        """Test InvalidInputError message formatting."""
        error = InvalidInputError("Test invalid input")
        assert "Test invalid input" in str(error)


class TestErrorScenarios:
    """Test error handling and edge cases."""
    
    def test_read_source_nonexistent_file_as_string(self):
        """Test that a non-existent file path is treated as raw string."""
        fake_path = "/this/path/does/not/exist.py"
        content, source_id = read_source(fake_path)
        
        assert content == fake_path
        assert source_id == 'raw_string'
    
    def test_language_mapper_edge_cases(self):
        """Test LanguageMapper with edge case inputs."""
        # Empty string
        assert LanguageMapper.get_language('') == 'plaintext'
        
        # Just extension (no basename) - this should be plaintext
        assert LanguageMapper.get_language('.py') == 'plaintext'
        
        # Multiple dots
        assert LanguageMapper.get_language('file.test.py') == 'Python'
        
        # Path objects
        assert LanguageMapper.get_language(Path('test.js')) == 'JavaScript'


class TestBatchProcessing:
    """Test batch directory processing functionality."""
    
    def create_test_directory_with_files(self, num_code_files=5, num_non_code_files=2):
        """Helper method to create a test directory with various files."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create code files
        code_files = [
            ('app.py', 'def main():\n    print("Hello from Python")'),
            ('server.js', 'console.log("Hello from JavaScript");'),
            ('main.go', 'package main\nfunc main() {\n    fmt.Println("Hello from Go")\n}'),
            ('component.tsx', 'const Component = () => <div>Hello from TypeScript</div>;'),
            ('style.css', 'body { color: blue; }'),
            ('config.json', '{"name": "test", "version": "1.0.0"}'),
            ('script.sh', '#!/bin/bash\necho "Hello from Shell"'),
        ]
        
        # Create the requested number of code files
        for i in range(min(num_code_files, len(code_files))):
            filename, content = code_files[i]
            (temp_dir / filename).write_text(content)
        
        # Create non-code files
        non_code_files = [
            ('README.md', '# Test Project\nThis is a test.'),
            ('notes.txt', 'Some random notes here.'),
            ('image.png', 'fake binary content'),
        ]
        
        for i in range(min(num_non_code_files, len(non_code_files))):
            filename, content = non_code_files[i]
            (temp_dir / filename).write_text(content)
        
        return temp_dir
    
    def test_parse_directory_success(self):
        """Test successful directory parsing with mixed file types."""
        test_dir = self.create_test_directory_with_files(3, 2)
        
        try:
            results = parse_directory(test_dir, max_files=5)
            
            # Should get all 3 code files (ignoring non-code files)
            assert len(results) == 3
            
            # Check structure of results
            for result in results:
                assert 'content' in result
                assert 'language' in result
                assert 'source' in result
                assert isinstance(result['content'], str)
                assert isinstance(result['language'], str)
                assert isinstance(result['source'], str)
                assert len(result['content']) > 0
            
            # Check that files are processed in alphabetical order
            sources = [result['source'] for result in results]
            filenames = [Path(source).name for source in sources]
            assert filenames == sorted(filenames)
            
        finally:
            # Clean up
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()
    
    def test_parse_directory_max_files_limit(self):
        """Test that max_files limit is respected."""
        test_dir = self.create_test_directory_with_files(7, 2)
        
        try:
            # Request only 3 files from a directory with 7 code files
            results = parse_directory(test_dir, max_files=3)
            assert len(results) == 3
            
            # Request more files than available
            results = parse_directory(test_dir, max_files=10)
            assert len(results) == 7  # Only 7 code files exist
            
        finally:
            # Clean up
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()
    
    def test_parse_directory_empty_directory(self):
        """Test parsing an empty directory."""
        test_dir = Path(tempfile.mkdtemp())
        
        try:
            results = parse_directory(test_dir)
            assert results == []
        finally:
            test_dir.rmdir()
    
    def test_parse_directory_no_code_files(self):
        """Test parsing a directory with no code files."""
        test_dir = self.create_test_directory_with_files(0, 3)
        
        try:
            results = parse_directory(test_dir)
            assert results == []
        finally:
            # Clean up
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()
    
    def test_parse_directory_validation_errors(self):
        """Test directory parsing validation errors."""
        # Test with non-existent directory
        fake_dir = Path("/this/path/does/not/exist")
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            parse_directory(fake_dir)
        
        # Test with invalid max_files
        test_dir = Path(tempfile.mkdtemp())
        try:
            with pytest.raises(InvalidInputError, match="max_files must be positive"):
                parse_directory(test_dir, max_files=0)
            
            with pytest.raises(InvalidInputError, match="max_files must be positive"):
                parse_directory(test_dir, max_files=-1)
        finally:
            test_dir.rmdir()
        
        # Test with file path instead of directory
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as f:
            f.write(b"print('hello')")
            temp_file = Path(f.name)
        
        try:
            with pytest.raises(NotADirectoryError, match="not a directory"):
                parse_directory(temp_file)
        finally:
            temp_file.unlink()
    
    def test_parse_directory_permission_denied(self):
        """Test directory parsing with permission errors."""
        test_dir = Path(tempfile.mkdtemp())
        
        try:
            # Mock os.access to simulate permission denied
            with patch('os.access', return_value=False):
                with pytest.raises(PermissionError, match="permission denied"):
                    parse_directory(test_dir)
        finally:
            test_dir.rmdir()
    
    def test_parse_directory_skip_problematic_files(self):
        """Test that problematic files are skipped gracefully."""
        test_dir = self.create_test_directory_with_files(2, 0)
        
        # Create a file that will cause an error (mock it to be too large)
        large_file = test_dir / "large.py"
        large_file.write_text("print('hello')")
        
        try:
            # Mock file size validation to fail for large.py
            original_validate = validate_file_input
            def mock_validate(file_path):
                if file_path.name == "large.py":
                    raise FileTooLargeError("File too large")
                return original_validate(file_path)
            
            with patch('shadow_ai.parser.validate_file_input', side_effect=mock_validate):
                results = parse_directory(test_dir)
                # Should get 2 files (skipping the problematic one)
                assert len(results) == 2
                
                # Verify the problematic file is not in results
                sources = [Path(result['source']).name for result in results]
                assert "large.py" not in sources
        
        finally:
            # Clean up
            for file in test_dir.iterdir():
                file.unlink()
            test_dir.rmdir()


class TestDirectoryStats:
    """Test directory statistics functionality."""
    
    def test_get_directory_stats_mixed_files(self):
        """Test directory statistics with mixed file types."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create various files
        files_to_create = [
            ('app.py', 'print("hello")'),
            ('server.js', 'console.log("hello")'),
            ('main.go', 'package main'),
            ('README.md', '# Project'),
            ('data.txt', 'some data'),
            ('style.css', 'body {}'),
        ]
        
        for filename, content in files_to_create:
            (temp_dir / filename).write_text(content)
        
        try:
            stats = get_directory_stats(temp_dir)
            
            assert stats['total_files'] == 6
            assert stats['code_files'] == 4  # .py, .js, .go, .css
            
            expected_languages = {
                'Python': 1,
                'JavaScript': 1, 
                'Go': 1,
                'CSS': 1
            }
            assert stats['languages'] == expected_languages
            
        finally:
            # Clean up
            for file in temp_dir.iterdir():
                file.unlink()
            temp_dir.rmdir()
    
    def test_get_directory_stats_empty_directory(self):
        """Test directory statistics for empty directory."""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            stats = get_directory_stats(temp_dir)
            
            assert stats['total_files'] == 0
            assert stats['code_files'] == 0
            assert stats['languages'] == {}
            
        finally:
            temp_dir.rmdir()
    
    def test_get_directory_stats_validation_errors(self):
        """Test directory statistics validation errors."""
        # Test with non-existent directory
        fake_dir = Path("/this/path/does/not/exist")
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            get_directory_stats(fake_dir)
        
        # Test with file path instead of directory
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as f:
            f.write(b"print('hello')")
            temp_file = Path(f.name)
        
        try:
            with pytest.raises(NotADirectoryError, match="not a directory"):
                get_directory_stats(temp_file)
        finally:
            temp_file.unlink()
    
    def test_get_directory_stats_permission_denied(self):
        """Test directory statistics with permission errors."""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Mock os.access to simulate permission denied
            with patch('os.access', return_value=False):
                with pytest.raises(PermissionError, match="cannot be read"):
                    get_directory_stats(temp_dir)
        finally:
            temp_dir.rmdir()


class TestErrorScenarios:
    """Test error handling and edge cases."""
    
    def test_read_source_nonexistent_file_as_string(self):
        """Test that a non-existent file path is treated as raw string."""
        fake_path = "/this/path/does/not/exist.py"
        content, source_id = read_source(fake_path)
        
        assert content == fake_path
        assert source_id == 'raw_string'
    
    def test_language_mapper_edge_cases(self):
        """Test LanguageMapper with edge case inputs."""
        # Empty string
        assert LanguageMapper.get_language('') == 'plaintext'
        
        # Just extension (no basename) - this should be plaintext
        assert LanguageMapper.get_language('.py') == 'plaintext'
        
        # Multiple dots
        assert LanguageMapper.get_language('file.test.py') == 'Python'
        
        # Path objects
        assert LanguageMapper.get_language(Path('test.js')) == 'JavaScript'

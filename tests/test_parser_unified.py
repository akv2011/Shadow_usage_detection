"""
Tests for the Unified Parser Interface

This test suite validates the main parse() and parse_with_stats() functions
that provide a unified interface for all input types (files, directories, strings).

Author: Shadow AI Detection Tool
Created: 2025-08-04
"""

import os
import tempfile
from pathlib import Path

import pytest

from shadow_ai.parser import parse, parse_with_stats, InvalidInputError


class TestUnifiedParserInterface:
    """Test the unified parser interface functionality."""
    
    def test_parse_single_file(self):
        """Test parsing a single file through unified interface."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def hello():\n    return 'Hello, World!'"
            f.write(test_content)
            temp_path = f.name
        
        try:
            results = parse(temp_path)
            
            # Should return a list with one item
            assert len(results) == 1
            
            result = results[0]
            assert result['content'] == test_content
            assert result['language'] == 'Python'
            assert result['source'] == temp_path
            
            # Check metadata
            assert 'metadata' in result
            metadata = result['metadata']
            assert metadata['input_type'] == 'file'
            assert metadata['file_size'] > 0
            assert metadata['file_extension'] == '.py'
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_directory(self):
        """Test parsing a directory through unified interface."""
        # Create test directory with files
        temp_dir = Path(tempfile.mkdtemp())
        
        test_files = [
            ('app.py', 'print("Python app")'),
            ('server.js', 'console.log("JavaScript server");'),
            ('README.md', '# Not a code file'),
        ]
        
        for filename, content in test_files:
            (temp_dir / filename).write_text(content)
        
        try:
            results = parse(temp_dir, max_files=10)
            
            # Should return 2 code files (excluding README.md)
            assert len(results) == 2
            
            # Check that all results have proper structure
            for result in results:
                assert 'content' in result
                assert 'language' in result
                assert 'source' in result
                assert 'metadata' in result
                
                metadata = result['metadata']
                assert metadata['input_type'] == 'directory_batch'
                assert metadata['directory'] == str(temp_dir)
                assert 'file_size' in metadata
                assert 'file_extension' in metadata
            
            # Verify specific languages are detected
            languages = {result['language'] for result in results}
            assert 'Python' in languages
            assert 'JavaScript' in languages
            
        finally:
            # Clean up
            for file in temp_dir.iterdir():
                file.unlink()
            temp_dir.rmdir()
    
    def test_parse_raw_string(self):
        """Test parsing raw string through unified interface."""
        test_code = "function greet(name) {\n    return `Hello, ${name}!`;\n}"
        
        results = parse(test_code)
        
        # Should return a list with one item
        assert len(results) == 1
        
        result = results[0]
        assert result['content'] == test_code
        assert result['language'] == 'plaintext'  # Raw strings default to plaintext
        assert result['source'] == 'raw_string'
        
        # Check metadata
        metadata = result['metadata']
        assert metadata['input_type'] == 'raw_string'
        assert metadata['content_length'] == len(test_code)
        assert metadata['estimated_lines'] == 3  # 2 newlines + 1
    
    def test_parse_empty_string(self):
        """Test parsing empty string through unified interface."""
        with pytest.raises(InvalidInputError, match="cannot be empty"):
            parse("")
    
    def test_parse_nonexistent_path_as_string(self):
        """Test that non-existent paths are treated as raw strings."""
        fake_path = "/definitely/not/a/real/path.py"
        
        results = parse(fake_path)
        
        assert len(results) == 1
        result = results[0]
        assert result['content'] == fake_path
        assert result['language'] == 'plaintext'
        assert result['source'] == 'raw_string'
        assert result['metadata']['input_type'] == 'raw_string'
    
    def test_parse_directory_max_files_limit(self):
        """Test that max_files parameter is respected in directory parsing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create 5 code files
        for i in range(5):
            (temp_dir / f"file{i}.py").write_text(f"print('File {i}')")
        
        try:
            # Request only 3 files
            results = parse(temp_dir, max_files=3)
            assert len(results) == 3
            
            # Verify metadata shows correct limit
            for result in results:
                # This is processed via parse_directory, so metadata is added there
                assert result['metadata']['input_type'] == 'directory_batch'
            
        finally:
            # Clean up
            for file in temp_dir.iterdir():
                file.unlink()
            temp_dir.rmdir()
    
    def test_parse_validation_errors(self):
        """Test that validation errors are properly propagated."""
        # Test with file that is actually a directory
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Parse should detect it's a directory and handle it correctly
            results = parse(temp_dir)
            assert isinstance(results, list)  # Should work as directory parsing
            
        finally:
            temp_dir.rmdir()


class TestParseWithStats:
    """Test the enhanced parser interface with statistics."""
    
    def test_parse_with_stats_single_file(self):
        """Test parse_with_stats with a single file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            test_content = "def test():\n    pass"
            f.write(test_content)
            temp_path = f.name
        
        try:
            response = parse_with_stats(temp_path)
            
            # Check response structure
            assert 'results' in response
            assert 'stats' in response
            assert 'summary' in response
            
            # Check results (same as parse())
            results = response['results']
            assert len(results) == 1
            assert results[0]['content'] == test_content
            
            # Check stats
            stats = response['stats']
            assert stats['input_type'] == 'file'
            assert stats['files_processed'] == 1
            assert stats['total_content_length'] == len(test_content)
            assert 'Python' in stats['languages_found']
            assert 'processing_time_seconds' in stats
            assert stats['processing_time_seconds'] > 0
            
            # Check summary
            assert isinstance(response['summary'], str)
            assert 'Processed single file' in response['summary']
            assert 'Python' in response['summary']
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_with_stats_directory(self):
        """Test parse_with_stats with a directory."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create test files
        (temp_dir / 'app.py').write_text('print("hello")')
        (temp_dir / 'script.js').write_text('console.log("hello");')
        
        try:
            response = parse_with_stats(temp_dir)
            
            # Check basic structure
            assert 'results' in response
            assert 'stats' in response
            assert 'summary' in response
            
            # Check stats for directory
            stats = response['stats']
            assert stats['input_type'] == 'directory'
            assert stats['files_processed'] == 2
            assert stats['total_content_length'] > 0
            assert set(stats['languages_found']) == {'JavaScript', 'Python'}
            
            # Check summary mentions directory
            assert 'directory' in response['summary'].lower()
            assert 'Python' in response['summary']
            assert 'JavaScript' in response['summary']
            
        finally:
            # Clean up
            for file in temp_dir.iterdir():
                file.unlink()
            temp_dir.rmdir()
    
    def test_parse_with_stats_raw_string(self):
        """Test parse_with_stats with raw string input."""
        test_code = "const x = 42;\nconsole.log(x);"
        
        response = parse_with_stats(test_code)
        
        # Check stats for raw string
        stats = response['stats']
        assert stats['input_type'] == 'raw_string'
        assert stats['files_processed'] == 1
        assert stats['total_content_length'] == len(test_code)
        assert 'plaintext' in stats['languages_found']
        
        # Check summary
        assert 'raw string' in response['summary'].lower()
        assert str(len(test_code)) in response['summary']
    
    def test_parse_with_stats_empty_directory(self):
        """Test parse_with_stats with empty directory."""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            response = parse_with_stats(temp_dir)
            
            stats = response['stats']
            assert stats['input_type'] == 'directory'
            assert stats['files_processed'] == 0
            assert stats['total_content_length'] == 0
            assert stats['languages_found'] == []
            
            assert 'Processed 0 files' in response['summary']
            
        finally:
            temp_dir.rmdir()
    
    def test_parse_with_stats_performance_tracking(self):
        """Test that performance metrics are captured."""
        test_code = "print('Performance test')"
        
        response = parse_with_stats(test_code)
        
        stats = response['stats']
        assert 'processing_time_seconds' in stats
        assert isinstance(stats['processing_time_seconds'], (int, float))
        assert stats['processing_time_seconds'] >= 0
        
        # Processing time should be reasonable (less than 1 second for simple string)
        assert stats['processing_time_seconds'] < 1.0

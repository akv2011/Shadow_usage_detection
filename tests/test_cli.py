"""
Tests for the CLI module.

Tests the command-line interface functionality including analyze, check, and scan commands.
"""

import pytest
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from pathlib import Path

from shadow_ai.cli import main, create_parser, format_analysis_results


class TestCLIParser:
    """Test CLI argument parsing."""

    def test_parser_creation(self):
        """Test that the argument parser is created correctly."""
        parser = create_parser()
        assert parser.prog == 'shadow-detect'
        assert 'Shadow AI Detection Tool' in parser.description

    def test_analyze_command_parsing(self):
        """Test parsing of analyze command."""
        parser = create_parser()
        args = parser.parse_args(['analyze', 'test.py'])
        assert args.command == 'analyze'
        assert args.file == 'test.py'

    def test_check_command_parsing(self):
        """Test parsing of check command."""
        parser = create_parser()
        args = parser.parse_args(['check', '--text', 'def test(): pass'])
        assert args.command == 'check'
        assert args.text == 'def test(): pass'

    def test_scan_command_parsing(self):
        """Test parsing of scan command."""
        parser = create_parser()
        args = parser.parse_args(['scan', '/path/to/dir', '--max-files', '10'])
        assert args.command == 'scan'
        assert args.directory == '/path/to/dir'
        assert args.max_files == 10


class TestCLIFormatting:
    """Test CLI output formatting."""

    def test_format_empty_results(self):
        """Test formatting of empty results."""
        result = format_analysis_results([])
        assert result == "No results to display."

    def test_format_single_result(self):
        """Test formatting of a single analysis result."""
        mock_result = {
            'source': 'test.py',
            'language': 'Python',
            'analysis': {
                'summary': {
                    'overall_suspicion_score': 50.0,
                    'risk_factors': ['High comment ratio', 'Generic variables']
                }
            }
        }
        result = format_analysis_results([mock_result])
        assert 'test.py' in result
        assert 'Python' in result
        assert 'Possibly AI-Generated' in result  # Result for 50% score
        assert '50.0%' in result

    def test_format_low_risk_result(self):
        """Test formatting of low risk result."""
        mock_result = {
            'source': 'test.py',
            'language': 'Python',
            'analysis': {
                'summary': {
                    'overall_suspicion_score': 20.0,
                    'risk_factors': []
                }
            }
        }
        result = format_analysis_results([mock_result])
        assert 'Likely Human-Written' in result
        assert 'No significant AI patterns detected' in result

    def test_format_high_risk_result(self):
        """Test formatting of high risk result."""
        mock_result = {
            'source': 'test.py',
            'language': 'Python',
            'analysis': {
                'summary': {
                    'overall_suspicion_score': 80.0,
                    'risk_factors': ['Multiple AI patterns']
                }
            }
        }
        result = format_analysis_results([mock_result])
        assert 'Likely AI-Generated' in result
        assert 'Multiple AI patterns' in result


class TestCLIIntegration:
    """Test CLI integration with engine and parser."""

    @patch('shadow_ai.cli.parse')
    @patch('shadow_ai.cli.analyze')
    def test_check_text_success(self, mock_analyze, mock_parse):
        """Test successful text analysis."""
        # Mock the parse function
        mock_parse.return_value = [{
            'content': 'def test(): pass',
            'language': 'python',
            'source': 'raw_string'
        }]
        
        # Mock the analyze function
        mock_analyze.return_value = {
            'summary': {
                'overall_suspicion_score': 30.0,
                'risk_factors': ['Test risk']
            }
        }
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('sys.argv', ['shadow-detect', 'check', '--text', 'def test(): pass']):
                result = main()
        
        assert result == 0
        output = mock_stdout.getvalue()
        assert 'raw_string' in output
        assert '30.0%' in output

    @patch('shadow_ai.cli.parse')
    def test_check_text_invalid_input(self, mock_parse):
        """Test text analysis with invalid input."""
        from shadow_ai.parser import InvalidInputError
        mock_parse.side_effect = InvalidInputError("Invalid input")
        
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            with patch('sys.argv', ['shadow-detect', 'check', '--text', '']):
                result = main()
        
        assert result == 1
        error_output = mock_stderr.getvalue()
        assert 'Invalid input' in error_output


class TestCLIMain:
    """Test main CLI entry point."""

    def test_main_no_command(self):
        """Test main function with no command."""
        with patch('sys.argv', ['shadow-detect']):
            with patch('sys.stdout', new_callable=StringIO):
                result = main()
        assert result == 1

    def test_main_keyboard_interrupt(self):
        """Test main function handling keyboard interrupt."""
        with patch('shadow_ai.cli.analyze_single_file') as mock_analyze:
            mock_analyze.side_effect = KeyboardInterrupt()
            with patch('sys.argv', ['shadow-detect', 'analyze', 'test.py']):
                with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    result = main()
            
            assert result == 1
            error_output = mock_stderr.getvalue()
            assert 'Operation cancelled' in error_output
        # - shadow-ai analyze <file>
        # - shadow-ai batch <directory>
        # - shadow-ai --help
        # - shadow-ai --version
        assert True, "Future CLI commands test placeholder"


def test_click_dependency():
    """Test that Click is available for CLI implementation."""
    try:
        import click

        assert hasattr(click, "command"), "Click command decorator not available"
        assert hasattr(click, "option"), "Click option decorator not available"
    except ImportError:
        pytest.fail("Click dependency not available for CLI implementation")

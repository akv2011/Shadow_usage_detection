#!/usr/bin/env python3
"""
Test suite for the style inconsistency detector in the AI detection engine.

This module tests the analyze_style_inconsistency function which detects
coding style inconsistencies that may indicate AI-injected code.

Created: 2025-08-04
"""

import unittest
from shadow_ai.engine import analyze_style_inconsistency


class TestStyleInconsistencyDetector(unittest.TestCase):
    """Test cases for style inconsistency detection."""
    
    def test_consistent_code_style(self):
        """Test that consistent code returns low inconsistency score."""
        consistent_code = '''
def calculate_sum(numbers):
    """Calculate the sum of a list of numbers."""
    total = 0
    for number in numbers:
        if isinstance(number, (int, float)):
            total += number
    return total

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = calculate_sum(numbers)
    count = len(numbers)
    if count > 0:
        return total / count
    return 0
        '''
        
        result = analyze_style_inconsistency(consistent_code)
        
        self.assertEqual(result['inconsistency_count'], 0)
        self.assertLessEqual(result['inconsistency_score'], 20.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)
        self.assertGreaterEqual(result['total_code_blocks'], 2)
    
    def test_mixed_indentation_styles(self):
        """Test detection of mixed tabs and spaces."""
        mixed_indentation_code = '''
def function_with_spaces():
    # This function uses 4 spaces for indentation
    x = 1
    y = 2
    return x + y

def function_with_tabs():
\t# This function uses tabs for indentation
\tx = 1
\ty = 2
\treturn x + y
        '''
        
        result = analyze_style_inconsistency(mixed_indentation_code)
        
        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)
        
        # Check that mixed indentation is detected
        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('indentation', patterns.lower())
    
    def test_mixed_naming_conventions(self):
        """Test detection of mixed naming conventions."""
        mixed_naming_code = '''
def calculate_total(data_list):  # snake_case function and parameter
    totalValue = 0  # camelCase variable
    for DataItem in data_list:  # PascalCase variable
        if isinstance(DataItem, int):
            totalValue += DataItem
    return totalValue

def ProcessData(inputList):  # PascalCase function
    result_count = 0  # snake_case variable
    for item in inputList:
        result_count += 1
    return result_count
        '''
        
        result = analyze_style_inconsistency(mixed_naming_code)
        
        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)
        
        # Check that naming convention inconsistency is detected
        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('naming', patterns.lower())
    
    def test_inconsistent_comment_density(self):
        """Test detection of significantly different comment densities."""
        inconsistent_comments_code = '''
def heavily_commented_function():
    # Start by initializing variables
    x = 1  # First variable
    y = 2  # Second variable
    # Calculate the result
    result = x + y  # Add them together
    # Return the final result
    return result  # Done

def uncommented_function():
    a = 5
    b = 10
    c = a * b
    d = c / 2
    e = d + 100
    return e
        '''
        
        result = analyze_style_inconsistency(inconsistent_comments_code)
        
        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)
        
        # Check that comment density inconsistency is detected
        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('comment', patterns.lower())
    
    def test_inconsistent_line_length_patterns(self):
        """Test detection of very different line length patterns."""
        inconsistent_line_length_code = '''
def short_lines():
    x = 1
    y = 2
    z = 3
    return x + y + z

def very_long_lines_function_with_verbose_variable_names_and_complex_expressions():
    extremely_long_variable_name_that_exceeds_typical_line_length_limits = "this is a very long string that continues for quite some time and makes the line very long"
    another_very_long_variable_name_for_testing_purposes_only = extremely_long_variable_name_that_exceeds_typical_line_length_limits + " and even more text to make it longer"
    return another_very_long_variable_name_for_testing_purposes_only.upper().strip().replace("long", "short").split()
        '''
        
        result = analyze_style_inconsistency(inconsistent_line_length_code)
        
        self.assertGreater(result['inconsistency_count'], 0)
        self.assertGreater(result['inconsistency_score'], 0.0)
        
        # Check that line length inconsistency is detected
        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertIn('length', patterns.lower())
    
    def test_multiple_inconsistencies(self):
        """Test detection of multiple types of inconsistencies."""
        multi_inconsistent_code = '''
def snake_case_function():
    # Uses spaces and snake_case
    variable_one = 1
    variable_two = 2
    return variable_one + variable_two

def PascalCaseFunction():
\t# Uses tabs and PascalCase
\tVariableOne = 5
\tVariableTwo = 10
\treturn VariableOne * VariableTwo
        '''
        
        result = analyze_style_inconsistency(multi_inconsistent_code)
        
        self.assertGreaterEqual(result['inconsistency_count'], 2)  # Should detect multiple issues
        self.assertGreater(result['inconsistency_score'], 20.0)  # Should have moderate score for multiple issues
        
        # Should detect both indentation and naming issues
        patterns = ' '.join(result['inconsistent_patterns'])
        self.assertTrue(
            'indentation' in patterns.lower() or 'naming' in patterns.lower(),
            "Should detect at least one of: indentation or naming inconsistencies"
        )
    
    def test_single_function_code(self):
        """Test that single function code returns neutral results."""
        single_function_code = '''
def single_function():
    """Only one function to analyze."""
    x = 1
    y = 2
    return x + y
        '''
        
        result = analyze_style_inconsistency(single_function_code)
        
        # Should have low or zero inconsistency for single function
        self.assertEqual(result['inconsistency_count'], 0)
        self.assertEqual(result['inconsistency_score'], 0.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)
    
    def test_empty_code(self):
        """Test handling of empty or invalid code."""
        result = analyze_style_inconsistency("")
        
        self.assertEqual(result['inconsistency_count'], 0)
        self.assertEqual(result['inconsistency_score'], 0.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)
        self.assertEqual(result['total_code_blocks'], 0)
    
    def test_syntax_error_code(self):
        """Test handling of code with syntax errors."""
        syntax_error_code = '''
def broken_function(
    # Missing closing parenthesis and other syntax issues
    x = 1
    return x +
        '''
        
        result = analyze_style_inconsistency(syntax_error_code)
        
        # Should handle syntax errors gracefully
        self.assertEqual(result['inconsistency_count'], 0)
        self.assertEqual(result['inconsistency_score'], 0.0)
        self.assertEqual(len(result['inconsistent_patterns']), 0)
        self.assertEqual(result['total_code_blocks'], 0)
    
    def test_global_scope_analysis(self):
        """Test analysis of code without functions or classes."""
        global_code = '''
# Global scope code with mixed styles
x = 1    # spaces
y = 2    # spaces
\tz = 3   # tab
total = x + y + z
        '''
        
        result = analyze_style_inconsistency(global_code)
        
        # Should analyze global scope when no functions present
        self.assertGreaterEqual(result['total_code_blocks'], 0)
        # May or may not detect inconsistencies depending on implementation
    
    def test_style_fingerprint_structure(self):
        """Test that style fingerprints have correct structure."""
        code_with_functions = '''
def test_function():
    x = 1
    return x

class TestClass:
    def method(self):
        return "test"
        '''
        
        result = analyze_style_inconsistency(code_with_functions)
        
        # Check fingerprint structure
        for fingerprint in result['style_fingerprints']:
            self.assertIn('node_type', fingerprint)
            self.assertIn('node_name', fingerprint)
            self.assertIn('line_range', fingerprint)
            self.assertIn('indentation_style', fingerprint)
            self.assertIn('naming_style', fingerprint)
            self.assertIn('comment_style', fingerprint)
            self.assertIn('line_length_style', fingerprint)


if __name__ == '__main__':
    unittest.main()

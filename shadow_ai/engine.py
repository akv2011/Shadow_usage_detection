"""
Core heuristic detection engine for AI-generated code analysis.

This module contains the main logic for analyzing code snippets and detecting
patterns that may indicate AI generation. It includes various heuristic checks
such as comment pattern analysis, variable naming analysis, code structure
analysis, and AI language pattern matching.
"""

import re
import ast
from typing import Dict, List, Any, Union
from .scoring import ConfidenceScorer


def analyze_comment_patterns(code_string: str) -> Dict[str, Any]:
    """
    Analyze comments in a code snippet for patterns indicative of AI generation.
    
    This function looks for:
    - Generic, templated comment structures
    - High comment-to-code ratios
    - Overly simplistic or repetitive comments
    - Comments that follow predictable patterns
    
    Args:
        code_string (str): The source code to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing analysis results:
            - 'generic_comments': Count of generic comment patterns
            - 'comment_to_code_ratio': Ratio of comment lines to code lines
            - 'repetitive_patterns': Count of repetitive comment structures
            - 'total_comments': Total number of comments found
    """
    if not code_string or not isinstance(code_string, str):
        return {
            'generic_comments': 0,
            'comment_to_code_ratio': 0.0,
            'repetitive_patterns': 0,
            'total_comments': 0
        }
    
    lines = code_string.split('\n')
    
    # Patterns that indicate generic, AI-generated comments
    # These patterns look for overly simple, templated comment structures
    generic_comment_patterns = [
        r'#\s*Function\s+(to\s+)?\w+(\s+\w+){0,2}\s*$',     # "# Function to calculate sum" (short and generic)
        r'#\s*Variable\s+(to\s+)?\w+(\s+\w+){0,2}\s*$',     # "# Variable to store result" (short and generic)
        r'#\s*Initialize\s+\w+(\s+\w+){0,1}\s*$',           # "# Initialize variable" (short and generic)
        r'#\s*Create\s+(a\s+)?\w+(\s+\w+){0,1}\s*$',        # "# Create a list" (short and generic)
        r'#\s*Set\s+(the\s+)?\w+(\s+\w+){0,1}\s*$',         # "# Set the value" (short and generic)
        r'#\s*Define\s+(a\s+)?\w+(\s+\w+){0,1}\s*$',        # "# Define a function" (short and generic)
        r'#\s*Calculate\s+(the\s+)?\w+(\s+\w+){0,1}\s*$',   # "# Calculate the result" (short and generic)
        r'#\s*Process\s+(the\s+)?\w+(\s+\w+){0,1}\s*$',     # "# Process the data" (short and generic)
        r'#\s*Return\s+(the\s+)?\w+(\s+\w+){0,1}\s*$',      # "# Return the result" (short and generic)
        r'#\s*Check\s+(if\s+)?\w+(\s+\w+){0,1}\s*$',        # "# Check if condition" (short and generic)
        r'#\s*TODO:?\s*[A-Z][a-z]+(\s+\w+){0,1}\s*$',       # "# TODO: Implement" (short and generic)
        r'#\s*[A-Z][a-z]+\s+[a-z]+\s+here\s*$',            # "# Insert code here"
        r'#\s*Example\s*(code|usage)\s*$',                  # "# Example code"
        r'#\s*Sample\s*(code|data)\s*$',                    # "# Sample code"
    ]
    
    comment_lines = []
    code_lines = []
    generic_comment_count = 0
    
    # Analyze each line
    for line in lines:
        stripped_line = line.strip()
        
        if not stripped_line:  # Skip empty lines
            continue
            
        if stripped_line.startswith('#'):
            comment_lines.append(stripped_line)
            
            # Check for generic patterns
            for pattern in generic_comment_patterns:
                if re.search(pattern, stripped_line, re.IGNORECASE):
                    generic_comment_count += 1
                    break  # Count each comment only once
        
        elif not stripped_line.startswith('#') and stripped_line:
            code_lines.append(stripped_line)
    
    # Calculate comment-to-code ratio
    total_code_lines = len(code_lines)
    total_comment_lines = len(comment_lines)
    
    if total_code_lines > 0:
        comment_to_code_ratio = total_comment_lines / total_code_lines
    else:
        comment_to_code_ratio = 0.0 if total_comment_lines == 0 else float('inf')
    
    # Check for repetitive patterns
    repetitive_patterns = _count_repetitive_comment_patterns(comment_lines)
    
    return {
        'generic_comments': generic_comment_count,
        'comment_to_code_ratio': round(comment_to_code_ratio, 3),
        'repetitive_patterns': repetitive_patterns,
        'total_comments': total_comment_lines
    }


def _count_repetitive_comment_patterns(comment_lines: List[str]) -> int:
    """
    Count repetitive comment patterns that might indicate AI generation.
    
    Args:
        comment_lines (List[str]): List of comment lines to analyze
        
    Returns:
        int: Count of detected repetitive patterns
    """
    if len(comment_lines) < 2:
        return 0
    
    repetitive_count = 0
    
    # Look for comments that follow the same structure
    # (same word count and similar patterns)
    structure_counts = {}
    
    for comment in comment_lines:
        # Remove the # and strip whitespace
        clean_comment = comment.lstrip('#').strip()
        
        if not clean_comment:
            continue
        
        # Create a structure pattern (word count + first/last words)
        words = clean_comment.split()
        if len(words) >= 2:
            structure = f"{len(words)}:{words[0].lower()}:{words[-1].lower()}"
            structure_counts[structure] = structure_counts.get(structure, 0) + 1
    
    # Count structures that appear multiple times
    for count in structure_counts.values():
        if count >= 3:  # 3 or more similar comments suggest repetitive pattern
            repetitive_count += count
    
    return repetitive_count


def analyze_variable_names(code_string: str) -> Dict[str, Any]:
    """
    Analyze variable and function names for patterns indicative of AI generation.
    
    This function looks for:
    - Generic, non-descriptive variable names
    - Generic function names
    - High percentage of generic names vs descriptive names
    
    Args:
        code_string (str): The source code to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing analysis results:
            - 'generic_names_count': Count of generic names found
            - 'total_names_count': Total number of names extracted
            - 'generic_percentage': Percentage of names that are generic (0-100)
            - 'generic_names_found': List of actual generic names found
    """
    if not code_string or not isinstance(code_string, str):
        return {
            'generic_names_count': 0,
            'total_names_count': 0,
            'generic_percentage': 0.0,
            'generic_names_found': []
        }
    
    # Common generic names often used in AI-generated code
    generic_names = {
        # Generic variables
        'data', 'result', 'results', 'temp', 'tmp', 'item', 'items', 'value', 'values',
        'output', 'input', 'obj', 'object', 'var', 'variable', 'element', 'elements',
        'content', 'text', 'string', 'number', 'num', 'count', 'total', 'sum',
        'list', 'array', 'dict', 'dictionary', 'response', 'request', 'params',
        'config', 'settings', 'options', 'args', 'kwargs', 'info', 'details',
        
        # Generic function names
        'process', 'handle', 'manage', 'execute', 'run', 'perform', 'do_task',
        'get_data', 'set_data', 'process_data', 'handle_data', 'main_function',
        'helper', 'utility', 'calculate', 'compute', 'convert', 'transform',
        'validate', 'check', 'verify', 'parse', 'format', 'generate', 'create',
        'update', 'delete', 'add', 'remove', 'insert', 'fetch', 'retrieve',
        
        # Single letter variables (often AI-generated in examples)
        'i', 'j', 'k', 'x', 'y', 'z', 'a', 'b', 'c', 'n', 'm'
    }
    
    try:
        # Parse the code using AST
        tree = ast.parse(code_string)
    except SyntaxError:
        # If code has syntax errors, return neutral result
        return {
            'generic_names_count': 0,
            'total_names_count': 0,
            'generic_percentage': 0.0,
            'generic_names_found': []
        }
    
    # Extract all names from the AST
    all_names = set()
    generic_names_found = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            # Variable names
            all_names.add(node.id)
        elif isinstance(node, ast.FunctionDef):
            # Function names
            all_names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            # Class names (less likely to be generic, but we'll track them)
            all_names.add(node.name)
        elif isinstance(node, ast.arg):
            # Function arguments
            all_names.add(node.arg)
    
    # Filter out built-in names and common keywords
    builtin_names = {
        'True', 'False', 'None', 'self', 'cls', '__init__', '__main__',
        'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
        'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'max', 'min',
        'open', 'file', 'abs', 'round', 'sorted', 'reversed', 'type',
        'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr'
    }
    
    # Remove built-in names
    filtered_names = all_names - builtin_names
    
    # Check for generic names
    for name in filtered_names:
        if name.lower() in generic_names:
            generic_names_found.append(name)
    
    total_names_count = len(filtered_names)
    generic_names_count = len(generic_names_found)
    
    if total_names_count > 0:
        generic_percentage = round((generic_names_count / total_names_count) * 100, 2)
    else:
        generic_percentage = 0.0
    
    return {
        'generic_names_count': generic_names_count,
        'total_names_count': total_names_count,
        'generic_percentage': generic_percentage,
        'generic_names_found': generic_names_found
    }


def analyze_code_structure(code_string: str) -> Dict[str, Any]:
    """
    Analyze code structure using AST for patterns indicative of AI generation.
    
    This function looks for:
    - Overly uniform function lengths
    - Consistent nesting depths
    - Limited variety in AST node types
    - Simplistic control flow patterns
    - Repetitive structural patterns
    
    Args:
        code_string (str): The source code to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing analysis results:
            - 'function_length_variance': Variance in function lengths (lower = more uniform)
            - 'average_nesting_depth': Average nesting depth across functions
            - 'node_type_diversity': Number of unique AST node types used
            - 'control_flow_complexity': Complexity score based on control structures
            - 'structural_uniformity_score': Overall uniformity score (0-100, higher = more uniform)
            - 'total_functions': Total number of functions analyzed
    """
    if not code_string or not isinstance(code_string, str):
        return {
            'function_length_variance': 0.0,
            'average_nesting_depth': 0.0,
            'node_type_diversity': 0,
            'control_flow_complexity': 0.0,
            'structural_uniformity_score': 0.0,
            'total_functions': 0
        }
    
    try:
        # Parse the code using AST
        tree = ast.parse(code_string)
    except SyntaxError:
        # If code has syntax errors, return neutral result
        return {
            'function_length_variance': 0.0,
            'average_nesting_depth': 0.0,
            'node_type_diversity': 0,
            'control_flow_complexity': 0.0,
            'structural_uniformity_score': 0.0,
            'total_functions': 0
        }
    
    # Collect metrics
    function_lengths = []
    nesting_depths = []
    node_types = set()
    control_flow_nodes = 0
    total_nodes = 0
    
    # Analyze each function in the code
    for node in ast.walk(tree):
        # Count all node types for diversity analysis
        node_types.add(type(node).__name__)
        total_nodes += 1
        
        # Count control flow structures
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match)):
            control_flow_nodes += 1
        
        # Analyze function structures
        if isinstance(node, ast.FunctionDef):
            # Calculate function length (number of statements)
            func_length = len(node.body)
            function_lengths.append(func_length)
            
            # Calculate maximum nesting depth for this function
            max_depth = _calculate_max_nesting_depth(node)
            nesting_depths.append(max_depth)
    
    # Calculate metrics
    total_functions = len(function_lengths)
    
    # Function length variance (lower = more uniform/suspicious)
    if len(function_lengths) > 1:
        mean_length = sum(function_lengths) / len(function_lengths)
        variance = sum((x - mean_length) ** 2 for x in function_lengths) / len(function_lengths)
        function_length_variance = round(variance, 2)
    else:
        function_length_variance = 0.0
    
    # Average nesting depth
    if nesting_depths:
        average_nesting_depth = round(sum(nesting_depths) / len(nesting_depths), 2)
    else:
        average_nesting_depth = 0.0
    
    # Node type diversity (variety of AST constructs used)
    node_type_diversity = len(node_types)
    
    # Control flow complexity
    if total_nodes > 0:
        control_flow_complexity = round((control_flow_nodes / total_nodes) * 100, 2)
    else:
        control_flow_complexity = 0.0
    
    # Calculate structural uniformity score (0-100, higher = more uniform/suspicious)
    uniformity_score = _calculate_uniformity_score(
        function_length_variance, average_nesting_depth, 
        node_type_diversity, control_flow_complexity, total_functions
    )
    
    return {
        'function_length_variance': function_length_variance,
        'average_nesting_depth': average_nesting_depth,
        'node_type_diversity': node_type_diversity,
        'control_flow_complexity': control_flow_complexity,
        'structural_uniformity_score': uniformity_score,
        'total_functions': total_functions
    }


def _calculate_max_nesting_depth(node: ast.AST, current_depth: int = 0) -> int:
    """
    Calculate the maximum nesting depth within an AST node.
    
    Args:
        node (ast.AST): The AST node to analyze
        current_depth (int): Current depth in the traversal
        
    Returns:
        int: Maximum nesting depth found
    """
    max_depth = current_depth
    
    # Node types that increase nesting depth
    nesting_nodes = (
        ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler,
        ast.FunctionDef, ast.ClassDef, ast.AsyncWith, ast.AsyncFor
    )
    
    for child in ast.iter_child_nodes(node):
        if isinstance(child, nesting_nodes):
            child_depth = _calculate_max_nesting_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        else:
            child_depth = _calculate_max_nesting_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)
    
    return max_depth


def _calculate_uniformity_score(
    func_variance: float, avg_nesting: float, node_diversity: int, 
    control_complexity: float, total_functions: int
) -> float:
    """
    Calculate a structural uniformity score based on various metrics.
    
    Args:
        func_variance (float): Variance in function lengths
        avg_nesting (float): Average nesting depth
        node_diversity (int): Number of unique node types
        control_complexity (float): Control flow complexity percentage
        total_functions (int): Total number of functions
        
    Returns:
        float: Uniformity score (0-100, higher = more uniform/suspicious)
    """
    if total_functions == 0:
        return 0.0
    
    score = 0.0
    
    # Low function length variance suggests uniformity (AI-like)
    if func_variance < 2.0:
        score += 25.0
    elif func_variance < 5.0:
        score += 15.0
    elif func_variance < 10.0:
        score += 5.0
    
    # Very low or very high nesting can be suspicious
    if avg_nesting < 1.0:
        score += 20.0  # Too simple
    elif avg_nesting > 5.0:
        score += 10.0  # Potentially over-engineered by AI
    
    # Low node type diversity suggests simple, repetitive code
    if node_diversity < 10:
        score += 20.0
    elif node_diversity < 15:
        score += 10.0
    
    # Very low control flow complexity suggests overly simple code
    if control_complexity < 5.0:
        score += 15.0
    elif control_complexity < 10.0:
        score += 5.0
    
    # Multiple identical-length functions are suspicious
    if total_functions >= 3 and func_variance < 1.0:
        score += 20.0
    
    return round(min(score, 100.0), 2)


def match_ai_language_patterns(code_string: str) -> Dict[str, Any]:
    """
    Scan comments and docstrings for AI language patterns and conversational artifacts.
    
    This function looks for:
    - Direct AI self-references
    - Conversational phrases typical of AI responses
    - Disclaimers and limitations commonly mentioned by AI
    - Generic example/template language
    
    Args:
        code_string (str): The source code to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing analysis results:
            - 'ai_phrases_found': List of detected AI phrases
            - 'ai_phrase_count': Total number of AI phrases detected
            - 'conversational_indicators': Count of conversational patterns
            - 'disclaimer_patterns': Count of AI disclaimer/limitation patterns
            - 'confidence_level': Confidence that AI language is present (0-100)
    """
    if not code_string or not isinstance(code_string, str):
        return {
            'ai_phrases_found': [],
            'ai_phrase_count': 0,
            'conversational_indicators': 0,
            'disclaimer_patterns': 0,
            'confidence_level': 0.0
        }
    
    # Extract all comments and docstrings
    comment_text = _extract_comments_and_docstrings(code_string)
    
    if not comment_text:
        return {
            'ai_phrases_found': [],
            'ai_phrase_count': 0,
            'conversational_indicators': 0,
            'disclaimer_patterns': 0,
            'confidence_level': 0.0
        }
    
    # Combine all text for analysis
    all_text = ' '.join(comment_text).lower()
    
    # Define AI language patterns
    ai_self_references = [
        r'\bas an ai\b',
        r'\bai language model\b',
        r'\bai assistant\b',
        r'\bi am an ai\b',
        r'\bi\'m an ai\b',
        r'\bchatgpt\b',
        r'\bgpt-\d+\b',
        r'\bclaude\b(?!\s+\w+\s+\w+)',  # Claude but not "Claude Shannon algorithm"
        r'\bcopilot\b(?!\s+\w+\s+\w+)', # GitHub Copilot but not "autopilot system"
        r'\bgemini\b(?!\s+\w+\s+\w+)',  # Google Gemini but not "Gemini constellation"
        r'\blanguage model\b',
        r'\bneural network\b(?!\s+implementation)',  # AI reference, not implementation
    ]
    
    conversational_patterns = [
        r'\bhere\'s\s+(?:an?\s+)?example\b',
        r'\bhere\s+is\s+(?:an?\s+)?example\b',
        r'\blet me\s+(?:help|show|explain|provide)\b',
        r'\bi\'ll\s+(?:help|show|explain|provide|create|write)\b',
        r'\byou\s+can\s+(?:use|try|modify|adapt)\b',
        r'\bfeel\s+free\s+to\b',
        r'\bhope\s+this\s+helps\b',
        r'\blet\s+me\s+know\s+if\b',
        r'\bif\s+you\s+(?:need|want|have)\b',
        r'\bplease\s+(?:note|let\s+me\s+know|feel\s+free)\b',
        r'\bthis\s+(?:should|will|can)\s+(?:help|work|solve)\b',
        r'\byou\s+(?:might|may|should|could)\s+(?:want|need|consider)\b',
    ]
    
    disclaimer_patterns = [
        r'\bi\s+cannot\s+(?:access|provide|guarantee)\b',
        r'\bi\s+don\'t\s+have\s+(?:access|real-time|current)\b',
        r'\breal-time\s+(?:data|information)\b',
        r'\bcurrent\s+(?:date|time|year)\b(?!\s+implementation)',
        r'\bup-to-date\s+information\b',
        r'\bmay\s+(?:vary|change|differ)\s+(?:depending|based)\b',
        r'\bplease\s+(?:verify|check|confirm|update)\b',
        r'\bas\s+of\s+my\s+last\s+(?:update|training)\b',
        r'\bknowledge\s+cutoff\b',
        r'\btraining\s+data\b',
        r'\bmay\s+not\s+be\s+(?:accurate|current|up-to-date)\b',
        r'\bconsult\s+(?:official|latest|current)\s+documentation\b',
    ]
    
    example_template_patterns = [
        r'\bsample\s+(?:code|implementation|usage)\b',
        r'\bexample\s+(?:code|implementation|usage)\b',
        r'\bbasic\s+(?:example|template|implementation)\b',
        r'\bsimple\s+(?:example|template|implementation)\b',
        r'\btemplate\s+(?:for|code)\b',
        r'\bplaceholder\s+(?:for|code|text)\b',
        r'\breplace\s+(?:this|these)\s+(?:with|values)\b',
        r'\bmodify\s+(?:as|this)\s+(?:needed|per)\b',
        r'\badjust\s+(?:as|this)\s+(?:needed|required)\b',
        r'\bcustomize\s+(?:as|this)\s+(?:needed|required)\b',
    ]
    
    # Count matches for each category
    ai_phrases_found = []
    conversational_count = 0
    disclaimer_count = 0
    
    # Check AI self-references
    for pattern in ai_self_references:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        for match in matches:
            ai_phrases_found.append(match)
    
    # Check conversational patterns
    for pattern in conversational_patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            conversational_count += 1
            # Also add to ai_phrases_found for tracking
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                ai_phrases_found.append(match.group())
    
    # Check disclaimer patterns
    for pattern in disclaimer_patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            disclaimer_count += 1
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                ai_phrases_found.append(match.group())
    
    # Check example/template patterns
    for pattern in example_template_patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                ai_phrases_found.append(match.group())
    
    # Calculate confidence level
    confidence_level = _calculate_ai_language_confidence(
        len(ai_phrases_found), conversational_count, disclaimer_count, len(comment_text)
    )
    
    return {
        'ai_phrases_found': list(set(ai_phrases_found)),  # Remove duplicates
        'ai_phrase_count': len(ai_phrases_found),
        'conversational_indicators': conversational_count,
        'disclaimer_patterns': disclaimer_count,
        'confidence_level': confidence_level
    }


def _extract_comments_and_docstrings(code_string: str) -> List[str]:
    """
    Extract all comments and docstrings from code.
    
    Args:
        code_string (str): The source code to analyze
        
    Returns:
        List[str]: List of comment and docstring text
    """
    comments_and_docs = []
    
    # Extract line comments
    lines = code_string.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            comments_and_docs.append(stripped[1:].strip())
    
    # Extract docstrings using AST
    try:
        tree = ast.parse(code_string)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                # Check if the first statement is a docstring
                if (node.body and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    comments_and_docs.append(node.body[0].value.value)
            # Module-level docstrings
            elif isinstance(node, ast.Module):
                if (node.body and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    comments_and_docs.append(node.body[0].value.value)
    except SyntaxError:
        # If AST parsing fails, just use line comments
        pass
    
    return comments_and_docs


def _calculate_ai_language_confidence(
    total_phrases: int, conversational_count: int, disclaimer_count: int, total_comments: int
) -> float:
    """
    Calculate confidence level that AI language patterns are present.
    
    Args:
        total_phrases (int): Total number of AI phrases found
        conversational_count (int): Number of conversational patterns
        disclaimer_count (int): Number of disclaimer patterns
        total_comments (int): Total number of comments/docstrings
        
    Returns:
        float: Confidence level (0-100)
    """
    if total_phrases == 0:
        return 0.0
    
    confidence = 0.0
    
    # Direct AI references are very strong indicators
    ai_reference_score = min(total_phrases * 30, 70)
    confidence += ai_reference_score
    
    # Multiple conversational patterns increase confidence
    if conversational_count >= 3:
        confidence += 20
    elif conversational_count >= 2:
        confidence += 15
    elif conversational_count >= 1:
        confidence += 10
    
    # Disclaimer patterns are strong indicators
    if disclaimer_count >= 2:
        confidence += 15
    elif disclaimer_count >= 1:
        confidence += 10
    
    # Adjust for comment density
    if total_comments > 0:
        phrase_density = total_phrases / total_comments
        if phrase_density > 0.5:  # More than half of comments contain AI patterns
            confidence += 10
        elif phrase_density > 0.25:
            confidence += 5
    
    return round(min(confidence, 100.0), 2)


def analyze_style_inconsistency(code_string: str) -> Dict[str, Any]:
    """
    Analyze code for style inconsistencies that may indicate AI-injected content.
    
    This function creates 'style fingerprints' for different parts of the code
    (functions, classes) and compares them to detect significant variations in:
    - Indentation style (tabs vs spaces, different amounts)
    - Variable naming conventions (camelCase vs snake_case)
    - Comment density and style
    - Line length patterns
    
    Args:
        code_string (str): The source code to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing analysis results:
            - 'style_fingerprints': List of style fingerprints for each code block
            - 'inconsistency_count': Number of style inconsistencies detected
            - 'inconsistency_score': Score from 0-100 indicating style uniformity
            - 'inconsistent_patterns': List of specific inconsistencies found
            - 'total_code_blocks': Total number of analyzable code blocks
    """
    if not code_string or not isinstance(code_string, str):
        return {
            'style_fingerprints': [],
            'inconsistency_count': 0,
            'inconsistency_score': 0.0,
            'inconsistent_patterns': [],
            'total_code_blocks': 0
        }
    
    try:
        # Parse the code into an AST
        tree = ast.parse(code_string)
    except SyntaxError:
        # Return neutral results for invalid code
        return {
            'style_fingerprints': [],
            'inconsistency_count': 0,
            'inconsistency_score': 0.0,
            'inconsistent_patterns': [],
            'total_code_blocks': 0
        }
    
    lines = code_string.split('\n')
    style_fingerprints = []
    
    # Analyze each function and class for style patterns
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            fingerprint = _create_style_fingerprint(node, lines)
            if fingerprint:
                style_fingerprints.append(fingerprint)
    
    # If we don't have enough code blocks, analyze the global scope
    if len(style_fingerprints) < 2:
        global_fingerprint = _create_global_style_fingerprint(lines)
        if global_fingerprint and len(style_fingerprints) == 0:
            style_fingerprints.append(global_fingerprint)
    
    total_code_blocks = len(style_fingerprints)
    
    if total_code_blocks < 2:
        # Need at least 2 blocks to compare styles
        return {
            'style_fingerprints': style_fingerprints,
            'inconsistency_count': 0,
            'inconsistency_score': 0.0,
            'inconsistent_patterns': [],
            'total_code_blocks': total_code_blocks
        }
    
    # Compare style fingerprints to detect inconsistencies
    inconsistencies = _detect_style_inconsistencies(style_fingerprints)
    
    # Calculate inconsistency score (0-100, higher means more inconsistent)
    inconsistency_score = _calculate_style_inconsistency_score(inconsistencies, total_code_blocks)
    
    return {
        'style_fingerprints': style_fingerprints,
        'inconsistency_count': len(inconsistencies),
        'inconsistency_score': inconsistency_score,
        'inconsistent_patterns': inconsistencies,
        'total_code_blocks': total_code_blocks
    }


def _create_style_fingerprint(node: ast.AST, lines: List[str]) -> Dict[str, Any]:
    """
    Create a style fingerprint for a specific AST node (function or class).
    
    Args:
        node (ast.AST): The AST node to analyze
        lines (List[str]): All lines of the source code
        
    Returns:
        Dict[str, Any]: Style fingerprint containing various style metrics
    """
    if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
        return None
    
    start_line = node.lineno - 1  # Convert to 0-based indexing
    end_line = node.end_lineno if node.end_lineno else start_line + 1
    
    # Extract the lines for this code block
    if start_line >= len(lines) or end_line > len(lines):
        return None
    
    block_lines = lines[start_line:end_line]
    
    # Analyze indentation style
    indentation_style = _analyze_indentation_style(block_lines)
    
    # Analyze variable naming patterns
    naming_style = _analyze_naming_style(node)
    
    # Analyze comment patterns
    comment_style = _analyze_comment_style(block_lines)
    
    # Analyze line length patterns
    line_length_style = _analyze_line_length_style(block_lines)
    
    return {
        'node_type': type(node).__name__,
        'node_name': getattr(node, 'name', 'anonymous'),
        'line_range': (start_line + 1, end_line),
        'indentation_style': indentation_style,
        'naming_style': naming_style,
        'comment_style': comment_style,
        'line_length_style': line_length_style
    }


def _create_global_style_fingerprint(lines: List[str]) -> Dict[str, Any]:
    """
    Create a style fingerprint for the global scope when no functions/classes exist.
    
    Args:
        lines (List[str]): All lines of the source code
        
    Returns:
        Dict[str, Any]: Style fingerprint for global scope
    """
    # Use the entire file as one block
    indentation_style = _analyze_indentation_style(lines)
    comment_style = _analyze_comment_style(lines)
    line_length_style = _analyze_line_length_style(lines)
    
    return {
        'node_type': 'Global',
        'node_name': 'global_scope',
        'line_range': (1, len(lines)),
        'indentation_style': indentation_style,
        'naming_style': {'style': 'unknown', 'consistency': 1.0},
        'comment_style': comment_style,
        'line_length_style': line_length_style
    }


def _analyze_indentation_style(block_lines: List[str]) -> Dict[str, Any]:
    """
    Analyze indentation patterns in a code block.
    
    Args:
        block_lines (List[str]): Lines of code to analyze
        
    Returns:
        Dict[str, Any]: Indentation style analysis
    """
    tab_count = 0
    space_counts = {}
    total_indented_lines = 0
    
    for line in block_lines:
        if not line.strip():  # Skip empty lines
            continue
            
        # Count leading whitespace
        leading_chars = len(line) - len(line.lstrip())
        if leading_chars > 0:
            total_indented_lines += 1
            
            if line.startswith('\t'):
                tab_count += 1
            else:
                # Count spaces
                space_count = 0
                for char in line:
                    if char == ' ':
                        space_count += 1
                    else:
                        break
                
                if space_count > 0:
                    space_counts[space_count] = space_counts.get(space_count, 0) + 1
    
    # Determine primary style
    if total_indented_lines == 0:
        return {'style': 'none', 'consistency': 1.0, 'tab_count': 0, 'space_counts': {}}
    
    if tab_count > len(space_counts):
        primary_style = 'tabs'
        consistency = tab_count / total_indented_lines
    else:
        primary_style = 'spaces'
        if space_counts:
            most_common_spaces = max(space_counts.values())
            consistency = most_common_spaces / total_indented_lines
        else:
            consistency = 0.0
    
    return {
        'style': primary_style,
        'consistency': round(consistency, 3),
        'tab_count': tab_count,
        'space_counts': space_counts
    }


def _analyze_naming_style(node: ast.AST) -> Dict[str, Any]:
    """
    Analyze variable and function naming patterns in an AST node.
    
    Args:
        node (ast.AST): The AST node to analyze
        
    Returns:
        Dict[str, Any]: Naming style analysis
    """
    names = []
    
    # Extract variable and function names from the node
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            names.append(child.id)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if child != node:  # Don't include the current node's name twice
                names.append(child.name)
        elif isinstance(child, ast.arg):
            names.append(child.arg)
    
    if not names:
        return {'style': 'unknown', 'consistency': 1.0}
    
    # Analyze naming conventions
    snake_case_count = 0
    camel_case_count = 0
    pascal_case_count = 0
    
    for name in names:
        if '_' in name and name.islower():
            snake_case_count += 1
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            camel_case_count += 1
        elif name[0].isupper() and any(c.isupper() for c in name[1:]):
            pascal_case_count += 1
    
    total_names = len(names)
    
    # Determine primary style
    style_counts = {
        'snake_case': snake_case_count,
        'camelCase': camel_case_count,
        'PascalCase': pascal_case_count
    }
    
    primary_style = max(style_counts, key=style_counts.get)
    consistency = style_counts[primary_style] / total_names
    
    return {
        'style': primary_style,
        'consistency': round(consistency, 3)
    }


def _analyze_comment_style(block_lines: List[str]) -> Dict[str, Any]:
    """
    Analyze comment patterns in a code block.
    
    Args:
        block_lines (List[str]): Lines of code to analyze
        
    Returns:
        Dict[str, Any]: Comment style analysis
    """
    total_lines = len([line for line in block_lines if line.strip()])
    comment_lines = 0
    inline_comments = 0
    block_comments = 0
    
    for line in block_lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        if stripped.startswith('#'):
            comment_lines += 1
            block_comments += 1
        elif '#' in line:
            comment_lines += 1
            inline_comments += 1
    
    if total_lines == 0:
        comment_density = 0.0
    else:
        comment_density = comment_lines / total_lines
    
    return {
        'comment_density': round(comment_density, 3),
        'inline_comments': inline_comments,
        'block_comments': block_comments
    }


def _analyze_line_length_style(block_lines: List[str]) -> Dict[str, Any]:
    """
    Analyze line length patterns in a code block.
    
    Args:
        block_lines (List[str]): Lines of code to analyze
        
    Returns:
        Dict[str, Any]: Line length style analysis
    """
    non_empty_lines = [line for line in block_lines if line.strip()]
    
    if not non_empty_lines:
        return {'average_length': 0.0, 'max_length': 0, 'variance': 0.0}
    
    lengths = [len(line) for line in non_empty_lines]
    average_length = sum(lengths) / len(lengths)
    max_length = max(lengths)
    
    # Calculate variance
    variance = sum((length - average_length) ** 2 for length in lengths) / len(lengths)
    
    return {
        'average_length': round(average_length, 1),
        'max_length': max_length,
        'variance': round(variance, 1)
    }


def _detect_style_inconsistencies(style_fingerprints: List[Dict[str, Any]]) -> List[str]:
    """
    Compare style fingerprints to detect inconsistencies.
    
    Args:
        style_fingerprints (List[Dict[str, Any]]): List of style fingerprints to compare
        
    Returns:
        List[str]: List of detected inconsistencies
    """
    inconsistencies = []
    
    if len(style_fingerprints) < 2:
        return inconsistencies
    
    # Check indentation style consistency
    indentation_styles = [fp['indentation_style']['style'] for fp in style_fingerprints]
    unique_indentation_styles = set(indentation_styles)
    
    if len(unique_indentation_styles) > 1:
        inconsistencies.append(f"Mixed indentation styles: {', '.join(unique_indentation_styles)}")
    
    # Check naming style consistency
    naming_styles = [fp['naming_style']['style'] for fp in style_fingerprints]
    unique_naming_styles = set(naming_styles)
    
    if len(unique_naming_styles) > 1 and 'unknown' not in unique_naming_styles:
        inconsistencies.append(f"Mixed naming conventions: {', '.join(unique_naming_styles)}")
    
    # Check for significant differences in comment density
    comment_densities = [fp['comment_style']['comment_density'] for fp in style_fingerprints]
    if comment_densities:
        max_density = max(comment_densities)
        min_density = min(comment_densities)
        
        if max_density - min_density > 0.5:  # More than 50% difference
            inconsistencies.append(f"Inconsistent comment density: {min_density:.1f} to {max_density:.1f}")
    
    # Check for significant differences in line length patterns
    line_length_variances = [fp['line_length_style']['variance'] for fp in style_fingerprints]
    if line_length_variances:
        max_variance = max(line_length_variances)
        min_variance = min(line_length_variances)
        
        if max_variance > 0 and min_variance > 0:
            variance_ratio = max_variance / min_variance
            if variance_ratio > 3.0:  # One block has 3x more line length variance
                inconsistencies.append(f"Inconsistent line length patterns: variance ratio {variance_ratio:.1f}")
    
    return inconsistencies


def _calculate_style_inconsistency_score(inconsistencies: List[str], total_blocks: int) -> float:
    """
    Calculate a score representing the level of style inconsistency.
    
    Args:
        inconsistencies (List[str]): List of detected inconsistencies
        total_blocks (int): Total number of code blocks analyzed
        
    Returns:
        float: Inconsistency score from 0-100 (higher = more inconsistent)
    """
    if not inconsistencies or total_blocks < 2:
        return 0.0
    
    # Base score depends on number of inconsistencies
    base_score = len(inconsistencies) * 20
    
    # Adjust based on the number of code blocks
    # More blocks with inconsistencies is more suspicious
    block_factor = min(total_blocks / 3, 2.0)  # Cap at 2x multiplier
    
    final_score = base_score * block_factor
    
    return round(min(final_score, 100.0), 1)


def analyze(code_string: str) -> Dict[str, Any]:
    """
    Main orchestrator function that runs all heuristic checks on code.
    
    This function coordinates the execution of all individual heuristic analysis
    functions and aggregates their results into a comprehensive analysis report.
    
    Args:
        code_string (str): The source code to analyze
        
    Returns:
        Dict[str, Any]: Comprehensive analysis results containing:
            - 'comment_patterns': Results from comment pattern analysis
            - 'variable_names': Results from variable naming analysis  
            - 'code_structure': Results from code structure analysis
            - 'ai_language_patterns': Results from AI language pattern matching
            - 'summary': High-level summary statistics
            - 'analysis_metadata': Metadata about the analysis
    """
    if not code_string or not isinstance(code_string, str):
        # Return empty results for invalid input
        empty_result = {
            'comment_patterns': {
                'generic_comments': 0,
                'comment_to_code_ratio': 0.0,
                'repetitive_patterns': 0,
                'total_comments': 0
            },
            'variable_names': {
                'generic_names_count': 0,
                'total_names_count': 0,
                'generic_percentage': 0.0,
                'generic_names_found': []
            },
            'code_structure': {
                'function_length_variance': 0.0,
                'average_nesting_depth': 0.0,
                'node_type_diversity': 0,
                'control_flow_complexity': 0.0,
                'structural_uniformity_score': 0.0,
                'total_functions': 0
            },
            'ai_language_patterns': {
                'ai_phrases_found': [],
                'ai_phrase_count': 0,
                'conversational_indicators': 0,
                'disclaimer_patterns': 0,
                'confidence_level': 0.0
            },
            'style_inconsistency': {
                'style_fingerprints': [],
                'inconsistency_count': 0,
                'inconsistency_score': 0.0,
                'inconsistent_patterns': [],
                'total_code_blocks': 0
            },
            'summary': {
                'total_indicators': 0,
                'risk_factors': [],
                'overall_suspicion_score': 0.0
            },
            'analysis_metadata': {
                'code_length': 0,
                'analysis_timestamp': None,
                'heuristics_run': 5,
                'errors_encountered': []
            }
        }
        return empty_result
    
    # Track analysis metadata
    import datetime
    analysis_timestamp = datetime.datetime.now().isoformat()
    errors_encountered = []
    
    # Run each heuristic analysis
    try:
        comment_results = analyze_comment_patterns(code_string)
    except Exception as e:
        errors_encountered.append(f"Comment analysis error: {str(e)}")
        comment_results = {
            'generic_comments': 0,
            'comment_to_code_ratio': 0.0,
            'repetitive_patterns': 0,
            'total_comments': 0
        }
    
    try:
        variable_results = analyze_variable_names(code_string)
    except Exception as e:
        errors_encountered.append(f"Variable analysis error: {str(e)}")
        variable_results = {
            'generic_names_count': 0,
            'total_names_count': 0,
            'generic_percentage': 0.0,
            'generic_names_found': []
        }
    
    try:
        structure_results = analyze_code_structure(code_string)
    except Exception as e:
        errors_encountered.append(f"Structure analysis error: {str(e)}")
        structure_results = {
            'function_length_variance': 0.0,
            'average_nesting_depth': 0.0,
            'node_type_diversity': 0,
            'control_flow_complexity': 0.0,
            'structural_uniformity_score': 0.0,
            'total_functions': 0
        }
    
    try:
        ai_language_results = match_ai_language_patterns(code_string)
    except Exception as e:
        errors_encountered.append(f"AI language analysis error: {str(e)}")
        ai_language_results = {
            'ai_phrases_found': [],
            'ai_phrase_count': 0,
            'conversational_indicators': 0,
            'disclaimer_patterns': 0,
            'confidence_level': 0.0
        }

    try:
        style_results = analyze_style_inconsistency(code_string)
    except Exception as e:
        errors_encountered.append(f"Style analysis error: {str(e)}")
        style_results = {
            'style_fingerprints': [],
            'inconsistency_count': 0,
            'inconsistency_score': 0.0,
            'inconsistent_patterns': [],
            'total_code_blocks': 0
        }

    # Calculate summary statistics using the new sophisticated scoring system
    heuristic_results = {
        'comment_patterns': comment_results,
        'variable_names': variable_results,
        'code_structure': structure_results,
        'ai_language_patterns': ai_language_results,
        'style_inconsistency': style_results
    }    # Calculate basic metrics for backward compatibility
    total_indicators = 0
    risk_factors = []
    
    # Analyze comment patterns
    if comment_results['generic_comments'] > 0:
        risk_factors.append(f"Generic comments detected ({comment_results['generic_comments']})")
        total_indicators += comment_results['generic_comments']
    
    if comment_results['comment_to_code_ratio'] > 0.8:
        risk_factors.append(f"High comment-to-code ratio ({comment_results['comment_to_code_ratio']})")
        total_indicators += 1
    
    if comment_results['repetitive_patterns'] > 0:
        risk_factors.append(f"Repetitive comment patterns ({comment_results['repetitive_patterns']})")
        total_indicators += 1
    
    # Analyze variable naming
    if variable_results['generic_percentage'] > 50:
        risk_factors.append(f"High generic variable usage ({variable_results['generic_percentage']}%)")
        total_indicators += 1
    
    # Analyze code structure
    if structure_results['structural_uniformity_score'] > 60:
        risk_factors.append(f"High structural uniformity ({structure_results['structural_uniformity_score']})")
        total_indicators += 1
    
    if structure_results['function_length_variance'] < 2.0 and structure_results['total_functions'] > 1:
        risk_factors.append(f"Low function length variance ({structure_results['function_length_variance']})")
        total_indicators += 1
    
    # Analyze AI language patterns
    if ai_language_results['ai_phrase_count'] > 0:
        risk_factors.append(f"AI language phrases detected ({ai_language_results['ai_phrase_count']})")
        total_indicators += ai_language_results['ai_phrase_count']
    
    if ai_language_results['confidence_level'] > 50:
        risk_factors.append(f"High AI language confidence ({ai_language_results['confidence_level']}%)")
        total_indicators += 1
    
    # Analyze style inconsistency
    if style_results['inconsistency_score'] > 40:
        risk_factors.append(f"Style inconsistency detected ({style_results['inconsistency_score']})")
        total_indicators += 1
    
    if style_results['inconsistency_count'] > 0:
        patterns = ', '.join(style_results['inconsistent_patterns'][:2])  # Show first 2 patterns
        risk_factors.append(f"Style patterns: {patterns}")
        total_indicators += style_results['inconsistency_count']
    
    # Use the new confidence scoring system
    scoring_results = ConfidenceScorer.calculate_confidence_score(heuristic_results)
    
    # Create summary with both old and new scoring for compatibility
    summary = {
        'total_indicators': total_indicators,
        'risk_factors': risk_factors,
        'overall_suspicion_score': scoring_results['confidence_score'],
        'risk_level': scoring_results['risk_level'],
        'component_scores': scoring_results['component_scores'],
        'weighted_factors': scoring_results['weighted_factors']
    }
    
    # Prepare analysis metadata
    analysis_metadata = {
        'code_length': len(code_string),
        'analysis_timestamp': analysis_timestamp,
        'heuristics_run': 5,
        'errors_encountered': errors_encountered
    }
    
    # Aggregate all results
    comprehensive_results = {
        'comment_patterns': comment_results,
        'variable_names': variable_results,
        'code_structure': structure_results,
        'ai_language_patterns': ai_language_results,
        'style_inconsistency': style_results,
        'summary': summary,
        'analysis_metadata': analysis_metadata
    }
    
    return comprehensive_results


def _calculate_summary_statistics(
    comment_results: Dict[str, Any],
    variable_results: Dict[str, Any], 
    structure_results: Dict[str, Any],
    ai_language_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate high-level summary statistics from all heuristic results.
    
    Args:
        comment_results: Results from comment pattern analysis
        variable_results: Results from variable naming analysis
        structure_results: Results from code structure analysis
        ai_language_results: Results from AI language pattern matching
        
    Returns:
        Dict[str, Any]: Summary statistics including total indicators and risk factors
    """
    risk_factors = []
    total_indicators = 0
    
    # Analyze comment patterns
    if comment_results['generic_comments'] > 0:
        risk_factors.append(f"Generic comments detected ({comment_results['generic_comments']})")
        total_indicators += comment_results['generic_comments']
    
    if comment_results['comment_to_code_ratio'] > 0.8:
        risk_factors.append(f"High comment-to-code ratio ({comment_results['comment_to_code_ratio']})")
        total_indicators += 1
    
    if comment_results['repetitive_patterns'] > 0:
        risk_factors.append(f"Repetitive comment patterns ({comment_results['repetitive_patterns']})")
        total_indicators += 1
    
    # Analyze variable naming
    if variable_results['generic_percentage'] > 50:
        risk_factors.append(f"High generic variable usage ({variable_results['generic_percentage']}%)")
        total_indicators += 1
    
    # Analyze code structure
    if structure_results['structural_uniformity_score'] > 60:
        risk_factors.append(f"High structural uniformity ({structure_results['structural_uniformity_score']})")
        total_indicators += 1
    
    if structure_results['function_length_variance'] < 2.0 and structure_results['total_functions'] > 1:
        risk_factors.append(f"Low function length variance ({structure_results['function_length_variance']})")
        total_indicators += 1
    
    # Analyze AI language patterns
    if ai_language_results['ai_phrase_count'] > 0:
        risk_factors.append(f"AI language phrases detected ({ai_language_results['ai_phrase_count']})")
        total_indicators += ai_language_results['ai_phrase_count']
    
    if ai_language_results['confidence_level'] > 50:
        risk_factors.append(f"High AI language confidence ({ai_language_results['confidence_level']}%)")
        total_indicators += 1
    
    # Calculate overall suspicion score
    # This is a preliminary score; Task 8 will implement more sophisticated scoring
    suspicion_factors = [
        comment_results['generic_comments'] * 5,  # Weight generic comments heavily
        min(comment_results['comment_to_code_ratio'] * 20, 20),  # Cap at 20 points
        comment_results['repetitive_patterns'] * 3,
        variable_results['generic_percentage'] * 0.5,  # Convert percentage to points
        structure_results['structural_uniformity_score'] * 0.3,
        ai_language_results['confidence_level'] * 0.4
    ]
    
    overall_suspicion_score = round(min(sum(suspicion_factors), 100.0), 2)
    
    return {
        'total_indicators': total_indicators,
        'risk_factors': risk_factors,
        'overall_suspicion_score': overall_suspicion_score
    }

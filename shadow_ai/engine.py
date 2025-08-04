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
            'summary': {
                'total_indicators': 0,
                'risk_factors': [],
                'overall_suspicion_score': 0.0
            },
            'analysis_metadata': {
                'code_length': 0,
                'analysis_timestamp': None,
                'heuristics_run': 4,
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
    
    # Calculate summary statistics
    summary = _calculate_summary_statistics(
        comment_results, variable_results, structure_results, ai_language_results
    )
    
    # Prepare analysis metadata
    analysis_metadata = {
        'code_length': len(code_string),
        'analysis_timestamp': analysis_timestamp,
        'heuristics_run': 4,
        'errors_encountered': errors_encountered
    }
    
    # Aggregate all results
    comprehensive_results = {
        'comment_patterns': comment_results,
        'variable_names': variable_results,
        'code_structure': structure_results,
        'ai_language_patterns': ai_language_results,
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

"""
Shadow AI Detection Tool

A heuristic-based tool for detecting AI-generated code patterns.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main modules
from .engine import analyze
from .parser import parse
from .cli import main as cli_main

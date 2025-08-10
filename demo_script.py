#!/usr/bin/env python3
"""
Shadow AI Detection Tool - Complete Demo Script
Run this script to see all the features in action!
"""

import subprocess
import sys
import time
import os

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"🎯 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode == 0:
            print(f"Warning: {result.stderr}")
        if result.returncode != 0:
            print(f"Error (exit code {result.returncode}): {result.stderr}")
    except Exception as e:
        print(f"Failed to run command: {e}")
    
    input("\nPress Enter to continue...")

def main():
    print("""
🚀 Shadow AI Detection Tool - Complete Demo
==========================================

This demo will showcase:
1. CLI Analysis (files and text)
2. Web Interface setup
3. API functionality
4. Real-world examples

Let's get started!
    """)
    
    input("Press Enter to begin...")
    
    # Demo 1: Analyze AI-generated sample
    run_command(
        'python -m shadow_ai.cli analyze demo_samples/ai_generated_sample.py',
        "Demo 1: Analyzing AI-Generated Code Sample"
    )
    
    # Demo 2: Analyze human-written sample
    run_command(
        'python -m shadow_ai.cli analyze demo_samples/human_written_sample.py',
        "Demo 2: Analyzing Human-Written Code Sample"
    )
    
    # Demo 3: Text analysis with AI pattern
    ai_code = '''def calculate_sum(numbers):
    """
    Calculate the sum of a list of numbers.
    
    Args:
        numbers (list): A list of numbers to sum
        
    Returns:
        int: The sum of all numbers in the list
    """
    # Initialize result variable
    result = 0
    
    # Iterate through each number in the list
    for number in numbers:
        # Add the current number to the result
        result += number
    
    # Return the final result
    return result'''
    
    run_command(
        f'python -m shadow_ai.cli check --text "{ai_code}"',
        "Demo 3: Analyzing AI-Pattern Text (verbose comments)"
    )
    
    # Demo 4: Text analysis with human pattern
    human_code = '''def sum_nums(nums):
    return sum(nums)

def avg(data):
    return sum(data) / len(data) if data else 0'''
    
    run_command(
        f'python -m shadow_ai.cli check --text "{human_code}"',
        "Demo 4: Analyzing Human-Pattern Text (concise style)"
    )
    
    # Demo 5: Scan directory
    run_command(
        'python -m shadow_ai.cli scan shadow_ai/ --max-files 3',
        "Demo 5: Scanning Directory (Project Files)"
    )
    
    # Demo 6: Show help
    run_command(
        'python -m shadow_ai.cli --help',
        "Demo 6: CLI Help Documentation"
    )
    
    print(f"""
🎉 Demo Complete!

🌐 Next Steps - Web Interface:
==============================
1. Run: python main.py
2. Open browser to: http://localhost:8000
3. Try the interactive interface
4. Check the API docs at: http://localhost:8000/docs

🔧 Key Features Demonstrated:
============================
✅ File analysis with confidence scoring
✅ Text analysis for quick checks
✅ Directory scanning for batch processing
✅ Pattern detection (AI vs Human coding styles)
✅ Multi-language support

🎯 Business Applications:
========================
• Code review automation
• Educational tool for AI pattern recognition
• CI/CD integration for quality assurance
• Research into AI coding behaviors

Thanks for watching the demo! 🚀
    """)

if __name__ == "__main__":
    main()

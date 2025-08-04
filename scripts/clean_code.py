#!/usr/bin/env python3
import re
import os
import glob

def clean_docstrings_and_comments(content):
    """Remove verbose docstrings and comments, keep only essential ones."""
    
    # Remove triple-quoted docstrings
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
    
    # Split into lines for processing
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip empty lines with only whitespace
        if not line.strip():
            cleaned_lines.append('')
            continue
            
        # Keep important comments (short and essential)
        if line.strip().startswith('#'):
            comment = line.strip()[1:].strip()
            # Keep short, useful comments
            if (len(comment) < 50 and 
                any(keyword in comment.lower() for keyword in 
                    ['todo', 'fixme', 'hack', 'note', 'important', 'warning'])):
                cleaned_lines.append(line)
            # Keep simple inline explanations
            elif (len(comment) < 30 and 
                  any(keyword in comment.lower() for keyword in 
                      ['check', 'parse', 'analyze', 'calculate', 'extract'])):
                cleaned_lines.append(f"    # {comment}")
            continue
            
        # Handle inline comments
        if '#' in line and not line.strip().startswith('#'):
            code_part, comment_part = line.split('#', 1)
            comment = comment_part.strip()
            # Keep short, useful inline comments
            if (len(comment) < 30 and 
                any(keyword in comment.lower() for keyword in 
                    ['todo', 'fixme', 'important', 'production'])):
                cleaned_lines.append(f"{code_part.rstrip()} # {comment}")
            else:
                cleaned_lines.append(code_part.rstrip())
        else:
            cleaned_lines.append(line)
    
    # Join lines and clean up extra whitespace
    result = '\n'.join(cleaned_lines)
    
    # Remove excessive empty lines (more than 2 consecutive)
    result = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', result)
    
    return result

def process_file(filepath):
    """Process a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned = clean_docstrings_and_comments(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        print(f"Cleaned: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    """Clean all Python files in the project."""
    # Get all Python files
    python_files = []
    
    # Main source files
    python_files.extend(glob.glob('shadow_ai/*.py'))
    python_files.extend(glob.glob('tests/*.py'))
    python_files.extend(glob.glob('scripts/*.py'))
    python_files.append('main.py')
    
    # Filter out this script itself
    python_files = [f for f in python_files if 'clean_code.py' not in f]
    
    print(f"Found {len(python_files)} Python files to clean")
    
    for filepath in python_files:
        if os.path.exists(filepath):
            process_file(filepath)
    
    print("Cleanup complete!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import ast
import os

def clean_engine_file():
    """Manually clean the engine.py file with careful preservation of code."""
    
    file_path = 'shadow_ai/engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove module docstring at the top
    lines = content.split('\n')
    cleaned_lines = []
    in_module_docstring = False
    skip_until_import = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip module docstring at the beginning
        if i < 20 and '"""' in line and not skip_until_import:
            if line.count('"""') == 2:  # Single line docstring
                skip_until_import = True
                i += 1
                continue
            elif line.count('"""') == 1:  # Start of multi-line docstring
                in_module_docstring = True
                i += 1
                continue
        
        if in_module_docstring:
            if '"""' in line:
                in_module_docstring = False
                skip_until_import = True
            i += 1
            continue
        
        # Skip function/class docstrings
        if ('def ' in line or 'class ' in line) and i + 1 < len(lines):
            cleaned_lines.append(line)
            i += 1
            # Check if next non-empty line is a docstring
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    cleaned_lines.append(lines[i])
                    i += 1
                    continue
                elif next_line.startswith('"""') or next_line.startswith("'''"):
                    # Skip the docstring
                    if next_line.count('"""') == 2 or next_line.count("'''") == 2:
                        # Single line docstring
                        i += 1
                        break
                    else:
                        # Multi-line docstring
                        quote_type = '"""' if '"""' in next_line else "'''"
                        i += 1
                        while i < len(lines) and quote_type not in lines[i]:
                            i += 1
                        i += 1  # Skip the closing quotes
                        break
                else:
                    break
            continue
        
        # Keep essential comments, remove verbose ones
        if line.strip().startswith('#'):
            comment = line.strip()[1:].strip()
            # Keep short, useful comments
            if (len(comment) < 50 and 
                any(keyword in comment.lower() for keyword in 
                    ['analyze', 'check', 'calculate', 'extract', 'parse', 'todo', 'fixme', 'important', 'note'])):
                cleaned_lines.append(f"    # {comment}")
            # Skip verbose explanatory comments
        else:
            # Handle inline comments
            if '#' in line and not line.strip().startswith('#'):
                code_part, comment_part = line.split('#', 1)
                comment = comment_part.strip()
                # Keep short, useful inline comments
                if (len(comment) < 30 and 
                    any(keyword in comment.lower() for keyword in 
                        ['todo', 'fixme', 'important', 'production', 'note'])):
                    cleaned_lines.append(f"{code_part.rstrip()} # {comment}")
                else:
                    cleaned_lines.append(code_part.rstrip())
            else:
                cleaned_lines.append(line)
        
        i += 1
    
    # Join and clean up
    result = '\n'.join(cleaned_lines)
    
    # Remove excessive empty lines
    import re
    result = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n', result)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"Cleaned {file_path}")

if __name__ == "__main__":
    clean_engine_file()

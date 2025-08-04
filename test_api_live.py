#!/usr/bin/env python3
"""
Simple test of the API endpoint
"""

import requests

# Test the API
data = {
    'code': '''def hello():
    print("Hello World")
    return "Hello"''',
    'language': 'python'
}

response = requests.post('http://127.0.0.1:8001/api/check', json=data)
print('Status:', response.status_code)

if response.status_code == 200:
    result = response.json()
    print('Result:', result['result'])
    print('Confidence:', result['confidence'])
    print('Patterns found:', len(result['patterns_found']))
    print('Source:', result['source'])
    print('Language:', result['language'])
else:
    print('Error:', response.text)

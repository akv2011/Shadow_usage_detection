#!/usr/bin/env python3
"""
Test frontend-backend integration
"""

import requests
import json

def test_api_integration():
    """Test that the API endpoints work as expected for the frontend."""
    
    base_url = "http://127.0.0.1:8001/api"
    
    # Test 1: Health check
    print("Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    print("✓ Health check passed")
    
    # Test 2: Text analysis
    print("\nTesting text analysis...")
    data = {
        "code": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
result = fibonacci(10)
print(f"Fibonacci of 10 is: {result}")""",
        "language": "python"
    }
    
    response = requests.post(f"{base_url}/check", json=data)
    assert response.status_code == 200
    result = response.json()
    
    print(f"  Result: {result['result']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"  Patterns found: {len(result['patterns_found'])}")
    print("✓ Text analysis passed")
    
    # Test 3: File upload simulation
    print("\nTesting file upload...")
    files = {
        'file': ('test.py', data['code'], 'text/plain')
    }
    
    response = requests.post(f"{base_url}/analyze", files=files)
    assert response.status_code == 200
    result = response.json()
    
    print(f"  Result: {result['result']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"  Source: {result['source']}")
    print("✓ File upload analysis passed")
    
    print("\n🎉 All frontend-backend integration tests passed!")

if __name__ == "__main__":
    test_api_integration()

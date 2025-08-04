from shadow_ai.engine import analyze

# Test the new scoring system with different examples

print("=== Test 1: Simple function ===")
result1 = analyze('def hello(): print("world")')
print(f"Score: {result1['summary']['overall_suspicion_score']}%")
print(f"Risk: {result1['summary']['risk_level']}")

print("\n=== Test 2: AI-like code with generic comments ===")
code2 = '''# This is a simple function to add two numbers
def add_numbers(a, b):
    # Initialize result variable
    result = a + b
    # Return the result
    return result'''

result2 = analyze(code2)
print(f"Score: {result2['summary']['overall_suspicion_score']}%")
print(f"Risk: {result2['summary']['risk_level']}")
print(f"Risk factors: {result2['summary']['risk_factors']}")

print("\n=== Test 3: Complex file (engine.py) ===")
with open('shadow_ai/engine.py', 'r') as f:
    engine_code = f.read()

result3 = analyze(engine_code)
print(f"Score: {result3['summary']['overall_suspicion_score']}%")
print(f"Risk: {result3['summary']['risk_level']}")
print(f"Component breakdown: {result3['summary']['component_scores']}")

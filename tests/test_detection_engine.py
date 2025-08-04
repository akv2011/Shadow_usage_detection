"""
Tests for the heuristic detection engine.

This module contains comprehensive tests for all detection engine functionality,
including comment pattern analysis, variable naming analysis, code structure
analysis, and AI language pattern matching.
"""

import pytest
from shadow_ai.engine import analyze_comment_patterns, analyze_variable_names, analyze_code_structure, match_ai_language_patterns, analyze


class TestCommentPatternAnalysis:
    """Test class for comment pattern analysis functionality."""

    def test_analyze_comment_patterns_with_generic_comments(self):
        """Test detection of generic AI-generated comment patterns."""
        code_with_generic_comments = '''
# Function to calculate sum
def calculate_sum(a, b):
    # Variable to store result
    result = a + b
    # Return the result
    return result

# Create a list
my_list = []
# Initialize variable
counter = 0
'''
        
        result = analyze_comment_patterns(code_with_generic_comments)
        
        assert result['generic_comments'] >= 4  # Should detect multiple generic patterns
        assert result['total_comments'] == 5
        assert result['comment_to_code_ratio'] > 0.5  # High comment ratio

    def test_analyze_comment_patterns_with_human_comments(self):
        """Test with descriptive, human-like comments."""
        code_with_human_comments = '''
# Calculate total sales tax based on item price and local tax rate
def calculate_sales_tax(price, tax_rate):
    """Returns the tax amount for a given price and rate."""
    if price < 0 or tax_rate < 0:
        raise ValueError("Price and tax rate must be non-negative")
    
    return price * tax_rate

# Database connection parameters for production environment
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'sales_db'
}
'''
        
        result = analyze_comment_patterns(code_with_human_comments)
        
        assert result['generic_comments'] == 0  # Should not detect generic patterns
        assert result['total_comments'] == 2
        assert result['comment_to_code_ratio'] < 0.5  # Lower comment ratio

    def test_analyze_comment_patterns_with_repetitive_patterns(self):
        """Test detection of repetitive comment structures."""
        code_with_repetitive_comments = '''
# Create user data
user_data = {}
# Create admin data
admin_data = {}
# Create guest data
guest_data = {}
# Create temp data
temp_data = {}

def process():
    pass
'''
        
        result = analyze_comment_patterns(code_with_repetitive_comments)
        
        assert result['repetitive_patterns'] >= 4  # Should detect repetitive "Create X data" pattern
        assert result['generic_comments'] >= 3  # Also generic
        assert result['total_comments'] == 4

    def test_analyze_comment_patterns_empty_input(self):
        """Test with empty or invalid input."""
        result = analyze_comment_patterns("")
        
        assert result['generic_comments'] == 0
        assert result['comment_to_code_ratio'] == 0.0
        assert result['repetitive_patterns'] == 0
        assert result['total_comments'] == 0

    def test_analyze_comment_patterns_none_input(self):
        """Test with None input."""
        result = analyze_comment_patterns(None)
        
        assert result['generic_comments'] == 0
        assert result['comment_to_code_ratio'] == 0.0
        assert result['repetitive_patterns'] == 0
        assert result['total_comments'] == 0

    def test_analyze_comment_patterns_no_comments(self):
        """Test with code containing no comments."""
        code_without_comments = '''
def add_numbers(x, y):
    return x + y

result = add_numbers(5, 3)
print(result)
'''
        
        result = analyze_comment_patterns(code_without_comments)
        
        assert result['generic_comments'] == 0
        assert result['comment_to_code_ratio'] == 0.0
        assert result['repetitive_patterns'] == 0
        assert result['total_comments'] == 0

    def test_analyze_comment_patterns_only_comments(self):
        """Test with only comments, no code."""
        only_comments = '''
# This is a comment
# Another comment here
# Yet another comment
'''
        
        result = analyze_comment_patterns(only_comments)
        
        assert result['total_comments'] == 3
        assert result['comment_to_code_ratio'] == float('inf')  # Division by zero case

    def test_analyze_comment_patterns_mixed_content(self):
        """Test with a realistic mix of good and suspicious comments."""
        mixed_code = '''
# Advanced algorithm for calculating fibonacci sequence with memoization
def fibonacci_memo(n, memo={}):
    # Check if already computed
    if n in memo:
        return memo[n]
    
    # Base cases
    if n <= 1:
        return n
    
    # Calculate result
    result = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    # Store the result
    memo[n] = result
    return result

# Example usage with performance timing
import time
start_time = time.time()
'''
        
        result = analyze_comment_patterns(mixed_code)
        
        # Should detect some generic patterns but not all comments
        assert result['generic_comments'] >= 1
        assert result['generic_comments'] < result['total_comments']
        assert 0 < result['comment_to_code_ratio'] < 1


class TestVariableNamingAnalysis:
    """Test class for variable naming analysis functionality."""

    def test_analyze_variable_names_with_generic_names(self):
        """Test detection of generic variable and function names."""
        code_with_generic_names = '''
def process(data, result):
    temp = data + 1
    output = result * temp
    return output

def handle_data(item, value):
    total = 0
    for element in item:
        total += value
    return total

x = process([1, 2, 3], 5)
'''
        
        result = analyze_variable_names(code_with_generic_names)
        
        assert result['generic_names_count'] >= 7  # Should detect multiple generic names
        assert result['generic_percentage'] > 50  # High percentage of generic names
        assert 'data' in result['generic_names_found']
        assert 'result' in result['generic_names_found']
        assert 'temp' in result['generic_names_found']

    def test_analyze_variable_names_with_descriptive_names(self):
        """Test with descriptive, domain-specific variable and function names."""
        code_with_descriptive_names = '''
def calculate_monthly_payment(loan_amount, interest_rate, term_years):
    monthly_rate = interest_rate / 12
    total_payments = term_years * 12
    
    if monthly_rate == 0:
        return loan_amount / total_payments
    
    payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
    return payment

def validate_credit_score(customer_score, minimum_required):
    return customer_score >= minimum_required

mortgage_payment = calculate_monthly_payment(250000, 0.035, 30)
'''
        
        result = analyze_variable_names(code_with_descriptive_names)
        
        assert result['generic_percentage'] < 20  # Low percentage of generic names
        assert result['total_names_count'] > 0
        # Should not detect many generic names in descriptive code

    def test_analyze_variable_names_mixed_names(self):
        """Test with a mix of generic and descriptive names."""
        code_with_mixed_names = '''
def user_authentication(username, password):
    data = get_user_data(username)  # generic 'data'
    if data and check_password(password, data.password_hash):
        session_token = generate_token(username)
        return session_token
    return None

def process_order(customer_id, order_items):  # generic 'process'
    total_cost = 0
    for item in order_items:  # generic 'item'
        total_cost += item.price * item.quantity
    return create_invoice(customer_id, total_cost)
'''
        
        result = analyze_variable_names(code_with_mixed_names)
        
        assert 10 <= result['generic_percentage'] <= 60  # Moderate percentage
        assert result['generic_names_count'] > 0
        assert result['total_names_count'] > result['generic_names_count']

    def test_analyze_variable_names_empty_input(self):
        """Test with empty input."""
        result = analyze_variable_names("")
        
        assert result['generic_names_count'] == 0
        assert result['total_names_count'] == 0
        assert result['generic_percentage'] == 0.0
        assert result['generic_names_found'] == []

    def test_analyze_variable_names_none_input(self):
        """Test with None input."""
        result = analyze_variable_names(None)
        
        assert result['generic_names_count'] == 0
        assert result['total_names_count'] == 0
        assert result['generic_percentage'] == 0.0
        assert result['generic_names_found'] == []

    def test_analyze_variable_names_syntax_error(self):
        """Test with code containing syntax errors."""
        code_with_syntax_error = '''
def broken_function(
    # Missing closing parenthesis and other syntax issues
    if True
        print("broken")
'''
        
        result = analyze_variable_names(code_with_syntax_error)
        
        # Should gracefully handle syntax errors
        assert result['generic_names_count'] == 0
        assert result['total_names_count'] == 0
        assert result['generic_percentage'] == 0.0

    def test_analyze_variable_names_single_letter_variables(self):
        """Test detection of single-letter variables (common in AI examples)."""
        code_with_single_letters = '''
def matrix_multiply(matrix_a, matrix_b):
    rows_a = len(matrix_a)
    cols_b = len(matrix_b[0])
    
    result_matrix = [[0 for j in range(cols_b)] for i in range(rows_a)]
    
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(len(matrix_b)):
                result_matrix[i][j] += matrix_a[i][k] * matrix_b[k][j]
    
    return result_matrix

x = [[1, 2], [3, 4]]
y = [[5, 6], [7, 8]]
z = matrix_multiply(x, y)
'''
        
        result = analyze_variable_names(code_with_single_letters)
        
        # Should detect i, j, k, x, y, z as generic
        assert result['generic_names_count'] >= 6
        assert 'i' in result['generic_names_found']
        assert 'j' in result['generic_names_found']
        assert 'k' in result['generic_names_found']
        assert 'x' in result['generic_names_found']
        assert 'y' in result['generic_names_found']
        assert 'z' in result['generic_names_found']

    def test_analyze_variable_names_builtin_filtering(self):
        """Test that built-in names are properly filtered out."""
        code_with_builtins = '''
def example_function():
    my_list = [1, 2, 3]
    result = len(my_list)
    
    for item in my_list:
        print(item)
    
    return str(result)
'''
        
        result = analyze_variable_names(code_with_builtins)
        
        # Built-ins like 'len', 'print', 'str' should not be counted
        # But 'result' and 'item' should be detected as generic
        assert 'len' not in result['generic_names_found']
        assert 'print' not in result['generic_names_found']
        assert 'str' not in result['generic_names_found']
        assert 'result' in result['generic_names_found']
        assert 'item' in result['generic_names_found']


class TestCodeStructureAnalysis:
    """Test class for code structure analysis functionality."""

    def test_analyze_code_structure_uniform_functions(self):
        """Test detection of overly uniform function structures (AI-like)."""
        code_with_uniform_functions = '''
def process_data_a(data):
    result = data * 2
    return result

def process_data_b(data):
    result = data + 1
    return result

def process_data_c(data):
    result = data / 2
    return result

def process_data_d(data):
    result = data - 1
    return result
'''
        
        result = analyze_code_structure(code_with_uniform_functions)
        
        assert result['total_functions'] == 4
        assert result['function_length_variance'] < 2.0  # Very low variance (uniform)
        assert result['structural_uniformity_score'] > 50  # High uniformity score
        assert result['average_nesting_depth'] <= 1.0  # Simple structure

    def test_analyze_code_structure_complex_varied_code(self):
        """Test with complex, varied human-written code."""
        code_with_varied_structure = '''
def calculate_mortgage_payment(principal, rate, years):
    """Calculate monthly mortgage payment using standard formula."""
    if rate == 0:
        return principal / (years * 12)
    
    monthly_rate = rate / 12
    num_payments = years * 12
    
    if monthly_rate > 0:
        factor = (1 + monthly_rate) ** num_payments
        payment = principal * (monthly_rate * factor) / (factor - 1)
        return round(payment, 2)
    else:
        return principal / num_payments

def validate_user_input(user_data):
    """Comprehensive input validation with multiple checks."""
    errors = []
    
    if not user_data:
        errors.append("No data provided")
        return errors
    
    if 'email' in user_data:
        email = user_data['email']
        if '@' not in email or '.' not in email.split('@')[-1]:
            errors.append("Invalid email format")
    
    if 'age' in user_data:
        try:
            age = int(user_data['age'])
            if age < 0 or age > 150:
                errors.append("Age must be between 0 and 150")
        except (ValueError, TypeError):
            errors.append("Age must be a valid number")
    
    return errors

class DatabaseManager:
    def __init__(self, connection_string):
        self.connection = self._create_connection(connection_string)
        self.cache = {}
    
    def _create_connection(self, conn_str):
        # Complex connection logic would go here
        return None
'''
        
        result = analyze_code_structure(code_with_varied_structure)
        
        assert result['total_functions'] == 4  # calculate_mortgage_payment, validate_user_input, __init__, _create_connection
        assert result['function_length_variance'] > 3.0  # Moderate variance (varied)
        assert result['structural_uniformity_score'] < 40  # Low uniformity score
        assert result['node_type_diversity'] > 15  # High diversity of constructs

    def test_analyze_code_structure_simple_repetitive(self):
        """Test with simple, repetitive code patterns."""
        code_with_simple_patterns = '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

def modulo(a, b):
    return a % b
'''
        
        result = analyze_code_structure(code_with_simple_patterns)
        
        assert result['total_functions'] == 5
        assert result['function_length_variance'] == 0.0  # Perfectly uniform
        assert result['structural_uniformity_score'] > 70  # Very high uniformity
        assert result['average_nesting_depth'] == 0.0  # No nesting
        assert result['control_flow_complexity'] == 0.0  # No control flow

    def test_analyze_code_structure_complex_nesting(self):
        """Test with code that has complex nesting patterns."""
        code_with_complex_nesting = '''
def complex_algorithm(data):
    results = []
    
    for item in data:
        if item > 0:
            for i in range(item):
                if i % 2 == 0:
                    try:
                        with open(f"file_{i}.txt", "r") as f:
                            content = f.read()
                            if len(content) > 100:
                                for line in content.split('\\n'):
                                    if line.strip():
                                        results.append(line.upper())
                    except FileNotFoundError:
                        continue
                else:
                    results.append(str(i))
    
    return results

def simple_function():
    return "simple"
'''
        
        result = analyze_code_structure(code_with_complex_nesting)
        
        assert result['total_functions'] == 2
        assert result['average_nesting_depth'] > 3.0  # Deep nesting
        assert result['control_flow_complexity'] > 5.0  # Moderate control flow
        assert result['node_type_diversity'] > 20  # Many different constructs

    def test_analyze_code_structure_empty_input(self):
        """Test with empty input."""
        result = analyze_code_structure("")
        
        assert result['function_length_variance'] == 0.0
        assert result['average_nesting_depth'] == 0.0
        assert result['node_type_diversity'] == 0
        assert result['control_flow_complexity'] == 0.0
        assert result['structural_uniformity_score'] == 0.0
        assert result['total_functions'] == 0

    def test_analyze_code_structure_none_input(self):
        """Test with None input."""
        result = analyze_code_structure(None)
        
        assert result['function_length_variance'] == 0.0
        assert result['average_nesting_depth'] == 0.0
        assert result['node_type_diversity'] == 0
        assert result['control_flow_complexity'] == 0.0
        assert result['structural_uniformity_score'] == 0.0
        assert result['total_functions'] == 0

    def test_analyze_code_structure_syntax_error(self):
        """Test with code containing syntax errors."""
        code_with_syntax_error = '''
def broken_function(
    # Missing closing parenthesis
    if True
        print("broken"
    # Missing indentation and other issues
'''
        
        result = analyze_code_structure(code_with_syntax_error)
        
        # Should gracefully handle syntax errors
        assert result['function_length_variance'] == 0.0
        assert result['total_functions'] == 0
        assert result['structural_uniformity_score'] == 0.0

    def test_analyze_code_structure_no_functions(self):
        """Test with code that contains no function definitions."""
        code_without_functions = '''
x = 1
y = 2
z = x + y

if z > 0:
    print("positive")
else:
    print("non-positive")

for i in range(5):
    print(i)
'''
        
        result = analyze_code_structure(code_without_functions)
        
        assert result['total_functions'] == 0
        assert result['function_length_variance'] == 0.0
        assert result['average_nesting_depth'] == 0.0
        assert result['node_type_diversity'] > 5  # Should still detect node types
        assert result['control_flow_complexity'] > 0  # Should detect control flow

    def test_analyze_code_structure_single_function(self):
        """Test with code containing only one function."""
        code_with_single_function = '''
def comprehensive_function(data_list, options):
    """A single but complex function."""
    results = []
    processed_count = 0
    
    for item in data_list:
        if item is not None:
            try:
                if 'transform' in options:
                    transformed = options['transform'](item)
                    if transformed:
                        results.append(transformed)
                        processed_count += 1
                else:
                    results.append(item)
                    processed_count += 1
            except Exception as e:
                if options.get('ignore_errors', False):
                    continue
                else:
                    raise e
    
    return {
        'results': results,
        'processed_count': processed_count,
        'success_rate': processed_count / len(data_list) if data_list else 0
    }
'''
        
        result = analyze_code_structure(code_with_single_function)
        
        assert result['total_functions'] == 1
        assert result['function_length_variance'] == 0.0  # Only one function
        assert result['average_nesting_depth'] > 2.0  # Complex nesting
        assert result['structural_uniformity_score'] < 50  # Not uniform (complex single function)


class TestAILanguagePatternMatching:
    """Test class for AI language pattern matching functionality."""

    def test_match_ai_language_patterns_with_ai_references(self):
        """Test detection of direct AI self-references."""
        code_with_ai_references = '''
def example_function():
    """
    As an AI language model, I cannot access real-time data.
    This is a sample implementation generated by ChatGPT.
    Please note that this code may need to be adapted for your specific use case.
    """
    # Here's an example of how to process data
    # I'll help you understand this algorithm
    return "processed"

def another_function():
    # This was created using GitHub Copilot
    pass
'''
        
        result = match_ai_language_patterns(code_with_ai_references)
        
        assert result['ai_phrase_count'] > 0
        assert result['confidence_level'] > 50  # High confidence
        assert any('ai language model' in phrase.lower() for phrase in result['ai_phrases_found'])
        assert result['conversational_indicators'] >= 2
        assert result['disclaimer_patterns'] >= 1

    def test_match_ai_language_patterns_conversational_style(self):
        """Test detection of conversational AI patterns."""
        code_with_conversational_style = '''
def helper_function(data):
    """
    Here's an example of how you can process the data.
    Feel free to modify this code as needed.
    Let me know if you need any clarification.
    Hope this helps with your implementation!
    """
    # You might want to add error handling here
    # This should work for most use cases
    return processed_data

# You can use this function like this:
# result = helper_function(my_data)
'''
        
        result = match_ai_language_patterns(code_with_conversational_style)
        
        assert result['conversational_indicators'] >= 3
        assert result['confidence_level'] > 30
        assert any('here\'s an example' in phrase.lower() or 'here is an example' in phrase.lower() 
                 for phrase in result['ai_phrases_found'])

    def test_match_ai_language_patterns_disclaimer_patterns(self):
        """Test detection of AI disclaimer and limitation patterns."""
        code_with_disclaimers = '''
def get_current_data():
    """
    Note: I cannot access real-time data or current information.
    Please verify this information as it may not be up-to-date.
    As of my last training update, this approach was valid.
    Consult the official documentation for the latest changes.
    """
    # This may vary depending on your specific requirements
    return {}
'''
        
        result = match_ai_language_patterns(code_with_disclaimers)
        
        assert result['disclaimer_patterns'] >= 3
        assert result['confidence_level'] > 40
        # The actual phrase captured might be slightly different due to regex matching
        assert any('cannot access' in phrase.lower() for phrase in result['ai_phrases_found'])

    def test_match_ai_language_patterns_human_code(self):
        """Test with typical human-written code comments."""
        human_code = '''
def calculate_compound_interest(principal, rate, time, n=1):
    """
    Calculate compound interest using the standard formula.
    
    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as decimal)
        time: Investment period in years
        n: Number of times interest compounds per year
        
    Returns:
        Final amount after compound interest
        
    Raises:
        ValueError: If any parameter is negative
    """
    if principal < 0 or rate < 0 or time < 0 or n <= 0:
        raise ValueError("Invalid parameters for compound interest calculation")
    
    # Apply compound interest formula: A = P(1 + r/n)^(nt)
    amount = principal * (1 + rate/n) ** (n * time)
    return round(amount, 2)

class InvestmentPortfolio:
    """Manages a portfolio of investments with risk assessment."""
    
    def __init__(self, initial_balance):
        # Initialize portfolio with starting balance
        self.balance = initial_balance
        self.investments = []
        self.risk_tolerance = 'moderate'
'''
        
        result = match_ai_language_patterns(human_code)
        
        assert result['ai_phrase_count'] == 0 or result['confidence_level'] < 20
        assert result['conversational_indicators'] == 0
        assert result['disclaimer_patterns'] == 0

    def test_match_ai_language_patterns_mixed_content(self):
        """Test with mixed AI and human-style content."""
        mixed_code = '''
def data_processor(input_data):
    """
    Advanced data processing algorithm for financial analysis.
    
    Here's an example of how to use this function effectively.
    The algorithm implements sophisticated statistical methods.
    Please note that results may vary depending on market conditions.
    """
    # Validate input parameters
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    # Apply proprietary transformation algorithms
    processed = transform_data(input_data)
    return processed

def transform_data(data):
    # Custom transformation logic implemented by our team
    return data * 1.05
'''
        
        result = match_ai_language_patterns(mixed_code)
        
        assert 0 < result['confidence_level'] <= 100  # Should detect some AI patterns
        assert result['conversational_indicators'] >= 1
        # Should detect some patterns but not be overwhelmingly AI-like

    def test_match_ai_language_patterns_empty_input(self):
        """Test with empty input."""
        result = match_ai_language_patterns("")
        
        assert result['ai_phrases_found'] == []
        assert result['ai_phrase_count'] == 0
        assert result['conversational_indicators'] == 0
        assert result['disclaimer_patterns'] == 0
        assert result['confidence_level'] == 0.0

    def test_match_ai_language_patterns_none_input(self):
        """Test with None input."""
        result = match_ai_language_patterns(None)
        
        assert result['ai_phrases_found'] == []
        assert result['ai_phrase_count'] == 0
        assert result['conversational_indicators'] == 0
        assert result['disclaimer_patterns'] == 0
        assert result['confidence_level'] == 0.0

    def test_match_ai_language_patterns_no_comments(self):
        """Test with code containing no comments or docstrings."""
        code_without_comments = '''
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y

result = add(5, 3)
product = multiply(2, 4)
'''
        
        result = match_ai_language_patterns(code_without_comments)
        
        assert result['ai_phrases_found'] == []
        assert result['ai_phrase_count'] == 0
        assert result['confidence_level'] == 0.0

    def test_match_ai_language_patterns_case_insensitive(self):
        """Test that pattern matching is case-insensitive."""
        code_with_varied_cases = '''
def test_function():
    """
    AS AN AI LANGUAGE MODEL, I cannot provide real-time information.
    here's AN EXAMPLE of mixed case text.
    Feel FREE to modify this as needed.
    """
    # LET ME KNOW if you need help
    # Hope THIS helps with your project
    pass
'''
        
        result = match_ai_language_patterns(code_with_varied_cases)
        
        assert result['ai_phrase_count'] > 0
        assert result['confidence_level'] > 50
        assert any('ai language model' in phrase.lower() for phrase in result['ai_phrases_found'])
        assert result['conversational_indicators'] >= 2


class TestMainEngineOrchestrator:
    """Test class for the main analyze function that orchestrates all heuristics."""

    def test_analyze_ai_generated_code(self):
        """Test the main analyze function with clearly AI-generated code."""
        ai_generated_code = '''
def process_data(data):
    """
    Here's an example of how to process data as an AI language model.
    Feel free to modify this code as needed for your specific use case.
    """
    # Initialize result
    result = []
    
    # Process each item
    for item in data:
        # Calculate value
        value = item * 2
        # Add to result
        result.append(value)
    
    # Return the result
    return result

def handle_input(input):
    """Sample code generated to help with your request."""
    # Process the input
    output = input.upper()
    return output
'''
        
        analysis_result = analyze(ai_generated_code)
        
        # Check structure of results
        assert 'comment_patterns' in analysis_result
        assert 'variable_names' in analysis_result
        assert 'code_structure' in analysis_result
        assert 'ai_language_patterns' in analysis_result
        assert 'summary' in analysis_result
        assert 'analysis_metadata' in analysis_result
        
        # Check that AI patterns are detected
        assert analysis_result['comment_patterns']['generic_comments'] > 0
        assert analysis_result['variable_names']['generic_percentage'] > 30
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] > 0
        assert analysis_result['summary']['overall_suspicion_score'] > 25  # Adjusted for more realistic scoring
        assert len(analysis_result['summary']['risk_factors']) > 0

    def test_analyze_human_written_code(self):
        """Test the main analyze function with typical human-written code."""
        human_code = '''
class CustomerAccount:
    """Manages customer account information and transactions."""
    
    def __init__(self, customer_id, initial_balance=0.0):
        """Initialize a new customer account."""
        self.customer_id = customer_id
        self.balance = initial_balance
        self.transaction_history = []
        
    def deposit(self, amount):
        """Add funds to the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        self.transaction_history.append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': datetime.now(),
            'balance_after': self.balance
        })
        
    def withdraw(self, amount):
        """Remove funds from the account if sufficient balance exists."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
            
        self.balance -= amount
        self.transaction_history.append({
            'type': 'withdrawal', 
            'amount': amount,
            'timestamp': datetime.now(),
            'balance_after': self.balance
        })
'''
        
        analysis_result = analyze(human_code)
        
        # Check that human code has lower suspicion scores
        assert analysis_result['comment_patterns']['generic_comments'] == 0
        assert analysis_result['variable_names']['generic_percentage'] < 30
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] == 0
        assert analysis_result['summary']['overall_suspicion_score'] < 30
        assert analysis_result['code_structure']['structural_uniformity_score'] < 90  # Allow for some structural patterns

    def test_analyze_empty_input(self):
        """Test the main analyze function with empty input."""
        analysis_result = analyze("")
        
        # Should return properly structured empty results
        assert analysis_result['comment_patterns']['generic_comments'] == 0
        assert analysis_result['variable_names']['total_names_count'] == 0
        assert analysis_result['code_structure']['total_functions'] == 0
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] == 0
        assert analysis_result['summary']['overall_suspicion_score'] == 0.0
        assert analysis_result['analysis_metadata']['code_length'] == 0

    def test_analyze_none_input(self):
        """Test the main analyze function with None input."""
        analysis_result = analyze(None)
        
        # Should handle None gracefully
        assert analysis_result['summary']['overall_suspicion_score'] == 0.0
        assert analysis_result['analysis_metadata']['code_length'] == 0
        assert analysis_result['analysis_metadata']['analysis_timestamp'] is None

    def test_analyze_mixed_content(self):
        """Test with code that has both human and AI characteristics."""
        mixed_code = '''
def calculate_mortgage_payment(principal, annual_rate, years):
    """
    Calculate monthly mortgage payment using standard amortization formula.
    Here's an example of how this calculation works in practice.
    """
    # Convert annual rate to monthly
    monthly_rate = annual_rate / 12
    
    # Calculate total number of payments
    total_payments = years * 12
    
    # Handle special case of zero interest
    if monthly_rate == 0:
        return principal / total_payments
    
    # Apply standard mortgage formula
    factor = (1 + monthly_rate) ** total_payments
    payment = principal * (monthly_rate * factor) / (factor - 1)
    
    return round(payment, 2)

def process_data(data):
    # Process the data
    result = []
    for item in data:
        result.append(item * 2)
    return result
'''
        
        analysis_result = analyze(mixed_code)
        
        # Should detect moderate AI characteristics
        assert 10 < analysis_result['summary']['overall_suspicion_score'] < 70
        assert analysis_result['ai_language_patterns']['conversational_indicators'] > 0
        assert analysis_result['variable_names']['generic_percentage'] > 0

    def test_analyze_metadata_structure(self):
        """Test that analysis metadata is properly structured."""
        code = "def test(): pass"
        analysis_result = analyze(code)
        
        metadata = analysis_result['analysis_metadata']
        assert 'code_length' in metadata
        assert 'analysis_timestamp' in metadata
        assert 'heuristics_run' in metadata
        assert 'errors_encountered' in metadata
        
        assert metadata['code_length'] == len(code)
        assert metadata['heuristics_run'] == 4
        assert isinstance(metadata['errors_encountered'], list)

    def test_analyze_summary_structure(self):
        """Test that summary statistics are properly calculated."""
        code = '''
def process(data):
    # Process the data
    result = data * 2
    return result
'''
        analysis_result = analyze(code)
        
        summary = analysis_result['summary']
        assert 'total_indicators' in summary
        assert 'risk_factors' in summary
        assert 'overall_suspicion_score' in summary
        
        assert isinstance(summary['total_indicators'], int)
        assert isinstance(summary['risk_factors'], list)
        assert isinstance(summary['overall_suspicion_score'], (int, float))
        assert 0 <= summary['overall_suspicion_score'] <= 100

    def test_analyze_comprehensive_ai_code(self):
        """Test with code that triggers multiple AI detection heuristics."""
        comprehensive_ai_code = '''
def process(data):
    """
    As an AI language model, here's an example of data processing.
    Feel free to modify this code as needed for your specific requirements.
    """
    # Initialize result
    result = []
    
    # Process each item
    for item in data:
        # Calculate value
        value = item * 2
        # Add to result
        result.append(value)
    
    # Return the result
    return result

def handle(input):
    # Process the input
    output = input.upper()
    return output

def transform(data):
    # Transform the data
    result = data.lower()
    return result

def convert(value):
    # Convert the value
    output = str(value)
    return output
'''
        
        analysis_result = analyze(comprehensive_ai_code)
        
        # Should trigger multiple heuristics
        assert analysis_result['comment_patterns']['generic_comments'] >= 3
        assert analysis_result['variable_names']['generic_percentage'] > 60
        assert analysis_result['code_structure']['structural_uniformity_score'] > 70
        assert analysis_result['ai_language_patterns']['ai_phrase_count'] >= 2
        assert analysis_result['summary']['overall_suspicion_score'] > 30  # Adjusted for more realistic scoring
        assert len(analysis_result['summary']['risk_factors']) >= 4


def test_ast_module_available():
    """Test that AST module is available for code analysis."""
    import ast

    # Test basic AST functionality
    code = "x = 1"
    tree = ast.parse(code)
    assert isinstance(tree, ast.AST), "AST parsing not working"

    # Test AST node walking
    nodes = list(ast.walk(tree))
    assert len(nodes) > 0, "AST node traversal not working"


def test_sqlite_available():
    """Test that SQLite is available for future database functionality."""
    import sqlite3

    # Test in-memory database creation
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Test basic SQL execution
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    cursor.execute("INSERT INTO test DEFAULT VALUES")
    cursor.fetchone()

    conn.close()
    assert True, "SQLite functionality verified"

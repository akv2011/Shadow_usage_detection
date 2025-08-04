#!/usr/bin/env python3
"""Test script for database logging functionality."""

import sys
sys.path.append('.')

from shadow_ai.engine import analyze
from shadow_ai.database import get_database

def test_logging():
    # Test the logging functionality
    test_code = '''def hello_world():
    print("Hello, World!")'''
    
    analysis_result = analyze(test_code)
    db = get_database()

    # Log a test analysis
    record_id = db.log_analysis(
        filename='test_code.py',
        result='Likely Human-Written',
        score=25,
        language='python',
        patterns=[],
        analysis_data=analysis_result
    )

    print(f'Test analysis logged with ID: {record_id}')

    # Verify it was logged
    history = db.get_history(limit=1)
    if history:
        record = history[0]
        print(f'Latest record: {record["filename"]} - {record["result"]} ({record["score"]}%)')
        print(f'Timestamp: {record["formatted_timestamp"]}')
    else:
        print('No records found')

if __name__ == "__main__":
    test_logging()

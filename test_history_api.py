#!/usr/bin/env python3
"""Test script for the history API endpoint."""

import sys
sys.path.append('.')

import requests
import json
from shadow_ai.database import get_database

def test_history_api():
    """Test the /api/history endpoint."""
    
    # First, add a few more test records to the database
    db = get_database()
    
    # Add some test records
    test_records = [
        {
            'filename': 'suspicious_code.py',
            'result': 'Likely AI-Generated',
            'score': 85,
            'language': 'python',
            'patterns': ['Generic variable names', 'Overly uniform structure']
        },
        {
            'filename': 'human_code.js',
            'result': 'Likely Human-Written',
            'score': 15,
            'language': 'javascript',
            'patterns': []
        }
    ]
    
    for record in test_records:
        db.log_analysis(
            filename=record['filename'],
            result=record['result'],
            score=record['score'],
            language=record['language'],
            patterns=record['patterns']
        )
    
    print("Added test records to database")
    
    # Test the history retrieval
    history = db.get_history(limit=5)
    print(f"Database contains {len(history)} records:")
    for record in history:
        print(f"  {record['filename']} - {record['result']} ({record['score']}%)")

if __name__ == "__main__":
    test_history_api()

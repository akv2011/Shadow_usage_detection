#!/usr/bin/env python3
"""
Database module for Shadow AI Detection Tool

This module provides database functionality for storing analysis history
using SQLite. It handles database initialization, connection management,
and CRUD operations for analysis records.

Author: Shadow AI Detection Tool
Created: 2025-08-04
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import os
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for analysis history."""
    
    def __init__(self, db_path: str = "data/history.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """
        Initialize the database and create tables if they don't exist.
        
        Creates the 'history' table with the following schema:
        - id: Primary key (auto-increment)
        - filename: Name of the analyzed file or 'text_input'
        - timestamp: ISO 8601 formatted timestamp
        - result: Analysis result verdict
        - score: Confidence score (0-100)
        - language: Detected programming language
        - patterns: JSON string of detected patterns
        - analysis_data: Full analysis results as JSON
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create history table with extended schema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        result TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        language TEXT,
                        patterns TEXT,
                        analysis_data TEXT
                    )
                """)
                
                # Create index on timestamp for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON history(timestamp DESC)
                """)
                
                conn.commit()
                logger.info(f"Database initialized successfully at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def log_analysis(
        self, 
        filename: str, 
        result: str, 
        score: int, 
        language: str = None,
        patterns: List[str] = None,
        analysis_data: Dict[str, Any] = None
    ) -> int:
        """
        Log an analysis result to the database.
        
        Args:
            filename: Name of the analyzed file or 'text_input'
            result: Analysis result verdict
            score: Confidence score (0-100)
            language: Detected programming language
            patterns: List of detected patterns
            analysis_data: Full analysis results
            
        Returns:
            int: ID of the inserted record
        """
        try:
            timestamp = datetime.now().isoformat()
            patterns_json = json.dumps(patterns) if patterns else "[]"
            analysis_json = json.dumps(analysis_data) if analysis_data else "{}"
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO history 
                    (filename, timestamp, result, score, language, patterns, analysis_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    filename, 
                    timestamp, 
                    result, 
                    score, 
                    language,
                    patterns_json,
                    analysis_json
                ))
                
                record_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Logged analysis for '{filename}' with score {score}")
                return record_id
                
        except sqlite3.Error as e:
            logger.error(f"Failed to log analysis: {e}")
            raise
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve analysis history from the database.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of analysis records as dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, filename, timestamp, result, score, language, patterns
                    FROM history 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries and parse JSON fields
                records = []
                for row in rows:
                    record = dict(row)
                    
                    # Parse patterns JSON
                    try:
                        record['patterns'] = json.loads(record['patterns']) if record['patterns'] else []
                    except json.JSONDecodeError:
                        record['patterns'] = []
                    
                    # Format timestamp for display
                    try:
                        dt = datetime.fromisoformat(record['timestamp'])
                        record['formatted_timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        record['formatted_timestamp'] = record['timestamp']
                    
                    records.append(record)
                
                logger.info(f"Retrieved {len(records)} history records")
                return records
                
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve history: {e}")
            raise
    
    def get_analysis_details(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed analysis data for a specific record.
        
        Args:
            record_id: ID of the record
            
        Returns:
            Full analysis data or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT analysis_data FROM history WHERE id = ?
                """, (record_id,))
                
                row = cursor.fetchone()
                
                if row and row['analysis_data']:
                    try:
                        return json.loads(row['analysis_data'])
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in analysis_data for record {record_id}")
                        return None
                
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get analysis details: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get analysis statistics from the database.
        
        Returns:
            Dictionary with various statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total analyses
                cursor.execute("SELECT COUNT(*) as total FROM history")
                total = cursor.fetchone()['total']
                
                # Results breakdown
                cursor.execute("""
                    SELECT result, COUNT(*) as count 
                    FROM history 
                    GROUP BY result
                """)
                results_breakdown = {row['result']: row['count'] for row in cursor.fetchall()}
                
                # Average score
                cursor.execute("SELECT AVG(score) as avg_score FROM history")
                avg_score_row = cursor.fetchone()
                avg_score = round(avg_score_row['avg_score'], 1) if avg_score_row['avg_score'] else 0
                
                # Recent activity (last 7 days)
                cursor.execute("""
                    SELECT COUNT(*) as recent_count 
                    FROM history 
                    WHERE datetime(timestamp) >= datetime('now', '-7 days')
                """)
                recent_count = cursor.fetchone()['recent_count']
                
                return {
                    'total_analyses': total,
                    'results_breakdown': results_breakdown,
                    'average_score': avg_score,
                    'recent_activity': recent_count
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get stats: {e}")
            raise


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """
    Get the global database instance (singleton pattern).
    
    Returns:
        DatabaseManager: The database manager instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


def init_database() -> None:
    """Initialize the database. Called on application startup."""
    get_database()

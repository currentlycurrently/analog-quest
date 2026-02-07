import sqlite3
from datetime import datetime
import os

# Get the absolute path to the database
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'papers.db')

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def log_action(action, details, papers=0, patterns=0, isomorphisms=0):
    """Log what we did in this session"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO processing_log
        (action, details, papers_processed, patterns_created, isomorphisms_found)
        VALUES (?, ?, ?, ?, ?)
    ''', (action, str(details), papers, patterns, isomorphisms))
    db.commit()
    db.close()
    print(f"[LOG] {action}: {details} (papers={papers}, patterns={patterns}, isomorphisms={isomorphisms})")

def get_stats():
    """Get current statistics from the database"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM stats')
    result = cursor.fetchone()
    db.close()

    if result:
        return {
            'total_papers': result[0] or 0,
            'total_patterns': result[1] or 0,
            'total_isomorphisms': result[2] or 0,
            'verified_isomorphisms': result[3] or 0,
            'domains_covered': result[4] or 0,
            'avg_patterns_per_paper': result[5] or 0
        }
    return None

def print_stats():
    """Print current statistics"""
    stats = get_stats()
    if stats:
        print("\n=== Database Statistics ===")
        print(f"Papers: {stats['total_papers']}")
        print(f"Patterns: {stats['total_patterns']}")
        print(f"Isomorphisms: {stats['total_isomorphisms']}")
        print(f"Verified: {stats['verified_isomorphisms']}")
        print(f"Domains: {stats['domains_covered']}")
        print(f"Avg patterns/paper: {stats['avg_patterns_per_paper']:.2f}")
        print("===========================\n")
    else:
        print("No statistics available yet.")

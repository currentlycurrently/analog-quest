#!/usr/bin/env python3
"""
Check the database schema to see what columns exist.
"""

import psycopg2
import os

def connect_db():
    """Connect to PostgreSQL database."""
    db_url = 'postgresql://user@localhost:5432/analog_quest'
    return psycopg2.connect(db_url)

def check_schema():
    """Check the schema of relevant tables."""
    conn = connect_db()
    cur = conn.cursor()

    # Check discovered_pairs columns
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'discovered_pairs'
        ORDER BY ordinal_position
    """)

    print("DISCOVERED_PAIRS TABLE:")
    print("-" * 40)
    for col in cur.fetchall():
        print(f"  {col[0]}: {col[1]}")

    # Check discoveries columns
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'discoveries'
        ORDER BY ordinal_position
    """)

    print("\nDISCOVERIES TABLE:")
    print("-" * 40)
    for col in cur.fetchall():
        print(f"  {col[0]}: {col[1]}")

    conn.close()

if __name__ == "__main__":
    check_schema()
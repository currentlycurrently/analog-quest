#!/usr/bin/env python3
"""
Inspect PostgreSQL database schema and current data state.
"""

import psycopg2
import json
from psycopg2.extras import RealDictCursor

def inspect_database():
    """Inspect the current state of the PostgreSQL database."""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="analog_quest",
        user="user"
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("=" * 80)
    print("POSTGRESQL DATABASE INSPECTION")
    print("=" * 80)

    # Get table schemas
    tables = ['papers', 'mechanisms', 'discovered_pairs', 'discoveries']

    for table in tables:
        print(f"\n{'=' * 80}")
        print(f"TABLE: {table}")
        print("=" * 80)

        # Get column info
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = '{table}'
            ORDER BY ordinal_position;
        """)

        columns = cur.fetchall()
        print("\nColumns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} "
                  f"(nullable: {col['is_nullable']}, default: {col['column_default']})")

        # Get row count
        cur.execute(f"SELECT COUNT(*) as count FROM {table};")
        count = cur.fetchone()['count']
        print(f"\nRow count: {count}")

        # Get sample rows
        if count > 0:
            cur.execute(f"SELECT * FROM {table} LIMIT 3;")
            samples = cur.fetchall()
            print("\nSample rows:")
            for i, row in enumerate(samples, 1):
                print(f"\n  Row {i}:")
                for key, value in row.items():
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"    {key}: {value}")

    # Specific checks for mechanisms
    print(f"\n{'=' * 80}")
    print("MECHANISM FORMAT ANALYSIS")
    print("=" * 80)

    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN description IS NOT NULL AND description != '' THEN 1 END) as with_description,
            COUNT(CASE WHEN structural_description IS NOT NULL AND structural_description != '' THEN 1 END) as with_structural_description,
            COUNT(CASE WHEN mechanism IS NOT NULL AND mechanism != '' THEN 1 END) as with_mechanism
        FROM mechanisms;
    """)

    stats = cur.fetchone()
    print(f"\nTotal mechanisms: {stats['total']}")
    print(f"With 'description' field: {stats['with_description']}")
    print(f"With 'structural_description' field: {stats['with_structural_description']}")
    print(f"With 'mechanism' field: {stats['with_mechanism']}")

    # Sample mechanisms with different formats
    print("\nSample mechanisms with OLD format (mechanism field only):")
    cur.execute("""
        SELECT id, mechanism, description, structural_description
        FROM mechanisms
        WHERE (description IS NULL OR description = '')
        AND mechanism IS NOT NULL AND mechanism != ''
        LIMIT 2;
    """)
    old_format = cur.fetchall()
    for mech in old_format:
        print(f"\n  ID {mech['id']}:")
        print(f"    mechanism: {mech['mechanism'][:100]}...")
        print(f"    description: {mech['description']}")
        print(f"    structural_description: {mech['structural_description']}")

    print("\nSample mechanisms with NEW format (description + structural_description):")
    cur.execute("""
        SELECT id, mechanism, description, structural_description
        FROM mechanisms
        WHERE description IS NOT NULL AND description != ''
        LIMIT 2;
    """)
    new_format = cur.fetchall()
    for mech in new_format:
        print(f"\n  ID {mech['id']}:")
        print(f"    mechanism: {mech['mechanism']}")
        print(f"    description: {mech['description'][:100] if mech['description'] else None}...")
        print(f"    structural_description: {mech['structural_description'][:100] if mech['structural_description'] else None}...")

    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_database()

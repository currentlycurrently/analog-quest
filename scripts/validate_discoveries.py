#!/usr/bin/env python3
"""
Validate discoveries.json data quality and referential integrity.

Checks:
1. All paper_ids exist in database
2. All arxiv_ids match database values
3. All domains match database values
4. No duplicate paper references
5. All required fields present
6. ArXiv links are valid format
7. Mechanism descriptions not empty

Run this before deploying discoveries.json to production.
"""

import json
import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERIES_PATH = PROJECT_ROOT / "app" / "data" / "discoveries.json"
DATABASE_PATH = PROJECT_ROOT / "database" / "papers.db"

class ValidationError:
    def __init__(self, severity, message):
        self.severity = severity  # 'error' or 'warning'
        self.message = message

    def __str__(self):
        icon = "❌" if self.severity == "error" else "⚠️ "
        return f"{icon} {self.message}"

def validate():
    print("=" * 80)
    print("VALIDATING DISCOVERIES.JSON")
    print("=" * 80)

    errors = []
    warnings = []

    # Load discoveries
    print(f"\n1. Loading discoveries from: {DISCOVERIES_PATH}")
    try:
        with open(DISCOVERIES_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        errors.append(ValidationError('error', f"Failed to load discoveries.json: {e}"))
        return errors, warnings

    discoveries = data.get('verified_isomorphisms', [])
    print(f"   Found {len(discoveries)} discoveries")

    # Connect to database
    print(f"\n2. Connecting to database: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        print("   ✓ Connected")
    except Exception as e:
        errors.append(ValidationError('error', f"Failed to connect to database: {e}"))
        return errors, warnings

    # Track paper usage
    paper_usage = defaultdict(int)
    unique_papers = set()

    print(f"\n3. Validating {len(discoveries)} discoveries...")

    for i, discovery in enumerate(discoveries, 1):
        disc_id = discovery.get('id')

        # Check required discovery fields
        required_disc_fields = ['id', 'rating', 'similarity', 'structural_explanation', 'paper_1', 'paper_2']
        for field in required_disc_fields:
            if field not in discovery:
                errors.append(ValidationError('error', f"Discovery {disc_id}: Missing required field '{field}'"))

        # Validate structural explanation
        if 'structural_explanation' in discovery:
            if not discovery['structural_explanation'] or len(discovery['structural_explanation']) < 50:
                warnings.append(ValidationError('warning', f"Discovery {disc_id}: Structural explanation too short (<50 chars)"))

        # Validate each paper
        for paper_key in ['paper_1', 'paper_2']:
            if paper_key not in discovery:
                continue

            paper = discovery[paper_key]
            paper_id = paper.get('paper_id')

            # Check required paper fields
            required_paper_fields = ['paper_id', 'arxiv_id', 'domain', 'title', 'mechanism']
            for field in required_paper_fields:
                if field not in paper:
                    errors.append(ValidationError('error', f"Discovery {disc_id}, {paper_key}: Missing required field '{field}'"))

            # Track paper usage
            if paper_id:
                paper_usage[paper_id] += 1
                unique_papers.add(paper_id)

            # Validate arxiv_id
            arxiv_id = paper.get('arxiv_id')
            if not arxiv_id or arxiv_id == 'N/A':
                warnings.append(ValidationError('warning', f"Discovery {disc_id}, {paper_key}: arxiv_id is 'N/A' (citation link won't work)"))
            elif arxiv_id:
                # Check arXiv ID format (basic validation)
                if not (arxiv_id.count('.') == 1 and 'v' in arxiv_id):
                    warnings.append(ValidationError('warning', f"Discovery {disc_id}, {paper_key}: arxiv_id format looks unusual: '{arxiv_id}'"))

            # Validate against database
            if paper_id:
                cursor.execute("""
                    SELECT arxiv_id, domain, title
                    FROM papers
                    WHERE id = ?
                """, (paper_id,))

                result = cursor.fetchone()

                if not result:
                    errors.append(ValidationError('error', f"Discovery {disc_id}, {paper_key}: paper_id {paper_id} NOT FOUND in database"))
                else:
                    db_arxiv, db_domain, db_title = result

                    # Check arxiv_id match
                    if arxiv_id != db_arxiv:
                        if arxiv_id == 'N/A' and db_arxiv:
                            errors.append(ValidationError('error', f"Discovery {disc_id}, {paper_key}: arxiv_id is 'N/A' but database has '{db_arxiv}'"))
                        elif arxiv_id and db_arxiv:
                            errors.append(ValidationError('error', f"Discovery {disc_id}, {paper_key}: arxiv_id mismatch (json: '{arxiv_id}', db: '{db_arxiv}')"))

                    # Check domain match
                    if paper.get('domain') != db_domain:
                        errors.append(ValidationError('error', f"Discovery {disc_id}, {paper_key}: domain mismatch (json: '{paper.get('domain')}', db: '{db_domain}')"))

                    # Check title match (allowing for minor differences)
                    if paper.get('title') != db_title:
                        warnings.append(ValidationError('warning', f"Discovery {disc_id}, {paper_key}: title might not match database"))

            # Validate mechanism description
            mechanism = paper.get('mechanism')
            if not mechanism or len(mechanism) < 50:
                warnings.append(ValidationError('warning', f"Discovery {disc_id}, {paper_key}: mechanism description too short (<50 chars)"))

    conn.close()

    # Check for duplicate papers
    print(f"\n4. Checking for paper duplication...")
    print(f"   Unique papers: {len(unique_papers)}")
    print(f"   Total paper references: {len(discoveries) * 2}")

    most_used = sorted(paper_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n   Most frequently used papers:")
    for paper_id, count in most_used:
        print(f"     Paper {paper_id}: used {count} times")
        if count > 5:
            warnings.append(ValidationError('warning', f"Paper {paper_id} used {count} times (unusually high)"))

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total discoveries: {len(discoveries)}")
    print(f"Unique papers: {len(unique_papers)}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"   {error}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")

    if not errors and not warnings:
        print("\n✅ VALIDATION PASSED: No errors or warnings!")
        print("\nDiscoveries.json is ready for production deployment.")
        return 0
    elif errors:
        print(f"\n❌ VALIDATION FAILED: {len(errors)} error(s) must be fixed before deployment")
        return 1
    else:
        print(f"\n⚠️  VALIDATION PASSED WITH WARNINGS: {len(warnings)} warning(s) - review recommended")
        return 0

if __name__ == "__main__":
    exit_code = validate()
    sys.exit(exit_code)

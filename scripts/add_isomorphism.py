#!/usr/bin/env python3
"""
Pipeline for adding new mathematical isomorphisms to the database.
This ensures quality and consistency when adding new discoveries.
"""

import psycopg2
import json
import sys
from datetime import datetime
from typing import Dict, Optional

def connect_db():
    """Connect to PostgreSQL database."""
    db_url = 'postgresql://user@localhost:5432/analog_quest'
    return psycopg2.connect(db_url)

class IsomorphismPipeline:
    """Pipeline for adding and validating isomorphisms."""

    def __init__(self):
        self.conn = connect_db()
        self.required_fields = [
            'title', 'isomorphism_class', 'mathematical_structure',
            'explanation', 'confidence', 'paper_1', 'paper_2'
        ]
        self.isomorphism_classes = [
            'HEAT_EQUATION', 'LOTKA_VOLTERRA', 'ISING_MODEL',
            'HOPF_BIFURCATION', 'KURAMOTO_MODEL', 'PERCOLATION',
            'RANDOM_WALK', 'BRANCHING_PROCESS', 'POWER_LAW',
            'WAVE_EQUATION', 'OTHER'
        ]

    def validate_isomorphism(self, data: Dict) -> tuple[bool, list[str]]:
        """Validate an isomorphism entry."""
        errors = []

        # Check required fields
        for field in self.required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate isomorphism class
        if 'isomorphism_class' in data:
            if data['isomorphism_class'] not in self.isomorphism_classes:
                errors.append(f"Invalid isomorphism_class. Must be one of: {', '.join(self.isomorphism_classes)}")

        # Validate confidence
        if 'confidence' in data:
            try:
                conf = float(data['confidence'])
                if conf < 0 or conf > 1:
                    errors.append("Confidence must be between 0 and 1")
            except ValueError:
                errors.append("Confidence must be a number")

        # Validate papers have required fields
        for paper_num in ['paper_1', 'paper_2']:
            if paper_num in data:
                paper = data[paper_num]
                if not isinstance(paper, dict):
                    errors.append(f"{paper_num} must be a dictionary")
                else:
                    if 'title' not in paper:
                        errors.append(f"{paper_num} missing title")
                    if 'domain' not in paper:
                        errors.append(f"{paper_num} missing domain")

        # Check mathematical structure is not empty
        if 'mathematical_structure' in data:
            if not data['mathematical_structure'].strip():
                errors.append("Mathematical structure cannot be empty")

        return len(errors) == 0, errors

    def check_duplicates(self, data: Dict) -> bool:
        """Check if this isomorphism already exists."""
        cur = self.conn.cursor()

        # Check by title
        cur.execute("""
            SELECT id FROM isomorphisms
            WHERE title = %s
        """, (data['title'],))

        if cur.fetchone():
            return True

        # Check by paper combination
        cur.execute("""
            SELECT i.id
            FROM isomorphisms i
            JOIN isomorphism_papers p1 ON i.id = p1.isomorphism_id AND p1.paper_role = 'source_1'
            JOIN isomorphism_papers p2 ON i.id = p2.isomorphism_id AND p2.paper_role = 'source_2'
            WHERE
                (p1.paper_title = %s AND p2.paper_title = %s)
                OR (p1.paper_title = %s AND p2.paper_title = %s)
        """, (
            data['paper_1']['title'], data['paper_2']['title'],
            data['paper_2']['title'], data['paper_1']['title']
        ))

        return cur.fetchone() is not None

    def add_isomorphism(self, data: Dict) -> int:
        """Add a new isomorphism to the database."""
        cur = self.conn.cursor()

        # Insert into isomorphisms table
        cur.execute("""
            INSERT INTO isomorphisms
            (title, isomorphism_class, mathematical_structure, explanation,
             confidence, verification_status, discovered_session, detailed_proof)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['title'],
            data['isomorphism_class'],
            data['mathematical_structure'],
            data['explanation'],
            data['confidence'],
            data.get('verification_status', 'pending'),
            data.get('discovered_session', 86),
            data.get('detailed_proof', '')
        ))

        iso_id = cur.fetchone()[0]

        # Insert paper 1
        cur.execute("""
            INSERT INTO isomorphism_papers
            (isomorphism_id, paper_role, paper_title, paper_domain,
             paper_arxiv_id, paper_abstract)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            iso_id, 'source_1',
            data['paper_1']['title'],
            data['paper_1']['domain'],
            data['paper_1'].get('arxiv_id'),
            data['paper_1'].get('abstract', '')
        ))

        # Insert paper 2
        cur.execute("""
            INSERT INTO isomorphism_papers
            (isomorphism_id, paper_role, paper_title, paper_domain,
             paper_arxiv_id, paper_abstract)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            iso_id, 'source_2',
            data['paper_2']['title'],
            data['paper_2']['domain'],
            data['paper_2'].get('arxiv_id'),
            data['paper_2'].get('abstract', '')
        ))

        # Also add to discoveries table for compatibility
        cur.execute("""
            INSERT INTO discoveries (id, similarity, rating, explanation, session)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            iso_id,
            data['confidence'],
            data.get('verification_status', 'pending'),
            data['explanation'],
            data.get('discovered_session', 86)
        ))

        self.conn.commit()
        return iso_id

    def add_from_json(self, json_file: str) -> bool:
        """Add isomorphism from a JSON file."""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Validate
            valid, errors = self.validate_isomorphism(data)
            if not valid:
                print("❌ Validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return False

            # Check duplicates
            if self.check_duplicates(data):
                print("❌ This isomorphism appears to already exist")
                return False

            # Add to database
            iso_id = self.add_isomorphism(data)
            print(f"✓ Added isomorphism with ID: {iso_id}")
            print(f"  Title: {data['title']}")
            print(f"  Class: {data['isomorphism_class']}")
            print(f"  Confidence: {data['confidence']}")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False

def create_example_json():
    """Create an example JSON file for new isomorphisms."""
    example = {
        "title": "Example: Network Percolation ↔ Disease Spread",
        "isomorphism_class": "PERCOLATION",
        "mathematical_structure": "P(p) = p^k for critical threshold",
        "explanation": "Both network robustness and disease spread follow percolation theory...",
        "detailed_proof": "Optional: Detailed mathematical proof here...",
        "confidence": 0.85,
        "verification_status": "pending",
        "discovered_session": 87,
        "paper_1": {
            "title": "Network Robustness and Fragility: Percolation on Random Graphs",
            "domain": "physics",
            "arxiv_id": "cond-mat/0007300",
            "abstract": "We study network robustness..."
        },
        "paper_2": {
            "title": "Epidemic Processes in Complex Networks",
            "domain": "epidemiology",
            "arxiv_id": "1408.2701",
            "abstract": "Disease spread on networks..."
        }
    }

    with open('example_isomorphism.json', 'w') as f:
        json.dump(example, f, indent=2)

    print("Created example_isomorphism.json")
    print("Edit this file with your isomorphism details, then run:")
    print("  python3 scripts/add_isomorphism.py example_isomorphism.json")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("ISOMORPHISM ADDITION PIPELINE")
        print("="*60)
        print("\nUsage:")
        print("  python3 scripts/add_isomorphism.py <json_file>")
        print("\nTo create an example JSON file:")
        print("  python3 scripts/add_isomorphism.py --example")
        print("\nRequired JSON fields:")
        print("  - title: Descriptive title")
        print("  - isomorphism_class: HEAT_EQUATION, LOTKA_VOLTERRA, etc.")
        print("  - mathematical_structure: The actual equations")
        print("  - explanation: Why these are isomorphic")
        print("  - confidence: 0.0 to 1.0")
        print("  - paper_1: {title, domain, arxiv_id (optional)}")
        print("  - paper_2: {title, domain, arxiv_id (optional)}")
        return

    if sys.argv[1] == '--example':
        create_example_json()
        return

    pipeline = IsomorphismPipeline()
    success = pipeline.add_from_json(sys.argv[1])

    if success:
        print("\n✓ Isomorphism successfully added to database")
        print("It will appear on the website after deployment")
    else:
        print("\n❌ Failed to add isomorphism")
        sys.exit(1)

if __name__ == "__main__":
    main()
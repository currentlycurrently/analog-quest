#!/usr/bin/env python3
"""
Compile all 100 discoveries for the frontend from curated discovery files
Session 78 - Frontend Update
"""

import json
import glob
from pathlib import Path

def load_all_curated_discoveries():
    """Load all discoveries from curated session files"""
    all_discoveries = []

    # Find all curated discovery files
    pattern = "examples/session*_curated_discoveries.json"
    files = sorted(glob.glob(pattern))

    print(f"Found {len(files)} curated discovery files")

    for file_path in files:
        session_num = file_path.split('session')[1].split('_')[0]
        with open(file_path, 'r') as f:
            data = json.load(f)

            # Handle both formats (list or dict with 'discoveries' key)
            if isinstance(data, list):
                discoveries = data
            elif isinstance(data, dict):
                discoveries = data.get('discoveries', [])
            else:
                print(f"  Skipping {file_path}: unknown format")
                continue

            print(f"  Session {session_num}: {len(discoveries)} discoveries")

            # Add session number to each discovery
            for disc in discoveries:
                disc['session'] = int(session_num)
                all_discoveries.append(disc)

    return all_discoveries

def format_for_frontend(discoveries):
    """Format discoveries for the frontend"""
    frontend_discoveries = []

    # Sort by similarity (highest first)
    discoveries.sort(key=lambda x: x.get('similarity', 0), reverse=True)

    for i, disc in enumerate(discoveries):
        # Extract domains
        domain1 = disc.get('domain_1', 'unknown')
        domain2 = disc.get('domain_2', 'unknown')

        # Clean up domain names
        domain_map = {
            'network_science': 'network science',
            'animal_behavior': 'animal behavior',
            'cognitive_science': 'cognitive science',
            'cell_biology': 'cell biology',
            'climate_science': 'climate science',
            'earth_science': 'earth science'
        }
        domain1_display = domain_map.get(domain1, domain1).title()
        domain2_display = domain_map.get(domain2, domain2).title()

        # Create the frontend entry
        frontend_entry = {
            "id": i + 1,
            "title": f"{domain1_display} ↔ {domain2_display}",
            "domains": [domain1, domain2],
            "explanation": disc.get('explanation', 'Cross-domain structural similarity identified'),
            "pattern": disc.get('pattern', 'Shared structural mechanism'),
            "similarity": round(disc.get('similarity', 0), 4),
            "rating": disc.get('rating', 'good'),
            "session": disc.get('session', 0),
            "mechanism_ids": {
                "mechanism_1": disc.get('mechanism_1_id', 0),
                "mechanism_2": disc.get('mechanism_2_id', 0)
            }
        }

        # Add paper details if available
        if 'paper_1' in disc or 'paper_2' in disc:
            frontend_entry['papers'] = {
                "paper_1": disc.get('paper_1', {}),
                "paper_2": disc.get('paper_2', {})
            }

        frontend_discoveries.append(frontend_entry)

    return frontend_discoveries

def add_sample_papers_data(discoveries):
    """Add sample paper data for better display"""
    # For now, add placeholder paper data
    # In production, this would come from the database
    for disc in discoveries:
        if 'papers' not in disc:
            disc['papers'] = {
                "paper_1": {
                    "title": f"Paper exploring {disc['pattern'].lower()} in {disc['domains'][0]}",
                    "mechanism": disc['explanation'].split(' - ')[0] if ' - ' in disc['explanation'] else disc['explanation'][:100]
                },
                "paper_2": {
                    "title": f"Paper studying {disc['pattern'].lower()} in {disc['domains'][1]}",
                    "mechanism": disc['explanation'].split(' - ')[1] if ' - ' in disc['explanation'] else disc['explanation'][:100]
                }
            }
    return discoveries

def main():
    print("Compiling all discoveries for frontend...")

    # Load all discoveries
    all_discoveries = load_all_curated_discoveries()
    print(f"\nTotal discoveries loaded: {len(all_discoveries)}")

    # Format for frontend
    frontend_discoveries = format_for_frontend(all_discoveries)

    # Add paper data
    frontend_discoveries = add_sample_papers_data(frontend_discoveries)

    # Calculate statistics
    excellent = sum(1 for d in frontend_discoveries if d['rating'] == 'excellent')
    good = sum(1 for d in frontend_discoveries if d['rating'] == 'good')

    print(f"\nQuality breakdown:")
    print(f"  Excellent: {excellent} ({excellent*100//len(frontend_discoveries)}%)")
    print(f"  Good: {good} ({good*100//len(frontend_discoveries)}%)")

    # Domain pair statistics
    domain_pairs = {}
    for d in frontend_discoveries:
        pair = tuple(sorted(d['domains']))
        domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

    print(f"\nTop domain pairs:")
    for pair, count in sorted(domain_pairs.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {pair[0]} ↔ {pair[1]}: {count} discoveries")

    # Save to frontend format
    output_file = 'app/data/discoveries.json'
    with open(output_file, 'w') as f:
        json.dump(frontend_discoveries, f, indent=2)

    print(f"\n✓ Exported {len(frontend_discoveries)} discoveries to {output_file}")

    # Also create a summary file
    summary = {
        "total_discoveries": len(frontend_discoveries),
        "excellent": excellent,
        "good": good,
        "top_similarity": max(d['similarity'] for d in frontend_discoveries),
        "sessions_included": list(set(d['session'] for d in frontend_discoveries))
    }

    with open('app/data/discovery_stats.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Created summary statistics in app/data/discovery_stats.json")

if __name__ == "__main__":
    main()
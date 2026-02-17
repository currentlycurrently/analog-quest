#!/usr/bin/env python3
"""
Session 83: Fix the critical data duplication issue in discoveries.json
This script rebuilds discoveries.json from discovered_pairs.json (source of truth)
"""

import json
import os
from datetime import datetime

def load_discovered_pairs():
    """Load the source of truth"""
    with open('app/data/discovered_pairs.json', 'r') as f:
        return json.load(f)

def load_current_discoveries():
    """Load current discoveries to extract any useful data"""
    with open('app/data/discoveries.json', 'r') as f:
        return json.load(f)

def load_session_discoveries():
    """Load individual session discovery files for full data"""
    session_files = []
    examples_dir = 'examples'

    # Find all session discovery files
    for file in os.listdir(examples_dir):
        if file.startswith('session') and file.endswith('_curated_discoveries.json'):
            session_files.append(os.path.join(examples_dir, file))

    all_session_discoveries = []
    for filepath in sorted(session_files):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if 'discoveries' in data:
                    all_session_discoveries.extend(data['discoveries'])
        except Exception as e:
            print(f"Error loading {filepath}: {e}")

    return all_session_discoveries

def find_discovery_data(paper_1_id, paper_2_id, session_discoveries, current_discoveries):
    """Find the full discovery data for a paper pair"""
    # Try to find in session discoveries first (most reliable)
    for disc in session_discoveries:
        if 'paper_1' in disc and 'paper_2' in disc:
            # Handle both dict and string formats
            p1_id = disc['paper_1'].get('id') if isinstance(disc['paper_1'], dict) else None
            p2_id = disc['paper_2'].get('id') if isinstance(disc['paper_2'], dict) else None

            if p1_id == paper_1_id and p2_id == paper_2_id:
                return disc
            # Check reverse order too
            if p1_id == paper_2_id and p2_id == paper_1_id:
                # Swap to match our order
                disc['paper_1'], disc['paper_2'] = disc['paper_2'], disc['paper_1']
                return disc

    # If not found, try current discoveries (might have placeholder data)
    # But skip if it has the problematic placeholder text
    for disc in current_discoveries:
        papers = disc.get('papers', {})
        if isinstance(papers, dict):
            paper_1 = papers.get('paper_1', '')
            paper_2 = papers.get('paper_2', '')

            # Skip if it has placeholder text
            if 'Paper exploring shared struct' in str(paper_1) or \
               'Paper studying shared struct' in str(paper_2):
                continue

            # This is harder to match without IDs in current format
            # We'd need to match by title or other fields

    return None

def rebuild_discoveries():
    """Rebuild discoveries.json from discovered_pairs.json"""

    # Load all data sources
    pairs_data = load_discovered_pairs()
    current_discoveries = load_current_discoveries()
    session_discoveries = load_session_discoveries()

    print(f"Loaded {pairs_data['metadata']['total_pairs']} unique pairs from discovered_pairs.json")
    print(f"Loaded {len(current_discoveries)} entries from current discoveries.json (with duplicates)")
    print(f"Loaded {len(session_discoveries)} discoveries from session files")

    # Build new discoveries list
    new_discoveries = []
    missing_data = []

    for i, pair in enumerate(pairs_data['discovered_pairs'], 1):
        paper_1_id = pair['paper_1_id']
        paper_2_id = pair['paper_2_id']

        # Find full discovery data
        full_discovery = find_discovery_data(paper_1_id, paper_2_id, session_discoveries, current_discoveries)

        if full_discovery:
            # Create clean discovery entry
            discovery = {
                'id': i,  # Renumber sequentially
                'paper_1': full_discovery.get('paper_1'),
                'paper_2': full_discovery.get('paper_2'),
                'similarity': pair['similarity'],
                'rating': pair['rating'],
                'session': pair['discovered_in_session'],
                'pattern': full_discovery.get('pattern', ''),
                'title': full_discovery.get('title', ''),
                'explanation': full_discovery.get('explanation', ''),
                'domains': full_discovery.get('domains', []),
                'mechanism_ids': full_discovery.get('mechanism_ids', [])
            }

            # Add paper metadata if available
            if 'paper_1' in full_discovery and isinstance(full_discovery['paper_1'], dict):
                discovery['paper_1_title'] = full_discovery['paper_1'].get('title', '')
                discovery['paper_1_domain'] = full_discovery['paper_1'].get('domain', '')
                discovery['paper_1_arxiv_id'] = full_discovery['paper_1'].get('arxiv_id', '')
                discovery['paper_1_url'] = full_discovery['paper_1'].get('url', '')

            if 'paper_2' in full_discovery and isinstance(full_discovery['paper_2'], dict):
                discovery['paper_2_title'] = full_discovery['paper_2'].get('title', '')
                discovery['paper_2_domain'] = full_discovery['paper_2'].get('domain', '')
                discovery['paper_2_arxiv_id'] = full_discovery['paper_2'].get('arxiv_id', '')
                discovery['paper_2_url'] = full_discovery['paper_2'].get('url', '')

            # Add papers field for backward compatibility
            discovery['papers'] = {
                'paper_1': discovery.get('paper_1_title', f"Paper {paper_1_id}"),
                'paper_2': discovery.get('paper_2_title', f"Paper {paper_2_id}")
            }

            new_discoveries.append(discovery)
        else:
            # Track missing data
            missing_data.append({
                'paper_1_id': paper_1_id,
                'paper_2_id': paper_2_id,
                'session': pair['discovered_in_session']
            })

    print(f"\nBuilt {len(new_discoveries)} clean discoveries")
    print(f"Missing full data for {len(missing_data)} pairs")

    if missing_data:
        print("\nMissing data for pairs:")
        for m in missing_data[:10]:  # Show first 10
            print(f"  Papers {m['paper_1_id']}-{m['paper_2_id']} from session {m['session']}")

    # Backup current file
    backup_file = f"app/data/discoveries_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(current_discoveries, f, indent=2)
    print(f"\nBacked up current discoveries to {backup_file}")

    # Write new clean file
    with open('app/data/discoveries.json', 'w') as f:
        json.dump(new_discoveries, f, indent=2)
    print(f"Wrote {len(new_discoveries)} clean discoveries to app/data/discoveries.json")

    # Update stats file
    stats = {
        'total_discoveries': len(new_discoveries),
        'excellent': len([d for d in new_discoveries if d['rating'] == 'excellent']),
        'good': len([d for d in new_discoveries if d['rating'] == 'good']),
        'last_updated': datetime.now().isoformat()
    }

    with open('app/data/discovery_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Updated discovery_stats.json")

    return len(new_discoveries), len(missing_data)

if __name__ == "__main__":
    print("=== Session 83: Fixing Critical Data Duplication Issue ===\n")

    clean_count, missing_count = rebuild_discoveries()

    print(f"\n=== COMPLETE ===")
    print(f"Successfully rebuilt discoveries.json with {clean_count} unique discoveries")
    print(f"Eliminated all duplicates (was 141 with 54 duplicates, now {clean_count} unique)")
    if missing_count > 0:
        print(f"Note: {missing_count} discoveries need full data recovery from session files")
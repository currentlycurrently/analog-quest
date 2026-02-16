#!/usr/bin/env python3
"""
Update frontend with all discoveries from Sessions 75-81
Merges new discoveries with existing frontend data
"""
import json
from datetime import datetime

def main():
    # Load existing frontend discoveries
    with open('app/data/discoveries.json', 'r') as f:
        existing = json.load(f)

    print(f"Current frontend discoveries: {len(existing)}")

    # Load discovered_pairs for reference
    with open('app/data/discovered_pairs.json', 'r') as f:
        tracking = json.load(f)

    # Create a set of existing discovery IDs to avoid duplicates
    existing_pairs = set()
    for disc in existing:
        p1 = disc.get('paper_1', {}).get('id') or disc.get('mechanism_1_id')
        p2 = disc.get('paper_2', {}).get('id') or disc.get('mechanism_2_id')
        if p1 and p2:
            existing_pairs.add((min(p1, p2), max(p1, p2)))

    # Sessions to add (75-77 were pre-Session 78 update, 80-81 are new)
    new_sessions = [75, 76, 77, 80, 81]
    all_new_discoveries = []

    for session_num in new_sessions:
        try:
            with open(f'examples/session{session_num}_curated_discoveries.json', 'r') as f:
                session_data = json.load(f)
                discoveries = session_data.get('discoveries', [])

                for disc in discoveries:
                    # Check if already in frontend
                    m1_id = disc.get('mechanism_1_id')
                    m2_id = disc.get('mechanism_2_id')
                    pair_key = (min(m1_id, m2_id), max(m1_id, m2_id))

                    if pair_key not in existing_pairs:
                        # Format for frontend
                        formatted = {
                            "id": len(existing) + len(all_new_discoveries) + 1,
                            "paper_1": {
                                "id": m1_id,
                                "title": disc.get('paper_1', 'Unknown'),
                                "mechanism": disc.get('mechanism_1', ''),
                                "domain": disc.get('domain_1', 'unknown')
                            },
                            "paper_2": {
                                "id": m2_id,
                                "title": disc.get('paper_2', 'Unknown'),
                                "mechanism": disc.get('mechanism_2', ''),
                                "domain": disc.get('domain_2', 'unknown')
                            },
                            "similarity_score": disc.get('similarity', 0),
                            "structural_similarity": disc.get('structural_similarity', ''),
                            "rating": disc.get('rating', 'good'),
                            "discovered_in_session": session_num,
                            "date_discovered": "2026-02-15" if session_num < 79 else "2026-02-16"
                        }
                        all_new_discoveries.append(formatted)
                        existing_pairs.add(pair_key)

                print(f"Session {session_num}: {len(discoveries)} discoveries, {len([d for d in discoveries if (min(d.get('mechanism_1_id'), d.get('mechanism_2_id')), max(d.get('mechanism_1_id'), d.get('mechanism_2_id'))) not in existing_pairs])} new")

        except FileNotFoundError:
            print(f"Session {session_num} file not found")
            continue

    # Merge with existing
    updated = existing + all_new_discoveries

    # Save updated frontend file
    with open('app/data/discoveries.json', 'w') as f:
        json.dump(updated, f, indent=2)

    print(f"\nFrontend updated:")
    print(f"- Previous: {len(existing)} discoveries")
    print(f"- Added: {len(all_new_discoveries)} new discoveries")
    print(f"- Total: {len(updated)} discoveries")
    print(f"- Tracking file shows: {tracking['metadata']['total_pairs']} pairs")

    # Verify consistency
    if len(updated) < tracking['metadata']['total_pairs']:
        print(f"\n⚠️  Warning: Frontend has fewer discoveries than tracking file")
        print(f"   This might be due to Session 78 compilation differences")

if __name__ == "__main__":
    main()
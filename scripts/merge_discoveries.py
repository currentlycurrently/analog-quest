#!/usr/bin/env python3
"""
Merge discoveries from Sessions 47-57 into the frontend discoveries.json format.

This script:
1. Reads the baseline discoveries.json (30 discoveries from Session 38)
2. Reads discovery files from Sessions 47, 49, 52, 54, 56, 57 (71 new discoveries)
3. Converts all to a unified format
4. Merges into a single discoveries.json with 101 total discoveries
5. Updates metadata and domain pair counts
"""

import json
from pathlib import Path
from collections import Counter

# Base path
BASE_DIR = Path(__file__).parent.parent
EXAMPLES_DIR = BASE_DIR / "examples"
APP_DATA_DIR = BASE_DIR / "app" / "data"

# Input files
BASELINE_FILE = APP_DATA_DIR / "discoveries.json"
SESSION_FILES = {
    47: EXAMPLES_DIR / "session47_verified_discoveries.json",
    49: EXAMPLES_DIR / "session49_curated_discoveries.json",
    52: EXAMPLES_DIR / "session52_curated_discoveries.json",
    54: EXAMPLES_DIR / "session54_curated_discoveries.json",
    56: EXAMPLES_DIR / "session56_curated_discoveries.json",
    57: EXAMPLES_DIR / "session57_curated_discoveries.json",
}

# Output file
OUTPUT_FILE = APP_DATA_DIR / "discoveries.json"


def normalize_domain_pair(domain1: str, domain2: str) -> str:
    """Normalize domain pair to alphabetical order for consistent counting."""
    domains = sorted([domain1, domain2])
    return f"{domains[0]}-{domains[1]}"


def convert_session47_discovery(disc: dict, id_offset: int, discovery_idx: int) -> dict:
    """Convert Session 47 format to unified format."""
    return {
        "id": id_offset + discovery_idx + 1,
        "original_candidate_id": f"session47_{discovery_idx}",
        "rating": disc["rating"],
        "similarity": disc["similarity"],
        "structural_explanation": disc.get("structural_explanation", ""),
        "paper_1": {
            "paper_id": disc["paper_1_id"],
            "arxiv_id": disc.get("arxiv_1", "N/A"),
            "domain": disc["domain_1"],
            "title": disc["title_1"],
            "mechanism": disc["mechanism_1"]
        },
        "paper_2": {
            "paper_id": disc["paper_2_id"],
            "arxiv_id": disc.get("arxiv_2", "N/A"),
            "domain": disc["domain_2"],
            "title": disc["title_2"],
            "mechanism": disc["mechanism_2"]
        }
    }


def convert_session_discovery(disc: dict, id_offset: int, discovery_idx: int, session_num: int) -> dict:
    """Convert Session 49+ format to unified format."""
    # Session 49, 52 format: has paper_1_id, paper_1_domain, etc.
    if "paper_1_id" in disc and "paper_1_domain" in disc:
        return {
            "id": id_offset + discovery_idx + 1,
            "original_candidate_id": f"session{session_num}_{discovery_idx}",
            "rating": disc["rating"],
            "similarity": disc["similarity"],
            "structural_explanation": disc.get("structural_explanation", ""),
            "paper_1": {
                "paper_id": disc["paper_1_id"],
                "arxiv_id": disc.get("paper_1_arxiv", "N/A"),
                "domain": disc.get("paper_1_domain", "unknown"),
                "title": disc.get("paper_1_title", "Untitled"),
                "mechanism": disc.get("paper_1_mechanism", "")
            },
            "paper_2": {
                "paper_id": disc["paper_2_id"],
                "arxiv_id": disc.get("paper_2_arxiv", "N/A"),
                "domain": disc.get("paper_2_domain", "unknown"),
                "title": disc.get("paper_2_title", "Untitled"),
                "mechanism": disc.get("paper_2_mechanism", "")
            }
        }
    # Session 54 format: has domains array, paper_ids array, mechanism_1/2
    elif "domains" in disc and "paper_ids" in disc:
        domains = disc["domains"]
        paper_ids = disc["paper_ids"]
        return {
            "id": id_offset + discovery_idx + 1,
            "original_candidate_id": f"session{session_num}_{disc.get('rank', discovery_idx)}",
            "rating": disc["rating"],
            "similarity": disc["similarity"],
            "structural_explanation": disc.get("structural_explanation", ""),
            "paper_1": {
                "paper_id": paper_ids[0],
                "arxiv_id": "N/A",  # Not provided in this format
                "domain": domains[0],
                "title": disc.get("title", "Untitled"),
                "mechanism": disc.get("mechanism_1", "")
            },
            "paper_2": {
                "paper_id": paper_ids[1],
                "arxiv_id": "N/A",  # Not provided in this format
                "domain": domains[1],
                "title": disc.get("title", "Untitled"),
                "mechanism": disc.get("mechanism_2", "")
            }
        }
    # Session 56, 57 format: has paper_1_id, domain_1, domain_2, title (shared), mechanism_1/2
    elif "paper_1_id" in disc and "domain_1" in disc and "domain_2" in disc:
        return {
            "id": id_offset + discovery_idx + 1,
            "original_candidate_id": f"session{session_num}_{disc.get('rank', discovery_idx)}",
            "rating": disc["rating"],
            "similarity": disc["similarity"],
            "structural_explanation": disc.get("structural_explanation", ""),
            "paper_1": {
                "paper_id": disc["paper_1_id"],
                "arxiv_id": "N/A",  # Not provided in this format
                "domain": disc["domain_1"],
                "title": disc.get("title", "Untitled"),
                "mechanism": disc.get("mechanism_1", "")
            },
            "paper_2": {
                "paper_id": disc["paper_2_id"],
                "arxiv_id": "N/A",  # Not provided in this format
                "domain": disc["domain_2"],
                "title": disc.get("title", "Untitled"),
                "mechanism": disc.get("mechanism_2", "")
            }
        }
    else:
        raise ValueError(f"Unknown discovery format in session {session_num}: keys={list(disc.keys())}")


def main():
    print("=" * 80)
    print("MERGING DISCOVERIES FOR FRONTEND UPDATE")
    print("=" * 80)

    # Load baseline
    print(f"\n1. Loading baseline from {BASELINE_FILE}...")
    with open(BASELINE_FILE, 'r') as f:
        baseline = json.load(f)

    baseline_count = len(baseline["verified_isomorphisms"])
    print(f"   ✓ Loaded {baseline_count} discoveries from Session 38")

    # Start with baseline discoveries
    all_discoveries = baseline["verified_isomorphisms"].copy()
    next_id = baseline_count + 1

    domain_pairs = Counter()

    # Count baseline domain pairs
    for disc in baseline["verified_isomorphisms"]:
        pair = normalize_domain_pair(disc["paper_1"]["domain"], disc["paper_2"]["domain"])
        domain_pairs[pair] += 1

    # Load and merge each session
    print("\n2. Loading new discovery sessions...")

    for session_num, filepath in sorted(SESSION_FILES.items()):
        print(f"   Session {session_num}: {filepath.name}")

        with open(filepath, 'r') as f:
            session_data = json.load(f)

        # Extract discoveries based on format
        if session_num == 47:
            session_discoveries = session_data["verified_discoveries"]
            converted = [
                convert_session47_discovery(disc, next_id - 1, i)
                for i, disc in enumerate(session_discoveries)
            ]
        elif session_num == 49:
            # Session 49 is a plain array
            session_discoveries = session_data if isinstance(session_data, list) else session_data.get("discoveries", [])
            converted = [
                convert_session_discovery(disc, next_id - 1, i, session_num)
                for i, disc in enumerate(session_discoveries)
            ]
        else:
            # Sessions 52, 54, 56, 57
            session_discoveries = session_data.get("discoveries", [])
            converted = [
                convert_session_discovery(disc, next_id - 1, i, session_num)
                for i, disc in enumerate(session_discoveries)
            ]

        # Add to collection
        all_discoveries.extend(converted)
        next_id += len(converted)

        # Count domain pairs
        for disc in converted:
            pair = normalize_domain_pair(disc["paper_1"]["domain"], disc["paper_2"]["domain"])
            domain_pairs[pair] += 1

        print(f"      ✓ Added {len(converted)} discoveries (IDs {next_id - len(converted)}-{next_id - 1})")

    # Calculate statistics
    total_discoveries = len(all_discoveries)
    excellent_count = sum(1 for d in all_discoveries if d["rating"] == "excellent")
    good_count = sum(1 for d in all_discoveries if d["rating"] == "good")

    similarities = [d["similarity"] for d in all_discoveries]
    sim_min = min(similarities)
    sim_max = max(similarities)
    sim_mean = sum(similarities) / len(similarities)

    print(f"\n3. Merged statistics:")
    print(f"   Total discoveries: {total_discoveries}")
    print(f"   Excellent: {excellent_count}")
    print(f"   Good: {good_count}")
    print(f"   Similarity range: {sim_min:.4f} - {sim_max:.4f} (mean: {sim_mean:.4f})")
    print(f"   Domain pairs: {len(domain_pairs)} unique pairs")

    # Create output structure (matching TypeScript types from lib/data.ts)
    output = {
        "metadata": {
            "session": 57,  # Latest session number
            "date": "2026-02-14",
            "description": "Manually curated verified isomorphisms from Sessions 38-57",
            "total_verified": total_discoveries,
            "excellent": excellent_count,
            "good": good_count,
            "similarity_range": {
                "min": sim_min,
                "max": sim_max,
                "mean": sim_mean
            },
            "methodology": "LLM extraction + semantic embeddings (384-dim) + manual curation",
            "selection_criteria": "All excellent + all good discoveries from manual curation"
        },
        "domain_pairs": dict(domain_pairs),
        "verified_isomorphisms": all_discoveries
    }

    # Write output
    print(f"\n4. Writing output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"   ✓ Successfully wrote {total_discoveries} discoveries")

    print("\n" + "=" * 80)
    print("MERGE COMPLETE!")
    print("=" * 80)
    print(f"Output: {OUTPUT_FILE}")
    print(f"Total: {total_discoveries} discoveries (30 baseline + 71 new)")
    print(f"Next: Run 'npm run build' to rebuild the site with {total_discoveries} discovery pages")
    print("=" * 80)


if __name__ == "__main__":
    main()

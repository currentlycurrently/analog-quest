#!/usr/bin/env python3
"""
Session 53: Generate embeddings and match candidates.

Combines:
- 134 existing mechanisms (Sessions 37, 46, 47, 48, 51)
- 36 new mechanisms (Session 53)
= 170 total mechanisms

Generates 384-dim embeddings and finds cross-domain matches.
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Paths
PROJECT_ROOT = Path(__file__).parent.parent

# Input file
ALL_MECHANISMS_PATH = PROJECT_ROOT / "examples" / "session53_all_mechanisms.json"

# Output files
EMBEDDINGS_PATH = PROJECT_ROOT / "examples" / "session53_embeddings.npy"
CANDIDATES_PATH = PROJECT_ROOT / "examples" / "session53_candidates.json"

# Parameters
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.35

def load_mechanisms():
    """Load all 170 mechanisms."""
    print("Loading mechanisms...")

    with open(ALL_MECHANISMS_PATH) as f:
        mechanisms = json.load(f)

    print(f"  Total mechanisms: {len(mechanisms)}")

    # Domain distribution
    domain_counts = {}
    for m in mechanisms:
        domain = m.get('domain', 'unknown')
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    print(f"\n  Domain distribution:")
    for domain in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {domain[0]}: {domain[1]} mechanisms")

    return mechanisms

def generate_embeddings(mechanisms):
    """Generate 384-dim embeddings for all mechanisms."""
    print(f"\nGenerating embeddings using {EMBEDDING_MODEL}...")

    model = SentenceTransformer(EMBEDDING_MODEL)

    # Extract mechanism descriptions (handle both field names)
    descriptions = []
    for m in mechanisms:
        if 'mechanism_description' in m:
            descriptions.append(m['mechanism_description'])
        elif 'mechanism' in m:
            descriptions.append(m['mechanism'])
        else:
            descriptions.append(m.get('description', ''))

    # Generate embeddings
    embeddings = model.encode(descriptions, show_progress_bar=True)

    print(f"  Embedding shape: {embeddings.shape}")
    print(f"  Embedding dimensions: {embeddings.shape[1]}")

    return embeddings

def find_cross_domain_matches(mechanisms, embeddings, threshold=0.35):
    """Find cross-domain matches above similarity threshold."""
    print(f"\nFinding cross-domain matches (threshold ≥{threshold})...")

    n = len(mechanisms)
    candidates = []

    # Compute cosine similarities
    similarities = cosine_similarity(embeddings)

    # Find matches
    for i in range(n):
        for j in range(i + 1, n):
            sim = similarities[i][j]

            # Cross-domain only
            domain_i = mechanisms[i].get('domain', 'unknown')
            domain_j = mechanisms[j].get('domain', 'unknown')

            if domain_i == domain_j:
                continue

            # Threshold filter
            if sim < threshold:
                continue

            # Skip same-paper duplicates
            paper_i = mechanisms[i].get('paper_id')
            paper_j = mechanisms[j].get('paper_id')
            if paper_i == paper_j:
                continue

            # Add candidate
            candidates.append({
                'mechanism_1_idx': i,
                'mechanism_2_idx': j,
                'paper_1_id': paper_i,
                'paper_2_id': paper_j,
                'domain_1': domain_i,
                'domain_2': domain_j,
                'similarity': float(sim),
                'mechanism_1': mechanisms[i].get('mechanism') or mechanisms[i].get('mechanism_description'),
                'mechanism_2': mechanisms[j].get('mechanism') or mechanisms[j].get('mechanism_description')
            })

    # Sort by similarity (highest first)
    candidates.sort(key=lambda x: x['similarity'], reverse=True)

    print(f"  Cross-domain candidates found: {len(candidates)}")

    if candidates:
        print(f"  Top similarity: {candidates[0]['similarity']:.4f}")
        print(f"  Similarity range: {candidates[-1]['similarity']:.4f} - {candidates[0]['similarity']:.4f}")

    return candidates

def analyze_domain_pairs(candidates):
    """Analyze domain pair distribution in candidates."""
    print(f"\nDomain pair distribution:")

    pair_counts = {}
    for c in candidates:
        d1, d2 = sorted([c['domain_1'], c['domain_2']])
        pair = f"{d1}-{d2}"
        pair_counts[pair] = pair_counts.get(pair, 0) + 1

    for pair, count in sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = count / len(candidates) * 100
        print(f"  {pair}: {count} ({pct:.1f}%)")

def main():
    print("=" * 80)
    print("SESSION 53: GENERATE EMBEDDINGS AND MATCH CANDIDATES")
    print("=" * 80)

    # Load mechanisms
    mechanisms = load_mechanisms()

    # Generate embeddings
    embeddings = generate_embeddings(mechanisms)

    # Save embeddings
    np.save(EMBEDDINGS_PATH, embeddings)
    print(f"\nSaved embeddings to: {EMBEDDINGS_PATH.name}")

    # Find cross-domain matches
    candidates = find_cross_domain_matches(mechanisms, embeddings, SIMILARITY_THRESHOLD)

    # Analyze domain pairs
    if candidates:
        analyze_domain_pairs(candidates)

    # Save candidates
    output_data = {
        'metadata': {
            'session': 53,
            'total_mechanisms': len(mechanisms),
            'new_mechanisms_this_session': 36,
            'embedding_model': EMBEDDING_MODEL,
            'embedding_dimensions': embeddings.shape[1],
            'similarity_threshold': SIMILARITY_THRESHOLD,
            'total_candidates': len(candidates),
            'top_similarity': candidates[0]['similarity'] if candidates else None
        },
        'candidates': candidates
    }

    with open(CANDIDATES_PATH, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSaved candidates to: {CANDIDATES_PATH.name}")
    print(f"  File size: {CANDIDATES_PATH.stat().st_size / 1024:.1f} KB")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total mechanisms: 134 → 170 (+36)")
    print(f"Embeddings generated: 170 × {embeddings.shape[1]} dimensions")
    print(f"Cross-domain candidates: {len(candidates)} (threshold ≥{SIMILARITY_THRESHOLD})")
    if candidates:
        print(f"Top similarity: {candidates[0]['similarity']:.4f}")
        print(f"Domains: {candidates[0]['domain_1']} ↔ {candidates[0]['domain_2']}")

    print(f"\n✅ Ready for curation in Session 54!")

if __name__ == "__main__":
    main()

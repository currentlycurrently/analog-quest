#!/usr/bin/env python3
"""
Session 48: Generate embeddings and match candidates.

Combines:
- 90 existing mechanisms (Sessions 37, 46, 47)
- 50 new mechanisms (Session 48)
= 140 total mechanisms

Generates 384-dim embeddings and finds cross-domain matches.
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Paths
PROJECT_ROOT = Path(__file__).parent.parent

# Input files
SESSION37_MECHANISMS = PROJECT_ROOT / "examples" / "session37_all_mechanisms.json"
SESSION48_MECHANISMS = PROJECT_ROOT / "examples" / "session48_extracted_mechanisms.json"

# Output files
ALL_MECHANISMS_PATH = PROJECT_ROOT / "examples" / "session48_all_mechanisms.json"
EMBEDDINGS_PATH = PROJECT_ROOT / "examples" / "session48_embeddings.npy"
CANDIDATES_PATH = PROJECT_ROOT / "examples" / "session48_candidates.json"

# Parameters
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.35

def load_mechanisms():
    """Load all mechanisms from previous sessions."""
    print("Loading existing mechanisms...")

    # Load Session 37/46/47 mechanisms (90 total)
    with open(SESSION37_MECHANISMS) as f:
        existing = json.load(f)

    print(f"  Existing mechanisms: {len(existing)}")

    # Load Session 48 mechanisms (50 new)
    with open(SESSION48_MECHANISMS) as f:
        new_mechanisms = json.load(f)

    print(f"  New mechanisms (Session 48): {len(new_mechanisms)}")

    # Combine
    all_mechanisms = existing + new_mechanisms
    print(f"  Total mechanisms: {len(all_mechanisms)}")

    return all_mechanisms

def generate_embeddings(mechanisms):
    """Generate 384-dim embeddings for all mechanisms."""
    print(f"\nGenerating embeddings using {EMBEDDING_MODEL}...")

    model = SentenceTransformer(EMBEDDING_MODEL)

    # Extract mechanism descriptions (handle both old and new field names)
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
    from sklearn.metrics.pairwise import cosine_similarity
    similarities = cosine_similarity(embeddings)

    # Find matches
    for i in range(n):
        for j in range(i + 1, n):
            sim = similarities[i][j]

            # Cross-domain only
            domain_i = mechanisms[i].get('domain', 'unknown')
            domain_j = mechanisms[j].get('domain', 'unknown')

            if domain_i == domain_j:
                continue  # Skip same-domain

            if sim >= threshold:
                # Get mechanism descriptions (handle both field names)
                mech_1 = mechanisms[i].get('mechanism_description') or mechanisms[i].get('mechanism', '')
                mech_2 = mechanisms[j].get('mechanism_description') or mechanisms[j].get('mechanism', '')

                candidates.append({
                    'paper_1_id': mechanisms[i]['paper_id'],
                    'paper_1_arxiv': mechanisms[i].get('arxiv_id', 'N/A'),
                    'paper_1_domain': domain_i,
                    'paper_1_title': mechanisms[i].get('title', ''),
                    'paper_1_mechanism': mech_1,
                    'paper_2_id': mechanisms[j]['paper_id'],
                    'paper_2_arxiv': mechanisms[j].get('arxiv_id', 'N/A'),
                    'paper_2_domain': domain_j,
                    'paper_2_title': mechanisms[j].get('title', ''),
                    'paper_2_mechanism': mech_2,
                    'similarity': float(sim),
                })

    # Sort by similarity (highest first)
    candidates.sort(key=lambda x: x['similarity'], reverse=True)

    print(f"  Cross-domain candidates found: {len(candidates)}")
    print(f"  Similarity range: {candidates[-1]['similarity']:.4f} - {candidates[0]['similarity']:.4f}")
    print(f"  Top match: {candidates[0]['similarity']:.4f} ({candidates[0]['paper_1_domain']} ↔ {candidates[0]['paper_2_domain']})")

    return candidates

def main():
    print("=" * 80)
    print("SESSION 48: EMBED AND MATCH")
    print("=" * 80)

    # Load mechanisms
    mechanisms = load_mechanisms()

    # Save combined mechanisms
    with open(ALL_MECHANISMS_PATH, 'w') as f:
        json.dump(mechanisms, f, indent=2)
    print(f"\nSaved all mechanisms to: {ALL_MECHANISMS_PATH}")

    # Generate embeddings
    embeddings = generate_embeddings(mechanisms)

    # Save embeddings
    np.save(EMBEDDINGS_PATH, embeddings)
    print(f"Saved embeddings to: {EMBEDDINGS_PATH}")

    # Find matches
    candidates = find_cross_domain_matches(mechanisms, embeddings, SIMILARITY_THRESHOLD)

    # Analyze candidates
    print(f"\n" + "=" * 80)
    print("CANDIDATE ANALYSIS")
    print("=" * 80)

    # Domain pair distribution
    domain_pairs = {}
    for c in candidates:
        pair = tuple(sorted([c['paper_1_domain'], c['paper_2_domain']]))
        domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

    print(f"\nTop domain pairs:")
    for pair, count in sorted(domain_pairs.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {pair[0]} ↔ {pair[1]}: {count} candidates")

    # Similarity distribution
    sim_ranges = {
        '≥0.60': len([c for c in candidates if c['similarity'] >= 0.60]),
        '0.50-0.60': len([c for c in candidates if 0.50 <= c['similarity'] < 0.60]),
        '0.45-0.50': len([c for c in candidates if 0.45 <= c['similarity'] < 0.50]),
        '0.40-0.45': len([c for c in candidates if 0.40 <= c['similarity'] < 0.45]),
        '0.35-0.40': len([c for c in candidates if 0.35 <= c['similarity'] < 0.40]),
    }

    print(f"\nSimilarity distribution:")
    for range_name, count in sim_ranges.items():
        pct = (count / len(candidates)) * 100 if candidates else 0
        print(f"  {range_name}: {count} ({pct:.1f}%)")

    # Save candidates
    output_data = {
        'metadata': {
            'session': 48,
            'total_mechanisms': len(mechanisms),
            'existing_mechanisms': 90,
            'new_mechanisms': 50,
            'similarity_threshold': SIMILARITY_THRESHOLD,
            'total_candidates': len(candidates),
            'top_similarity': candidates[0]['similarity'] if candidates else 0,
            'model': EMBEDDING_MODEL,
        },
        'candidates': candidates,
        'domain_pair_distribution': {f"{k[0]}-{k[1]}": v for k, v in domain_pairs.items()},
        'similarity_distribution': sim_ranges,
    }

    with open(CANDIDATES_PATH, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSaved {len(candidates)} candidates to: {CANDIDATES_PATH}")

    # Top 10 preview
    print(f"\n" + "=" * 80)
    print("TOP 10 CANDIDATES (for manual curation)")
    print("=" * 80)

    for i, c in enumerate(candidates[:10], 1):
        print(f"\n[{i}] Similarity: {c['similarity']:.4f}")
        print(f"    {c['paper_1_domain']} (paper {c['paper_1_id']}) ↔ {c['paper_2_domain']} (paper {c['paper_2_id']})")
        print(f"    {c['paper_1_title'][:70]}...")
        print(f"    {c['paper_2_title'][:70]}...")

    print(f"\n✅ Next step: Manual curation of top 10-15 candidates to reach 50+ discoveries")

if __name__ == "__main__":
    main()

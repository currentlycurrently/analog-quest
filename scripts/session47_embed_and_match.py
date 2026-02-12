#!/usr/bin/env python3
"""
Session 47: Generate embeddings for all 90 mechanisms and find cross-domain matches.

Uses sentence-transformers (all-MiniLM-L6-v2) for 384-dim embeddings.
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MECHANISMS_PATH = PROJECT_ROOT / "examples" / "session47_all_mechanisms.json"
EMBEDDINGS_PATH = PROJECT_ROOT / "examples" / "session47_embeddings.npy"
CANDIDATES_PATH = PROJECT_ROOT / "examples" / "session47_candidates.json"

def main():
    print("=" * 80)
    print("SESSION 47 - EMBEDDING & MATCHING")
    print("=" * 80)

    # Load all mechanisms
    print(f"\n1. Loading mechanisms from {MECHANISMS_PATH}...")
    with open(MECHANISMS_PATH, 'r') as f:
        mechanisms = json.load(f)
    print(f"   Loaded {len(mechanisms)} mechanisms")

    # Extract mechanism texts
    mechanism_texts = [m['mechanism'] for m in mechanisms]

    # Generate embeddings
    print(f"\n2. Generating 384-dim embeddings...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(mechanism_texts, show_progress_bar=True)
    print(f"   Generated embeddings: {embeddings.shape}")

    # Save embeddings
    np.save(EMBEDDINGS_PATH, embeddings)
    print(f"   Saved embeddings to {EMBEDDINGS_PATH}")

    # Compute similarity matrix
    print(f"\n3. Computing cosine similarity matrix...")
    similarity_matrix = cosine_similarity(embeddings)
    print(f"   Similarity matrix: {similarity_matrix.shape}")

    # Find cross-domain matches (threshold >= 0.35)
    print(f"\n4. Finding cross-domain matches (threshold >= 0.35)...")
    candidates = []
    threshold = 0.35

    for i in range(len(mechanisms)):
        for j in range(i+1, len(mechanisms)):
            sim = similarity_matrix[i, j]

            # Only cross-domain matches
            if mechanisms[i]['domain'] == mechanisms[j]['domain']:
                continue

            # Threshold filter
            if sim < threshold:
                continue

            candidates.append({
                'mechanism_1_idx': i,
                'mechanism_2_idx': j,
                'paper_1_id': mechanisms[i].get('paper_id', 'N/A'),
                'paper_2_id': mechanisms[j].get('paper_id', 'N/A'),
                'arxiv_1': mechanisms[i].get('arxiv_id', 'N/A'),
                'arxiv_2': mechanisms[j].get('arxiv_id', 'N/A'),
                'domain_1': mechanisms[i]['domain'],
                'domain_2': mechanisms[j]['domain'],
                'title_1': mechanisms[i].get('title', 'No title'),
                'title_2': mechanisms[j].get('title', 'No title'),
                'mechanism_1': mechanisms[i]['mechanism'],
                'mechanism_2': mechanisms[j]['mechanism'],
                'similarity': float(sim),
                'rating': None,  # To be filled during manual curation
                'structural_explanation': None  # To be filled during manual curation
            })

    # Sort by similarity (highest first)
    candidates.sort(key=lambda x: x['similarity'], reverse=True)

    print(f"   Found {len(candidates)} cross-domain candidates")
    print(f"   Similarity range: {candidates[-1]['similarity']:.4f} - {candidates[0]['similarity']:.4f}")

    # Save candidates
    with open(CANDIDATES_PATH, 'w') as f:
        json.dump({
            'metadata': {
                'total_mechanisms': len(mechanisms),
                'total_candidates': len(candidates),
                'threshold': threshold,
                'max_similarity': candidates[0]['similarity'],
                'min_similarity': candidates[-1]['similarity'],
                'mean_similarity': np.mean([c['similarity'] for c in candidates]),
            },
            'candidates': candidates
        }, f, indent=2)

    print(f"   Saved candidates to {CANDIDATES_PATH}")

    # Show top 10
    print(f"\n5. Top 10 candidates:")
    for i, cand in enumerate(candidates[:10], 1):
        print(f"\n   [{i}] Similarity: {cand['similarity']:.4f}")
        print(f"       {cand['domain_1']} ↔ {cand['domain_2']}")
        print(f"       Paper 1 ({cand['paper_1_id']}): {cand['title_1'][:60]}...")
        print(f"       Paper 2 ({cand['paper_2_id']}): {cand['title_2'][:60]}...")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total mechanisms: {len(mechanisms)}")
    print(f"Cross-domain candidates (≥{threshold}): {len(candidates)}")
    print(f"Top similarity: {candidates[0]['similarity']:.4f}")
    print(f"Mean similarity: {np.mean([c['similarity'] for c in candidates]):.4f}")

    print(f"\nNext step:")
    print(f"Manually curate top 50-100 candidates to select 20-25 best discoveries")

if __name__ == "__main__":
    main()

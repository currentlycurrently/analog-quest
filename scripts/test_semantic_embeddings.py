#!/usr/bin/env python3
"""
Session 35: Semantic Embedding Validation Test

Quick test to validate that semantic embeddings can match
the 9 LLM-extracted mechanisms from Session 34.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def load_mechanisms(input_file):
    """Load the 9 mechanisms from Session 34."""
    with open(input_file, 'r') as f:
        return json.load(f)

def generate_embeddings(mechanisms, model_name='all-MiniLM-L6-v2'):
    """Generate embeddings for all mechanisms."""
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)

    print(f"Generating embeddings for {len(mechanisms)} mechanisms...")
    texts = [m['mechanism'] for m in mechanisms]
    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings

def calculate_similarities(embeddings):
    """Calculate pairwise cosine similarities."""
    return cosine_similarity(embeddings)

def find_cross_domain_pairs(mechanisms, similarities, threshold=0.75):
    """Find cross-domain pairs above threshold."""
    pairs = []

    for i in range(len(mechanisms)):
        for j in range(i+1, len(mechanisms)):
            # Only cross-domain
            if mechanisms[i]['subdomain'] == mechanisms[j]['subdomain']:
                continue

            sim = similarities[i, j]
            pairs.append({
                'paper_1_id': mechanisms[i]['paper_id'],
                'paper_1_subdomain': mechanisms[i]['subdomain'],
                'paper_1_title': mechanisms[i]['title'],
                'paper_1_mechanism': mechanisms[i]['mechanism'],
                'paper_2_id': mechanisms[j]['paper_id'],
                'paper_2_subdomain': mechanisms[j]['subdomain'],
                'paper_2_title': mechanisms[j]['title'],
                'paper_2_mechanism': mechanisms[j]['mechanism'],
                'similarity': float(sim),
                'domain_pair': f"{mechanisms[i]['subdomain']} ↔ {mechanisms[j]['subdomain']}"
            })

    # Sort by similarity descending
    pairs.sort(key=lambda x: -x['similarity'])

    return pairs

def print_similarity_matrix(mechanisms, similarities):
    """Print the full 9x9 similarity matrix."""
    print("\n" + "="*80)
    print("FULL SIMILARITY MATRIX (9x9)")
    print("="*80)

    # Print header
    print(f"{'':10}", end="")
    for i, m in enumerate(mechanisms):
        print(f" {i:6}", end="")
    print()

    # Print rows
    for i, m in enumerate(mechanisms):
        print(f"{i} ({m['subdomain']:10})", end="")
        for j in range(len(mechanisms)):
            if i == j:
                print(f" {'1.000':>6}", end="")
            else:
                print(f" {similarities[i,j]:>6.3f}", end="")
        print()

    print("\nMechanism IDs:")
    for i, m in enumerate(mechanisms):
        print(f"  {i}: ID {m['paper_id']} - {m['subdomain']} - {m['title'][:50]}")

def main():
    """Run embedding validation test."""

    print("="*80)
    print("SESSION 35: SEMANTIC EMBEDDING VALIDATION TEST")
    print("="*80)

    # Load mechanisms
    print("\nStep 1: Loading 9 mechanisms from Session 34...")
    mechanisms = load_mechanisms('examples/session34_llm_mechanisms_final.json')
    print(f"Loaded {len(mechanisms)} mechanisms")

    # Domain breakdown
    domain_counts = {}
    for m in mechanisms:
        domain_counts[m['subdomain']] = domain_counts.get(m['subdomain'], 0) + 1
    print("\nDomain breakdown:")
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count}")

    # Generate embeddings
    print("\nStep 2: Generating semantic embeddings...")
    embeddings = generate_embeddings(mechanisms)
    print(f"Generated embeddings with shape: {embeddings.shape}")

    # Calculate similarities
    print("\nStep 3: Calculating pairwise cosine similarities...")
    similarities = calculate_similarities(embeddings)

    # Print full matrix
    print_similarity_matrix(mechanisms, similarities)

    # Find cross-domain pairs
    print("\nStep 4: Finding cross-domain pairs...")
    all_pairs = find_cross_domain_pairs(mechanisms, similarities, threshold=0.0)
    print(f"Total cross-domain pairs: {len(all_pairs)}")

    # Statistics
    sims = [p['similarity'] for p in all_pairs]
    print(f"\nCross-domain similarity statistics:")
    print(f"  Max: {max(sims):.3f}")
    print(f"  Mean: {np.mean(sims):.3f}")
    print(f"  Median: {np.median(sims):.3f}")
    print(f"  Min: {min(sims):.3f}")

    # Count above different thresholds
    print(f"\nNumber of cross-domain pairs above different thresholds:")
    for thresh in [0.85, 0.80, 0.75, 0.70, 0.65, 0.60]:
        count = sum(1 for s in sims if s >= thresh)
        print(f"  ≥{thresh}: {count}")

    # Show top 10 pairs
    print("\n" + "="*80)
    print("TOP 10 CROSS-DOMAIN PAIRS BY EMBEDDING SIMILARITY")
    print("="*80)
    for i, pair in enumerate(all_pairs[:10]):
        print(f"\n{i+1}. Similarity: {pair['similarity']:.3f}")
        print(f"   Domain Pair: {pair['domain_pair']}")
        print(f"   Paper 1 (ID {pair['paper_1_id']}): {pair['paper_1_title'][:60]}")
        print(f"   Paper 2 (ID {pair['paper_2_id']}): {pair['paper_2_title'][:60]}")
        print(f"   Mechanism 1: {pair['paper_1_mechanism'][:100]}...")
        print(f"   Mechanism 2: {pair['paper_2_mechanism'][:100]}...")

    # Save results
    output_file = 'examples/session35_embedding_test_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'total_mechanisms': len(mechanisms),
            'total_cross_domain_pairs': len(all_pairs),
            'similarity_stats': {
                'max': float(max(sims)),
                'mean': float(np.mean(sims)),
                'median': float(np.median(sims)),
                'min': float(min(sims))
            },
            'top_10_pairs': all_pairs[:10]
        }, f, indent=2)

    print(f"\n\nResults saved to {output_file}")

    # Decision recommendation
    print("\n" + "="*80)
    print("QUICK ASSESSMENT")
    print("="*80)
    high_quality = sum(1 for s in sims if s >= 0.75)
    medium_quality = sum(1 for s in sims if 0.70 <= s < 0.75)

    if high_quality >= 2:
        print("✅ SUCCESS: Found ≥2 pairs with similarity ≥0.75")
        print("   Recommendation: Proceed to scale embeddings to all papers")
    elif high_quality + medium_quality >= 2:
        print("⚠️ PARTIAL SUCCESS: Found matches at 0.70-0.75 range")
        print("   Recommendation: Review quality, consider lowering threshold")
    else:
        print("❌ EMBEDDINGS DON'T WORK: No high-similarity pairs found")
        print("   Recommendation: Rethink approach")

    print("\nNext: Manual review of top pairs in SESSION35_EMBEDDING_TEST.md")

if __name__ == '__main__':
    main()

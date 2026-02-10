#!/usr/bin/env python3
"""
Session 36: Generate embeddings for diverse mechanisms and find cross-domain matches.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load mechanisms
with open('examples/session36_diverse_mechanisms.json', 'r') as f:
    mechanisms = json.load(f)

print(f"Loaded {len(mechanisms)} mechanisms")

# Generate embeddings using all-MiniLM-L6-v2 (384-dim, same as Session 35)
model = SentenceTransformer('all-MiniLM-L6-v2')

mechanism_texts = [m['mechanism'] for m in mechanisms]
embeddings = model.encode(mechanism_texts)

print(f"Generated {len(embeddings)} embeddings (shape: {embeddings.shape})")

# Calculate pairwise cosine similarities (CROSS-DOMAIN ONLY)
all_similarities = []

for i in range(len(mechanisms)):
    for j in range(i+1, len(mechanisms)):
        # Only cross-domain pairs
        domain_i = mechanisms[i]['domain']
        domain_j = mechanisms[j]['domain']

        if domain_i != domain_j:
            sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            all_similarities.append({
                'paper_1_id': mechanisms[i]['paper_id'],
                'paper_1_domain': domain_i,
                'paper_1_title': mechanisms[i]['title'],
                'paper_1_mechanism': mechanisms[i]['mechanism'],
                'paper_2_id': mechanisms[j]['paper_id'],
                'paper_2_domain': domain_j,
                'paper_2_title': mechanisms[j]['title'],
                'paper_2_mechanism': mechanisms[j]['mechanism'],
                'similarity': float(sim)
            })

# Sort by similarity (descending)
all_similarities.sort(key=lambda x: x['similarity'], reverse=True)

print(f"\nTotal cross-domain pairs: {len(all_similarities)}")

# Statistics
similarities_values = [s['similarity'] for s in all_similarities]
print(f"Max similarity: {max(similarities_values):.4f}")
print(f"Mean similarity: {np.mean(similarities_values):.4f}")
print(f"Median similarity: {np.median(similarities_values):.4f}")
print(f"Min similarity: {min(similarities_values):.4f}")

# Threshold analysis
thresholds = [0.75, 0.70, 0.65, 0.60, 0.55]
print("\nThreshold analysis:")
for thresh in thresholds:
    count = sum(1 for s in similarities_values if s >= thresh)
    print(f"  ≥{thresh:.2f}: {count} pairs")

# Save top 20 matches
top_20 = all_similarities[:20]
with open('examples/session36_embedding_matches.json', 'w') as f:
    json.dump({
        'total_cross_domain_pairs': len(all_similarities),
        'statistics': {
            'max_similarity': float(max(similarities_values)),
            'mean_similarity': float(np.mean(similarities_values)),
            'median_similarity': float(np.median(similarities_values)),
            'min_similarity': float(min(similarities_values))
        },
        'threshold_counts': {
            f'ge_{thresh:.2f}'.replace('.', '_'): sum(1 for s in similarities_values if s >= thresh)
            for thresh in thresholds
        },
        'top_20_matches': top_20
    }, f, indent=2)

print(f"\nSaved results to examples/session36_embedding_matches.json")

# Print top 10 for quick review
print("\n=== TOP 10 MATCHES ===")
for i, match in enumerate(top_20[:10], 1):
    print(f"\n{i}. Similarity: {match['similarity']:.4f}")
    print(f"   [{match['paper_1_domain']}] {match['paper_1_title']}")
    print(f"   [{match['paper_2_domain']}] {match['paper_2_title']}")

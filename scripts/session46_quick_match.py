#!/usr/bin/env python3
"""
Quick workflow test for Session 46:
1. Combine existing 54 mechanisms + 5 new = 59 total
2. Generate embeddings (384-dim)
3. Find cross-domain matches (threshold ≥0.35)
4. Output top 10 candidates for quick review
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Load existing 54 mechanisms from Session 37
with open(PROJECT_ROOT / "examples" / "session37_all_mechanisms.json") as f:
    existing = json.load(f)

print(f"Loaded {len(existing)} existing mechanisms (Session 37)")

# Load 5 new mechanisms from Session 46
with open(PROJECT_ROOT / "examples" / "session46_extracted_mechanisms.json") as f:
    new_data = json.load(f)
    new = new_data['mechanisms']

print(f"Loaded {len(new)} new mechanisms (Session 46)")

# Normalize domain field (existing have 'subdomain', new have 'domain')
for m in existing:
    if 'subdomain' in m and 'domain' not in m:
        m['domain'] = m['subdomain'].split('.')[0] if '.' in m['subdomain'] else m['subdomain']

# Combine
all_mechanisms = existing + new
print(f"Total: {len(all_mechanisms)} mechanisms")

# Generate embeddings
print(f"\nGenerating embeddings...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

texts = [m['mechanism'] for m in all_mechanisms]
embeddings = model.encode(texts, show_progress_bar=True)

print(f"Embeddings shape: {embeddings.shape}")

# Find cross-domain matches
print(f"\nFinding cross-domain matches (threshold ≥0.35)...")

similarity_matrix = cosine_similarity(embeddings)
candidates = []

for i in range(len(all_mechanisms)):
    for j in range(i + 1, len(all_mechanisms)):
        sim = similarity_matrix[i, j]

        # Cross-domain only
        if all_mechanisms[i]['domain'] == all_mechanisms[j]['domain']:
            continue

        # Threshold ≥0.35
        if sim < 0.35:
            continue

        candidates.append({
            'mechanism_1_id': i,
            'mechanism_2_id': j,
            'similarity': float(sim),
            'paper_1': all_mechanisms[i],
            'paper_2': all_mechanisms[j],
        })

# Sort by similarity
candidates.sort(key=lambda x: x['similarity'], reverse=True)

print(f"Found {len(candidates)} cross-domain candidates")
print(f"Similarity range: {candidates[-1]['similarity']:.3f} - {candidates[0]['similarity']:.3f}")

# Top 10
print(f"\nTop 10 candidates for quick review:\n")
for i, c in enumerate(candidates[:10], 1):
    p1 = c['paper_1']
    p2 = c['paper_2']
    print(f"[{i}] Similarity: {c['similarity']:.3f}")
    print(f"    Domains: {p1['domain']} ↔ {p2['domain']}")
    print(f"    Paper 1 ({p1['paper_id']}): {p1['title'][:60]}...")
    print(f"    Paper 2 ({p2['paper_id']}): {p2['title'][:60]}...")
    print()

# Save all candidates
output_path = PROJECT_ROOT / "examples" / "session46_candidates.json"
with open(output_path, 'w') as f:
    json.dump({
        'metadata': {
            'total_mechanisms': len(all_mechanisms),
            'existing_mechanisms': len(existing),
            'new_mechanisms': len(new),
            'total_candidates': len(candidates),
            'threshold': 0.35,
        },
        'candidates': candidates[:50],  # Top 50
    }, f, indent=2)

print(f"Saved top 50 candidates to: {output_path}")
print(f"\nNext: Manually review top 10 and select 3-5 best for validation")

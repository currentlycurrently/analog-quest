#!/usr/bin/env python3
"""
Session 37 Part 3: Generate semantic embeddings for all mechanisms.

Combines mechanisms from Sessions 34, 36, and 37.
Uses sentence-transformers (all-MiniLM-L6-v2) to generate 384-dim embeddings.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

def main():
    # Load all mechanisms
    all_mechanisms = []

    files = [
        'examples/session34_llm_mechanisms_final.json',
        'examples/session36_diverse_mechanisms.json',
        'examples/session37_new_mechanisms.json'
    ]

    for filename in files:
        try:
            with open(filename, 'r') as f:
                mechs = json.load(f)
                all_mechanisms.extend(mechs)
                print(f"Loaded {len(mechs)} mechanisms from {filename}")
        except FileNotFoundError:
            print(f"Warning: {filename} not found, skipping")

    print(f"\nTotal mechanisms: {len(all_mechanisms)}")

    # Load sentence transformer model
    print("Loading sentence-transformers model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Extract mechanism texts
    mechanism_texts = [m['mechanism'] for m in all_mechanisms]

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(mechanism_texts, show_progress_bar=True)

    # Save embeddings
    np.save('examples/session37_embeddings.npy', embeddings)
    print(f"\nEmbeddings shape: {embeddings.shape}")
    print(f"Saved to: examples/session37_embeddings.npy")

    # Save mechanism metadata for reference
    with open('examples/session37_all_mechanisms.json', 'w') as f:
        json.dump(all_mechanisms, f, indent=2)
    print(f"Saved {len(all_mechanisms)} mechanisms to: examples/session37_all_mechanisms.json")

    # Print summary by domain
    domain_counts = {}
    for m in all_mechanisms:
        domain = m['domain']
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    print(f"\nMechanisms by domain:")
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {domain}: {count}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Find potentially genuine structural matches by filtering out technique-based matches.
"""

import sqlite3
import json
import re

# Technique terms that indicate same-technique matches
TECHNIQUE_TERMS = {
    # ML techniques
    'gnn', 'graph neural network', 'transformer', 'attention', 'self-attention',
    'lstm', 'rnn', 'cnn', 'resnet', 'bert', 'gpt', 'neural network',
    'deep learning', 'machine learning', 'reinforcement learning',

    # Physics techniques
    'black hole', 'renormalization group', 'quantum field theory',
    'lattice gauge', 'monte carlo', 'path integral',

    # Math techniques
    'fourier transform', 'wavelet', 'singular value decomposition',

    # Generic ML terms
    'latent', 'embedding', 'encoder', 'decoder', 'autoencoder',
    'generative model', 'diffusion model', 'variational',
}

def has_technique_overlap(text1, text2):
    """Check if two texts share technique-specific terms."""
    text1_lower = text1.lower()
    text2_lower = text2.lower()

    shared_terms = []
    for term in TECHNIQUE_TERMS:
        if term in text1_lower and term in text2_lower:
            shared_terms.append(term)

    return len(shared_terms) > 0, shared_terms

def main():
    conn = sqlite3.connect('database/papers.db')
    cursor = conn.cursor()

    # Query medium-high similarity matches (0.77-0.85)
    query = """
    SELECT i.id, i.similarity_score,
           p1.domain, p1.subdomain, p1.title as title1,
           p2.domain, p2.subdomain, p2.title as title2,
           pat1.structural_description as pattern1,
           pat2.structural_description as pattern2
    FROM isomorphisms i
    JOIN patterns pat1 ON i.pattern_1_id = pat1.id
    JOIN patterns pat2 ON i.pattern_2_id = pat2.id
    JOIN papers p1 ON pat1.paper_id = p1.id
    JOIN papers p2 ON pat2.paper_id = p2.id
    WHERE i.similarity_score >= 0.77 AND i.similarity_score < 0.85
    ORDER BY i.similarity_score DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    print(f"Total matches in 0.77-0.85 range: {len(rows)}")
    print()

    clean_matches = []
    technique_matches = []

    for row in rows:
        match_id, similarity, dom1, subdom1, title1, dom2, subdom2, title2, pattern1, pattern2 = row

        # Check for technique overlap in titles and patterns
        combined1 = f"{title1} {pattern1}"
        combined2 = f"{title2} {pattern2}"

        has_overlap, shared_terms = has_technique_overlap(combined1, combined2)

        if has_overlap:
            technique_matches.append({
                'id': match_id,
                'similarity': similarity,
                'shared_terms': shared_terms,
                'domains': f"{dom1}.{subdom1} ↔ {dom2}.{subdom2}",
                'title1': title1,
                'title2': title2
            })
        else:
            clean_matches.append({
                'id': match_id,
                'similarity': similarity,
                'domains': f"{dom1}.{subdom1} ↔ {dom2}.{subdom2}",
                'title1': title1,
                'title2': title2,
                'pattern1': pattern1[:200],
                'pattern2': pattern2[:200]
            })

    print(f"Technique matches: {len(technique_matches)} ({len(technique_matches)/len(rows)*100:.1f}%)")
    print(f"Clean matches: {len(clean_matches)} ({len(clean_matches)/len(rows)*100:.1f}%)")
    print()

    print("=" * 80)
    print("TOP 20 CLEAN MATCHES (No obvious technique overlap):")
    print("=" * 80)

    for i, match in enumerate(clean_matches[:20], 1):
        print(f"\n{i}. Match #{match['id']} (similarity: {match['similarity']:.3f})")
        print(f"   Domains: {match['domains']}")
        print(f"   Paper 1: {match['title1']}")
        print(f"   Paper 2: {match['title2']}")
        print(f"   Pattern 1: {match['pattern1']}...")
        print(f"   Pattern 2: {match['pattern2']}...")

    # Save to file
    with open('examples/session33_clean_matches.json', 'w') as f:
        json.dump({
            'total_matches': len(rows),
            'technique_matches': len(technique_matches),
            'clean_matches': len(clean_matches),
            'top_20_clean': clean_matches[:20]
        }, f, indent=2)

    print(f"\n\nSaved to examples/session33_clean_matches.json")

    conn.close()

if __name__ == '__main__':
    main()

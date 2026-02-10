#!/usr/bin/env python3
"""
Match extracted LLM mechanisms for Session 34.

Uses cosine similarity on mechanism text (V2.2 approach).
Filters for cross-domain matches only (different subdomains).
Threshold: ≥0.77 similarity.
"""

import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_mechanisms(input_file):
    """Load extracted mechanisms."""
    with open(input_file, 'r') as f:
        return json.load(f)

def compute_similarities(mechanisms):
    """Compute pairwise cosine similarities."""

    # Extract mechanism texts
    texts = [m['mechanism'] for m in mechanisms]

    # Vectorize using TF-IDF
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words='english',
        min_df=1
    )

    tfidf_matrix = vectorizer.fit_transform(texts)

    # Compute cosine similarities
    similarities = cosine_similarity(tfidf_matrix)

    return similarities

def find_cross_domain_matches(mechanisms, similarities, threshold=0.77):
    """Find cross-domain matches above threshold."""

    matches = []

    for i in range(len(mechanisms)):
        for j in range(i+1, len(mechanisms)):
            # Check if cross-domain (different subdomains)
            if mechanisms[i]['subdomain'] == mechanisms[j]['subdomain']:
                continue  # Skip same-domain matches

            similarity = similarities[i, j]

            if similarity >= threshold:
                matches.append({
                    'paper_1_id': mechanisms[i]['paper_id'],
                    'paper_1_subdomain': mechanisms[i]['subdomain'],
                    'paper_1_title': mechanisms[i]['title'],
                    'paper_1_mechanism': mechanisms[i]['mechanism'],
                    'paper_2_id': mechanisms[j]['paper_id'],
                    'paper_2_subdomain': mechanisms[j]['subdomain'],
                    'paper_2_title': mechanisms[j]['title'],
                    'paper_2_mechanism': mechanisms[j]['mechanism'],
                    'similarity': float(similarity),
                    'domain_pair': f"{mechanisms[i]['subdomain']} ↔ {mechanisms[j]['subdomain']}"
                })

    # Sort by similarity descending
    matches.sort(key=lambda x: -x['similarity'])

    return matches

def main():
    """Match LLM-extracted mechanisms."""

    print("Loading mechanisms...")
    mechanisms = load_mechanisms('examples/session34_llm_mechanisms_final.json')
    print(f"Loaded {len(mechanisms)} mechanisms")

    print("\nDomain breakdown:")
    domain_counts = {}
    for m in mechanisms:
        domain_counts[m['subdomain']] = domain_counts.get(m['subdomain'], 0) + 1
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count}")

    print("\nComputing pairwise similarities...")
    similarities = compute_similarities(mechanisms)
    print(f"Computed {len(mechanisms) * (len(mechanisms)-1) // 2} pairwise similarities")

    print("\nFinding cross-domain matches (≥0.77 threshold)...")
    matches = find_cross_domain_matches(mechanisms, similarities, threshold=0.77)
    print(f"Found {len(matches)} cross-domain matches")

    # Save matches
    output_file = 'examples/session34_candidate_matches.json'
    with open(output_file, 'w') as f:
        json.dump(matches, f, indent=2)

    print(f"\nSaved matches to {output_file}")

    # Show summary
    if matches:
        print("\nMatch summary:")
        print(f"  Total matches: {len(matches)}")
        print(f"  Top similarity: {matches[0]['similarity']:.3f}")
        print(f"  Average similarity: {np.mean([m['similarity'] for m in matches]):.3f}")
        print(f"  Median similarity: {np.median([m['similarity'] for m in matches]):.3f}")

        print("\nTop 5 matches:")
        for i, match in enumerate(matches[:5]):
            print(f"\n  {i+1}. Similarity: {match['similarity']:.3f}")
            print(f"     {match['domain_pair']}")
            print(f"     Paper 1 (ID {match['paper_1_id']}): {match['paper_1_title'][:60]}")
            print(f"     Paper 2 (ID {match['paper_2_id']}): {match['paper_2_title'][:60]}")

        # Domain pair statistics
        print("\nDomain pairs:")
        domain_pairs = {}
        for match in matches:
            pair = match['domain_pair']
            domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

        for pair, count in sorted(domain_pairs.items(), key=lambda x: -x[1]):
            print(f"  {pair}: {count}")

    else:
        print("\nNo matches found above threshold!")

if __name__ == '__main__':
    main()

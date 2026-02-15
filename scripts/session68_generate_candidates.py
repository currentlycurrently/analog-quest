#!/usr/bin/env python3

import json
import psycopg2
from psycopg2.extras import RealDictCursor

def get_cross_domain_candidates(threshold=0.35):
    """Get cross-domain candidate pairs from PostgreSQL using pgvector"""

    conn = psycopg2.connect(
        dbname="analog_quest",
        user="user",
        host="localhost"
    )

    # Query for cross-domain pairs with cosine similarity >= threshold
    # Using cosine distance operator <=> (where 0 is identical, 2 is opposite)
    # So we need similarity >= 0.35 means distance <= 0.65
    max_distance = 1 - threshold

    query = """
    WITH mechanism_pairs AS (
        SELECT
            m1.id as mechanism_1_id,
            m2.id as mechanism_2_id,
            m1.paper_id as paper_1_id,
            m2.paper_id as paper_2_id,
            p1.domain as domain_1,
            p2.domain as domain_2,
            p1.subdomain as subdomain_1,
            p2.subdomain as subdomain_2,
            p1.title as title_1,
            p2.title as title_2,
            m1.mechanism as mechanism_1,
            m2.mechanism as mechanism_2,
            1 - (m1.embedding <=> m2.embedding) as similarity
        FROM mechanisms m1
        CROSS JOIN mechanisms m2
        LEFT JOIN papers p1 ON m1.paper_id = p1.id
        LEFT JOIN papers p2 ON m2.paper_id = p2.id
        WHERE m1.id < m2.id  -- Avoid duplicates and self-matches
        AND m1.embedding <=> m2.embedding <= %s  -- Cosine distance threshold
        AND (p1.domain != p2.domain OR p1.domain IS NULL OR p2.domain IS NULL)  -- Cross-domain only
    )
    SELECT * FROM mechanism_pairs
    ORDER BY similarity DESC
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (max_distance,))
        candidates = cur.fetchall()

    conn.close()

    return candidates

def analyze_candidates(candidates):
    """Analyze the candidate pairs"""

    # Domain pair analysis
    domain_pairs = {}
    for c in candidates:
        domain1 = c['domain_1'] or 'unknown'
        domain2 = c['domain_2'] or 'unknown'

        # Sort to ensure consistent ordering
        pair = tuple(sorted([domain1, domain2]))
        domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

    # Similarity distribution
    similarities = [c['similarity'] for c in candidates]
    if similarities:
        max_sim = max(similarities)
        min_sim = min(similarities)
        avg_sim = sum(similarities) / len(similarities)
    else:
        max_sim = min_sim = avg_sim = 0

    # Count by similarity ranges
    ranges = {
        '0.70-1.00': 0,
        '0.60-0.69': 0,
        '0.50-0.59': 0,
        '0.40-0.49': 0,
        '0.35-0.39': 0
    }

    for sim in similarities:
        if sim >= 0.70:
            ranges['0.70-1.00'] += 1
        elif sim >= 0.60:
            ranges['0.60-0.69'] += 1
        elif sim >= 0.50:
            ranges['0.50-0.59'] += 1
        elif sim >= 0.40:
            ranges['0.40-0.49'] += 1
        elif sim >= 0.35:
            ranges['0.35-0.39'] += 1

    return {
        'total_candidates': len(candidates),
        'max_similarity': max_sim,
        'min_similarity': min_sim,
        'avg_similarity': avg_sim,
        'domain_pairs': domain_pairs,
        'similarity_ranges': ranges
    }

def check_duplicates():
    """Check against already discovered pairs"""
    try:
        with open('app/data/discovered_pairs.json', 'r') as f:
            discovered = json.load(f)

        discovered_pairs = set()
        for pair in discovered.get('discovered_pairs', []):
            # Add both orderings to the set
            discovered_pairs.add((pair['paper_1_id'], pair['paper_2_id']))
            discovered_pairs.add((pair['paper_2_id'], pair['paper_1_id']))

        return discovered_pairs
    except FileNotFoundError:
        print("Warning: discovered_pairs.json not found")
        return set()

def save_candidates(candidates):
    """Save candidates to JSON file"""

    # Check for duplicates
    discovered_pairs = check_duplicates()

    # Filter out already discovered pairs
    new_candidates = []
    duplicate_count = 0

    for c in candidates:
        pair = (c['paper_1_id'], c['paper_2_id'])
        if pair not in discovered_pairs:
            new_candidates.append({
                'mechanism_1_id': c['mechanism_1_id'],
                'mechanism_2_id': c['mechanism_2_id'],
                'paper_1_id': c['paper_1_id'],
                'paper_2_id': c['paper_2_id'],
                'domain_1': c['domain_1'] or 'unknown',
                'domain_2': c['domain_2'] or 'unknown',
                'subdomain_1': c['subdomain_1'] or 'unknown',
                'subdomain_2': c['subdomain_2'] or 'unknown',
                'title_1': c['title_1'],
                'title_2': c['title_2'],
                'mechanism_1': c['mechanism_1'],
                'mechanism_2': c['mechanism_2'],
                'similarity': round(c['similarity'], 4)
            })
        else:
            duplicate_count += 1

    # Analyze new candidates only
    analysis = analyze_candidates(new_candidates)

    # Convert domain_pairs tuples to strings for JSON serialization
    domain_pairs_str = {}
    for pair, count in analysis['domain_pairs'].items():
        key = f"{pair[0]}-{pair[1]}"
        domain_pairs_str[key] = count
    analysis['domain_pairs'] = domain_pairs_str

    output = {
        'session': 68,
        'total_mechanisms': 233,
        'threshold': 0.35,
        'total_candidates': len(new_candidates),
        'duplicates_filtered': duplicate_count,
        'analysis': analysis,
        'candidates': new_candidates[:1000]  # Limit to top 1000
    }

    with open('examples/session68_candidates.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Saved {len(new_candidates)} new candidates to session68_candidates.json")
    if duplicate_count > 0:
        print(f"Filtered out {duplicate_count} already discovered pairs")

    return output

def main():
    # Get cross-domain candidates
    print("Generating cross-domain candidates from PostgreSQL...")
    candidates = get_cross_domain_candidates(threshold=0.35)

    print(f"Found {len(candidates)} total cross-domain candidates (threshold >= 0.35)")

    # Save to file
    output = save_candidates(candidates)

    # Print analysis
    analysis = output['analysis']
    print(f"\nCandidate Analysis (after filtering duplicates):")
    print(f"  Total new candidates: {analysis['total_candidates']}")
    print(f"  Max similarity: {analysis['max_similarity']:.4f}")
    print(f"  Min similarity: {analysis['min_similarity']:.4f}")
    print(f"  Avg similarity: {analysis['avg_similarity']:.4f}")

    print(f"\nSimilarity ranges:")
    for range_name, count in sorted(analysis['similarity_ranges'].items(), reverse=True):
        print(f"  {range_name}: {count} candidates")

    print(f"\nTop domain pairs:")
    sorted_pairs = sorted(analysis['domain_pairs'].items(), key=lambda x: x[1], reverse=True)
    for pair, count in sorted_pairs[:10]:
        print(f"  {pair[0]}-{pair[1]}: {count} candidates")

if __name__ == "__main__":
    main()
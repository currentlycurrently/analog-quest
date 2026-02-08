"""
Cross-domain isomorphism matching V3 with improved confidence scoring.

Session 16: Added multi-factor confidence scoring including:
- Text similarity (50% weight)
- Domain distance (20% weight) - cross-domain matches score higher
- Mathematical content (15% weight) - equations are strong evidence
- Structural depth (15% weight) - more detailed patterns more reliable

Also filters false positives marked by false_positive_filter.py.
"""

import sqlite3
from collections import Counter
from tqdm import tqdm
import sys
sys.path.append('scripts')
from synonyms import normalize_mechanism_type, has_high_value_terms, has_only_generic_overlap

def get_domain_distance(domain1, domain2):
    """
    Returns 0.0-1.0 score for how distant two domains are.
    More distant = higher score = more interesting match.
    """
    # Same domain = 0 (not interesting for cross-domain discovery)
    if domain1 == domain2:
        return 0.0

    # Related domains within same family = 0.3-0.4
    related_groups = [
        {'cs.AI', 'cs.LG', 'cs.NE', 'stat.ML', 'cs.CL', 'cs.CV'},  # ML family
        {'physics.comp-ph', 'cond-mat', 'physics.flu-dyn', 'physics.plasm-ph', 'physics.geo-ph'},  # Physics
        {'q-bio.BM', 'q-bio.CB', 'q-bio.MN', 'q-bio.SC', 'q-bio.TO'},  # Biology
        {'math.OC', 'math.PR', 'stat.TH', 'math.NA', 'math.DS'},  # Math/Stats
        {'econ.GN', 'econ.EM', 'q-fin'},  # Economics/Finance
    ]

    for group in related_groups:
        if domain1 in group and domain2 in group:
            return 0.4

    # Different top-level domains = 0.7-1.0 (most interesting!)
    domain1_prefix = domain1.split('.')[0] if '.' in domain1 else domain1
    domain2_prefix = domain2.split('.')[0] if '.' in domain2 else domain2

    # Cross-domain distance matrix
    distance_matrix = {
        ('cs', 'physics'): 0.8,
        ('cs', 'q-bio'): 0.9,
        ('cs', 'math'): 0.7,
        ('cs', 'econ'): 0.85,
        ('physics', 'q-bio'): 0.9,
        ('physics', 'math'): 0.7,
        ('physics', 'econ'): 0.85,
        ('q-bio', 'math'): 0.8,
        ('q-bio', 'econ'): 0.9,
        ('math', 'econ'): 0.75,
        ('cond-mat', 'cs'): 0.8,
        ('cond-mat', 'q-bio'): 0.85,
        ('stat', 'cs'): 0.6,
        ('stat', 'physics'): 0.75,
        ('stat', 'q-bio'): 0.7,
        ('q-fin', 'cs'): 0.8,
        ('q-fin', 'physics'): 0.85,
        ('astro-ph', 'q-bio'): 1.0,  # Very distant!
    }

    key = tuple(sorted([domain1_prefix, domain2_prefix]))
    return distance_matrix.get(key, 0.9)  # Default: very distant

def calculate_text_similarity(text1, text2):
    """
    Calculate text similarity based on word overlap (TF-IDF style).
    Returns 0.0-1.0 score.
    """
    # Tokenize and lowercase
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # Remove very short words
    words1 = {w for w in words1 if len(w) > 3}
    words2 = {w for w in words2 if len(w) > 3}

    if not words1 or not words2:
        return 0.0

    # Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    if union == 0:
        return 0.0

    return intersection / union

def calculate_confidence_score(pattern1, pattern2, text_similarity):
    """
    Multi-factor confidence scoring.

    Factors:
    1. Text similarity (50% weight) - baseline measure
    2. Domain distance (20% weight) - cross-domain more interesting
    3. Mathematical content (15% weight) - equations are strong evidence
    4. Structural depth (15% weight) - detailed patterns more reliable

    Returns: 0.0-1.0 confidence score
    """
    score = 0.0

    # Factor 1: Text similarity (50% weight)
    score += 0.5 * text_similarity

    # Factor 2: Domain distance (20% weight)
    domain_distance = get_domain_distance(pattern1['domain'], pattern2['domain'])
    score += 0.2 * domain_distance

    # Factor 3: Mathematical content (15% weight)
    # Patterns with substantial text (not just metrics) that likely contain equations
    has_math1 = pattern1.get('has_equation', 0) == 1 or len(pattern1['structural_description']) > 100
    has_math2 = pattern2.get('has_equation', 0) == 1 or len(pattern2['structural_description']) > 100

    if has_math1 and has_math2:
        score += 0.15
    elif has_math1 or has_math2:
        score += 0.075  # Partial credit

    # Factor 4: Structural depth (15% weight)
    # Longer descriptions with high-value terms indicate more structural content
    depth1 = min(len(pattern1['structural_description']) / 200.0, 1.0)
    depth2 = min(len(pattern2['structural_description']) / 200.0, 1.0)
    avg_depth = (depth1 + depth2) / 2
    score += 0.15 * avg_depth

    return min(score, 1.0)  # Cap at 1.0

def find_cross_domain_matches(min_similarity=0.6):
    """
    Find cross-domain isomorphisms with improved V3 scoring.

    Args:
        min_similarity: Minimum confidence score threshold (default 0.6)

    Returns:
        List of (pattern1_id, pattern2_id, confidence_score, explanation) tuples
    """
    print(f"[MATCH V3] Finding cross-domain isomorphisms (min_confidence={min_similarity})")
    print("[MATCH V3] Using multi-factor scoring: text + domain distance + math + depth")

    conn = sqlite3.connect('database/papers.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all patterns EXCEPT false positives
    cursor.execute('''
        SELECT p.id, p.paper_id, p.structural_description, p.mechanism_type,
               p.canonical_mechanism, p.has_equation, pa.domain, pa.title
        FROM patterns p
        JOIN papers pa ON p.paper_id = pa.id
        WHERE p.extraction_method NOT LIKE '%_FP%'
    ''')

    patterns = [dict(row) for row in cursor.fetchall()]
    print(f"[MATCH V3] Loaded {len(patterns)} patterns (excluding false positives)")

    # Group by canonical mechanism for efficiency
    by_mechanism = {}
    for p in patterns:
        mechanism = p['canonical_mechanism'] or p['mechanism_type']
        if mechanism not in by_mechanism:
            by_mechanism[mechanism] = []
        by_mechanism[mechanism].append(p)

    matches = []
    comparisons = 0
    filtered_generic = 0

    # Compare patterns with same mechanism type
    for mechanism, group in by_mechanism.items():
        if len(group) < 2:
            continue

        # Compare all pairs within this mechanism type
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                p1, p2 = group[i], group[j]

                # Skip same domain matches (not interesting)
                if p1['domain'] == p2['domain']:
                    continue

                comparisons += 1

                # Filter generic-only overlaps
                if has_only_generic_overlap(p1['structural_description'], p2['structural_description']):
                    filtered_generic += 1
                    continue

                # Calculate text similarity
                text_sim = calculate_text_similarity(
                    p1['structural_description'],
                    p2['structural_description']
                )

                # Calculate multi-factor confidence score
                confidence = calculate_confidence_score(p1, p2, text_sim)

                if confidence >= min_similarity:
                    # Create explanation
                    domain_dist = get_domain_distance(p1['domain'], p2['domain'])
                    explanation = (
                        f"Shared mechanism: {mechanism}. "
                        f"Text similarity: {text_sim:.2f}. "
                        f"Domain distance: {domain_dist:.2f}. "
                        f"Confidence: {confidence:.2f}"
                    )

                    matches.append((
                        min(p1['id'], p2['id']),  # pattern_1_id (smaller first)
                        max(p1['id'], p2['id']),  # pattern_2_id
                        confidence,
                        explanation,
                        p1['domain'],
                        p2['domain']
                    ))

    print(f"[MATCH V3] Made {comparisons:,} cross-domain comparisons")
    print(f"[MATCH V3] Filtered {filtered_generic:,} generic-only overlaps ({100*filtered_generic/comparisons:.1f}%)")
    print(f"[MATCH V3] Found {len(matches):,} potential isomorphisms")

    conn.close()
    return matches

def store_matches(matches):
    """Store isomorphisms in database."""
    conn = sqlite3.connect('database/papers.db')
    cursor = conn.cursor()

    # Clear old isomorphisms
    print("[MATCH V3] Clearing old isomorphisms...")
    cursor.execute('DELETE FROM isomorphisms')

    # Insert new matches
    for p1_id, p2_id, confidence, explanation, domain1, domain2 in tqdm(matches, desc="Storing isomorphisms"):
        try:
            cursor.execute('''
                INSERT INTO isomorphisms
                (pattern_1_id, pattern_2_id, similarity_score, explanation,
                 domain_1, domain_2, discovery_method)
                VALUES (?, ?, ?, ?, ?, ?, 'v3_multifactor')
            ''', (p1_id, p2_id, confidence, explanation, domain1, domain2))
        except sqlite3.IntegrityError:
            # Duplicate, skip
            continue

    conn.commit()
    conn.close()

    print(f"[MATCH V3] Stored {len(matches):,} isomorphisms")

def show_top_matches(limit=10):
    """Display top matches."""
    conn = sqlite3.connect('database/papers.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT i.similarity_score, i.domain_1, i.domain_2,
               p1.canonical_mechanism, p1.structural_description as desc1,
               p2.structural_description as desc2,
               pa1.title as title1, pa2.title as title2
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers pa1 ON p1.paper_id = pa1.id
        JOIN papers pa2 ON p2.paper_id = pa2.id
        ORDER BY i.similarity_score DESC
        LIMIT ?
    ''', (limit,))

    print(f"\n[TOP MATCHES] Top {limit} Cross-Domain Isomorphisms:")
    print("=" * 80)

    for row in cursor.fetchall():
        confidence_label = "high confidence" if row['similarity_score'] >= 0.7 else "medium confidence"
        print(f"\nConfidence: {row['similarity_score']:.2f} ({confidence_label})")
        print(f"Mechanism: {row['canonical_mechanism']}")
        print(f"Domains: {row['domain_1']} ↔ {row['domain_2']}")
        print(f"Paper 1: {row['title1'][:60]}...")
        print(f"Paper 2: {row['title2'][:60]}...")
        print("-" * 80)

    conn.close()

if __name__ == '__main__':
    import sys

    min_sim = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6

    matches = find_cross_domain_matches(min_similarity=min_sim)
    store_matches(matches)
    show_top_matches(10)

    print(f"\n[SUCCESS] Found and stored {len(matches):,} cross-domain isomorphisms (v3 algorithm)")

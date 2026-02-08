"""
Improved pattern matching using synonym normalization and context-aware filtering.

Session 11: Enhanced matching algorithm that:
1. Uses canonical mechanisms instead of raw mechanism types
2. Weights high-value technical terms more heavily
3. Filters matches that only share generic academic terms
4. Applies synonym-aware comparison

This should improve precision from ~60% toward 70-80%.
"""

import sqlite3
from utils import get_db, log_action
from synonyms import (
    normalize_mechanism_type, has_high_value_terms,
    has_only_generic_overlap, HIGH_VALUE_TECHNICAL_TERMS,
    GENERIC_ACADEMIC_TERMS
)
from tqdm import tqdm
import re

def calculate_similarity_v2(pattern1, pattern2):
    """
    Calculate similarity between two patterns using improved algorithm.

    Improvements over v1:
    - Uses canonical mechanisms
    - Weights high-value technical terms
    - Filters generic overlap
    - Bonus for shared equations

    Returns:
        float: Similarity score between 0 and 1
    """
    score = 0.0

    # 1. Canonical mechanism matching (stronger signal than before)
    if pattern1.get('canonical_mechanism') == pattern2.get('canonical_mechanism'):
        score += 0.6  # Increased from 0.5 because canonical is more reliable

    # 2. High-value technical term matching (NEW)
    desc1 = pattern1['structural_description'].lower()
    desc2 = pattern2['structural_description'].lower()

    high_value_1 = has_high_value_terms(desc1)
    high_value_2 = has_high_value_terms(desc2)

    shared_high_value = set(high_value_1) & set(high_value_2)

    if shared_high_value:
        # Each shared high-value term adds significant weight
        score += min(len(shared_high_value) * 0.15, 0.4)  # Cap at 0.4

    # 3. Filter generic-only overlap (NEW)
    if has_only_generic_overlap(desc1, desc2) and not shared_high_value:
        # Heavily penalize matches that only share generic terms
        score *= 0.3

    # 4. Text similarity (improved with better stopwords)
    common_words = set(GENERIC_ACADEMIC_TERMS) | {
        'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
        'can', 'this', 'that', 'these', 'those', 'with', 'from', 'by', 'as', 'we',
        'our', 'their', 'its', 'his', 'her', 'them', 'us', 'it', 'they', 'which',
        'who', 'where', 'when', 'how', 'what', 'why', 'there', 'here', 'show',
        'shows', 'shown', 'present', 'presents', 'presented', 'describe', 'describes'
    }

    words1 = set(re.findall(r'\w+', desc1)) - common_words
    words2 = set(re.findall(r'\w+', desc2)) - common_words

    if words1 and words2:
        # Jaccard similarity (but weighted less than before)
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        text_sim = intersection / union if union > 0 else 0
        score += text_sim * 0.3  # Reduced from 0.5

    # 5. Equation bonus REMOVED (Session 19.6)
    # Session 19.5 validation showed equation bonus had 0% precision
    # Equations are domain-specific, not structural signals

    return min(score, 1.0)  # Cap at 1.0

def find_cross_domain_matches_v2(min_similarity=0.80, limit=None):
    """
    Find cross-domain pattern matches using improved algorithm.

    Args:
        min_similarity: Minimum similarity score to store (0-1)
        limit: Maximum number of matches to find (None = no limit)

    Returns:
        Number of isomorphisms found
    """
    print(f"\n[MATCH V2] Finding cross-domain isomorphisms (min_similarity={min_similarity})")
    print("[MATCH V2] Using synonym normalization and context-aware filtering")

    db = get_db()
    cursor = db.cursor()

    # Get all patterns with their canonical mechanisms
    # Exclude patterns marked as false positives (extraction_method contains '_FP')
    cursor.execute('''
        SELECT p.id, p.structural_description, p.mechanism_type,
               p.canonical_mechanism, p.has_equation,
               pap.domain, pap.id as paper_id, pap.title
        FROM patterns p
        JOIN papers pap ON p.paper_id = pap.id
        WHERE (p.extraction_method IS NULL OR p.extraction_method NOT LIKE '%_FP%')
        ORDER BY p.id
    ''')

    patterns = []
    for row in cursor.fetchall():
        patterns.append({
            'id': row[0],
            'structural_description': row[1],
            'mechanism_type': row[2],
            'canonical_mechanism': row[3],
            'has_equation': row[4],
            'domain': row[5],
            'paper_id': row[6],
            'paper_title': row[7]
        })

    print(f"[MATCH V2] Loaded {len(patterns)} patterns")

    # Compare all pairs from different domains
    matches = []
    comparisons = 0
    filtered_generic = 0

    for i in range(len(patterns)):
        for j in range(i + 1, len(patterns)):
            p1 = patterns[i]
            p2 = patterns[j]

            # Only compare patterns from different domains
            if p1['domain'] == p2['domain']:
                continue

            comparisons += 1

            # Pre-filter: Skip if only generic overlap
            if has_only_generic_overlap(
                p1['structural_description'],
                p2['structural_description']
            ):
                filtered_generic += 1
                continue

            similarity = calculate_similarity_v2(p1, p2)

            if similarity >= min_similarity:
                matches.append((p1, p2, similarity))

    print(f"[MATCH V2] Made {comparisons} cross-domain comparisons")
    print(f"[MATCH V2] Filtered {filtered_generic} generic-only overlaps")
    print(f"[MATCH V2] Found {len(matches)} potential isomorphisms")

    # Sort by similarity (highest first) and apply limit if specified
    matches.sort(key=lambda x: x[2], reverse=True)
    if limit is not None:
        matches = matches[:limit]
        print(f"[MATCH V2] Limiting to top {limit} matches")

    # Clear old isomorphisms table
    print("[MATCH V2] Clearing old isomorphisms...")
    cursor.execute('DELETE FROM isomorphisms')

    # Store in database
    stored = 0
    for p1, p2, similarity in tqdm(matches, desc="Storing isomorphisms"):
        try:
            # Create explanation
            explanation = f"Both patterns are {p1['canonical_mechanism']} mechanisms. "
            explanation += f"Domain 1: {p1['domain']} - '{p1['paper_title'][:80]}...'. "
            explanation += f"Domain 2: {p2['domain']} - '{p2['paper_title'][:80]}...'. "

            # Check for high-value terms
            high_value_1 = has_high_value_terms(p1['structural_description'])
            high_value_2 = has_high_value_terms(p2['structural_description'])
            shared_high_value = set(high_value_1) & set(high_value_2)

            if shared_high_value:
                explanation += f"Shared technical terms: {', '.join(list(shared_high_value)[:3])}. "

            cursor.execute('''
                INSERT INTO isomorphisms
                (pattern_1_id, pattern_2_id, similarity_score, explanation, confidence_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                p1['id'],
                p2['id'],
                similarity,
                explanation,
                'high' if similarity >= 0.7 else 'medium' if similarity >= 0.6 else 'low'
            ))
            stored += 1
        except Exception as e:
            print(f"\n[ERROR] Failed to store isomorphism: {e}")
            continue

    db.commit()
    db.close()

    log_action('match_v2', f'Found {stored} isomorphisms (min_similarity={min_similarity})',
               isomorphisms=stored)

    print(f"\n[MATCH V2] Complete: {stored} isomorphisms stored")
    print(f"[MATCH V2] Filtered {filtered_generic} generic overlaps ({filtered_generic/comparisons*100:.1f}% of comparisons)")

    return stored

def show_top_matches(limit=10):
    """Display the top matches found."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT
            i.similarity_score,
            i.confidence_level,
            p1.canonical_mechanism,
            pap1.domain as domain1,
            pap2.domain as domain2,
            pap1.title as title1,
            pap2.title as title2
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers pap1 ON p1.paper_id = pap1.id
        JOIN papers pap2 ON p2.paper_id = pap2.id
        ORDER BY i.similarity_score DESC
        LIMIT ?
    ''', (limit,))

    print(f"\n[TOP MATCHES] Top {limit} Cross-Domain Isomorphisms:")
    print("=" * 80)

    for row in cursor.fetchall():
        score, confidence, mechanism, dom1, dom2, title1, title2 = row
        print(f"\nSimilarity: {score:.2f} ({confidence} confidence)")
        print(f"Mechanism: {mechanism}")
        print(f"Domains: {dom1} ↔ {dom2}")
        print(f"Paper 1: {title1[:70]}...")
        print(f"Paper 2: {title2[:70]}...")
        print("-" * 80)

    db.close()

if __name__ == '__main__':
    import sys

    min_similarity = float(sys.argv[1]) if len(sys.argv) > 1 else 0.80

    count = find_cross_domain_matches_v2(min_similarity=min_similarity)
    print(f'\n[SUCCESS] Found and stored {count} cross-domain isomorphisms (v2 algorithm)')

    if count > 0:
        show_top_matches(limit=10)

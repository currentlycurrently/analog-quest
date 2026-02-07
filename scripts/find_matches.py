import sqlite3
from utils import get_db, log_action
from tqdm import tqdm
import re

def calculate_similarity(pattern1, pattern2):
    """
    Calculate similarity between two patterns.

    Returns:
        float: Similarity score between 0 and 1
    """
    score = 0.0

    # 1. If same mechanism_type, very strong signal
    if pattern1['mechanism_type'] == pattern2['mechanism_type']:
        score += 0.5

    # 2. Text similarity in structural descriptions
    desc1 = pattern1['structural_description'].lower()
    desc2 = pattern2['structural_description'].lower()

    # Extract key words (remove common words and academic boilerplate)
    common_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or',
                    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                    'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
                    'can', 'this', 'that', 'these', 'those', 'with', 'from', 'by', 'as', 'we',
                    'our', 'their', 'its', 'his', 'her', 'them', 'us', 'it', 'they', 'which',
                    'who', 'where', 'when', 'how', 'what', 'why', 'there', 'here', 'show',
                    'shows', 'shown', 'present', 'presents', 'presented', 'describe', 'describes',

                    # Academic boilerplate (added Session 4 to reduce false positives)
                    'critical', 'critically', 'significant', 'significantly', 'key', 'important',
                    'importantly', 'novel', 'new', 'effective', 'effectively', 'efficient',
                    'efficiently', 'robust', 'robustly', 'stable', 'stably', 'strong', 'strongly',
                    'comprehensive', 'extensively', 'approach', 'method', 'propose', 'proposed',
                    'framework', 'model', 'system', 'results', 'result', 'findings', 'finding',
                    'analysis', 'study', 'research', 'paper', 'work', 'investigate', 'examined',
                    'demonstrate', 'demonstrated', 'provide', 'provides', 'using', 'used', 'based'}

    words1 = set(re.findall(r'\w+', desc1)) - common_words
    words2 = set(re.findall(r'\w+', desc2)) - common_words

    if words1 and words2:
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        text_sim = intersection / union if union > 0 else 0
        score += text_sim * 0.5

    return score

def find_cross_domain_matches(min_similarity=0.5, limit=100):
    """
    Find cross-domain pattern matches (isomorphisms).

    Args:
        min_similarity: Minimum similarity score to store (0-1)
        limit: Maximum number of matches to find

    Returns:
        Number of isomorphisms found
    """
    print(f"\n[MATCH] Finding cross-domain isomorphisms (min_similarity={min_similarity})")

    db = get_db()
    cursor = db.cursor()

    # Get all patterns with their paper domains
    cursor.execute('''
        SELECT p.id, p.structural_description, p.mechanism_type,
               pap.domain, pap.id as paper_id, pap.title
        FROM patterns p
        JOIN papers pap ON p.paper_id = pap.id
        ORDER BY p.id
    ''')

    patterns = []
    for row in cursor.fetchall():
        patterns.append({
            'id': row[0],
            'structural_description': row[1],
            'mechanism_type': row[2],
            'domain': row[3],
            'paper_id': row[4],
            'paper_title': row[5]
        })

    print(f"[MATCH] Loaded {len(patterns)} patterns")

    # Compare all pairs from different domains
    matches = []
    comparisons = 0

    for i in range(len(patterns)):
        for j in range(i + 1, len(patterns)):
            p1 = patterns[i]
            p2 = patterns[j]

            # Only compare patterns from different domains
            if p1['domain'] == p2['domain']:
                continue

            comparisons += 1
            similarity = calculate_similarity(p1, p2)

            if similarity >= min_similarity:
                matches.append((p1, p2, similarity))

    print(f"[MATCH] Made {comparisons} cross-domain comparisons")
    print(f"[MATCH] Found {len(matches)} potential isomorphisms")

    # Sort by similarity (highest first) and limit
    matches.sort(key=lambda x: x[2], reverse=True)
    matches = matches[:limit]

    # Store in database
    stored = 0
    for p1, p2, similarity in tqdm(matches, desc="Storing isomorphisms"):
        try:
            # Create explanation
            explanation = f"Both patterns are {p1['mechanism_type']} mechanisms. "
            explanation += f"Domain 1: {p1['domain']} - '{p1['paper_title'][:80]}...'. "
            explanation += f"Domain 2: {p2['domain']} - '{p2['paper_title'][:80]}...'. "

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
        except sqlite3.IntegrityError:
            # Isomorphism already exists
            pass
        except Exception as e:
            print(f"\n[ERROR] Failed to store isomorphism: {e}")
            continue

    db.commit()
    db.close()

    log_action('match', f'Found {stored} isomorphisms (min_similarity={min_similarity})',
               isomorphisms=stored)

    print(f"\n[MATCH] Complete: {stored} isomorphisms stored")

    return stored

def show_top_matches(limit=10):
    """Display the top matches found."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT
            i.similarity_score,
            i.confidence_level,
            p1.mechanism_type,
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

    min_similarity = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5

    count = find_cross_domain_matches(min_similarity=min_similarity)
    print(f'\n[SUCCESS] Found and stored {count} cross-domain isomorphisms')

    if count > 0:
        show_top_matches(limit=10)

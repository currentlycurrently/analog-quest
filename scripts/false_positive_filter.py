"""
False Positive Filter for Pattern Matching

Identifies and filters out patterns that rely primarily on generic or
misleading terms that don't represent true structural isomorphisms.
"""

# Terms that are too generic - appear everywhere but mean nothing structural
FALSE_POSITIVE_TERMS = {
    'fine-tuning',
    'fine tuning',
    'deep learning',
    'machine learning',
    'neural network',  # Unless part of specific mechanism like "graph neural network"
    'data',
    'model',
    'system',
    'algorithm',
    'method',
    'approach',
    'technique',
    'framework',
    'training',  # ML-specific unless clearly about learning dynamics
    'testing',
    'validation',
    'experiment',
    'performance',
    'accuracy',
    'evaluation',
    'baseline',
    'benchmark',
}

# These are OK if combined with structural terms, but not alone
WEAK_TERMS = {
    'optimization',  # OK with "constraint" or "gradient"
    'network',       # OK with "topology" or "dynamics"
    'learning',      # OK with "reinforcement" or "adaptive"
    'control',       # OK with "feedback" or "stability"
    'prediction',
    'classification',
    'regression',
}

def count_meaningful_words(text):
    """Count words that are long enough to be meaningful."""
    words = text.lower().split()
    return len([w for w in words if len(w) > 4])

def count_false_positive_terms(text):
    """Count how many false positive terms appear in text."""
    text_lower = text.lower()
    return sum(1 for term in FALSE_POSITIVE_TERMS if term in text_lower)

def has_structural_content(text):
    """
    Check if text has actual structural content beyond generic terms.
    Structural indicators: cause-effect, dynamics, relationships, equations.
    """
    structural_indicators = [
        'leads to',
        'causes',
        'results in',
        'increases',
        'decreases',
        'oscillates',
        'converges',
        'diverges',
        'equilibrium',
        'stability',
        'dynamics',
        'relationship',
        'correlation',
        'feedback',
        'coupling',
        'interaction',
        'mechanism',
        'process',
        'phase',
        'transition',
        'topology',
        'structure',
        'pattern',
    ]

    text_lower = text.lower()
    return any(indicator in text_lower for indicator in structural_indicators)

def is_false_positive_pattern(pattern_desc, mechanism_type=None):
    """
    Returns True if pattern relies primarily on false positive terms.

    Args:
        pattern_desc: The structural description text
        mechanism_type: The pattern's mechanism type (optional)

    Returns:
        Boolean indicating if this is likely a false positive
    """
    desc_lower = pattern_desc.lower()

    # Special case: "fine_tuning" mechanism is almost always a false positive
    if mechanism_type == 'fine_tuning':
        # Unless it describes HOW fine-tuning works structurally
        if not has_structural_content(pattern_desc):
            return True

    # Count meaningful words vs false positive terms
    meaningful_count = count_meaningful_words(pattern_desc)
    fp_count = count_false_positive_terms(pattern_desc)

    # If there are no meaningful words, it's definitely a false positive
    if meaningful_count == 0:
        return True

    # If >40% of meaningful words are from blocklist, it's a false positive
    if fp_count / meaningful_count > 0.4:
        # Unless there's clear structural content
        if not has_structural_content(pattern_desc):
            return True

    # Patterns that are just performance numbers (e.g., "0.919 without fine-tuning")
    if any(char.isdigit() for char in pattern_desc) and len(pattern_desc) < 50:
        # Very short patterns with numbers are likely just metrics
        if fp_count > 0:
            return True

    return False

def filter_false_positives_from_db(db_connection):
    """
    Mark false positive patterns in database.
    Returns count of patterns marked as false positives.
    """
    cursor = db_connection.cursor()

    # Get all patterns
    cursor.execute('''
        SELECT id, structural_description, mechanism_type, canonical_mechanism
        FROM patterns
    ''')

    patterns = cursor.fetchall()
    fp_count = 0
    fp_details = []

    for pattern_id, desc, mechanism_type, canonical in patterns:
        if is_false_positive_pattern(desc, mechanism_type):
            fp_count += 1
            fp_details.append({
                'id': pattern_id,
                'description': desc[:100],
                'mechanism': mechanism_type,
                'canonical': canonical
            })

            # Mark as false positive by adding a flag
            cursor.execute('''
                UPDATE patterns
                SET extraction_method = extraction_method || '_FP'
                WHERE id = ?
            ''', (pattern_id,))

    db_connection.commit()

    return fp_count, fp_details

if __name__ == '__main__':
    import sqlite3

    # Test the filter
    conn = sqlite3.connect('database/papers.db')

    print("[FALSE POSITIVE FILTER] Analyzing patterns...")
    fp_count, fp_details = filter_false_positives_from_db(conn)

    print(f"\n[RESULT] Marked {fp_count} patterns as false positives")

    # Show examples
    if fp_details:
        print("\n[EXAMPLES] First 10 false positives:")
        for i, fp in enumerate(fp_details[:10], 1):
            print(f"  {i}. ID {fp['id']}: {fp['mechanism']} - {fp['description']}...")

    conn.close()
    print("\n[SUCCESS] False positive filtering complete")

import sqlite3
import re
from utils import get_db, log_action
from tqdm import tqdm

def simple_extract(abstract):
    """
    VERY simple pattern extraction to start.
    We'll improve this dramatically over time.

    This version uses keyword matching to identify potential patterns.
    Future versions will use NLP, ML, and more sophisticated analysis.
    """
    patterns = []

    # Look for common pattern keywords
    # Each keyword maps to a mechanism type
    keywords = {
        'feedback': 'feedback_loop',
        'positive feedback': 'positive_feedback',
        'negative feedback': 'negative_feedback',
        'cascade': 'cascade',
        'cascading': 'cascade',
        'threshold': 'threshold',
        'critical point': 'threshold',  # More specific than just "critical"
        'network': 'network_effect',
        'oscillat': 'oscillation',
        'periodic': 'oscillation',
        'equilib': 'equilibrium',
        'stability': 'equilibrium',  # Changed from "stable" to "stability"
        'bifurcation': 'bifurcation',
        'phase transition': 'phase_transition',
        'emergence': 'emergence',
        'emergent': 'emergence',
        'scaling': 'scaling',
        'power law': 'scaling',
        'symmetry breaking': 'symmetry_breaking',
        'diffusion': 'diffusion',
        'spread': 'diffusion',
        'optimization': 'optimization',
        'optimal': 'optimization',
        'competition': 'competition',
        'competitive': 'competition',
        'cooperation': 'cooperation',
        'collaborative': 'cooperation',
        'saturation': 'saturation',
        'decay': 'decay',
        'exponential growth': 'growth',
        'exponential decay': 'decay',
        'resonance': 'resonance',

        # Math-specific keywords (added Session 4)
        'combinatorial': 'combinatorial',
        'graph theory': 'graph',
        'algorithmic': 'algorithmic',
        'asymptotic': 'asymptotic',
        'polynomial': 'complexity',
        'complexity': 'complexity',
        'bound': 'bound',
        'convergence': 'convergence',
        'approximation': 'approximation',
        'recursive': 'recursion',
        'induction': 'induction',

        # Economics-specific keywords (added Session 4)
        'incentive': 'incentive',
        'allocation': 'allocation',
        'strategic': 'strategic',
        'market': 'market',
        'supply and demand': 'supply_demand',
        'pricing': 'pricing',
        'game theor': 'game_theory',
        'nash equilibrium': 'equilibrium',
        'pareto': 'pareto',
        'welfare': 'welfare',
        'auction': 'auction',
        'mechanism design': 'mechanism_design',

        # Biology-specific keywords (added Session 5)
        'signaling': 'signaling',
        'signal transduction': 'signaling',
        'pathway': 'pathway',
        'regulatory': 'regulatory',
        'regulation': 'regulatory',
        'expression': 'expression',
        'gene expression': 'expression',
        'protein': 'protein',
        'enzyme': 'enzyme',
        'metabol': 'metabolism',
        'synthesis': 'synthesis',
        'transcription': 'transcription',
        'mutation': 'mutation',
        'adaptation': 'adaptation',
        'evolution': 'evolution',
        'selection': 'selection',
        'homeostasis': 'homeostasis',
        'inhibit': 'inhibition',
        'activation': 'activation',
        'binding': 'binding',

        # Materials science keywords (added Session 9)
        'crystal': 'crystal_structure',
        'crystalline': 'crystal_structure',
        'lattice': 'lattice',
        'defect': 'defect',
        'dislocation': 'dislocation',
        'grain boundary': 'grain_boundary',
        'nucleation': 'nucleation',
        'elastic': 'elastic',
        'plastic': 'plastic',
        'deformation': 'deformation',
        'fracture': 'fracture',
        'annealing': 'annealing',
        'microstructure': 'microstructure',
        'strain': 'strain',
        'interface': 'interface',
        'morphology': 'morphology',
    }

    abstract_lower = abstract.lower()

    # Split into sentences
    sentences = re.split(r'[.!?]+', abstract)

    for keyword, pattern_type in keywords.items():
        if keyword in abstract_lower:
            # Extract sentence containing the keyword
            for sent in sentences:
                if keyword in sent.lower() and sent.strip():
                    patterns.append({
                        'type': pattern_type,
                        'description': sent.strip(),
                        'confidence': 0.3  # Low confidence for this simple method
                    })
                    break  # Only take first occurrence of each pattern type

    return patterns

def extract_from_unprocessed(limit=20):
    """
    Extract patterns from papers that don't have patterns yet

    Args:
        limit: Maximum number of papers to process in this run

    Returns:
        Tuple of (papers_processed, patterns_created)
    """
    print(f"\n[EXTRACT] Starting pattern extraction (limit={limit})")

    db = get_db()
    cursor = db.cursor()

    # Find papers without patterns
    cursor.execute('''
        SELECT p.id, p.title, p.abstract, p.domain
        FROM papers p
        WHERE NOT EXISTS (
            SELECT 1 FROM patterns pt WHERE pt.paper_id = p.id
        )
        LIMIT ?
    ''', (limit,))

    papers = cursor.fetchall()

    if not papers:
        print("[EXTRACT] No unprocessed papers found")
        db.close()
        return 0, 0

    print(f"[EXTRACT] Found {len(papers)} papers to process")

    pattern_count = 0
    papers_with_patterns = 0

    for paper_id, title, abstract, domain in tqdm(papers, desc="Extracting patterns"):
        if not abstract:
            continue

        patterns = simple_extract(abstract)

        if patterns:
            papers_with_patterns += 1

        for p in patterns:
            try:
                cursor.execute('''
                    INSERT INTO patterns
                    (paper_id, structural_description, mechanism_type, confidence,
                     extraction_method)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    paper_id,
                    p['description'],
                    p['type'],
                    p['confidence'],
                    'simple_v1'
                ))
                pattern_count += 1
            except Exception as e:
                print(f"\n[ERROR] Failed to insert pattern: {e}")
                continue

    db.commit()
    db.close()

    log_action('extract', f'Processed {len(papers)} papers, found {pattern_count} patterns',
               patterns=pattern_count)

    print(f"\n[EXTRACT] Complete: {pattern_count} patterns from {papers_with_patterns}/{len(papers)} papers")
    return len(papers), pattern_count

if __name__ == '__main__':
    import sys

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20

    papers, patterns = extract_from_unprocessed(limit)
    print(f'\n[SUCCESS] Extracted {patterns} patterns from {papers} papers')

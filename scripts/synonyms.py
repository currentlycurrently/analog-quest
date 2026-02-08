"""
Synonym dictionary for mechanism normalization.

This maps various ways of describing the same mechanism to canonical forms.
Built incrementally as we discover recurring patterns across domains.

Session 11: Initial version based on Session 10 quality review findings.
"""

# Core mechanism types with their synonyms
MECHANISM_SYNONYMS = {
    'feedback_loop': [
        'feedback', 'feedback loop', 'reinforcement', 'amplification',
        'self-reinforcing', 'circular causation', 'feedback mechanism'
    ],

    'positive_feedback': [
        'positive feedback', 'reinforcing loop', 'amplification',
        'virtuous cycle', 'vicious cycle', 'snowball effect'
    ],

    'negative_feedback': [
        'negative feedback', 'balancing loop', 'homeostasis',
        'stabilizing', 'dampening', 'regulatory'
    ],

    'network_effect': [
        'network effect', 'network effects', 'frequency-dependent',
        'coordination', 'externality', 'metcalfe', 'preferential attachment'
    ],

    'diffusion_process': [
        'diffusion', 'spreading', 'propagation', 'contagion',
        'transmission', 'dissemination', 'percolation'
    ],

    # NOTE: Context matters! "diffusion model" (generative AI) vs "heat diffusion" (physics)
    'diffusion_generative': [
        'diffusion model', 'denoising diffusion', 'score-based diffusion',
        'ddpm', 'ddim'
    ],

    'cascade': [
        'cascade', 'cascading', 'avalanche', 'chain reaction',
        'domino effect', 'tipping cascade'
    ],

    'scaling_law': [
        'scaling law', 'scaling laws', 'power law', 'scale-free',
        'scale invariance', 'scaling behavior', 'neural scaling'
    ],

    'optimization': [
        'optimization', 'maximization', 'minimization', 'optimal',
        'optimizing', 'optimize'
    ],

    # Specific optimization methods (more precise than generic "optimization")
    'quantum_classical_optimization': [
        'quantum-classical', 'hybrid quantum', 'quantum annealing',
        'quantum optimization', 'qaoa'
    ],

    'threshold_dynamics': [
        'threshold', 'critical point', 'tipping point', 'phase transition',
        'bifurcation', 'critical threshold'
    ],

    'emergence': [
        'emergence', 'emergent', 'self-organization', 'spontaneous order',
        'bottom-up', 'collective behavior'
    ],

    'convergence': [
        'convergence', 'converges', 'asymptotic', 'limiting behavior',
        'γ-convergence', 'spectral convergence'
    ],

    'equilibrium': [
        'equilibrium', 'steady state', 'balance', 'stability',
        'stable state', 'nash equilibrium'
    ],

    'oscillation': [
        'oscillation', 'oscillate', 'periodic', 'cycle', 'cycling',
        'predator-prey', 'limit cycle'
    ],

    'growth_process': [
        'exponential growth', 'logistic growth', 'growth', 'expansion',
        'proliferation'
    ],

    'decay_process': [
        'decay', 'exponential decay', 'degradation', 'depletion',
        'dissipation'
    ],

    'competition': [
        'competition', 'competitive', 'rivalry', 'contest',
        'zero-sum', 'competitive exclusion'
    ],

    'cooperation': [
        'cooperation', 'cooperative', 'collaboration', 'mutualism',
        'symbiosis', 'coordination game'
    ],

    'strategic_behavior': [
        'strategic', 'game theory', 'game-theoretic', 'strategic interaction',
        'nash', 'mechanism design'
    ],

    'adaptation': [
        'adaptation', 'adaptive', 'learning', 'evolution',
        'evolutionary', 'selection'
    ],

    'selection_process': [
        'selection', 'natural selection', 'evolutionary selection',
        'preferential', 'winner-take-all'
    ]
}

# Technical terms that indicate structural similarity when shared
HIGH_VALUE_TECHNICAL_TERMS = [
    # Quantum computing
    'quantum-classical', 'quantum annealing', 'qaoa', 'variational quantum',

    # Scaling laws
    'scaling law', 'power law', 'neural scaling', 'broken scaling',

    # Advanced convergence
    'γ-convergence', 'spectral convergence', 'eyring-kramers',

    # Graph theory
    'graph neural network', 'gnn', 'graph optimization', 'combinatorial optimization',

    # Specific biological mechanisms
    'gene expression', 'protein binding', 'signal transduction', 'metabolic pathway',

    # Physics/Materials
    'phase transition', 'critical phenomena', 'lattice structure', 'crystal defect',

    # Economics
    'nash equilibrium', 'pareto efficiency', 'mechanism design', 'auction theory',

    # Machine learning specifics
    'lora', 'fine-tuning', 'transformer', 'attention mechanism',

    # Mathematical structures
    'bifurcation', 'dynamical system', 'chaotic', 'strange attractor'
]

# Generic terms that should NOT drive matches (avoid false positives)
GENERIC_ACADEMIC_TERMS = [
    # Generic ML/AI
    'neural network', 'deep learning', 'machine learning', 'artificial intelligence',

    # Generic methods
    'model', 'algorithm', 'method', 'approach', 'framework',

    # Generic optimization (without specific method)
    'optimization', 'optimal', 'minimize', 'maximize',

    # Generic results language
    'performance', 'accuracy', 'efficiency', 'effectiveness',
    'robust', 'significant', 'improvement', 'state-of-the-art',

    # Generic evolution/change
    'evolution', 'change', 'dynamics', 'behavior',

    # Generic complexity
    'complexity', 'complex', 'complicated',

    # Generic networks
    'network', 'system', 'structure'
]

def normalize_mechanism_type(mechanism_type):
    """
    Normalize a mechanism type to its canonical form.

    Args:
        mechanism_type: String mechanism type from pattern

    Returns:
        Canonical mechanism type or original if no mapping found
    """
    mechanism_lower = mechanism_type.lower().strip()

    for canonical, synonyms in MECHANISM_SYNONYMS.items():
        if mechanism_lower in [s.lower() for s in synonyms]:
            return canonical

    return mechanism_type

def get_canonical_mechanisms(text):
    """
    Extract all canonical mechanism types mentioned in text.

    Args:
        text: Text to analyze

    Returns:
        Set of canonical mechanism types found
    """
    text_lower = text.lower()
    found_mechanisms = set()

    for canonical, synonyms in MECHANISM_SYNONYMS.items():
        for synonym in synonyms:
            if synonym.lower() in text_lower:
                found_mechanisms.add(canonical)
                break

    return found_mechanisms

def has_high_value_terms(text):
    """
    Check if text contains high-value technical terms.

    Args:
        text: Text to analyze

    Returns:
        List of high-value technical terms found
    """
    text_lower = text.lower()
    return [term for term in HIGH_VALUE_TECHNICAL_TERMS if term in text_lower]

def has_only_generic_overlap(text1, text2):
    """
    Check if two texts only share generic academic terms (likely false positive).

    Args:
        text1, text2: Texts to compare

    Returns:
        True if only generic overlap, False if substantive overlap
    """
    text1_lower = text1.lower()
    text2_lower = text2.lower()

    # Find shared terms
    shared_generic = [term for term in GENERIC_ACADEMIC_TERMS
                      if term in text1_lower and term in text2_lower]

    shared_specific = [term for term in HIGH_VALUE_TECHNICAL_TERMS
                       if term in text1_lower and term in text2_lower]

    # If they share specific terms, it's real
    if shared_specific:
        return False

    # If they only share generic terms, likely false positive
    if shared_generic and not shared_specific:
        return True

    return False

if __name__ == '__main__':
    # Test the synonym system
    print("Testing synonym normalization:")
    print(f"'feedback' -> {normalize_mechanism_type('feedback')}")
    print(f"'reinforcement' -> {normalize_mechanism_type('reinforcement')}")
    print(f"'network effects' -> {normalize_mechanism_type('network effects')}")
    print(f"'quantum-classical' -> {normalize_mechanism_type('quantum-classical')}")

    print("\nTesting mechanism extraction:")
    text = "We study positive feedback loops and network effects in scaling laws."
    print(f"Text: {text}")
    print(f"Mechanisms: {get_canonical_mechanisms(text)}")

    print("\nTesting high-value terms:")
    text2 = "Quantum annealing combined with graph neural networks."
    print(f"Text: {text2}")
    print(f"High-value terms: {has_high_value_terms(text2)}")

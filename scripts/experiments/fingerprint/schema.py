"""Structural fingerprint schema + controlled vocabulary.

Single source of truth for what a fingerprint looks like. Used by
prompts.py (to tell the model what to emit), fingerprint.py (to validate
what came back), and match_and_evaluate.py (to score pairs).

Design constraint: everything here must be notation-independent. A
fingerprint describes the *mathematical structure* of a paper's core model,
never its LaTeX surface form.
"""

OBJECT_TYPES = [
    'ode',                  # ordinary differential equation(s)
    'pde',                  # partial differential equation(s)
    'sde',                  # stochastic differential / Langevin equation(s)
    'discrete_update',      # discrete-time map / iterative update rule
    'optimization',         # minimization/maximization problem
    'variational',          # variational principle / functional to extremize
    'stochastic_process',   # Markov chain, master equation, point process
    'network_dynamics',     # dynamics coupled on a graph
    'statistical_model',    # probabilistic model / inference setup
    'algebraic',            # algebraic/geometric structure, no dynamics
    'game_theoretic',       # strategic interaction / equilibrium concept
    'other',
]

# Object types that are routinely two faces of the same structure.
# Used for soft compatibility scoring, NOT hard blocking — several canonical
# isomorphisms cross type lines (Langevin SDE <-> Fokker-Planck PDE,
# replicator ODE <-> multiplicative-weights discrete update).
TYPE_COMPAT = {
    frozenset(['sde', 'pde']): 0.6,           # Fokker-Planck duality
    frozenset(['sde', 'stochastic_process']): 0.7,
    frozenset(['ode', 'discrete_update']): 0.7,  # discretization
    frozenset(['ode', 'sde']): 0.6,           # noise added/removed
    frozenset(['optimization', 'variational']): 0.8,
    frozenset(['optimization', 'discrete_update']): 0.5,  # iterative solvers
    frozenset(['ode', 'network_dynamics']): 0.6,
    frozenset(['pde', 'network_dynamics']): 0.4,
    frozenset(['statistical_model', 'optimization']): 0.5,  # inference as opt
    frozenset(['statistical_model', 'variational']): 0.5,
    frozenset(['game_theoretic', 'ode']): 0.5,  # evolutionary dynamics
    frozenset(['game_theoretic', 'optimization']): 0.5,
}

# Controlled vocabulary of structural features. The model may ONLY use these
# tags. Definitions are shown to the model verbatim; keep them crisp.
STRUCTURAL_FEATURES = {
    # -- dynamics shape --
    'first_order_in_time': 'highest time derivative (or update depth) is first order',
    'second_order_in_time': 'second time derivative / inertia term present',
    'exponential_growth_or_decay': 'linear term producing exponential solutions',
    'logistic_saturation': 'growth limited by quadratic self-interaction (x(1-x/K) shape)',
    'oscillatory_dynamics': 'intrinsic oscillation / rotation in state space',
    'damping_term': 'dissipative term removing energy/amplitude',
    'driving_term': 'external forcing/source term',
    'threshold_nonlinearity': 'discontinuous or sigmoidal switch behavior',
    'multiplicative_interaction': 'product of two distinct state variables (xy-type coupling)',
    'quadratic_self_interaction': 'state variable interacting with itself (x^2-type)',
    'time_delay': 'delayed argument / memory kernel',
    # -- space / diffusion / transport --
    'diffusion_term': 'second spatial derivative / Laplacian smoothing',
    'advection_term': 'first-order spatial transport term',
    'nonlinear_flux': 'flux depends nonlinearly on the state (e.g. Burgers uu_x)',
    'shock_formation': 'characteristics cross; weak solutions/shocks matter',
    'boundary_conditions_central': 'boundary/initial conditions are structurally essential',
    # -- stochasticity --
    'additive_noise': 'state-independent noise term',
    'multiplicative_noise': 'state-dependent noise term',
    'probability_flow': 'evolution of a probability density/distribution',
    'detailed_balance': 'equilibrium/reversibility condition on transitions',
    'jump_process': 'discrete stochastic transitions between states',
    # -- coupling / network --
    'pairwise_coupling': 'interaction enters through pairs of units',
    'mean_field_coupling': 'each unit feels the average of all others',
    'phase_coupling': 'interaction through phase differences (sin(θj-θi)-type)',
    'network_topology_matters': 'graph structure appears explicitly in the model',
    'spin_or_binary_units': 'units take two discrete states (±1, S/I, on/off)',
    # -- energy / variational / optimization --
    'energy_functional': 'scalar function whose landscape governs dynamics',
    'gradient_flow': 'dynamics follow the negative gradient of a functional',
    'free_energy_minimization': 'energy-entropy tradeoff being extremized',
    'entropy_term': 'entropy/log-probability appears in the objective',
    'variational_bound': 'objective is a bound on an intractable quantity',
    'constrained_optimization': 'explicit constraints / Lagrange multipliers',
    'multiplicative_update': 'update multiplies state by exponentiated signal, then normalizes',
    'transport_cost': 'objective is a cost of moving mass between distributions',
    'fixed_point_equilibrium': 'solution characterized as a fixed point / equilibrium',
    'convexity_central': 'convexity/concavity is load-bearing for the results',
    # -- conservation / symmetry --
    'conservation_law': 'a quantity is exactly conserved by the dynamics',
    'normalization_constraint': 'state lives on a simplex / probabilities sum to 1',
    'symmetry_breaking': 'symmetric model with asymmetric solutions/transitions',
    'phase_transition': 'qualitative change at a critical parameter value',
    'scale_invariance': 'power laws / self-similarity / renormalization',
    # -- compartments / populations --
    'compartmental_flow': 'population mass flows between labeled compartments',
    'mass_action_kinetics': 'rates proportional to products of concentrations',
    'replication_selection': 'growth rate proportional to relative fitness/payoff',
    'competitive_exclusion': 'entities competing for a shared limited resource',
    'predator_prey_asymmetry': 'one population grows at the direct expense of another',
}

# v2: a second, coarser view of the same model. Different fields dress the
# same skeleton differently (stochastic vs deterministic, discrete vs
# continuous, equilibrium vs dynamics); v1 measured that single-view
# fingerprints split such pairs (see results/ANALYSIS-2026-07-05.md).
SKELETON_SCHEMA = {
    'type': 'object',
    'required': ['object_type', 'summary', 'structural_features'],
    'properties': {
        'object_type': {'enum': OBJECT_TYPES},
        'summary': {'type': 'string'},
        'structural_features': {
            'type': 'array',
            'items': {'enum': sorted(STRUCTURAL_FEATURES)},
            'minItems': 1,
        },
    },
}

FINGERPRINT_JSON_SCHEMA = {
    'type': 'object',
    'required': ['arxiv_id', 'core_model', 'deterministic_skeleton', 'confidence'],
    'properties': {
        'arxiv_id': {'type': 'string'},
        'core_model': {
            'type': 'object',
            'required': ['object_type', 'structure_summary', 'canonical_form',
                         'linearity', 'stochastic', 'spatial_structure',
                         'structural_features', 'variables'],
            'properties': {
                'object_type': {'enum': OBJECT_TYPES},
                'structure_summary': {
                    'type': 'string',
                    'description': 'One sentence, notation-independent, no field jargon',
                },
                'canonical_form': {
                    'type': 'string',
                    'description': 'Core equation in neutral variables x,y,t,...; LaTeX',
                },
                'linearity': {'enum': ['linear', 'nonlinear', 'mixed']},
                'stochastic': {'type': 'boolean'},
                'spatial_structure': {'enum': ['none', 'continuum', 'lattice', 'network']},
                'structural_features': {
                    'type': 'array',
                    'items': {'enum': sorted(STRUCTURAL_FEATURES)},
                    'minItems': 1,
                },
                'variables': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['role', 'meaning'],
                        'properties': {
                            'role': {'enum': ['state', 'time', 'space', 'parameter',
                                              'control', 'noise', 'objective']},
                            'meaning': {'type': 'string'},
                        },
                    },
                },
            },
        },
        'deterministic_skeleton': SKELETON_SCHEMA,
        'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'notes': {'type': 'string'},
    },
}


def validate_fingerprint(fp):
    """Minimal structural validation (no external deps). Returns list of errors."""
    errors = []
    if not isinstance(fp, dict):
        return ['fingerprint is not an object']
    for key in ('arxiv_id', 'core_model', 'confidence'):
        if key not in fp:
            errors.append('missing key: %s' % key)
    cm = fp.get('core_model')
    if not isinstance(cm, dict):
        return errors + ['core_model is not an object']
    if cm.get('object_type') not in OBJECT_TYPES:
        errors.append('bad object_type: %r' % cm.get('object_type'))
    if cm.get('linearity') not in ('linear', 'nonlinear', 'mixed'):
        errors.append('bad linearity: %r' % cm.get('linearity'))
    if cm.get('spatial_structure') not in ('none', 'continuum', 'lattice', 'network'):
        errors.append('bad spatial_structure: %r' % cm.get('spatial_structure'))
    if not isinstance(cm.get('stochastic'), bool):
        errors.append('stochastic must be boolean')
    feats = cm.get('structural_features')
    if not isinstance(feats, list) or not feats:
        errors.append('structural_features must be a non-empty list')
    else:
        unknown = [f for f in feats if f not in STRUCTURAL_FEATURES]
        if unknown:
            errors.append('unknown structural_features: %r' % unknown)
    if not isinstance(cm.get('structure_summary'), str) or not cm.get('structure_summary'):
        errors.append('missing structure_summary')
    sk = fp.get('deterministic_skeleton')
    if not isinstance(sk, dict):
        errors.append('missing deterministic_skeleton (schema v2)')
    else:
        if sk.get('object_type') not in OBJECT_TYPES:
            errors.append('bad skeleton object_type: %r' % sk.get('object_type'))
        sfeats = sk.get('structural_features')
        if not isinstance(sfeats, list) or not sfeats:
            errors.append('skeleton structural_features must be a non-empty list')
        else:
            unknown = [f for f in sfeats if f not in STRUCTURAL_FEATURES]
            if unknown:
                errors.append('unknown skeleton structural_features: %r' % unknown)
        if not isinstance(sk.get('summary'), str) or not sk.get('summary'):
            errors.append('missing skeleton summary')
    return errors

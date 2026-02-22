# Methodology Rebuild Specification - Analog Quest v2.0

**Date**: 2026-02-22
**Status**: Technical Design Document
**Purpose**: Rebuild extraction and similarity systems to find REAL structural isomorphisms

---

## Executive Summary

**The Problem**: Current system produces "sophisticated keyword matching" - finding trivial similarities like "feedback loops exist in multiple domains" rather than non-obvious mathematical equivalences.

**The Solution**: Deep mathematical structure extraction + rigorous similarity algorithms = publication-worthy cross-domain discoveries.

**Success Metric**: ONE discovery that makes a professor say "Holy shit, I never thought of that connection!"

---

## Table of Contents

1. [What Constitutes a REAL Discovery](#1-what-constitutes-a-real-discovery)
2. [Current System Failures](#2-current-system-failures)
3. [Target Discovery Examples](#3-target-discovery-examples)
4. [Deep Extraction System Design](#4-deep-extraction-system-design)
5. [Similarity Detection Algorithms](#5-similarity-detection-algorithms)
6. [Quality Evaluation Framework](#6-quality-evaluation-framework)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Technical Requirements](#8-technical-requirements)
9. [Validation Strategy](#9-validation-strategy)
10. [Success Criteria](#10-success-criteria)

---

## 1. What Constitutes a REAL Discovery

### 1.1 Definition: Structural Isomorphism

A **structural isomorphism** is a mathematical equivalence between systems from different domains where:

1. **The mathematical form is identical** (not just similar)
2. **The connection is non-obvious** (not "both have networks")
3. **The insight is actionable** (enables knowledge transfer between domains)
4. **The domains are genuinely different** (not subcategories of the same field)

### 1.2 Real vs. Fake Examples

#### ❌ FAKE (Current System)
- "Both economics and biology have feedback loops"
- "Networks have clustering properties in multiple domains"
- "Spatial patterns emerge in different systems"

**Problem**: These are semantic similarities, not structural equivalences.

#### ✅ REAL (Target System)

**Example 1: Lotka-Volterra Equations**
- **Domain 1**: Chemical oscillators (autocatalytic reactions)
- **Domain 2**: Ecology (predator-prey dynamics)
- **Domain 3**: Economics (Goodwin model - wages and employment)
- **Mathematical Form**:
  ```
  dx/dt = αx - βxy
  dy/dt = δxy - γy
  ```
- **Why It Matters**: Solutions discovered in chemistry can predict ecological dynamics. Economic cycles follow predator-prey mathematics.

**Example 2: Heat/Diffusion Equation**
- **Domain 1**: Physics (heat conduction)
- **Domain 2**: Finance (Black-Scholes options pricing)
- **Domain 3**: Neuroscience (action potential propagation)
- **Domain 4**: Image processing (edge detection)
- **Mathematical Form**:
  ```
  ∂u/∂t = α∇²u
  ```
- **Why It Matters**: Black-Scholes literally applies heat equation solutions to price derivatives. Same PDE governs fundamentally different phenomena.

**Example 3: Hopf Bifurcation**
- **Domain 1**: Climate science (ice age cycles)
- **Domain 2**: Neuroscience (neural oscillations)
- **Domain 3**: Fluid dynamics (Rayleigh-Bénard convection)
- **Mathematical Form**: Emergence of periodic orbits when eigenvalues cross imaginary axis
- **Why It Matters**: Universal mechanism for onset of oscillations across physical, biological, and Earth systems.

### 1.3 Key Characteristics of Real Discoveries

1. **Mathematical Precision**: Can write down the same equations/graphs/operators
2. **Non-Obviousness**: Domain experts wouldn't naturally make the connection
3. **Explanatory Power**: Understanding one system helps understand the other
4. **Predictive Value**: Can transfer solutions/methods between domains
5. **Cross-Domain**: Truly different fields (not "ecology ↔ microbial ecology")

---

## 2. Current System Failures

### 2.1 Shallow Extraction

**Current Method**:
```python
# Essentially: GPT-4 summarizes abstract in one sentence
mechanism = llm.extract("Describe the mechanism in this abstract")
```

**What It Misses**:
- Actual equations (LaTeX/MathML)
- Graph structures (nodes, edges, relationships)
- Dynamical systems properties (stability, bifurcations)
- Topological features (homology, homotopy)
- Symbolic relationships (algebraic structures)

**Current Output Example**:
> "System exhibits feedback loops where component A affects component B"

**What We Need**:
```json
{
  "equations": [
    {
      "form": "dx/dt = f(x,y,params)",
      "symbolic": "Derivative(x(t), t) == alpha*x - beta*x*y",
      "type": "coupled_ode",
      "order": 1,
      "variables": ["x", "y"],
      "parameters": ["alpha", "beta"]
    }
  ],
  "graph_structure": {
    "nodes": ["x", "y"],
    "edges": [
      {"from": "x", "to": "y", "type": "inhibition"},
      {"from": "y", "to": "x", "type": "activation"}
    ],
    "motifs": ["negative_feedback_loop"]
  },
  "dynamical_properties": {
    "stability": "limit_cycle",
    "bifurcation_parameters": ["alpha", "beta"],
    "conserved_quantities": []
  }
}
```

### 2.2 Naive Similarity Detection

**Current Method**:
```python
# Cosine similarity of text embeddings
similarity = cosine(embed(text1), embed(text2))
if similarity > 0.35:
    # "Discovery!"
```

**Why This Fails**:
- "feedback loop" matches "feedback loop" regardless of structure
- Semantic similarity ≠ structural equivalence
- No mathematical comparison
- No graph isomorphism checking
- No equation structure matching

**Example Failure**:
- Paper 1: "Predator-prey feedback dynamics" (Lotka-Volterra)
- Paper 2: "Climate feedback loops" (different structure)
- Current system: 0.68 similarity → "Discovery!"
- Reality: Structurally different mechanisms

### 2.3 No Cross-Database Integration

**Critical Finding**: ZERO discoveries linking arXiv and OpenAlex papers.

All 133 "discoveries" are within the same data source. The "cross-domain" claim is mostly different subcategories of the same field (e.g., "q-bio.NC ↔ q-bio.PE").

### 2.4 Quality vs. Quantity Mismatch

**Current Status**: 133 "discoveries"
**Estimated Real Discoveries**: < 10

Most are trivial observations that wouldn't merit publication in any scientific venue.

---

## 3. Target Discovery Examples

### 3.1 Known Cross-Domain Isomorphisms (Ground Truth)

These are established mathematical equivalences we SHOULD be able to rediscover:

#### Discovery 1: Lotka-Volterra = Chemical Oscillators = Economic Cycles
- **Domains**: Chemistry (1910), Ecology (1925), Economics (Goodwin model)
- **Mathematical Form**: Coupled nonlinear ODEs with negative feedback
- **Equations**:
  ```
  dx/dt = αx - βxy
  dy/dt = δxy - γy
  ```
- **Papers to Test**:
  - Lotka (1910): "Contribution to the Theory of Periodic Reactions"
  - Volterra (1926): "Variations and Fluctuations in Numbers of Coexisting Species"
  - Goodwin (1967): "A Growth Cycle Model"

#### Discovery 2: Black-Scholes = Heat Equation
- **Domains**: Finance, Physics
- **Mathematical Form**: Parabolic PDE
- **Transformation**:
  ```
  Black-Scholes: ∂V/∂t + (1/2)σ²S²∂²V/∂S² + rS∂V/∂S - rV = 0

  [via substitution: S=e^x, V=e^(-rt)u, τ=T-t]

  Heat Equation: ∂u/∂τ = α∂²u/∂x²
  ```
- **Papers to Test**:
  - Black & Scholes (1973): "The Pricing of Options and Corporate Liabilities"
  - Any heat conduction paper in physics

#### Discovery 3: SIR Model = Chemical Kinetics = Rumor Spreading
- **Domains**: Epidemiology, Chemistry, Social networks
- **Mathematical Form**: Compartmental flow model
- **Equations**:
  ```
  dS/dt = -βSI
  dI/dt = βSI - γI
  dR/dt = γI
  ```
- **Isomorphic to**:
  - Chemical reactions: A + B → 2B (autocatalytic)
  - Information cascades in networks
  - Market adoption dynamics

#### Discovery 4: Hopf Bifurcation (Universal Oscillation Onset)
- **Domains**: Climate, Neuroscience, Fluid dynamics, Laser physics
- **Mathematical Criterion**: Pair of complex eigenvalues crosses imaginary axis
- **Normal Form**:
  ```
  dz/dt = (μ + iω)z - |z|²z
  ```
- **Examples**:
  - Ice age cycles (Saltzman 1982)
  - Neural oscillators (FitzHugh-Nagumo)
  - Rayleigh-Bénard convection
  - Laser threshold

#### Discovery 5: Ising Model = Neural Networks = Social Consensus
- **Domains**: Statistical physics, Neuroscience, Sociology
- **Mathematical Form**: Spin systems on graphs
- **Hamiltonian**:
  ```
  H = -Σ J_ij s_i s_j - Σ h_i s_i
  ```
- **Isomorphic to**:
  - Ferromagnetic phase transitions
  - Hopfield neural networks (memory storage)
  - Opinion dynamics (voter models)

### 3.2 Novel Discoveries We Should Find

These are hypothetical but plausible cross-domain equivalences:

#### Hypothetical 1: Gene Regulatory Networks = Electronic Circuits
- **Shared Structure**: Boolean logic gates, feedback inhibition, oscillators
- **Mathematical Form**: Coupled Hill equations ≈ Kirchhoff's laws with nonlinear elements
- **Why Non-Obvious**: Biology vs. Engineering

#### Hypothetical 2: Swarm Robotics = Protein Folding
- **Shared Structure**: Local interaction rules → global minimum energy configuration
- **Mathematical Form**: Energy landscape navigation with distributed agents
- **Why Non-Obvious**: Macro vs. Molecular scale

#### Hypothetical 3: Supply Chain Networks = Vascular Systems
- **Shared Structure**: Hierarchical branching, flow optimization, resilience to disruption
- **Mathematical Form**: Murray's Law (optimal pipe diameter scaling)
- **Why Non-Obvious**: Economics vs. Physiology

---

## 4. Deep Extraction System Design

### 4.1 Architecture Overview

```
PDF/LaTeX → [ Extraction Pipeline ] → Structured Objects → Database
                    ↓
        ┌───────────────────────────┐
        │  Mathematical Structures  │
        ├───────────────────────────┤
        │ 1. Equations              │
        │ 2. Graphs                 │
        │ 3. Dynamical Systems      │
        │ 4. Topological Features   │
        │ 5. Symbolic Algebra       │
        └───────────────────────────┘
```

### 4.2 Component 1: Equation Extraction

**Input**: Full paper text (PDF → LaTeX)
**Output**: Structured equation objects

#### Tools:
- **PDFFigures 2.0**: Extract equations from PDFs
- **LaTeXML**: Parse LaTeX to MathML
- **SymPy**: Symbolic mathematics library
- **tex2sympy**: Convert LaTeX equations to SymPy

#### Process:
```python
import sympy as sp
from tex2sympy import tex2sympy

# 1. Extract LaTeX equations from paper
equations_latex = extract_latex_equations(pdf_path)

# 2. Convert to SymPy symbolic form
equations_symbolic = []
for eq_latex in equations_latex:
    try:
        eq_sympy = tex2sympy(eq_latex)
        equations_symbolic.append(eq_sympy)
    except:
        # Fallback: manual parsing or LLM assistance
        pass

# 3. Analyze equation structure
for eq in equations_symbolic:
    analysis = {
        'type': classify_equation(eq),  # ODE, PDE, algebraic, etc.
        'variables': list(eq.free_symbols),
        'parameters': extract_parameters(eq),
        'order': get_differential_order(eq),
        'linearity': check_linearity(eq),
        'coupling': find_coupled_vars(eq),
        'conservation_laws': find_conserved_quantities(eq)
    }
```

#### Equation Classification:
```python
def classify_equation(eq):
    """Classify equation by mathematical type"""
    if has_derivatives(eq):
        if is_partial_derivative(eq):
            return classify_pde(eq)  # heat, wave, Laplace, etc.
        else:
            return classify_ode(eq)  # linear, nonlinear, order
    elif is_algebraic(eq):
        return classify_algebraic(eq)  # polynomial, rational, etc.
    elif is_difference_equation(eq):
        return 'discrete_dynamical'
    else:
        return 'unknown'
```

#### Canonical Forms:
```python
def to_canonical_form(eq):
    """Transform equation to standard form for comparison"""
    # Examples:
    # - ODEs: dx/dt = f(x, params)
    # - PDEs: ∂u/∂t = L[u] (linear operator form)
    # - Algebraic: polynomial with sorted terms

    canonical = sp.simplify(eq)
    canonical = alphabetize_variables(canonical)
    canonical = normalize_parameters(canonical)
    return canonical
```

### 4.3 Component 2: Graph Structure Extraction

**Input**: Paper text + equations
**Output**: Network/graph objects

#### Tools:
- **NetworkX**: Graph analysis
- **graph-tool**: High-performance graphs (C++)
- **igraph**: Graph algorithms
- **LLM assistance**: Extract verbal descriptions of interactions

#### Process:
```python
import networkx as nx
from collections import defaultdict

# 1. Extract interaction graph from equations
def equation_to_graph(equations):
    """Convert system of equations to directed graph"""
    G = nx.DiGraph()

    for eq in equations:
        lhs_var = get_lhs_variable(eq)  # e.g., dx/dt → x
        rhs_vars = get_rhs_variables(eq)  # e.g., αx - βxy → [x, y]

        for rhs_var in rhs_vars:
            if rhs_var != lhs_var:
                # Determine edge type (activation/inhibition)
                influence = compute_influence(eq, lhs_var, rhs_var)
                G.add_edge(rhs_var, lhs_var,
                          influence=influence,
                          functional_form=str(eq))

    return G

# 2. Extract network from text descriptions
def text_to_graph(text, llm):
    """Use LLM to extract interaction networks from prose"""
    prompt = """
    Extract the causal network from this text.

    For each relationship:
    - Source entity
    - Target entity
    - Type of influence (positive/negative/neutral)
    - Mechanism (how source affects target)

    Example output:
    {
      "nodes": ["A", "B", "C"],
      "edges": [
        {"from": "A", "to": "B", "type": "activation", "mechanism": "catalyzes"},
        {"from": "B", "to": "A", "type": "inhibition", "mechanism": "depletes"}
      ]
    }

    Text: {text}
    """

    network = llm.extract_structured(prompt, schema=NetworkSchema)
    return network_to_graph(network)

# 3. Compute graph features
def analyze_graph(G):
    """Extract structural features"""
    return {
        'motifs': find_motifs(G),  # feedback loops, feedforward, etc.
        'centrality': nx.betweenness_centrality(G),
        'strongly_connected_components': list(nx.strongly_connected_components(G)),
        'cycles': list(nx.simple_cycles(G)),
        'feedback_loops': identify_feedback_loops(G),
        'cascade_structures': identify_cascades(G)
    }
```

#### Graph Motifs Library:
```python
MOTIFS = {
    'negative_feedback_loop': lambda G: find_cycles_with_sign(G, sign=-1),
    'positive_feedback_loop': lambda G: find_cycles_with_sign(G, sign=+1),
    'feedforward_loop': lambda G: find_feedforward_motifs(G),
    'bi_fan': lambda G: find_bifan_motifs(G),
    'cascade': lambda G: find_cascade_structures(G)
}
```

### 4.4 Component 3: Dynamical Systems Analysis

**Input**: System of differential equations
**Output**: Dynamical properties

#### Tools:
- **SymPy**: Symbolic analysis
- **scipy.integrate**: Numerical simulation
- **pyDSTool**: Dynamical systems toolbox
- **AUTO-07p**: Continuation and bifurcation analysis

#### Process:
```python
from sympy import symbols, diff, Matrix, solve
import numpy as np
from scipy.integrate import odeint

# 1. Stability analysis
def analyze_stability(equations, equilibria):
    """Compute linearization and eigenvalues"""
    x, y = symbols('x y')

    # Jacobian matrix at equilibrium
    J = Matrix([
        [diff(equations[0], x), diff(equations[0], y)],
        [diff(equations[1], x), diff(equations[1], y)]
    ])

    for eq_point in equilibria:
        J_eval = J.subs({x: eq_point[0], y: eq_point[1]})
        eigenvalues = J_eval.eigenvals()

        yield {
            'equilibrium': eq_point,
            'eigenvalues': eigenvalues,
            'stability': classify_stability(eigenvalues),
            'type': classify_equilibrium_type(eigenvalues)
        }

# 2. Bifurcation detection
def detect_bifurcations(equations, param_range):
    """Scan parameter space for bifurcations"""
    bifurcations = []

    for param_value in param_range:
        eqs_at_param = substitute_parameter(equations, param_value)
        equilibria = find_equilibria(eqs_at_param)

        # Check for bifurcation signatures
        if hopf_criterion(equilibria):
            bifurcations.append({
                'type': 'hopf',
                'parameter_value': param_value,
                'critical_eigenvalues': get_critical_eigenvalues(equilibria)
            })

        if saddle_node_criterion(equilibria):
            bifurcations.append({
                'type': 'saddle_node',
                'parameter_value': param_value
            })

    return bifurcations

# 3. Classify dynamical regime
def classify_dynamics(equations, initial_conditions, time_span):
    """Determine type of dynamics via simulation"""
    trajectory = simulate(equations, initial_conditions, time_span)

    # Analyze trajectory
    if is_fixed_point(trajectory):
        return {'type': 'equilibrium', 'attractor': trajectory[-1]}
    elif is_limit_cycle(trajectory):
        return {'type': 'periodic', 'period': estimate_period(trajectory)}
    elif is_chaotic(trajectory):
        return {'type': 'chaotic', 'lyapunov_exponent': compute_lyapunov(trajectory)}
    elif is_quasiperiodic(trajectory):
        return {'type': 'quasiperiodic', 'frequencies': fft_analysis(trajectory)}
    else:
        return {'type': 'unknown'}
```

#### Dynamical Equivalence Classes:
```python
DYNAMICAL_CLASSES = {
    'linear_stable': {'eigenvalues': 'all negative real parts'},
    'linear_unstable': {'eigenvalues': 'at least one positive real part'},
    'center': {'eigenvalues': 'purely imaginary'},
    'saddle': {'eigenvalues': 'mixed signs'},
    'spiral': {'eigenvalues': 'complex conjugate pairs'},
    'hopf_bifurcation': {'eigenvalues': 'cross imaginary axis'},
    'limit_cycle': {'trajectory': 'periodic attractor'},
    'chaos': {'lyapunov_exponent': '> 0'}
}
```

### 4.5 Component 4: Topological Feature Extraction

**Input**: Time series data, spatial patterns, network structures
**Output**: Topological invariants

#### Tools:
- **Gudhi**: Computational topology and persistent homology
- **Ripser**: Fast persistent homology computation
- **giotto-tda**: Topological data analysis for ML

#### Process:
```python
from gudhi import SimplexTree, RipsComplex
from giotto-tda import homology

# 1. Persistent homology of time series
def extract_topology_from_timeseries(data):
    """Compute persistent homology of delay embedding"""
    # Takens embedding
    embedded = time_delay_embedding(data, delay=10, dimension=3)

    # Build Rips complex
    rips = RipsComplex(points=embedded, max_edge_length=2.0)
    simplex_tree = rips.create_simplex_tree(max_dimension=2)

    # Compute persistence
    persistence = simplex_tree.persistence()

    return {
        'betti_numbers': compute_betti_numbers(persistence),
        'persistence_diagram': persistence,
        'topological_features': extract_features(persistence)
    }

# 2. Network topology
def extract_network_topology(graph):
    """Compute topological features of networks"""
    # Convert to clique complex
    clique_complex = nx.find_cliques(graph.to_undirected())
    simplex_tree = build_simplex_tree_from_cliques(clique_complex)

    # Homology groups
    homology_groups = simplex_tree.persistence()

    return {
        'euler_characteristic': compute_euler_char(graph),
        'homology': homology_groups,
        'holes': count_holes(homology_groups)
    }
```

### 4.6 Component 5: Full Text Processing

**Input**: PDF file
**Output**: All structured objects

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ExtractedStructures:
    """Complete structural extraction from a paper"""
    paper_id: int
    arxiv_id: str

    # Mathematical objects
    equations: List[EquationObject]
    graphs: List[GraphObject]
    dynamical_systems: List[DynamicalSystemObject]
    topological_features: List[TopologicalObject]

    # Metadata
    extraction_confidence: float
    extraction_method: str

def deep_extraction_pipeline(pdf_path, arxiv_id):
    """Full pipeline from PDF to structured objects"""

    # 1. Convert PDF to structured text
    latex_text = pdf_to_latex(pdf_path)
    sections = parse_sections(latex_text)

    # 2. Extract equations
    equations = []
    for eq_latex in extract_equations(latex_text):
        eq_obj = EquationObject(
            latex=eq_latex,
            sympy=tex2sympy(eq_latex),
            canonical_form=to_canonical_form(eq_latex),
            classification=classify_equation(eq_latex),
            variables=extract_variables(eq_latex),
            parameters=extract_parameters(eq_latex)
        )
        equations.append(eq_obj)

    # 3. Extract graphs from equations + text
    graphs = []
    if equations:
        graph_from_eqs = equations_to_graph(equations)
        graphs.append(graph_from_eqs)

    graph_from_text = text_to_graph(sections['methods'] + sections['results'])
    if graph_from_text:
        graphs.append(graph_from_text)

    # 4. Dynamical systems analysis
    dynamical_systems = []
    if is_dynamical_system(equations):
        ds_obj = DynamicalSystemObject(
            equations=equations,
            stability=analyze_stability(equations),
            bifurcations=detect_bifurcations(equations),
            regime=classify_dynamics(equations)
        )
        dynamical_systems.append(ds_obj)

    # 5. Topological analysis (if applicable)
    topological_features = []
    if has_network_data(sections):
        topo = extract_network_topology(graphs[0])
        topological_features.append(topo)

    # 6. Package results
    return ExtractedStructures(
        paper_id=get_paper_id(arxiv_id),
        arxiv_id=arxiv_id,
        equations=equations,
        graphs=graphs,
        dynamical_systems=dynamical_systems,
        topological_features=topological_features,
        extraction_confidence=compute_confidence(),
        extraction_method='deep_v2'
    )
```

### 4.7 Extraction Quality Metrics

```python
def evaluate_extraction_quality(extracted: ExtractedStructures):
    """Score extraction completeness and reliability"""

    score = {
        'has_equations': len(extracted.equations) > 0,
        'has_graphs': len(extracted.graphs) > 0,
        'has_dynamics': len(extracted.dynamical_systems) > 0,

        'equation_parseable': sum(1 for eq in extracted.equations if eq.sympy is not None),
        'graph_analyzable': sum(1 for g in extracted.graphs if len(g.nodes) > 0),

        'richness_score': compute_richness(extracted),
        'confidence': extracted.extraction_confidence
    }

    # Overall quality tier
    if score['richness_score'] > 0.7 and score['has_equations']:
        tier = 'high_quality'
    elif score['richness_score'] > 0.4:
        tier = 'medium_quality'
    else:
        tier = 'low_quality'

    score['quality_tier'] = tier
    return score
```

---

## 5. Similarity Detection Algorithms

### 5.1 Multi-Level Similarity Architecture

```
Extracted Structures → [ Similarity Detection ] → Scored Matches
                              ↓
                    ┌─────────────────────┐
                    │  Similarity Layers  │
                    ├─────────────────────┤
                    │ 1. Equation Match   │ → 0.0-1.0
                    │ 2. Graph Isomorph   │ → 0.0-1.0
                    │ 3. Dynamical Equiv  │ → 0.0-1.0
                    │ 4. Topological Sim  │ → 0.0-1.0
                    └─────────────────────┘
                              ↓
                    Weighted Combination → Final Score
```

### 5.2 Layer 1: Equation Structure Matching

**Goal**: Detect when two equations have the same mathematical form despite different variables/parameters.

#### Algorithm:
```python
from sympy import symbols, simplify, diff
from sympy.abc import x, y, t

def equation_similarity(eq1, eq2):
    """
    Compute structural similarity between two equations

    Returns:
        score (0.0-1.0): 1.0 = structurally identical
        mapping (dict): variable correspondences
    """

    # Step 1: Normalize to canonical form
    canon1 = to_canonical_form(eq1)
    canon2 = to_canonical_form(eq2)

    # Step 2: Try variable mappings
    vars1 = list(eq1.free_symbols)
    vars2 = list(eq2.free_symbols)

    if len(vars1) != len(vars2):
        return 0.0, None

    # Generate all possible variable mappings
    from itertools import permutations
    best_score = 0.0
    best_mapping = None

    for perm in permutations(vars2):
        mapping = dict(zip(vars1, perm))
        eq1_mapped = canon1.subs(mapping)

        # Compare structure
        score = symbolic_distance(eq1_mapped, canon2)

        if score > best_score:
            best_score = score
            best_mapping = mapping

    return best_score, best_mapping

def symbolic_distance(expr1, expr2):
    """Compute similarity via symbolic manipulation"""

    # Exact match
    if simplify(expr1 - expr2) == 0:
        return 1.0

    # Structural equivalence (same derivatives, same terms)
    structure1 = get_equation_structure(expr1)
    structure2 = get_equation_structure(expr2)

    # Compare:
    # - Differential order
    # - Number of terms
    # - Nonlinearity type
    # - Coupling structure

    score = 0.0

    if structure1['order'] == structure2['order']:
        score += 0.2

    if structure1['linearity'] == structure2['linearity']:
        score += 0.2

    if structure1['coupling_type'] == structure2['coupling_type']:
        score += 0.3

    # Term structure similarity
    term_sim = jaccard_similarity(structure1['term_types'], structure2['term_types'])
    score += 0.3 * term_sim

    return score
```

#### Equation Structure Representation:
```python
def get_equation_structure(eq):
    """Extract structural features of equation"""
    return {
        'order': get_differential_order(eq),
        'linearity': check_linearity(eq),
        'coupling_type': identify_coupling(eq),
        'term_types': categorize_terms(eq),
        'symmetries': find_symmetries(eq),
        'conservation_laws': find_conserved_quantities(eq)
    }

def categorize_terms(eq):
    """Identify types of terms (linear, quadratic, etc.)"""
    terms = eq.as_ordered_terms()

    term_types = set()
    for term in terms:
        if is_linear(term):
            term_types.add('linear')
        elif is_quadratic(term):
            term_types.add('quadratic')
        elif is_polynomial(term):
            term_types.add(f'polynomial_{degree(term)}')
        elif has_derivative(term):
            term_types.add(f'derivative_{get_order(term)}')
        elif is_exponential(term):
            term_types.add('exponential')
        elif is_trigonometric(term):
            term_types.add('trigonometric')

    return term_types
```

### 5.3 Layer 2: Graph Isomorphism Detection

**Goal**: Determine if two interaction networks have the same structure.

#### Algorithm:
```python
import networkx as nx
from networkx.algorithms import isomorphism

def graph_similarity(G1, G2):
    """
    Compute graph similarity including:
    - Exact isomorphism
    - Approximate isomorphism
    - Motif similarity
    """

    # Step 1: Check exact isomorphism
    if nx.is_isomorphic(G1, G2):
        # Get the mapping
        matcher = isomorphism.DiGraphMatcher(G1, G2,
            node_match=lambda n1, n2: True,  # Allow any node mapping
            edge_match=edge_type_match)

        if matcher.is_isomorphic():
            return 1.0, matcher.mapping

    # Step 2: Approximate isomorphism via graph edit distance
    ged = graph_edit_distance(G1, G2)
    max_size = max(len(G1.nodes), len(G2.nodes))

    approx_score = 1.0 - (ged / max_size)

    # Step 3: Motif-based similarity
    motifs1 = extract_all_motifs(G1)
    motifs2 = extract_all_motifs(G2)

    motif_similarity = jaccard_similarity(motifs1, motifs2)

    # Combine scores
    final_score = 0.5 * approx_score + 0.5 * motif_similarity

    return final_score, None

def edge_type_match(edge1, edge2):
    """Match edges by influence type"""
    # Both activating or both inhibiting
    return edge1.get('influence') == edge2.get('influence')

def extract_all_motifs(G):
    """Find all 3-node motifs"""
    motifs = set()

    for subgraph in all_3_node_subgraphs(G):
        motif_type = classify_motif(subgraph)
        motifs.add(motif_type)

    return motifs

def classify_motif(subgraph):
    """Identify motif type (feedback loop, feedforward, etc.)"""
    # Implementation based on motif library
    if has_cycle(subgraph):
        if cycle_length(subgraph) == 2:
            return 'mutual_regulation'
        elif cycle_length(subgraph) == 3:
            edge_signs = get_edge_signs(subgraph)
            if product(edge_signs) < 0:
                return 'negative_feedback_loop'
            else:
                return 'positive_feedback_loop'
    elif is_feedforward_loop(subgraph):
        return 'feedforward_loop'
    else:
        return 'other'
```

### 5.4 Layer 3: Dynamical Systems Equivalence

**Goal**: Determine if two systems have equivalent dynamics (beyond equation form).

#### Algorithm:
```python
def dynamical_equivalence(ds1, ds2):
    """
    Check for dynamical equivalence:
    - Same stability properties
    - Same bifurcation structure
    - Same phase portrait topology
    """

    score = 0.0

    # 1. Stability comparison
    if ds1.stability_type == ds2.stability_type:
        score += 0.3

    # 2. Bifurcation structure
    bif_sim = compare_bifurcations(ds1.bifurcations, ds2.bifurcations)
    score += 0.3 * bif_sim

    # 3. Dynamical regime
    if ds1.regime == ds2.regime:
        score += 0.2

    # 4. Normal form equivalence
    if has_same_normal_form(ds1, ds2):
        score += 0.2

    return score

def compare_bifurcations(bif1_list, bif2_list):
    """Compare bifurcation structures"""

    # Extract bifurcation types
    types1 = set(b['type'] for b in bif1_list)
    types2 = set(b['type'] for b in bif2_list)

    # Jaccard similarity of bifurcation types
    return jaccard_similarity(types1, types2)

def has_same_normal_form(ds1, ds2):
    """
    Check if systems reduce to same normal form
    (e.g., both reduce to Hopf normal form)
    """

    # Classify by normal form
    nf1 = identify_normal_form(ds1)
    nf2 = identify_normal_form(ds2)

    return nf1 == nf2 and nf1 is not None

NORMAL_FORMS = {
    'hopf': lambda ds: (
        ds.stability_type == 'spiral' and
        has_supercritical_hopf_bifurcation(ds)
    ),
    'saddle_node': lambda ds: (
        has_saddle_node_bifurcation(ds)
    ),
    'pitchfork': lambda ds: (
        has_pitchfork_bifurcation(ds)
    ),
    # ... other universal unfoldings
}
```

### 5.5 Layer 4: Topological Similarity

**Goal**: Compare persistent homology and topological features.

#### Algorithm:
```python
from scipy.spatial.distance import directed_hausdorff

def topological_similarity(topo1, topo2):
    """
    Compare topological features:
    - Persistence diagrams
    - Betti numbers
    - Euler characteristic
    """

    score = 0.0

    # 1. Betti numbers (simple but powerful)
    if topo1['betti_numbers'] == topo2['betti_numbers']:
        score += 0.3

    # 2. Persistence diagram distance
    pd1 = topo1['persistence_diagram']
    pd2 = topo2['persistence_diagram']

    # Bottleneck distance between persistence diagrams
    bottleneck_dist = compute_bottleneck_distance(pd1, pd2)

    # Normalize to [0, 1]
    pd_similarity = 1.0 / (1.0 + bottleneck_dist)
    score += 0.5 * pd_similarity

    # 3. Euler characteristic
    if topo1.get('euler_characteristic') == topo2.get('euler_characteristic'):
        score += 0.2

    return score

def compute_bottleneck_distance(pd1, pd2):
    """Bottleneck distance between persistence diagrams"""
    from gudhi.bottleneck import bottleneck_distance

    # Convert to point clouds
    points1 = [(birth, death) for (dim, (birth, death)) in pd1 if death != float('inf')]
    points2 = [(birth, death) for (dim, (birth, death)) in pd2 if death != float('inf')]

    return bottleneck_distance(points1, points2)
```

### 5.6 Combined Similarity Score

```python
def compute_structural_similarity(paper1_structures, paper2_structures):
    """
    Master function: combine all similarity layers

    Returns:
        total_score: Overall structural similarity (0.0-1.0)
        breakdown: Individual layer scores
        evidence: Supporting details for the match
    """

    scores = {}
    evidence = {}

    # Layer 1: Equation similarity
    if paper1_structures.equations and paper2_structures.equations:
        eq_scores = []
        for eq1 in paper1_structures.equations:
            for eq2 in paper2_structures.equations:
                score, mapping = equation_similarity(eq1.sympy, eq2.sympy)
                eq_scores.append(score)
                if score > 0.7:
                    evidence['equations'] = {
                        'eq1': str(eq1.latex),
                        'eq2': str(eq2.latex),
                        'mapping': mapping,
                        'score': score
                    }

        scores['equation'] = max(eq_scores) if eq_scores else 0.0
    else:
        scores['equation'] = 0.0

    # Layer 2: Graph similarity
    if paper1_structures.graphs and paper2_structures.graphs:
        graph_scores = []
        for g1 in paper1_structures.graphs:
            for g2 in paper2_structures.graphs:
                score, mapping = graph_similarity(g1, g2)
                graph_scores.append(score)
                if score > 0.7:
                    evidence['graph'] = {
                        'motifs_in_common': find_common_motifs(g1, g2),
                        'score': score
                    }

        scores['graph'] = max(graph_scores) if graph_scores else 0.0
    else:
        scores['graph'] = 0.0

    # Layer 3: Dynamical equivalence
    if paper1_structures.dynamical_systems and paper2_structures.dynamical_systems:
        dyn_scores = []
        for ds1 in paper1_structures.dynamical_systems:
            for ds2 in paper2_structures.dynamical_systems:
                score = dynamical_equivalence(ds1, ds2)
                dyn_scores.append(score)
                if score > 0.7:
                    evidence['dynamics'] = {
                        'shared_bifurcations': get_shared_bifurcations(ds1, ds2),
                        'shared_regime': ds1.regime,
                        'score': score
                    }

        scores['dynamics'] = max(dyn_scores) if dyn_scores else 0.0
    else:
        scores['dynamics'] = 0.0

    # Layer 4: Topological similarity
    if paper1_structures.topological_features and paper2_structures.topological_features:
        topo_scores = []
        for t1 in paper1_structures.topological_features:
            for t2 in paper2_structures.topological_features:
                score = topological_similarity(t1, t2)
                topo_scores.append(score)
                if score > 0.7:
                    evidence['topology'] = {
                        'betti_numbers': t1['betti_numbers'],
                        'score': score
                    }

        scores['topology'] = max(topo_scores) if topo_scores else 0.0
    else:
        scores['topology'] = 0.0

    # Weighted combination (prefer equation and graph matches)
    weights = {
        'equation': 0.4,
        'graph': 0.3,
        'dynamics': 0.2,
        'topology': 0.1
    }

    total_score = sum(scores[layer] * weights[layer] for layer in scores)

    return {
        'total_score': total_score,
        'breakdown': scores,
        'evidence': evidence,
        'confidence': compute_match_confidence(scores, evidence)
    }
```

### 5.7 Why This Beats Cosine Similarity

**Current System**:
```python
# Cosine similarity on text embeddings
embed1 = model.encode("feedback loops regulate cell size")
embed2 = model.encode("feedback mechanisms control growth")
similarity = cosine(embed1, embed2)  # → 0.78 (HIGH!)
```
**Problem**: Matches on semantics, not structure.

**New System**:
```python
# Structural comparison
equations1 = [dx/dt = αx - βxy, dy/dt = δxy - γy]  # Lotka-Volterra
equations2 = [dS/dt = -βSI, dI/dt = βSI - γI]      # SIR model

eq_similarity = equation_similarity(equations1[0], equations2[0])
# → 0.4 (different structure despite similar semantics)

equations3 = [dA/dt = k1*A*B - k2*A, dB/dt = k2*A - k3*B]  # Chemical kinetics

eq_similarity = equation_similarity(equations1[0], equations3[0])
# → 0.85 (SAME STRUCTURE despite different domains!)
```

**Result**: Find REAL mathematical equivalences, not semantic similarities.

---

## 6. Quality Evaluation Framework

### 6.1 Discovery Rating Criteria

#### Tier 1: Publication-Worthy (Score ≥ 9/10)

**Criteria**:
1. **Mathematical Precision**: Can write down identical equations/graphs
2. **Non-Obviousness**: Domain experts wouldn't naturally connect these fields
3. **Novelty**: Not already documented in literature
4. **Actionable**: Enables specific knowledge/method transfer
5. **Cross-Domain**: Genuinely different fields (not subcategories)

**Example**:
> "The Hodgkin-Huxley equations for neural action potentials reduce to the same normal form as the van der Pol oscillator used in laser physics, suggesting neuronal spike generation could be analyzed using laser threshold theory."

**Why Excellent**:
- Specific equations identified
- Non-obvious connection (neuroscience ↔ laser physics)
- Enables method transfer (laser theory → neuroscience)
- Documented normal form equivalence

#### Tier 2: Research-Grade (Score 7-8/10)

**Criteria**:
1. Structural similarity verified mathematically
2. Connection may be known in specialized circles but not widely
3. Useful for teaching/understanding
4. Partial knowledge transfer possible

**Example**:
> "Supply chain network optimization uses the same graph algorithms as vascular system modeling (Murray's Law for optimal branching), though optimization criteria differ."

**Why Good**:
- Specific algorithm identified
- Practical connection (engineering ↔ biology)
- Method transfer with caveats

#### Tier 3: Interesting but Known (Score 5-6/10)

**Criteria**:
1. Valid structural similarity
2. Already well-documented
3. Educational value
4. Limited research novelty

**Example**:
> "Random walks in social networks follow the same diffusion mathematics as Brownian motion in physics."

**Why Moderate**:
- True but well-known connection
- Already in textbooks
- Limited novelty

#### Tier 4: Weak/Superficial (Score < 5/10)

**Criteria**:
1. Semantic similarity without structural equivalence
2. Trivial observation
3. No actionable insight
4. Too vague to verify

**Example**:
> "Both economics and biology have feedback loops."

**Why Weak**:
- No specific mathematical structure
- Trivial observation
- No method transfer possible

### 6.2 Validation Protocol

#### Stage 1: Automated Filtering
```python
def automated_quality_check(match):
    """First-pass filtering before human review"""

    flags = {
        'has_equations': match['evidence'].get('equations') is not None,
        'has_graph': match['evidence'].get('graph') is not None,
        'cross_domain': match['paper1_domain'] != match['paper2_domain'],
        'high_structural_score': match['total_score'] > 0.7,
        'low_semantic_score': match.get('semantic_score', 1.0) < 0.6,
        # ^ If semantic is low but structural is high → interesting!
    }

    # Require at least 3/5 flags
    if sum(flags.values()) >= 3:
        return 'PASS_TO_HUMAN'
    else:
        return 'REJECT'
```

#### Stage 2: Expert Review
```python
EXPERT_REVIEW_QUESTIONS = [
    "Can you write down the mathematical equivalence explicitly?",
    "Would a domain expert in Field A know about this connection to Field B?",
    "Does this enable any specific method/theory transfer?",
    "Is this documented in existing literature? (cite if yes)",
    "Rate non-obviousness (1-10):",
    "Rate actionability (1-10):",
    "Overall publication potential (reject/minor interest/significant/major):"
]
```

#### Stage 3: Literature Search
```python
def check_novelty(discovery):
    """Search literature for prior documentation"""

    query = f"{discovery['concept']} AND {discovery['domain1']} AND {discovery['domain2']}"

    # Search:
    # - Google Scholar
    # - arXiv
    # - CrossRef

    results = search_literature(query)

    if len(results) > 0:
        return {
            'novelty': 'low',
            'prior_work': results[:5]
        }
    else:
        return {
            'novelty': 'high',
            'prior_work': []
        }
```

### 6.3 Non-Obviousness Scoring

```python
def compute_non_obviousness(paper1, paper2, match):
    """
    Quantify how surprising/non-obvious the connection is

    Factors:
    - Domain distance (how different are the fields?)
    - Terminology overlap (low overlap → more surprising)
    - Citation overlap (papers cite common work?)
    - Semantic vs structural score gap
    """

    score = 0.0

    # Domain distance
    domain_dist = compute_domain_distance(paper1.domain, paper2.domain)
    score += domain_dist * 0.3

    # Terminology overlap (inverse)
    term_overlap = compute_terminology_overlap(paper1.text, paper2.text)
    score += (1.0 - term_overlap) * 0.2

    # Citation overlap (inverse)
    citation_overlap = len(set(paper1.citations) & set(paper2.citations))
    score += (1.0 / (1.0 + citation_overlap)) * 0.2

    # Structural vs semantic gap
    structural_sim = match['total_score']
    semantic_sim = cosine(embed(paper1.abstract), embed(paper2.abstract))

    gap = structural_sim - semantic_sim
    if gap > 0:  # High structural, low semantic → very non-obvious!
        score += gap * 0.3

    return score

def compute_domain_distance(domain1, domain2):
    """
    How different are two domains?

    Uses domain taxonomy:
    - Same field, different subfield: 0.3
    - Related fields (physics-chemistry): 0.5
    - Distant fields (biology-economics): 0.8
    - Very distant (neuroscience-finance): 1.0
    """

    DOMAIN_GRAPH = {
        ('physics', 'chemistry'): 0.5,
        ('physics', 'math'): 0.4,
        ('biology', 'chemistry'): 0.5,
        ('biology', 'ecology'): 0.3,
        ('economics', 'sociology'): 0.4,
        ('neuroscience', 'biology'): 0.3,
        # ... very distant pairs
        ('neuroscience', 'finance'): 1.0,
        ('ecology', 'computer_science'): 0.9,
    }

    pair = tuple(sorted([domain1, domain2]))
    return DOMAIN_GRAPH.get(pair, 0.7)  # Default: moderately distant
```

### 6.4 Actionability Scoring

```python
def compute_actionability(match):
    """
    Can this discovery enable specific actions?

    Examples of actionable:
    - "Use algorithm X from Field A to solve problem Y in Field B"
    - "Theory T from Field A predicts phenomenon P in Field B"
    - "Method M from Field A optimizes process Q in Field B"
    """

    score = 0.0

    # Has specific algorithm/method transfer?
    if match['evidence'].get('transferable_method'):
        score += 0.4

    # Has predictive value?
    if match['evidence'].get('predictive_capability'):
        score += 0.3

    # Suggests concrete experiment/test?
    if match['evidence'].get('testable_hypothesis'):
        score += 0.3

    return score
```

### 6.5 Ground Truth Validation

**Strategy**: Test system on known isomorphisms.

```python
GROUND_TRUTH_ISOMORPHISMS = [
    {
        'id': 'lotka_volterra',
        'paper1': 'Lotka 1910 - Chemical Oscillations',
        'paper2': 'Volterra 1926 - Predator-Prey',
        'expected_match_score': 0.9,  # Should score very high
        'equation_equivalence': True
    },
    {
        'id': 'black_scholes_heat',
        'paper1': 'Black & Scholes 1973 - Options Pricing',
        'paper2': 'Fourier 1822 - Heat Conduction',
        'expected_match_score': 0.85,
        'equation_equivalence': True
    },
    {
        'id': 'hopf_bifurcation',
        'paper1': 'FitzHugh 1961 - Neural Oscillations',
        'paper2': 'Lorenz 1963 - Atmospheric Convection',
        'expected_match_score': 0.75,  # Same bifurcation type
        'normal_form_equivalence': True
    },
    # ... add more known examples
]

def validate_on_ground_truth():
    """Test system performance on known isomorphisms"""

    results = []

    for gt in GROUND_TRUTH_ISOMORPHISMS:
        paper1 = fetch_paper(gt['paper1'])
        paper2 = fetch_paper(gt['paper2'])

        structures1 = deep_extraction_pipeline(paper1)
        structures2 = deep_extraction_pipeline(paper2)

        match = compute_structural_similarity(structures1, structures2)

        results.append({
            'ground_truth_id': gt['id'],
            'expected_score': gt['expected_match_score'],
            'actual_score': match['total_score'],
            'error': abs(gt['expected_match_score'] - match['total_score']),
            'detected': match['total_score'] > 0.7
        })

    # Performance metrics
    detection_rate = sum(1 for r in results if r['detected']) / len(results)
    mean_error = sum(r['error'] for r in results) / len(results)

    print(f"Detection Rate: {detection_rate * 100:.1f}%")
    print(f"Mean Score Error: {mean_error:.3f}")

    return results
```

---

## 7. Implementation Roadmap

### Phase 1: Proof of Concept (Weeks 1-4)

**Goal**: Demonstrate that deep extraction + structural matching can rediscover ONE known isomorphism.

#### Week 1: Extraction Prototype
- [ ] Implement equation extraction (LaTeX → SymPy)
- [ ] Test on 5 papers with known equations
- [ ] Success: Extract ≥80% of equations correctly

**Papers to Test**:
1. Lotka (1910) - Chemical oscillations
2. Volterra (1926) - Predator-prey
3. Black & Scholes (1973) - Options pricing
4. FitzHugh (1961) - Neural oscillations
5. Turing (1952) - Morphogenesis

**Deliverable**: `extraction_prototype.py` that outputs EquationObjects

#### Week 2: Equation Similarity
- [ ] Implement canonical form conversion
- [ ] Implement symbolic similarity
- [ ] Test on Lotka vs. Volterra (should match ≥0.9)

**Test Cases**:
```python
# Test 1: Exact match with different variables
eq1 = "dx/dt = αx - βxy"
eq2 = "dN/dt = rN - aNP"
assert equation_similarity(eq1, eq2)[0] > 0.9

# Test 2: Different structure
eq3 = "dx/dt = α(1 - x/K)x"  # Logistic growth
assert equation_similarity(eq1, eq3)[0] < 0.5
```

**Deliverable**: `equation_matcher.py` with validation tests

#### Week 3: Graph Extraction and Matching
- [ ] Implement equation → graph conversion
- [ ] Implement graph isomorphism detection
- [ ] Test on feedback loop examples

**Test Cases**:
- Negative feedback loop in ecology vs. engineering
- Positive feedback loop in economics vs. climate

**Deliverable**: `graph_matcher.py`

#### Week 4: End-to-End Test
- [ ] Full pipeline: PDF → Structures → Matches
- [ ] Target: Rediscover Lotka-Volterra equivalence
- [ ] Success: Match score ≥0.85 between chemistry and ecology papers

**Deliverable**: `poc_results.md` documenting success/failure

### Phase 2: Similarity Engine (Weeks 5-7)

**Goal**: Implement all four similarity layers and validate on ground truth.

#### Week 5: Dynamical Systems Layer
- [ ] Implement stability analysis
- [ ] Implement bifurcation detection
- [ ] Test on Hopf bifurcation examples

**Deliverable**: `dynamics_matcher.py`

#### Week 6: Topological Layer
- [ ] Implement persistent homology extraction
- [ ] Implement bottleneck distance
- [ ] Test on network topology examples

**Deliverable**: `topology_matcher.py`

#### Week 7: Integration and Validation
- [ ] Combine all layers into master similarity function
- [ ] Validate on 10 ground truth isomorphisms
- [ ] Target: ≥80% detection rate, <0.15 mean error

**Deliverable**: `validation_report.md` with ground truth results

### Phase 3: Quality at Scale (Weeks 8-12)

**Goal**: Process 1,000 papers DEEPLY and find publication-worthy discoveries.

#### Week 8: Paper Selection
- [ ] Identify high-quality paper sources
- [ ] Focus on equation-rich domains
- [ ] Target: 200 papers from each domain (physics, biology, economics, chemistry, neuroscience)

**Selection Criteria**:
- Must contain mathematical models (not pure empirical)
- Full text available
- Published in reputable venues
- Recent (2015+) or seminal classics

**Deliverable**: Curated list of 1,000 papers with metadata

#### Week 9-10: Deep Extraction
- [ ] Run extraction pipeline on all 1,000 papers
- [ ] Quality check: Manual review of 50 random extractions
- [ ] Fix extraction bugs found during review

**Target Metrics**:
- Equation extraction rate: ≥70%
- Graph extraction rate: ≥60%
- Overall extraction quality: ≥75%

**Deliverable**: Database with 1,000 deeply analyzed papers

#### Week 11: Candidate Generation
- [ ] Run similarity matching across all pairs
- [ ] Filter candidates with score ≥0.70
- [ ] Apply non-obviousness and cross-domain filters

**Expected Output**: 100-500 high-quality candidates

**Deliverable**: `candidates_ranked.json`

#### Week 12: Expert Curation
- [ ] Manual review of top 100 candidates
- [ ] Rate each using publication-worthy criteria
- [ ] Literature search for novelty check

**Target**:
- ≥10 publication-worthy discoveries (Tier 1)
- ≥20 research-grade discoveries (Tier 2)

**Deliverable**: `verified_discoveries_v2.json` with quality ratings

### Phase 4: Production System (Weeks 13-16)

**Goal**: Build scalable, automated system for ongoing discovery.

#### Week 13: Database Schema
- [ ] Design schema for structured objects (equations, graphs, etc.)
- [ ] Migrate from flat JSON to relational database
- [ ] Index for fast similarity queries

**Schema**:
```sql
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    arxiv_id VARCHAR,
    title TEXT,
    domain VARCHAR,
    extraction_quality FLOAT
);

CREATE TABLE equations (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id),
    latex TEXT,
    sympy TEXT,
    canonical_form TEXT,
    equation_type VARCHAR,
    variables JSONB,
    parameters JSONB
);

CREATE TABLE graphs (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id),
    nodes JSONB,
    edges JSONB,
    motifs JSONB
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    paper1_id INTEGER REFERENCES papers(id),
    paper2_id INTEGER REFERENCES papers(id),
    total_score FLOAT,
    equation_score FLOAT,
    graph_score FLOAT,
    dynamics_score FLOAT,
    topology_score FLOAT,
    evidence JSONB,
    human_rating VARCHAR,
    publication_potential VARCHAR
);
```

**Deliverable**: PostgreSQL schema + migration scripts

#### Week 14: API and Frontend
- [ ] REST API for querying discoveries
- [ ] Update frontend to show mathematical structures
- [ ] Display equations (LaTeX rendering)
- [ ] Show graph visualizations

**Deliverable**: Updated analog.quest with structural details

#### Week 15: Automation
- [ ] Automated weekly paper ingestion
- [ ] Automated extraction pipeline
- [ ] Automated candidate generation
- [ ] Human review queue interface

**Deliverable**: `automated_pipeline.py` with scheduling

#### Week 16: Documentation and Launch
- [ ] Complete technical documentation
- [ ] Write blog post explaining methodology
- [ ] Prepare academic paper draft
- [ ] Soft launch to beta users

**Deliverable**: Public launch of Analog Quest v2.0

---

## 8. Technical Requirements

### 8.1 Software Stack

#### Core Libraries
```
Python 3.10+

# Mathematical processing
sympy==1.12
scipy==1.11.0
numpy==1.24.0

# NLP and extraction
spacy==3.7.0
transformers==4.35.0
sentence-transformers==2.2.2

# Graph analysis
networkx==3.2
graph-tool==2.58  # or igraph
python-igraph==0.11.3

# Topological data analysis
gudhi==3.9.0
giotto-tda==0.6.0
ripser==0.6.4

# PDF processing
pdfplumber==0.10.3
PyMuPDF==1.23.0  # fitz
pdf2image==1.16.3

# LaTeX processing
pylatexenc==2.10
tex2py==0.1.0  # or custom parser

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# ML/LLM
openai==1.3.0  # for GPT-4 assistance
anthropic==0.7.0  # for Claude assistance

# Visualization
matplotlib==3.8.0
plotly==5.18.0

# Utilities
tqdm==4.66.0
joblib==1.3.2
```

#### Infrastructure
```
Database: PostgreSQL 15+
Compute: GPU optional but helpful for embeddings
Storage: ~100GB for 10,000 papers with full text
Memory: 16GB+ RAM recommended
```

### 8.2 Data Requirements

#### Paper Sources
1. **arXiv** (primary)
   - API: https://arxiv.org/help/api/
   - Full text: LaTeX source available for most papers
   - Coverage: Physics, CS, Math, Q-Bio, Econ, Stats

2. **OpenAlex** (secondary)
   - API: https://docs.openalex.org/
   - Metadata + abstracts (full text via DOI)
   - Coverage: All domains

3. **PubMed Central** (biomedical)
   - API: https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
   - Full text available for open access papers

#### Storage Estimates
- Raw PDFs: ~1MB per paper → 10GB for 10,000 papers
- Extracted text: ~100KB per paper → 1GB
- Structured objects: ~50KB per paper → 500MB
- Embeddings: ~1KB per equation → 100MB
- Total: ~12GB for 10,000 papers

### 8.3 Computational Requirements

#### Extraction Pipeline
- **CPU-bound**: PDF parsing, equation extraction
- **Time**: ~30 seconds per paper (serial)
- **Parallelization**: Easily parallelizable across papers
- **Estimate**: 1,000 papers in ~8 hours (4 cores)

#### Similarity Matching
- **Equation matching**: O(n²) comparisons but fast per pair (~0.01s)
- **Graph isomorphism**: O(n²) but expensive per pair (~1s worst case)
- **Optimization**: Blocking/filtering to reduce pairs
- **Estimate**: 1,000 papers → 500K pairs → ~50 hours (with filtering)

#### Embeddings (if used)
- **GPU helpful**: 100x speedup for batch embeddings
- **Time**: ~0.1s per text on GPU → 100 seconds for 1,000 papers

### 8.4 LLM Assistance

**When to Use LLMs**:
1. **Text-to-graph extraction**: When equations unavailable but mechanisms described verbally
2. **Equation normalization**: Help identify variable roles
3. **Quality evaluation**: Explain why match is interesting
4. **Literature search**: Check novelty via semantic search

**When NOT to Use LLMs**:
1. **Equation extraction**: Use symbolic parsers (SymPy)
2. **Graph isomorphism**: Use NetworkX algorithms
3. **Similarity scoring**: Use mathematical algorithms

**Cost Estimate**:
- LLM calls: ~100-200 per paper (for assistance)
- Cost: ~$0.05 per paper (GPT-4 Turbo)
- Total: $500 for 10,000 papers

---

## 9. Validation Strategy

### 9.1 Ground Truth Validation

**Step 1: Compile Ground Truth**
- Identify 20-30 known cross-domain isomorphisms from literature
- Include papers that established each connection
- Document expected match scores

**Step 2: Run System on Ground Truth**
- Extract structures from all ground truth papers
- Compute similarity scores
- Compare to expected scores

**Step 3: Analyze Errors**
- False negatives: Known isomorphisms we missed (< 20% acceptable)
- False positives: High scores where no real equivalence (should be 0)
- Score calibration: Are scores meaningful?

**Success Criteria**:
- Detection rate ≥80% (find 16+ of 20 ground truth cases)
- False positive rate <10%
- Score error <0.15 (predicted vs. actual)

### 9.2 Expert Review

**Process**:
1. Select 50 random high-scoring candidates
2. Recruit domain experts (5-10 people across fields)
3. Ask experts to rate:
   - Is the structural equivalence correct? (Yes/No)
   - How surprising is this connection? (1-10)
   - How useful/actionable is it? (1-10)
   - Would this merit publication? (Reject/Minor/Significant/Major)

**Success Criteria**:
- ≥70% of candidates confirmed as valid by experts
- ≥30% rated as "surprising" (≥7/10)
- ≥20% rated as publication-worthy (Significant or Major)

### 9.3 A/B Testing: New vs. Old

**Setup**:
- Run BOTH systems on same 1,000 papers
- Old: Text embeddings + cosine similarity
- New: Deep extraction + structural matching

**Comparison Metrics**:

| Metric | Old System | New System | Target |
|--------|-----------|-----------|---------|
| Top-100 precision (expert-verified) | ~15% | ??? | ≥50% |
| Non-obviousness score | ~3/10 | ??? | ≥7/10 |
| Actionability score | ~2/10 | ??? | ≥6/10 |
| Publication-worthy rate | ~0% | ??? | ≥10% |
| Cross-database matches | 0% | ??? | ≥30% |

**Success Criteria**: New system beats old on ALL metrics by ≥2x

### 9.4 Novelty Validation

**Process**:
1. For each high-rated discovery, search literature
2. Query: "{concept} AND {domain1} AND {domain2}"
3. Manually review top 20 results
4. If connection already documented → mark as "known"
5. If no documentation → mark as "novel"

**Tools**:
- Google Scholar
- Semantic Scholar API
- Connected Papers (visualization)
- CrossRef API

**Success Criteria**:
- ≥50% of top discoveries are genuinely novel (not documented)
- ≥20% are highly novel (no papers within 2 degrees of separation)

### 9.5 Reproducibility Testing

**Process**:
1. Extract structures from same paper twice (idempotency test)
2. Different extraction methods (PDF vs. LaTeX source)
3. Different parameter settings

**Success Criteria**:
- ≥95% consistency in equation extraction
- ≥90% consistency in graph extraction
- ≥85% consistency in final match scores

---

## 10. Success Criteria

### 10.1 Minimum Viable Success (3 months)

**Extraction**:
- [ ] Equation extraction works on ≥70% of math-heavy papers
- [ ] Graph extraction works on ≥60% of papers
- [ ] Extraction quality validated on 100 papers

**Matching**:
- [ ] Rediscover ≥80% of ground truth isomorphisms
- [ ] False positive rate <15%
- [ ] Non-obviousness score ≥6/10 on average

**Discoveries**:
- [ ] Find ≥10 publication-worthy discoveries
- [ ] ≥5 verified as novel by literature search
- [ ] ≥3 confirmed as surprising by domain experts

**Infrastructure**:
- [ ] Database supports structural objects
- [ ] API exposes match details
- [ ] Frontend displays equations and graphs

### 10.2 Strong Success (6 months)

**Scale**:
- [ ] 10,000 papers deeply analyzed
- [ ] 100+ publication-worthy discoveries
- [ ] ≥30% cross-database matches (arXiv + OpenAlex)

**Quality**:
- [ ] Top-100 precision ≥60% (expert-verified)
- [ ] Non-obviousness ≥7/10
- [ ] Actionability ≥6/10
- [ ] ≥20 discoveries novel enough to publish

**Impact**:
- [ ] Academic paper submitted documenting methodology
- [ ] ≥1 "holy shit" discovery that gets cited
- [ ] External researchers using the platform

### 10.3 Exceptional Success (12 months)

**Discovery**:
- [ ] ≥500 verified structural isomorphisms
- [ ] ≥50 publication-worthy discoveries
- [ ] ≥5 discoveries lead to actual research collaborations
- [ ] ≥1 discovery leads to new theory/application

**Adoption**:
- [ ] 1,000+ active users
- [ ] 10+ academic citations
- [ ] Researchers contribute discoveries
- [ ] Integration with other research tools

**Methodology**:
- [ ] Methodology paper published in top venue
- [ ] Other projects adopt the approach
- [ ] Open-source ecosystem develops

---

## Appendix A: Example Discoveries (Target Quality)

### Discovery 1: Lotka-Volterra Equivalence

**Paper 1**: Lotka (1910) - "Contribution to the Theory of Periodic Reactions"
**Domain**: Chemistry (autocatalytic reactions)
**Equations**:
```
dX/dt = k₁X - k₂XY
dY/dt = k₃XY - k₄Y
```

**Paper 2**: Volterra (1926) - "Fluctuations in the Abundance of a Species"
**Domain**: Ecology (predator-prey)
**Equations**:
```
dN/dt = rN - aNP
dP/dt = baNP - mP
```

**Structural Match**:
- Equation similarity: 0.95 (identical form)
- Graph: Negative feedback loop
- Dynamics: Periodic orbits (limit cycles)

**Explanation**:
"Both systems describe two-component interactions where component 1 grows autonomously, component 2 depends on component 1 for growth, and component 1 is consumed/inhibited by component 2. This creates coupled oscillations with phase lag. The mathematical structure is identical despite describing chemical concentrations vs. biological populations."

**Non-Obviousness**: 9/10 (chemistry ↔ ecology in 1910 was revolutionary)
**Actionability**: 8/10 (chemical reaction theory applies to ecology)
**Publication Potential**: MAJOR (this DID lead to major publications)

### Discovery 2: Black-Scholes as Heat Equation

**Paper 1**: Black & Scholes (1973) - "The Pricing of Options and Corporate Liabilities"
**Domain**: Finance
**Equation**:
```
∂V/∂t + ½σ²S²∂²V/∂S² + rS∂V/∂S - rV = 0
```

**Paper 2**: Fourier (1822) - "Théorie Analytique de la Chaleur"
**Domain**: Physics (heat conduction)
**Equation**:
```
∂u/∂t = α∂²u/∂x²
```

**Structural Match**:
- Equation similarity: 0.90 (same PDE class after transformation)
- Transform: `S = e^x, V = e^(-rt)u, τ = T - t`
- Dynamics: Diffusion process

**Explanation**:
"Through variable substitution, the Black-Scholes PDE for option pricing transforms into the standard heat/diffusion equation. This means centuries of heat conduction theory (Green's functions, boundary conditions, analytical solutions) directly apply to financial derivatives pricing."

**Non-Obviousness**: 10/10 (physics ↔ finance)
**Actionability**: 10/10 (physics methods solve finance problems)
**Publication Potential**: MAJOR (Nobel Prize in Economics 1997)

### Discovery 3: Ising Model = Hopfield Networks

**Paper 1**: Ising (1925) - "Contribution to the Theory of Ferromagnetism"
**Domain**: Statistical physics
**Hamiltonian**:
```
H = -Σ Jᵢⱼsᵢsⱼ - Σ hᵢsᵢ
```

**Paper 2**: Hopfield (1982) - "Neural Networks and Physical Systems with Emergent Collective Computational Abilities"
**Domain**: Neuroscience/AI
**Energy Function**:
```
E = -Σ wᵢⱼsᵢsⱼ - Σ θᵢsᵢ
```

**Structural Match**:
- Equation similarity: 1.0 (identical mathematical form)
- Graph: Fully connected network
- Dynamics: Energy minimization → stable states

**Explanation**:
"Hopfield networks use the exact same mathematical formalism as Ising spin glasses from statistical physics. Neurons = spins, synaptic weights = coupling constants, neural states = energy minima. This equivalence imports spin glass theory (replica symmetry breaking, memory capacity calculations) into neuroscience."

**Non-Obviousness**: 9/10 (physics ↔ neuroscience)
**Actionability**: 9/10 (physics theory predicts neural network behavior)
**Publication Potential**: MAJOR (Hopfield paper has 30,000+ citations)

---

## Appendix B: Implementation Checklist

### Phase 1: Proof of Concept
- [ ] Set up development environment
- [ ] Install required libraries (SymPy, NetworkX, etc.)
- [ ] Collect 5 test papers with known equations
- [ ] Implement LaTeX → SymPy conversion
- [ ] Implement canonical form generation
- [ ] Implement equation similarity function
- [ ] Test on Lotka-Volterra example
- [ ] Implement equation → graph conversion
- [ ] Implement graph isomorphism detection
- [ ] Document POC results

### Phase 2: Similarity Engine
- [ ] Implement stability analysis
- [ ] Implement bifurcation detection
- [ ] Implement persistent homology extraction
- [ ] Implement bottleneck distance
- [ ] Combine all similarity layers
- [ ] Collect ground truth isomorphisms
- [ ] Validate on ground truth
- [ ] Fix bugs identified during validation
- [ ] Document validation results

### Phase 3: Quality at Scale
- [ ] Curate 1,000 paper list
- [ ] Implement automated PDF download
- [ ] Run extraction pipeline on all papers
- [ ] Manual QA on 50 random extractions
- [ ] Run similarity matching
- [ ] Filter candidates (score ≥0.70, cross-domain)
- [ ] Manual review of top 100 candidates
- [ ] Literature novelty search
- [ ] Rate discoveries by publication potential
- [ ] Document verified discoveries

### Phase 4: Production System
- [ ] Design PostgreSQL schema
- [ ] Migrate data to database
- [ ] Build REST API
- [ ] Update frontend for structural display
- [ ] Implement LaTeX rendering
- [ ] Implement graph visualization
- [ ] Build automated pipeline
- [ ] Set up weekly paper ingestion
- [ ] Create human review queue
- [ ] Write documentation
- [ ] Soft launch to beta users
- [ ] Gather feedback
- [ ] Public launch

---

## Appendix C: References

### Scientific Background
1. Strogatz, S. H. (2015). *Nonlinear Dynamics and Chaos*. Westview Press.
2. Guckenheimer, J., & Holmes, P. (1983). *Nonlinear Oscillations, Dynamical Systems, and Bifurcations of Vector Fields*. Springer.
3. Kuznetsov, Y. A. (2004). *Elements of Applied Bifurcation Theory*. Springer.
4. Newman, M. (2018). *Networks*. Oxford University Press.
5. Edelsbrunner, H., & Harer, J. (2010). *Computational Topology: An Introduction*. AMS.

### Cross-Domain Examples
6. Lotka, A. J. (1910). "Contribution to the Theory of Periodic Reactions". *J. Phys. Chem.* 14(3): 271-274.
7. Volterra, V. (1926). "Fluctuations in the Abundance of a Species". *Nature* 118: 558-560.
8. Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities". *J. Political Economy* 81(3): 637-654.
9. Hopfield, J. J. (1982). "Neural Networks and Physical Systems with Emergent Collective Computational Abilities". *PNAS* 79(8): 2554-2558.

### Technical Methods
10. Meurer, A., et al. (2017). "SymPy: Symbolic Computing in Python". *PeerJ Computer Science* 3:e103.
11. Hagberg, A., Swart, P., & Schult, D. (2008). "Exploring Network Structure with NetworkX". *SciPy Conference*.
12. Maria, C., et al. (2014). "The Gudhi Library: Simplicial Complexes and Persistent Homology". *ICMS*.
13. Nature Communications (2024). "Structured Information Extraction from Scientific Text with Large Language Models". 15(1): 1418.

### Similar Projects
14. Symbolic Mathematics Tools: SymPy, SageMath, Wolfram Alpha
15. Topological Data Analysis: Ripser, giotto-tda, Mapper
16. Scientific Knowledge Extraction: Semantic Scholar, Connected Papers, Elicit.org

---

**END OF SPECIFICATION**

---

## Next Steps

1. **Review and Approve**: Stakeholder review of this specification
2. **Prioritize**: Decide on timeline (3, 6, or 12 month target)
3. **Resource Allocation**: Assign team members or identify need for hiring
4. **Begin Phase 1**: Start with proof of concept on known isomorphisms
5. **Iterate**: Expect to refine methodology based on POC results

**Key Decision Point**: Should we aim for "minimum viable success" (3 months) or "strong success" (6 months)?

My recommendation: **6-month timeline** balances ambition with achievability, gives time for proper validation, and allows for iteration when things don't work perfectly the first time.

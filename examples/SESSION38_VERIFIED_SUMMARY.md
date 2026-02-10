# Session 38: Verified Isomorphisms

**Date**: 2026-02-10
**Total Verified**: 30
- Excellent: 10
- Good: 20

**Similarity Range**: 0.4447 - 0.7364
**Mean Similarity**: 0.5355

## Methodology
LLM extraction + semantic embeddings (384-dim) + manual curation

## Top Domain Pairs
- econ-q-bio: 7
- physics-q-bio: 5
- q-bio-unknown: 4
- econ-physics: 4
- econ-unknown: 3
- nlin-unknown: 2
- cs-econ: 2
- cs-physics: 1
- cs-unknown: 1
- econ-nlin: 1

## Top 10 Isomorphisms

### 1. Similarity: 0.7364 (EXCELLENT)

**Domains**: unknown ↔ q-bio

**Paper 1**: Effects of multi-phase control mechanism on fibroblast dynamics

**Paper 2**: Coarse-graining and stochastic oscillations in cell-size homeostasis

**Structural Explanation**: Both describe cell size feedback control through phase-specific mechanisms (sizer/timer/adder). Extrinsic (population-density) vs intrinsic (size-deviation) feedback loops. Trade-offs between control strategies. Perfect structural isomorphism across different cell types.

---

### 2. Similarity: 0.7064 (EXCELLENT)

**Domains**: unknown ↔ q-bio

**Paper 1**: Effects of multi-phase control mechanism on fibroblast dynamics

**Paper 2**: Cell size control in bacteria

**Structural Explanation**: Both describe size homeostasis through feedback. Extrinsic noise and population structure jointly determine size distributions. Noise integration and control strategies. Same mechanism as #1 but different organisms (fibroblasts vs bacteria).

---

### 3. Similarity: 0.6692 (EXCELLENT)

**Domains**: unknown ↔ econ

**Paper 1**: Collaboration for the Bioeconomy -- Evidence from Innovation Output in Sweden

**Paper 2**: Strategic Interactions in Science and Technology Networks

**Structural Explanation**: Network position determines productivity through strategic complementarities. Central nodes access diverse knowledge/connections. Preferential attachment reinforces centrality advantage. Isomorphism: innovation networks (Sweden) vs science/tech networks.

---

### 4. Similarity: 0.6278 (GOOD)

**Domains**: unknown ↔ q-bio

**Paper 1**: Effects of multi-phase control mechanism on fibroblast dynamics

**Paper 2**: Cell proliferation maintains cell area polydispersity in the growing fruit fly wing epithelium

**Structural Explanation**: Both about cell size control but through different mechanisms. Paper 1: feedback across phases. Paper 2: proliferation-driven variability vs mechanical relaxation. Related but not perfect structural match.

---

### 5. Similarity: 0.5999 (GOOD)

**Domains**: unknown ↔ nlin

**Paper 1**: Discrete dynamical systems with scaling and inversion symmetries

**Paper 2**: Chaotic Dynamics in Black Holes

**Structural Explanation**: Both describe positive Lyapunov exponents (sensitivity to initial conditions), scaling laws, and self-similarity. One in discrete dynamical systems with fractal attractors, one in black hole particle motion. Solid structural match.

---

### 6. Similarity: 0.5997 (EXCELLENT)

**Domains**: econ ↔ q-bio

**Paper 1**: Human-AI Cooperation in Public Goods Game

**Paper 2**: Indirect Reciprocity with Environmental Feedback

**Structural Explanation**: Cooperation shaped by behavioral feedback AND resource constraints. Strategic behavior creates reputation/norms while simultaneously affecting shared resources. Feedback between social dynamics and ecological/environmental state. Perfect two-layer coupling.

---

### 7. Similarity: 0.5703 (GOOD)

**Domains**: unknown ↔ nlin

**Paper 1**: Discrete dynamical systems with scaling and inversion symmetries

**Paper 2**: Critical Slowing Down at Bifurcations

**Structural Explanation**: Both involve scaling laws and critical behavior. Paper 1: fractal attractors and self-similarity. Paper 2: critical slowing down at bifurcations with diverging timescales. Related mathematical structures.

---

### 8. Similarity: 0.5687 (GOOD)

**Domains**: unknown ↔ econ

**Paper 1**: Collaboration for the Bioeconomy -- Evidence from Innovation Output in Sweden

**Paper 2**: R&D Spillovers and Regional Innovation

**Structural Explanation**: Both about R&D/innovation networks. Network centrality → innovation output. Strategic interactions (Paper 2 adds Stackelberg/Nash equilibrium). Spillovers through connections. Solid match but Paper 1 more specific.

---

### 9. Similarity: 0.5484 (EXCELLENT)

**Domains**: q-bio ↔ physics

**Paper 1**: Free-Rider Problem in Shared Resources

**Paper 2**: The impact of heterogeneity on the co-evolution of cooperation and epidemics

**Structural Explanation**: Free-rider problem with multi-stability and hysteresis (shared resource cleaning) vs cooperation-epidemic coevolution with structural heterogeneity. Both show: heterogeneity as double-edged (creates leverage points AND weak links), multi-stability, and strategic trade-offs between local/global incentives. Beautiful isomorphism!

---

### 10. Similarity: 0.5443 (GOOD)

**Domains**: econ ↔ cs

**Paper 1**: DeFi Credit Exposures and Contagion

**Paper 2**: Seed Node Position and Network Damage

**Structural Explanation**: Shock propagation through networks. Network topology determines cascade extent. DeFi contagion vs physical network damage. Seed node position critical in both. Solid structural match.

---


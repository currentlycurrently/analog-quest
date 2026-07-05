# Atlas classification — results

- papers classified: 54
- templates in library: 50

## C1 — classification recall
- 27/30 = 0.90 (criterion >= 0.80)
- **PASS**
- misses:
  - 2004.01025 (wanted ['mirror_descent_multiplicative_weights'], got ['gradient_descent'])
  - 1612.08949 (wanted ['logistic_growth'], got ['replicator_dynamics'])
  - 2007.02182 (wanted ['paraxial_schrodinger'], got ['linear_schrodinger'])

## C2 — atlas join (cross-domain co-classification)
- STRICT (exact template match): 9/15 total (7/12 primary)
- EQUIV-CLASS (template_equivalences.json, authored post-hoc — see its provenance note): 13/15 total (10/12 primary)
- criterion: >= 10/15 total co-classify
- **strict FAIL / equiv PASS**

| pair | strict | equiv | shared template(s) | held-out |
|---|---|---|---|---|
| black_scholes_heat | NO | yes | black_scholes_pde |  |
| ising_hopfield | yes | yes | binary_spin_energy |  |
| lotka_volterra_econ | yes | yes | lotka_volterra |  |
| sir_rumor | yes | yes | sir_compartmental |  |
| kuramoto_powergrid | yes | yes | kuramoto_phase_oscillators |  |
| fokker_planck_diffusion_models | yes | yes | fokker_planck, langevin_sde |  |
| replicator_mirror_descent | NO | NO | — |  |
| logistic_adoption | NO | NO | — |  |
| oscillator_rlc | yes | yes | damped_driven_oscillator |  |
| burgers_traffic | NO | yes | burgers_equation |  |
| maxent_inference | NO | yes | maximum_entropy_free_energy |  |
| optimal_transport_econ | yes | yes | optimal_transport |  |
| cable_telegrapher | yes | yes | cable_telegrapher_equation | y |
| paraxial_schrodinger | NO | yes | paraxial_schrodinger | y |
| sine_gordon_josephson | yes | yes | sine_gordon | y |

## C3 — precision on distractor assignments
- distractor assignments (conf >= 0.6) reviewed: 15
- upheld: 14 = 0.93 (criterion >= 0.70)
- **PASS**

## Non-planted (distractor) assignments, for reference

- 2401.00621 -> linear_schrodinger (conf 0.85, twist: fractional Laplacian with L2-normalized constraint and subcritical nonlinear perturbation)
- 2401.00623 -> linear_schrodinger (conf 0.82, twist: coupled gauge fields and supercritical exponential nonlinearity in Chern-Simons gauge theory)
- 2401.00822 -> langevin_sde (conf 0.85, twist: eigenvalue dynamics of density matrices under continuous quantum monitoring with dephasing)
- 2401.00839 -> bellman_equation (conf 0.80, twist: value function and equilibrium characterization in repeated games with endogenous information disclosure)
- 2401.00940 -> nash_equilibrium (conf 0.75, twist: best-response allocation under congestion costs on multi-dimensional delivery networks)
- 2401.00948 -> binary_spin_energy (conf 0.90, twist: ferrimagnetic two-sublattice Ising model with asymmetric magnetic moments and hidden excited ground-state degeneracy)
- 2401.01397 -> logistic_growth (conf 0.75, twist: discrete Bass diffusion model on Cartesian networks with boundary effects reducing adoption rates exponentially with distance from boundaries)
- 2401.01632 -> master_equation (conf 0.85, twist: multitype consumer-resource birth-death processes with parameter-redundancy structure revealing identifiability out-of-equilibrium via generating functions)
- 2401.01850 -> markov_chain (conf 0.85, twist: two-state discrete system with exponentially-distributed dwell times)
- 2401.09955 -> langevin_sde (conf 0.80, twist: regime-switching with random parameters and jump components)


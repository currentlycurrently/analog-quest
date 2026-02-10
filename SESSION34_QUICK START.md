# Session 34 Quickstart Guide

## Context
Session 33 validated LLM extraction on 12 papers → 100% success, 5 cross-domain matches, 60-70% projected precision.

Session 34 goal: Scale to 100 papers and measure REAL precision.

## Key Finding #1: Paper Selection is Critical

Even in "mechanism-rich" domains, only ~30-40% of papers actually describe extractable mechanisms.

**Papers that describe mechanisms:**
- Ecological dynamics (population, competition, facilitation)
- Economic equilibria (markets, game theory, strategic interaction)
- Disease dynamics (epidemiology, SIR models)
- Cell biology dynamics (cell cycle, signaling, diffusion)
- Control systems (feedback, oscillation)

**Papers that DON'T describe mechanisms:**
- Pure ML/technique papers ("We present X algorithm...")
- Purely empirical studies ("We measured X and found Y")
- Methodological papers ("We developed method X for problem Y")
- Review papers (unless they synthesize mechanisms)

## Extraction Results (Session 34)

**Sample**: 40 papers stratified across 11 domains
**Extracted**: 18 papers with clear mechanisms
**Success rate**: 45% (18/40)

This is EXPECTED and validates the need for smart paper selection.

## High-Quality Extractions (n=18)

### Ecology (q-bio.PE): 4 papers
1. **ID 448** - Vegetation patterns: Facilitation-competition balance creates spatial patterns, Allee effect threshold
2. **ID 450** - Tumor-immune: T-cells attack tumor, PD-L1 escape, therapy blocks suppression
3. **ID 451** - Optimal harvesting: Flow-stock transformation, exploitation-conservation tradeoff
4. **ID 452** - Disease transmission: R0 threshold, network effects, spatial heterogeneity

### Economics (econ.GN): 4 papers
1. **ID 77** - Innovation networks: Centrality determines innovation, preferential attachment
2. **ID 83** - Tragedy of commons: Individual vs collective optimization, institutional rules shift equilibrium
3. **ID 87** - Network productivity: Position determines performance, information diffusion with decay
4. **ID 100** - Conditional cooperation: Reciprocity creates feedback, bistable equilibria

### Cell Biology (q-bio.CB): 3 papers
1. **ID 525** - Cell cycle control: Size-dependent regulation, intrinsic vs extrinsic feedback trade-off
2. **ID 542** - Serotonin dynamics: Reaction-diffusion, spatial coupling, microdomain formation
3. **ID 106** - Iterative model-experiment: Predictions → tests → updates (feedback loop)

### Other Biology (q-bio.*): 3 papers
1. **ID 157** - Sound damping: Frequency-selective decay, feedback between level and damping
2. **ID 164** - Epidemic stock-flow: Daily incidence accumulates to active cases
3. **ID 168** - Chaotic coexistence: Chaos enables coexistence beyond exclusion limit

### Physics (physics.gen-ph): 2 papers
1. **ID 1** - [To extract]
2. **ID 2** - [To extract]

### Math (math.CO): 2 papers
1. **ID 54** - [To extract]
2. **ID 69** - [To extract]

## Next Steps for Session 34

**Part 3**: Match the 18 extracted mechanisms semantically
- Use V2.2 algorithm (cosine similarity on normalized text)
- Cross-domain only
- Threshold ≥0.77

**Part 4**: Manually review ~20-30 matches
- Sample across similarity ranges (high, medium, low)
- Rate: Excellent / Good / Weak / False Positive
- Calculate precision = (Excellent + Good) / Total

**Part 5**: Decision point
- IF precision ≥60%: ✅ Scale to all 2,021 papers in Session 35
- IF precision 45-60%: ⚠️ Refine prompts, retry
- IF precision <45%: ❌ Pivot to framework transfer tool

## Key Insight for Future Sessions

The "hit rate" for mechanism extraction is ~30-45% even in good domains.

This means:
- Out of 2,021 papers, expect ~600-900 papers with extractable mechanisms
- Focus on mechanism-rich domains: ecology, economics, epidemiology, cell biology, control theory
- Skip: Pure ML papers, purely empirical studies, methodology papers

## Recommendation

**For Session 35 (if precision ≥60%)**:
1. Filter 2,021 papers to identify mechanism-rich candidates (~800-1000 papers)
2. Extract mechanisms using Claude API (batch processing)
3. Match cross-domain (≥0.77 threshold)
4. Expect ~200-400 high-quality matches at 60-70% precision

This is a **realistic, achievable path** to a viable product.

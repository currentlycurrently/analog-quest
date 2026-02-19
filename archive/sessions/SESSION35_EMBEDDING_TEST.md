# SESSION 35: Semantic Embedding Validation Test

**Date**: 2026-02-10
**Test Duration**: 30 minutes
**Status**: **CRITICAL FINDINGS - Embeddings improve but don't reach threshold**

---

## EXECUTIVE SUMMARY

**Goal**: Validate that semantic embeddings can match the 9 LLM-extracted mechanisms from Session 34.

**Result**:
- ✅ Embeddings work MUCH better than TF-IDF (max 0.657 vs 0.139)
- ❌ Top similarity (0.657) still below target threshold (0.75)
- ⚠️ Only 1 pair above 0.65, 0 pairs above 0.75

**Recommendation**: **Need more diverse mechanisms before scaling**

---

## TEST SETUP

**Input**: 9 LLM-extracted mechanisms from Session 34
**Model**: sentence-transformers (all-MiniLM-L6-v2)
**Method**: Cosine similarity on 384-dimensional embeddings
**Evaluation**: Cross-domain pairs only (different subdomains)

**Domain Breakdown**:
- q-bio.PE (ecology): 4 papers
- q-bio.CB (cell biology): 2 papers
- econ.GN (economics): 1 paper
- q-bio.QM (quantitative biology): 1 paper
- physics.gen-ph (physics): 1 paper

---

## RESULTS

### Similarity Statistics (29 cross-domain pairs)

- **Max similarity**: **0.657**
- **Mean similarity**: 0.215
- **Median similarity**: 0.216
- **Min similarity**: -0.050

### Threshold Analysis

| Threshold | Cross-Domain Pairs |
|-----------|-------------------|
| ≥0.85 | **0** |
| ≥0.80 | **0** |
| ≥0.75 | **0** |
| ≥0.70 | **0** |
| ≥0.65 | **1** |
| ≥0.60 | **1** |

**Finding**: No pairs reach our target threshold of 0.75.

---

## TOP 5 PAIRS - MANUAL REVIEW

### 1. Similarity: 0.657 (HIGHEST)

**Domain Pair**: q-bio.PE (Ecology/Epidemiology) ↔ q-bio.QM (Quantitative Biology)

**Paper 1 (ID 452)**: Island Ecosystem Services
- **Mechanism**: "Transmission rate increases with infected density. Recovery rate decreases infection duration. When transmission exceeds recovery (R0>1), epidemic spreads exponentially. Vaccination reduces susceptible population shifting R0 below 1. Spatial heterogeneity creates local pockets where R0 varies."
- **Type**: Epidemic dynamics (SIR model, population-level)

**Paper 2 (ID 370)**: Virulence-Transmission Relationships
- **Mechanism**: "Pathogen virulence (harm to host) causally influences transmission rate (spread to new hosts). Increased virulence may increase transmission initially but reduces host mobility decreasing spread. Trade-off creates optimal virulence level maximizing transmission. Evolutionary dynamics drive virulence toward this optimum."
- **Type**: Evolutionary tradeoff (organism-level)

**Assessment**: **RELATED BUT NOT ISOMORPHIC**
- Both describe disease transmission mechanisms
- BUT: Paper 1 is population-level dynamics (epidemic spread)
- Paper 2 is organism-level evolution (virulence optimization)
- Different scales, different mechanisms
- This is a "same topic" match, not a "same structure" match
- **Quality**: Moderate - related but not a true isomorphism

---

### 2. Similarity: 0.363

**Domain Pair**: q-bio.PE (Ecology) ↔ q-bio.QM (Quantitative Biology)

**Paper 1 (ID 448)**: Vegetation Patterns (Allee Effect)
- **Mechanism**: "Plants facilitate neighboring growth through local resource modification. Facilitation competes with resource competition. When precipitation is intermittent, facilitation-competition balance creates spatial vegetation patterns. Below threshold density, vegetation collapses due to weakened facilitation."

**Paper 2 (ID 370)**: Virulence-Transmission (same as above)

**Assessment**: **WEAK MATCH**
- Vegetation patterns vs pathogen evolution
- Both have optimization/tradeoffs but different structures
- Not a meaningful isomorphism
- **Quality**: Weak

---

### 3. Similarity: 0.363

**Domain Pair**: q-bio.PE (Ecology) ↔ q-bio.CB (Cell Biology)

**Paper 1 (ID 448)**: Vegetation Patterns (Allee Effect)
- **Mechanism**: (same as #2)

**Paper 2 (ID 525)**: Cell Cycle Control
- **Mechanism**: "Cell size determined by control mechanisms across cell cycle phases. Population-density-dependent regulation limits total cell numbers (extrinsic feedback). Cell-size-dependent regulation suppresses size variability (intrinsic feedback). Trade-off between extrinsic and intrinsic control."

**Assessment**: **WEAK MATCH**
- Both have feedback and control mechanisms
- But: Vegetation spatial patterns vs cell size homeostasis
- Different structural mechanisms
- **Quality**: Weak

---

### 4. Similarity: 0.334

**Domain Pair**: q-bio.CB (Cell Biology) ↔ physics.gen-ph (Physics)

**Paper 1 (ID 525)**: Cell Cycle Control (same as #3)

**Paper 2 (ID 2)**: Chaotic Dynamical Systems
- **Mechanism**: "System state evolves discretely through iterated function. Scaling symmetry preserves dynamics under magnification/contraction. Near fixed points, small perturbations grow exponentially (positive Lyapunov exponent) causing sensitive dependence. Trajectories confined to fractal attractor with non-integer dimension."

**Assessment**: **WEAK MATCH**
- Cell cycle homeostasis vs chaotic dynamics
- Both have dynamic evolution but fundamentally different structures
- **Quality**: Weak

---

### 5. Similarity: 0.318

**Domain Pair**: q-bio.PE (Ecology/Epidemiology) ↔ q-bio.CB (Cell Biology)

**Paper 1 (ID 452)**: Epidemic Transmission (same as #1)

**Paper 2 (ID 525)**: Cell Cycle Control (same as #3)

**Assessment**: **WEAK MATCH**
- Epidemic R0 threshold vs cell size homeostasis
- Both have regulation/control but different mechanisms
- **Quality**: Weak

---

## ANALYSIS: Why Embeddings Underperform

### 1. Sample Limitations

**Problem**: Only 9 mechanisms, heavily skewed to biology
- 4 ecology (q-bio.PE)
- 2 cell biology (q-bio.CB)
- 1 quantitative biology (q-bio.QM)
- 1 economics (econ.GN)
- 1 physics (physics.gen-ph)

**Result**: 77.8% of papers are biology (7/9)
- Most cross-domain pairs are biology ↔ biology
- Not truly "cross-domain" in spirit (ecology vs cell biology are both biology)
- Missing high-diversity pairs like economics ↔ physics, sociology ↔ ecology

### 2. Comparison with TF-IDF

| Method | Max Similarity | Pairs ≥0.75 | Pairs ≥0.65 |
|--------|---------------|-------------|-------------|
| **TF-IDF** (Session 34) | 0.139 | 0 | 0 |
| **Embeddings** (Session 35) | 0.657 | 0 | 1 |

**Embeddings are 4.7x better than TF-IDF** (0.657 vs 0.139)

But still not good enough for our 0.75 threshold.

### 3. What's Missing?

**High-quality isomorphisms require**:
1. **True cross-domain diversity** (not just biology subfields)
   - Economics ↔ Ecology (e.g., tragedy of commons ↔ resource depletion)
   - Physics ↔ Sociology (e.g., phase transitions ↔ social tipping points)
   - Control theory ↔ Economics (e.g., feedback loops in markets vs circuits)

2. **More mechanisms** to increase match probability
   - With only 9 mechanisms, we have 29 cross-domain pairs
   - Need ~50-100 mechanisms to have ~500-1000 pairs
   - Higher probability of finding true isomorphisms

3. **Mechanism-rich papers** (not just any papers)
   - Session 34 showed only 22.5% of papers have extractable mechanisms
   - Need to be very selective

---

## KEY FINDING: Domain Diversity is Critical

**The top match (0.657)** is epidemic transmission ↔ pathogen evolution.
- Both are about disease transmission
- But they're "related topics" not "structural isomorphisms"

**True isomorphisms** would be:
- Tragedy of commons (economics) ↔ Resource overexploitation (ecology)
- Network centrality (sociology) ↔ Innovation hubs (economics)
- Feedback control (engineering) ↔ Homeostasis (biology)
- Phase transitions (physics) ↔ Social tipping points (sociology)

**We don't have these diverse pairs in our sample!**

---

## COMPARISON TO SESSION 33

In Session 33, we manually extracted 12 mechanisms and found 5 cross-domain matches.

Let me check if those were higher quality:

**Session 33 matches** (from SESSION33_EXPERIMENTS.md):
1. Feedback loops (3 papers, 3 domains) - Economics, Biology, Physics
2. Network effects (2 papers, 2 domains) - Economics, Sociology
3. Threshold dynamics (2 papers, 2 domains) - Ecology, Microbiology
4. Strategic interaction (2 papers, same domain) - Economics
5. Flow-stock transformations (2 papers) - Epidemiology, Ecology

These were MANUALLY identified, not algorithmically matched.

**The lesson**: True isomorphisms may be rare even with good embeddings.

---

## DECISION POINT

### Option A: Scale Anyway (NOT RECOMMENDED)

- Extract all 2,021 papers → ~450-500 mechanisms
- Generate embeddings, match with 0.65 threshold (relaxed)
- Review top 30-50 matches
- **Risk**: Still might not find high-quality matches
- **Timeline**: 2-3 sessions

### Option B: Get More Diverse Sample FIRST (RECOMMENDED)

- Manually select 20-30 mechanism-rich papers from TRULY diverse domains:
  - Economics (game theory, markets, networks)
  - Ecology (population dynamics, resource competition)
  - Sociology (collective behavior, social networks)
  - Physics (phase transitions, chaos)
  - Engineering (control systems, optimization)
- Extract mechanisms (LLM)
- Test embeddings on this diverse set
- IF successful (≥3 matches at ≥0.65), THEN scale
- **Timeline**: 1 session to test, 2-3 to scale if successful

### Option C: Manual Curation (HONEST PATH)

- Accept that algorithmic matching has limitations
- Manually curate 20-30 high-quality isomorphisms
- Use embeddings to find *candidates*, manually verify
- Launch with curated set, grow organically
- **Timeline**: 2-3 sessions for manual curation

---

## RECOMMENDATION FOR SESSION 36

**Proceed with Option B: Get More Diverse Sample**

**Why**:
1. Current sample is 77.8% biology - not diverse enough
2. Embeddings work better than TF-IDF but need better input
3. Quick test (1 session) before committing to full scale
4. If this fails, pivot to Option C (manual curation)

**How**:
1. Select 20-30 mechanism-rich papers from truly diverse domains
   - 5 economics (game theory, markets, tragedy of commons)
   - 5 ecology (predator-prey, resource dynamics, Allee effects)
   - 5 sociology/network science (collective behavior, social networks)
   - 5 physics (phase transitions, chaos, critical phenomena)
   - 5 control theory/engineering (feedback, stability, optimization)
2. Extract mechanisms using Session 33/34 prompt
3. Generate embeddings, test matching
4. Target: Find ≥3 matches at ≥0.65 similarity
5. If successful → scale to all papers
6. If unsuccessful → pivot to manual curation (Option C)

**Expected outcome**: Validate embeddings work with diverse mechanisms OR discover we need manual curation

---

## FILES CREATED

1. `scripts/test_semantic_embeddings.py` - Embedding test script
2. `examples/session35_embedding_test_results.json` - Test results (top 10 pairs)
3. `SESSION35_EMBEDDING_TEST.md` - This document

---

## TIME SPENT

~1 hour:
- Setup and embedding generation: 20 min
- Analysis and manual review: 20 min
- Documentation: 20 min

---

## KEY TAKEAWAYS

1. ✅ **Embeddings work 4.7x better than TF-IDF** (0.657 vs 0.139)
2. ❌ **Still below target threshold** (0.657 vs 0.75)
3. ⚠️ **Sample too biology-heavy** (77.8% biology papers)
4. 🎯 **Need true domain diversity** for isomorphisms
5. 📊 **Small sample size** (9 mechanisms → 29 pairs)
6. 🔍 **Quality assessment**: Top match is "related topics" not "structural isomorphism"

**The path forward**: Test with diverse 20-30 paper sample before scaling.

---

**Last Updated**: 2026-02-10
**Test Status**: Complete
**Decision**: Proceed with Option B (diverse sample test)

# GROWTH STRATEGY.md

**Version**: 1.0
**Date**: 2026-02-10
**Based on**: Session 38 manual curation results (165 candidates reviewed)

---

## Executive Summary

After launching with **30 verified cross-domain isomorphisms**, this document outlines a sustainable, data-driven strategy to grow to **100+ verified isomorphisms** over 6 months through iterative expansion cycles.

**Key Insight**: Manual curation is essential. We generate candidates algorithmically, but quality requires human judgment to identify genuine structural isomorphisms vs superficial similarity.

---

## Current State (Session 38)

### What We Have
- **Papers in database**: 2,021 (keyword-based corpus)
- **LLM-extracted mechanisms**: 54 (domain-neutral, structural)
- **Verified isomorphisms**: 30 (10 excellent + 20 good)
- **Similarity range**: 0.44-0.74 (mean: 0.54)
- **Methodology**: LLM extraction + semantic embeddings (384-dim) + manual curation

### Quality Metrics from Session 38
- **Overall precision**: 24.2% (40/165 candidates were good or excellent)
- **Top-30 precision**: 87.5% (7/8 candidates)
- **Top-60 precision**: 60% (24/40 candidates)
- **Top-100 precision**: 42.4% (39/92 candidates)

**Takeaway**: Quality is concentrated at higher similarity scores, but excellent matches exist at low scores too (lowest excellent match: 0.44).

---

## Domain Pair Performance Analysis

### Tier 1: High-Precision Pairs (>50% precision)
*Prioritize finding more of these*

| Domain Pair | Precision | Excellent | Good | Total Candidates |
|-------------|-----------|-----------|------|------------------|
| **cs ↔ physics** | 100% | 1 | 1 | 2 |
| **econ ↔ nlin** | 100% | 0 | 1 | 1 |
| **econ ↔ physics** | 58.3% | 1 | 6 | 12 |
| **nlin ↔ unknown** | 50% | 0 | 2 | 4 |

**Strategy**: Actively seek more papers in these pairs, especially cs↔physics (100% precision but only 2 samples).

### Tier 2: Medium-Precision Pairs (25-50% precision)
*Balanced risk/reward*

| Domain Pair | Precision | Excellent | Good | Total Candidates |
|-------------|-----------|-----------|------|------------------|
| **cs ↔ econ** | 40% | 1 | 1 | 5 |
| **econ ↔ unknown** | 37.5% | 1 | 2 | 8 |
| **cs ↔ unknown** | 33.3% | 1 | 0 | 3 |
| **econ ↔ q-bio** | 28% | 1 | 6 | 25 |

**Strategy**: econ↔q-bio has high volume (25 candidates) and decent precision (28%). Good for scaling.

### Tier 3: Low-Precision Pairs (<25% precision)
*Avoid or be highly selective*

| Domain Pair | Precision | Excellent | Good | Total Candidates |
|-------------|-----------|-----------|------|------------------|
| physics ↔ q-bio | 22.5% | 2 | 7 | 40 |
| q-bio ↔ unknown | 13.9% | 2 | 3 | 36 |
| physics ↔ unknown | 5.9% | 0 | 1 | 17 |

**Strategy**: physics↔q-bio has 40 candidates (largest volume) but low precision. Only review top similarity scores.

### Zero-Precision Pairs (Avoid)
- nlin ↔ q-bio: 0% (0/7)
- cs ↔ q-bio: 0% (0/4)
- cs ↔ nlin: 0% (0/1)

---

## Similarity Threshold Strategy

### Observed Precision by Threshold

| Threshold | Candidates | Excellent | Good | Total Good+ | Precision |
|-----------|------------|-----------|------|-------------|-----------|
| **≥0.65 (ultra-high)** | 4 | 3 | 0 | 3 | **75%** |
| **≥0.57 (top-30)** | 8 | 4 | 3 | 7 | **87.5%** |
| **≥0.47 (top-60)** | 40 | 8 | 16 | 24 | **60%** |
| **≥0.40 (top-100)** | 92 | 10 | 29 | 39 | **42.4%** |
| **≥0.35 (all)** | 165 | 10 | 30 | 40 | **24.2%** |

### Recommended Thresholds

**For quality launches (conservative):**
- **Threshold**: ≥0.47
- **Expected precision**: 60%
- **Review effort**: ~40 candidates per expansion cycle
- **Expected yield**: ~24 verified isomorphisms per cycle

**For volume growth (balanced):**
- **Threshold**: ≥0.40
- **Expected precision**: 42%
- **Review effort**: ~100 candidates per expansion cycle
- **Expected yield**: ~42 verified isomorphisms per cycle

**For discovery (liberal):**
- **Threshold**: ≥0.35
- **Expected precision**: 24%
- **Review effort**: ~150-200 candidates per expansion cycle
- **Expected yield**: ~40-50 verified isomorphisms per cycle

**Recommendation**: Start with **≥0.47 threshold (60% precision)** for first few expansions. Lower threshold to 0.40 later if we need volume.

---

## Mechanism Type Performance

### High-Value Mechanism Types (>50% precision)
*Actively seek papers with these mechanisms*

| Mechanism Type | Precision | Excellent | Good | Total |
|----------------|-----------|-----------|------|-------|
| **coevolution** | 63% | 4 | 13 | 27 |
| **strategic** | 56% | 5 | 9 | 25 |
| **cooperation** | 50% | 3 | 12 | 30 |

**Examples:**
- Coevolution: Network-attribute feedback, opinion-network dynamics, cooperation-epidemic
- Strategic: Game theory, relative performance concerns, strategic complementarities
- Cooperation: Public goods, free-rider problems, reciprocity

### Medium-Value Types (30-40% precision)
*Good supporting mechanisms*

| Mechanism Type | Precision | Excellent | Good | Total |
|----------------|-----------|-----------|------|-------|
| **centrality** | 37.1% | 3 | 10 | 35 |
| **feedback** | 34.2% | 8 | 17 | 73 |
| **network** | 31.6% | 7 | 24 | 98 |
| **epidemic** | 31.2% | 1 | 9 | 32 |
| **heterogeneity** | 30.6% | 1 | 14 | 49 |

### Low-Value Types (<20% precision)
*Avoid or be highly selective*

| Mechanism Type | Precision | Total |
|----------------|-----------|-------|
| oscillation | 8.7% | 23 |
| chaos | 12% | 25 |
| scaling | 12.5% | 16 |
| phase_transition | 16.2% | 37 |

**Why low precision?** These are often mathematical/technical terms that appear across domains but don't necessarily indicate structural isomorphism.

---

## Domain Representation Analysis

### Current Mechanism Count by Domain

| Domain | Mechanism Count | % of Total |
|--------|----------------|------------|
| **q-bio** | 112 | 34% |
| **physics** | 71 | 21% |
| **unknown** | 68 | 21% |
| **econ** | 51 | 15% |
| **cs** | 15 | 5% |
| **nlin** | 13 | 4% |

### Domain Balance Issues

**Over-represented:**
- q-bio (34%) - biology-heavy sample from Sessions 34-37

**Under-represented:**
- **cs (5%)** - Only 15 mechanisms despite 352 papers in database!
- **nlin (4%)** - Only 13 mechanisms

**Strategic priority:** Extract more mechanisms from **cs** and **nlin** domains to balance representation and unlock high-precision pairs (cs↔physics: 100%, econ↔nlin: 100%).

---

## Expansion Cycle Structure

### Cycle Timeline (Every 2-3 weeks)

**Phase 1: Strategic Paper Selection (1-2 hours)**
- Select 50-100 mechanism-rich papers from database
- Target domains: Prioritize Tier 1 pairs and under-represented domains (cs, nlin)
- Use keyword filtering for efficiency (50% hit rate vs 22.5% random)

**Phase 2: LLM Mechanism Extraction (2-3 hours)**
- Manually extract 20-30 new mechanisms (domain-neutral language)
- Target: 50% hit rate (1 mechanism per 2 papers)
- Focus on high-value mechanism types (coevolution, strategic, cooperation)

**Phase 3: Embedding Generation & Matching (30 minutes)**
- Generate 384-dim embeddings for new mechanisms
- Match against existing corpus (cross-domain only)
- Apply threshold filter (≥0.47 or ≥0.40 depending on quality/volume goal)

**Phase 4: Manual Curation (2-3 hours)**
- Review 40-100 candidates (depending on threshold)
- Rate: excellent / good / weak / false
- Write structural explanations for excellent/good matches
- Select 15-30 verified isomorphisms

**Phase 5: Documentation & Launch (1 hour)**
- Update frontend with new discoveries
- Document findings in PROGRESS.md
- Update METRICS.md

**Total time per cycle: 6-10 hours**

---

## 6-Month Growth Projection

### Conservative Path (≥0.47 threshold, 60% precision)

| Month | Cycles | Papers Reviewed | New Mechanisms | Candidates | Verified | Cumulative Total |
|-------|--------|----------------|----------------|------------|----------|------------------|
| **Feb** | 1 | 50 | 25 | 40 | 24 | **54** |
| **Mar** | 2 | 100 | 50 | 80 | 48 | **102** |
| **Apr** | 2 | 100 | 50 | 80 | 48 | **150** |
| **May** | 2 | 100 | 50 | 80 | 48 | **198** |
| **Jun** | 1 | 50 | 25 | 40 | 24 | **222** |
| **Jul** | 1 | 50 | 25 | 40 | 24 | **246** |

**6-month outcome: ~250 verified isomorphisms** from **450 new papers** and **225 new mechanisms**.

### Aggressive Path (≥0.40 threshold, 42% precision)

| Month | Cycles | Papers Reviewed | New Mechanisms | Candidates | Verified | Cumulative Total |
|-------|--------|----------------|----------------|------------|----------|------------------|
| **Feb** | 1 | 75 | 38 | 100 | 42 | **72** |
| **Mar** | 2 | 150 | 75 | 200 | 84 | **156** |
| **Apr** | 2 | 150 | 75 | 200 | 84 | **240** |
| **May** | 2 | 150 | 75 | 200 | 84 | **324** |
| **Jun** | 1 | 75 | 38 | 100 | 42 | **366** |
| **Jul** | 1 | 75 | 38 | 100 | 42 | **408** |

**6-month outcome: ~400 verified isomorphisms** from **675 new papers** and **339 new mechanisms**.

---

## Quality Maintenance Strategy

### Quality Controls

1. **Manual curation always required** - No automated acceptance
2. **Structural explanations mandatory** - Forces deep understanding
3. **Conservative ratings** - When in doubt, rate "weak" not "good"
4. **Regular audits** - Every 50 isomorphisms, audit random sample
5. **User feedback loop** - Track which discoveries resonate with users

### Rating Guidelines

**Excellent** (rare, ~6% of candidates):
- Clear structural isomorphism across domains
- Same causal relationships and feedback loops
- Different terminology but identical mechanism
- "This is the SAME thing in different fields"

**Good** (selective, ~18% of candidates):
- Strong structural similarity
- Shared key features (feedback, topology, dynamics)
- Minor differences in implementation or scope
- "These are cousins, not twins"

**Weak** (majority, ~72% of candidates):
- Superficial similarity
- Shared keywords but different mechanisms
- Vague analogies
- "These might be related but not really isomorphic"

**False** (rare, ~2% of candidates):
- No meaningful connection
- Spurious embedding similarity
- "These have nothing to do with each other"

---

## Domain Expansion Priorities

### Priority 1: Unlock High-Precision Pairs (Months 1-2)

**Target domains:**
- **cs** (currently 15 mechanisms → goal: 60 mechanisms)
- **nlin** (currently 13 mechanisms → goal: 30 mechanisms)

**Expected unlocks:**
- More cs↔physics pairs (100% precision)
- More econ↔nlin pairs (100% precision)
- More cs↔econ pairs (40% precision)

**Effort:** 2 cycles focused on cs/nlin papers

### Priority 2: Deepen Economics Coverage (Months 3-4)

**Target domains:**
- **econ** (currently 51 mechanisms → goal: 100 mechanisms)
- **q-fin** (finance, under-represented in current sample)

**Expected unlocks:**
- More econ↔physics pairs (58.3% precision, high yield)
- More econ↔q-bio pairs (28% precision, high volume)

**Effort:** 2 cycles focused on economics/finance papers

### Priority 3: Explore New Domains (Months 5-6)

**Target domains:**
- **math** (network theory, game theory, dynamical systems)
- **neuroscience** (distinct from q-bio, cognitive mechanisms)
- **social sciences** (sociology, anthropology)

**Expected unlocks:**
- New domain pairs (unknown precision, discovery mode)
- Interdisciplinary connections

**Effort:** 2 cycles exploring new domains

---

## Success Metrics

### Quantity Metrics
- **Total verified isomorphisms**: 100+ by Month 3, 200+ by Month 6
- **Expansion cycles completed**: 8-10 cycles in 6 months
- **New mechanisms extracted**: 200-300 in 6 months

### Quality Metrics
- **Precision maintained**: ≥40% overall precision
- **Excellent ratio**: ≥5% of all verified isomorphisms rated excellent
- **User engagement**: Track which discoveries get shared/cited

### Diversity Metrics
- **Domain coverage**: ≥8 domains represented
- **Domain balance**: No domain >40% of mechanisms
- **Unique domain pairs**: ≥15 distinct pairs

### Efficiency Metrics
- **Hit rate**: Maintain ≥40% extraction hit rate (strategic selection)
- **Review efficiency**: ≤3 hours per 40 candidates reviewed
- **Cycle time**: Complete expansion cycle in ≤10 hours

---

## Risk Management

### Risk 1: Precision Degradation
**Symptom**: Precision drops below 30% overall
**Response**:
- Raise similarity threshold (0.47 → 0.55)
- Focus on Tier 1 domain pairs only
- Increase rating standards

### Risk 2: Extraction Fatigue
**Symptom**: Hit rate drops below 30%
**Response**:
- Improve keyword filtering
- Target more mechanism-rich subdomains
- Take break and return with fresh perspective

### Risk 3: Diminishing Returns
**Symptom**: New mechanisms produce few new matches
**Response**:
- Expand to new domains
- Lower similarity threshold (0.47 → 0.40)
- Focus on under-represented domain pairs

### Risk 4: Time Overruns
**Symptom**: Cycles taking >12 hours
**Response**:
- Reduce scope (40 candidates → 30 candidates)
- Batch reviews more efficiently
- Skip low-precision domain pairs

---

## Open Questions

### For User Feedback
1. Which discoveries are most interesting to users?
2. Do users prefer quantity (400) or quality (250)?
3. Are structural explanations clear enough?
4. What domains are users most interested in?

### For Future Research
1. Can we automate rating "weak" vs "false"?
2. Should we train a custom embedding model?
3. Can we improve precision beyond 60% without manual review?
4. What's the ceiling for number of genuine isomorphisms?

---

## Immediate Next Steps (Session 40+)

**Session 40: Frontend Build (Part 1)**
- Implement v1 web interface for 30 verified isomorphisms
- Static site with Next.js 14+ and Tailwind CSS
- Launch MVP to start gathering user feedback

**Session 41: Frontend Build (Part 2)**
- Polish UI/UX
- Deploy to Vercel
- Share publicly for feedback

**Session 42: First Expansion Cycle**
- Follow Phase 1-5 outlined above
- Target: cs and nlin domains (Priority 1)
- Goal: Add 20-30 new verified isomorphisms
- Test and refine expansion cycle process

---

## Document Maintenance

**Review frequency**: After every 2 expansion cycles (~monthly)
**Update triggers**:
- Precision drops >10pp
- New high-precision domain pairs discovered
- Major methodology changes

**Last updated**: 2026-02-10 (Session 39)
**Next review**: After Session 44 (2 cycles completed)

---

## Appendix: Detailed Analysis Data

See `examples/session39_analysis.json` for complete precision data:
- Domain pair precision breakdown (all 14 pairs)
- Similarity range precision (5 thresholds)
- Mechanism type precision (14 types)
- Domain mechanism counts


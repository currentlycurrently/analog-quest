# SESSION 67 - Alternative Strategy Decision Report

## Executive Summary

**DECISION: PIVOT TO EXISTING CORPUS** 🔄

After testing alternative strategies following Session 66's failure with refined search terms, the evidence suggests we should **pivot away from the 50K fetch goal** and instead focus on maximizing value from our existing 4,690 papers.

---

## Test Results Summary

### 1. Simple Terms with Quality Filtering (✅ Partial Success)

**Results**:
- Papers fetched: 601 from 32 terms
- Papers kept (score ≥6): 267 (44.4% pass rate)
- Average score of kept papers: 7.82/10 (excellent!)
- High-value rate: 55.9% overall
- Very high-value rate: 31.4% overall

**Key Findings**:
- Quality filtering works: We can get high-quality papers (avg 7.82/10)
- But volume is insufficient: Only 8.3 papers per term average
- To reach 15,000 high-quality papers: Would need ~1,800 search terms
- Diminishing returns: Many terms overlap, finding new ones is hard

**Verdict**: Works for quality, fails for scale

### 2. Hybrid Source Test (⚠️ Limited Test)

**OpenAlex Results** (10 terms tested):
- Papers fetched: 131
- Average score: 5.52/10
- High-value rate: 59.5%
- Very high-value rate: 35.9%

**arXiv Results**: Failed due to API issues

**Key Finding**: OpenAlex remains the best bulk source, but quality varies significantly by search term

### 3. Session 66 Refined Terms (❌ Failed)

**Results**:
- High-value rate: 33.8% (vs 51.5% baseline)
- Average score: 4.15/10 (vs 4.98 baseline)
- **Conclusion**: Complex search terms reduce quality

---

## Analysis: Why 50K Fetch is Not Viable

### Quality-Volume Trade-off

| Approach | Quality | Volume | Verdict |
|----------|---------|---------|---------|
| Random OpenAlex | 51.5% high-value | ✅ Easy 50K | ❌ Too much noise |
| Simple terms filtered | 100% high-value | ❌ Hard to get 15K | ⚠️ Doesn't scale |
| Refined terms | 33.8% high-value | ✅ Easy volume | ❌ Quality too low |
| Existing corpus | 28.8% high-value | Limited to 4,690 | ✅ Already available |

### The Mathematics Don't Work

To achieve our goal of 200+ discoveries:
1. Need ~5,000-8,000 mechanisms extracted
2. At 60% hit rate, need ~10,000-13,000 high-value papers
3. OpenAlex at 50% high-value rate = need 20,000-26,000 total papers
4. But quality varies wildly (0-88% per search term)
5. No reliable way to predict which terms give quality

### Search Term Exhaustion

- Session 65: 147 terms → 2,358 papers (16 per term avg)
- Session 67: 32 best terms → 267 quality papers (8.3 per term)
- Many terms overlap in results
- Finding 1,000+ unique high-performing terms is unrealistic
- Academic vocabulary doesn't match our idealized mechanism terms

---

## Alternative Path: Mine Existing Corpus

### What We Have
- **4,690 papers** already in database
- **631 high-value papers** (score ≥5/10) identified in Session 48
- **200 mechanisms** already extracted
- **46 verified discoveries** (after deduplication)

### Potential Remaining
- **431 high-value papers** not yet processed for mechanisms
- Estimated **250-300 additional mechanisms** extractable
- Potential for **100-150 more discoveries** from existing data

### Why This Makes Sense
1. **No fetch overhead** - Data already available
2. **Known quality** - Already scored all papers
3. **Proven success** - Session 48 showed ~100% hit rate on papers ≥7/10
4. **Realistic timeline** - Can complete in 5-10 sessions
5. **Cost-effective** - No API costs, just extraction time

---

## Recommendation: Three-Phase Pivot Plan

### Phase 1: Complete Existing Corpus Mining (Sessions 68-72)
- Extract mechanisms from remaining 431 high-value papers
- Target: 250-300 additional mechanisms (total: 450-500)
- Generate 2,000+ new cross-domain candidates
- Curate top 200-300 candidates
- Goal: 100-150 total discoveries

### Phase 2: Update Frontend (Sessions 73-74)
- Deploy 100-150 discoveries to analog.quest
- Add discovery statistics and visualizations
- Improve UI/UX based on patterns found
- Create "methodology" page explaining the process

### Phase 3: Strategic Expansion (Sessions 75-80)
- IF Phase 1 successful, consider targeted fetches:
  - Use only proven high-scoring domains (physics, cs, q-bio)
  - Focus on specific high-value search terms
  - Small batches (1,000 papers at a time)
  - Strict quality filtering (≥7/10 only)
- OR pivot to different approach entirely

---

## Decision Rationale

### Why NOT 50K Fetch
1. **Quality Crisis**: Can't maintain quality at scale
2. **Search Term Limits**: Not enough good terms for targeted fetch
3. **Time Investment**: Months of curation for dubious value
4. **Noise Problem**: 70% of papers would be low-value

### Why Mine Existing Corpus
1. **Proven Quality**: Hit rates of 60-100% on scored papers
2. **Immediate Value**: Can start extracting today
3. **Realistic Goals**: 100-150 discoveries is achievable
4. **No Wasted Effort**: Every paper processed is high-value
5. **Faster Results**: 5-10 sessions vs 30+ for 50K approach

---

## Immediate Next Steps (Session 68)

1. **Select next batch** of 50 papers (score = 7/10)
2. **Extract mechanisms** manually (expect 30-40 mechanisms)
3. **Generate candidates** using PostgreSQL
4. **Track progress** toward 100 discovery goal
5. **Document learnings** for future strategy

---

## Success Metrics for Pivot

- **Mechanisms**: 450-500 total (up from 200)
- **Discoveries**: 100-150 total (up from 46)
- **Precision**: Maintain 30-40% in curation
- **Timeline**: Complete by Session 75
- **Cost**: Minimal (just time investment)

---

## Conclusion

The dream of 50,000 papers and 200+ discoveries is **not viable** with current approaches. OpenAlex quality is too variable, search terms don't scale, and the filtering overhead is massive.

**The pragmatic path**: Mine the existing 4,690 papers thoroughly, extract all possible value, and demonstrate a working system with 100-150 real discoveries.

This is still **2-3x more discoveries** than we have now, achievable in weeks not months, and builds on proven successes.

**Quality over quantity. Depth over breadth. Real discoveries over inflated numbers.**

---

*Session 67 - 2026-02-15*
*Decision: Pivot to existing corpus mining*
*Next: Session 68 - Extract mechanisms from next 50 papers (score=7)*
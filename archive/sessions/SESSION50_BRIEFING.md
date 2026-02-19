# Session 50 Briefing - Mechanism Vocabulary Analysis

**Date**: 2026-02-12
**Previous Session**: Session 49 - Curation Complete (41 → 53 Discoveries)
**Your Mission**: Analyze mechanism vocabulary to prototype keyword-targeted arXiv search

---

## Current State

**Discoveries**: 53 (30 from Session 38, 11 from Session 47, 12 from Session 49)
**Mechanisms**: 104 (extracted from 2,194 papers)
**Papers Scored**: 2,194 (avg 3.31/10, 631 high-value ≥5/10)
**Remaining High-Value Papers**: ~526 papers (631 - 105 already extracted)

---

## The Problem

**Current workflow is slow**:
- Manual extraction: ~12-15 mechanisms/hour
- Random arXiv fetching: 3.3/10 avg mechanism richness
- Strategic domain fetching: 3.9/10 avg (+18% better but still wasteful)
- **Session 47 fetch waste**: 63% duplicates (220/350 papers)

**The opportunity**:
If we can identify **structural keywords** that predict mechanism-rich papers, we can:
- Fetch targeted papers with >50% hit rate (vs 22-40% random)
- **10x efficiency improvement**: 30-40 mechanisms per session vs 3-5
- Eliminate fetch waste by searching specific terms

---

## Your Task: Mechanism Vocabulary Analysis

Build a prototype keyword-targeted arXiv search system by analyzing the 104 mechanisms we've already extracted.

### Part 1: Extract Structural Keywords (1-2 hours)

**Objective**: Identify 20-30 high-signal keywords/phrases that predict mechanism richness

**Method**:
1. Read all 104 mechanisms from `examples/session48_all_mechanisms.json`
2. Extract frequently recurring structural terms:
   - **Process words**: feedback, coevolution, cascade, oscillation, equilibrium
   - **Relationship words**: trade-off, complementarity, threshold, heterogeneity
   - **Dynamics words**: bifurcation, criticality, emergence, self-organization
3. Count term frequency across mechanisms
4. Identify top 20-30 keywords with >10% occurrence rate
5. Group into categories (feedback systems, network effects, evolutionary dynamics, etc.)

**Output**: `examples/session50_structural_keywords.json`
```json
{
  "keywords": [
    {
      "term": "feedback",
      "count": 45,
      "percentage": 43.3,
      "category": "feedback_systems",
      "example_mechanism_ids": [525, 540, 461]
    },
    // ... more
  ],
  "categories": {
    "feedback_systems": ["feedback", "positive feedback", "negative feedback", ...],
    "network_effects": ["centrality", "heterogeneity", "cascade", ...],
    "evolutionary_dynamics": ["coevolution", "selection", "adaptation", ...],
    // ... more
  }
}
```

### Part 2: Test Keywords Against Known Papers (30-60 min)

**Objective**: Validate that keywords actually predict mechanism richness

**Method**:
1. Read `examples/session48_all_papers_scored.json` (2,194 papers with scores)
2. For each high-value paper (score ≥7/10):
   - Check if abstract contains any top-20 keywords
   - Calculate keyword hit rate
3. Compare keyword presence in high-value (≥7/10) vs low-value (<5/10) papers
4. Identify keywords with best discrimination power

**Output**: `examples/session50_keyword_validation.json`
```json
{
  "validation_results": {
    "high_value_papers": {
      "total": 251,
      "with_keywords": 215,
      "hit_rate": 0.856
    },
    "low_value_papers": {
      "total": 1563,
      "with_keywords": 687,
      "hit_rate": 0.440
    },
    "discrimination_power": 0.416
  },
  "keyword_performance": [
    {
      "term": "feedback",
      "high_value_hit_rate": 0.65,
      "low_value_hit_rate": 0.23,
      "discrimination": 0.42
    },
    // ... more
  ]
}
```

### Part 3: Build arXiv Search Queries (30-60 min)

**Objective**: Design targeted arXiv search queries using validated keywords

**Method**:
1. Select top 10-15 keywords with highest discrimination power
2. Build arXiv API queries combining:
   - Keywords (in abstract or title)
   - Good domains (q-bio, physics.soc-ph, cs.AI, cs.LG, etc.)
   - Recent papers (2024-2025)
3. Design 3-5 query templates:
   - Feedback systems: `abs:feedback AND (cat:q-bio OR cat:physics.soc-ph)`
   - Network dynamics: `abs:heterogeneity AND abs:network AND cat:econ`
   - Evolutionary dynamics: `abs:coevolution AND cat:q-bio`

**Output**: `examples/session50_search_queries.json`
```json
{
  "query_templates": [
    {
      "name": "feedback_systems",
      "keywords": ["feedback", "control", "homeostasis"],
      "domains": ["q-bio", "physics.soc-ph"],
      "query": "abs:feedback AND (cat:q-bio.* OR cat:physics.soc-ph)",
      "expected_hit_rate": 0.65
    },
    // ... more
  ]
}
```

### Part 4: Test Queries (Optional, 30 min)

**Objective**: Fetch 20-30 papers using keyword queries and score them

**Method**:
1. Use arXiv API to fetch 20-30 papers with top query
2. Score papers for mechanism richness (0-10 scale)
3. Calculate actual hit rate
4. Compare to baseline (3.3/10 random, 3.9/10 strategic domains)

**Success Criterion**: >50% hit rate (avg score ≥5/10 or >50% papers score ≥5/10)

---

## Expected Outcomes

**Minimum Success**:
- 20+ structural keywords identified
- Validation shows >60% discrimination power
- 3-5 arXiv search queries designed

**Target Success**:
- 30+ keywords with categorization
- >70% discrimination power validated
- 5-8 targeted queries
- Test queries achieve >50% hit rate

**Stretch Success**:
- Full keyword taxonomy (50+ terms)
- Tested queries achieve >60% hit rate
- 10x efficiency improvement validated
- Ready to use keyword search as standard workflow

---

## Key Files to Read

**Before starting**:
1. **CLAUDE.md** - Your core mission and principles
2. **PROGRESS.md** - Sessions 37-49 context
3. **METRICS.md** - Current stats (104 mechanisms, 53 discoveries)
4. **SESSION49_SUMMARY.md** - What just happened (if exists)

**Reference during work**:
5. `examples/session48_all_mechanisms.json` - All 104 mechanisms to analyze
6. `examples/session48_all_papers_scored.json` - 2,194 scored papers for validation
7. `scripts/score_all_papers.py` - Reference for scoring logic

---

## Why This Matters

**Current bottleneck**: Manual extraction is slow, random fetching is wasteful

**If keyword search works** (>50% hit rate):
- **10x efficiency**: 30-40 mechanisms per session vs 3-5
- **Zero fetch waste**: No duplicates, no irrelevant papers
- **Scalable path to 500+ mechanisms**: Can reach target in 10-15 sessions vs 100+
- **Validation of approach**: Structural patterns ARE detectable from text

**The vision**: Move from "fetch random papers and hope" to "fetch papers we KNOW have mechanisms"

---

## After Session 50

**If keyword search validates** (>50% hit rate):
- **Session 51**: Extract 30-40 mechanisms using keyword search
- **Session 52**: Continue curation (review 461 remaining Session 48 candidates)
- **Session 53**: Update frontend with 60+ discoveries

**If keyword search fails** (<50% hit rate):
- Continue mining existing 526 high-value papers
- Refine scoring algorithm
- Consider LLM-assisted extraction to speed up manual process

---

## Success Criteria

**Must achieve**:
- [ ] 20+ structural keywords extracted from 104 mechanisms
- [ ] Validation against 2,194 papers (hit rate calculated)
- [ ] 3-5 arXiv search queries designed
- [ ] Documentation: SESSION50_SUMMARY.md

**Target**:
- [ ] 30+ keywords with discrimination power >60%
- [ ] 5-8 targeted queries
- [ ] Test queries on 20-30 papers
- [ ] Hit rate >50% (validates approach)

---

## Time Estimate

- Part 1 (Extract keywords): 1-2 hours
- Part 2 (Validate keywords): 30-60 min
- Part 3 (Build queries): 30-60 min
- Part 4 (Test queries - optional): 30 min
- Documentation: 30 min
- **Total**: 3-4 hours

---

## Tools You'll Need

**Python libraries**:
- `json` - read/write JSON files
- `re` - regex for text processing
- `collections.Counter` - term frequency counting
- `scripts/fetch_papers.py` - arXiv API fetching (if testing)
- `scripts/score_all_papers.py` - reference for scoring

**arXiv API basics**:
```python
# Example query format
query = "abs:feedback AND (cat:q-bio.* OR cat:physics.soc-ph)"
# Fetch recent papers
base_url = "http://export.arxiv.org/api/query"
params = {
    "search_query": query,
    "start": 0,
    "max_results": 30,
    "sortBy": "submittedDate",
    "sortOrder": "descending"
}
```

---

## Questions to Answer

As you work through this:

1. **What are the most frequent structural terms?** (feedback, heterogeneity, etc.)
2. **Do these terms actually predict mechanism richness?** (>60% discrimination?)
3. **Can we build targeted queries with >50% hit rate?** (vs 33% random)
4. **Which categories are most promising?** (feedback systems, network effects, etc.)
5. **Is this approach 10x better than random fetching?** (efficiency validation)

---

## Remember

This is **exploratory research** - we're testing whether keyword-targeted search can 10x our efficiency.

**It's okay if it doesn't work perfectly**. Document what you learn:
- Which keywords work vs don't work
- Whether discrimination power is sufficient
- What alternative approaches might work better

**If it validates** (>50% hit rate), this becomes our standard workflow and unlocks the path to 500+ mechanisms.

**Good luck!** You're potentially unlocking 10x efficiency for the entire project. 🚀

---

**Files to Create**:
1. `examples/session50_structural_keywords.json` - Extracted keywords with frequencies
2. `examples/session50_keyword_validation.json` - Validation results
3. `examples/session50_search_queries.json` - Designed arXiv queries
4. `SESSION50_SUMMARY.md` - Session results and findings
5. Optional: `examples/session50_test_results.json` - Test query results

**Update After Session**:
- PROGRESS.md - Add Session 50 entry
- METRICS.md - Update if test queries fetched new papers
- DAILY_GOALS.md - Set Session 51 goals based on results

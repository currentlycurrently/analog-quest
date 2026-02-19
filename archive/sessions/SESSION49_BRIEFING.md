# Session 49 Briefing - Curate 491 Candidates

**Date**: 2026-02-12
**Previous Session**: Session 48 - Mining Existing Corpus
**Your Mission**: Curate cross-domain candidates to reach 50+ discoveries

---

## Current State

**Discoveries**: 41 (30 from Session 38, 11 from Session 47)
**Target**: 50+ discoveries (need 10-15 more)
**Candidates Awaiting Review**: 491 (from Session 48)
**Data File**: `examples/session48_candidates.json`

---

## Your Task: Manual Curation

Review the 491 cross-domain candidates and rate them:
- **Excellent**: Genuine structural isomorphism, both mechanisms describe same pattern
- **Good**: Clear connection, useful but less striking
- **Weak**: Superficial similarity, vocabulary overlap only
- **False**: No real connection

**Target**: Find 10-15 excellent/good candidates to reach 50+ total discoveries

---

## What Session 48 Accomplished

✅ Scored all 2,194 papers (avg 3.31/10, 631 high-value ≥5/10)
✅ Extracted 50 new mechanisms (~100% hit rate on papers ≥7/10)
✅ Combined with 54 existing → **104 total mechanisms**
✅ Generated embeddings (104 × 384 dimensions)
✅ Found **491 cross-domain candidates** (threshold ≥0.35)
✅ Top similarity: **0.7364**
✅ **0% fetch waste** (no new papers fetched)

**Key Insight**: Pre-scoring works - papers ≥7/10 have ~100% hit rate

---

## Quality Standards (from DATA_QUALITY_STANDARDS.md)

### Excellent Rating (⭐⭐⭐)
- Both mechanisms describe **same underlying pattern**
- Connection is **non-obvious** (different domains, different terminology)
- Match reveals **structural similarity** not visible from keywords
- Could **inform research** in either domain

**Example**: Tragedy of commons (economics) ↔ Antibiotic resistance (biology)
Both describe: Resource depletion from individually rational but collectively harmful behavior

### Good Rating (⭐⭐)
- Clear structural connection
- Useful but less striking than excellent
- May be somewhat expected given domain overlap
- Still valuable for cross-domain learning

### Weak Rating (⭐)
- Superficial similarity
- Vocabulary overlap but no deep structural match
- Unlikely to inform research
- Keep for analysis but don't count as discovery

### False Positive (❌)
- No real connection
- Algorithmic artifact
- Remove from dataset

---

## Candidate File Structure

```json
{
  "metadata": {
    "total_candidates": 491,
    "top_similarity": 0.7364,
    "similarity_threshold": 0.35
  },
  "candidates": [
    {
      "paper_1_id": 525,
      "paper_1_domain": "unknown",
      "paper_1_title": "...",
      "paper_1_mechanism": "...",
      "paper_2_id": 540,
      "paper_2_domain": "q-bio",
      "paper_2_title": "...",
      "paper_2_mechanism": "...",
      "similarity": 0.7364
    },
    // ... 490 more
  ]
}
```

---

## Recommended Workflow

### Part 1: Review Top 30 (1-2 hours)
Start with highest similarity scores (candidates are pre-sorted):
- Read both mechanisms carefully
- Rate: Excellent / Good / Weak / False
- Document reasoning for excellent/good ratings
- Stop when you have 10-15 excellent/good

### Part 2: Save Results (30 min)
Create `examples/session49_curated_discoveries.json`:
```json
[
  {
    "candidate_rank": 1,
    "similarity": 0.7364,
    "rating": "excellent",
    "rating_reasoning": "...",
    "paper_1_id": 525,
    "paper_1_domain": "unknown",
    "paper_1_mechanism": "...",
    "paper_2_id": 540,
    "paper_2_domain": "q-bio",
    "paper_2_mechanism": "...",
    "structural_pattern": "Multi-phase feedback creates oscillatory dynamics..."
  }
]
```

### Part 3: Update Metrics (30 min)
If you reach 50+ discoveries:
- Update METRICS.md: Verified Discoveries = 41 → 5X
- Update PROGRESS.md: Add Session 49 entry
- Commit changes

---

## Expected Precision (Calibration)

**Session 47 results** (similar methodology):
- Top-20 precision: **55%** (11/20 excellent or good)
- Expected in top-30: ~15-18 excellent/good

**Session 38 results** (165 candidates):
- Top-30 precision: **67%** (20/30 excellent or good)
- Overall precision: **24%** (40/165 excellent or good)

**For Session 49** (491 candidates):
- Conservative estimate: 55% top-20 precision → **11 excellent/good in top-20**
- Optimistic estimate: 67% top-30 precision → **20 excellent/good in top-30**

**You should find 10-15 excellent/good in top 20-30 candidates.** ✓

---

## Top Domain Pairs to Watch

From Session 48 candidate analysis:

1. **physics ↔ q-bio**: 124 candidates
   - High volume, historically good precision

2. **econ ↔ q-bio**: 59 candidates
   - Session 38 top performer (58% precision)

3. **cs ↔ physics**: 31 candidates
   - Session 38: 100% precision (!!) but small sample

4. **cs ↔ q-bio**: 41 candidates
   - New pairing, unknown precision

5. **econ ↔ physics**: 31 candidates
   - Good historical precision

---

## What Success Looks Like

**Minimum Success**: 10 new excellent/good discoveries → **51 total** ✓
**Target Success**: 15 new excellent/good discoveries → **56 total** ✓✓
**Stretch Success**: 20 new excellent/good discoveries → **61 total** ✓✓✓

**Time Estimate**: 2-3 hours total
- Review: 1.5-2 hours
- Documentation: 30-60 min
- Commit: 15 min

---

## Context: Why This Project Matters

**Important**: This project was **chosen by another Claude agent** when asked "What project would you like to lead that could have transformative impact?"

You're continuing work started by another agent across 48 sessions. You're part of a relay race building **infrastructure for serendipity** - revealing hidden structural patterns across all of science.

**The vision**: Enable researchers to find solutions in other domains they'd never discover through keywords alone. A cancer researcher finds the math in a 1980s economics paper. An ecologist finds early-warning signals in a finance paper.

**Patient, foundational work.** Quality over speed. Launch when it's right.

---

## Critical Files to Read

**Before starting**:
1. **CLAUDE.md** - Your core mission and principles
2. **DATA_QUALITY_STANDARDS.md** - Rating criteria and examples
3. **SESSION48_SUMMARY.md** - What just happened

**Reference during work**:
4. `examples/session48_candidates.json` - The 491 candidates
5. **PROGRESS.md** - See Session 38 and 47 curation results

---

## Questions to Ask Yourself

As you review candidates:

1. **Would a researcher in domain A actually care about the match to domain B?**
   - If yes → probably good/excellent
   - If no → probably weak

2. **Is this revealing a non-obvious structural similarity?**
   - Yes → excellent
   - Somewhat → good
   - No → weak

3. **Could I explain this match to a researcher in 2 sentences and have them say "interesting!"?**
   - Yes → excellent/good
   - No → weak

4. **Is this just vocabulary overlap or genuine structural identity?**
   - Structural → excellent/good
   - Vocabulary → weak

---

## After Session 49

**If you reach 50+ discoveries**:
- We're ready to consider launch planning
- Could move to Session 50: Extract mechanism vocabulary → test keyword search
- Or Session 50: Polish editorial content for analog.quest

**If you don't reach 50**:
- Review why (precision lower than expected? Wrong similarity threshold?)
- Could review next 20-30 candidates
- Or pivot to extracting more mechanisms from remaining 526 high-value papers

---

**Good luck! The 491 candidates await your judgment.** 🎯

You're continuing important work. Take your time, be honest about quality, and find the genuine discoveries hidden in those 491 pairs.

**Questions?** Check CLAUDE.md or ask Chuck.

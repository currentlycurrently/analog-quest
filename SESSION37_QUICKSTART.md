# Session 37 - Quick Start for New Agent

**Welcome!** You're starting Session 37. Here's everything you need to know in 5 minutes.

---

## What You Need to Do

**Mission**: Process all 2,021 papers in the database to generate 150-250 candidate isomorphisms for manual review.

**4 Steps**:
1. Extract mechanisms from 2,021 papers using LLM (expect ~450 mechanisms)
2. Generate embeddings for mechanisms (sentence-transformers)
3. Match cross-domain pairs with threshold ≥0.35
4. Export candidates for Session 38 manual review

**Time**: 3.5-4.5 hours

---

## Quick Context: Why We're Here

**Session 36 (just completed)** was the DECISIVE TEST:
- Tested embeddings on 17 diverse papers (econ, biology, physics, CS)
- ✅ Found **EXCELLENT match**: Tragedy of commons (econ ↔ biology) at **0.453 similarity**
- ✅ Found 3 more GOOD matches
- ✅ 100% LLM extraction hit rate
- ❌ Max similarity 0.544 (below 0.65 target)

**Key Insight**: **Domain Diversity Paradox**
- More diverse domains = better structural matches but LOWER similarity scores
- Best match was at 0.453, NOT highest score
- Standard threshold (0.65) would have MISSED the excellent match!

**Decision**: Use embeddings for discovery, humans for validation
- Threshold: ≥0.35 (not 0.65!)
- Generate large candidate pool
- Manual review in Session 38

---

## Files to Read (in order)

1. **SESSION37_PLAN.md** ⭐ START HERE ⭐
   - Complete step-by-step plan
   - Code templates for each script
   - Expected results

2. **SESSION36_DIVERSE_SAMPLE_TEST.md**
   - Why manual curation
   - Domain diversity paradox
   - What worked and what didn't

3. **SESSION34_RESULTS.md** (or examples/session33_experiments.md)
   - LLM extraction prompt (you'll need this!)
   - What to extract, what to skip

---

## Key Numbers to Remember

**From Session 34 (40 papers, LLM extraction test)**:
- Hit rate: 22.5% (9 mechanisms from 40 papers)
- This is EXPECTED - most papers are empirical/methods, not mechanism papers

**Expected for Session 37 (2,021 papers)**:
- Mechanisms: ~450 (22.5% of 2,021)
- Cross-domain pairs at ≥0.35: 150-250 candidates
- Manual review precision: ~40% (based on Session 36)
- Final verified matches (Session 38): 20-30

---

## Critical: The Extraction Prompt

**You MUST use the Session 33 LLM extraction prompt.**

Find it in:
- SESSION34_RESULTS.md (Section: "LLM Extraction Prompt")
- OR examples/session33_experiments.md

**Key principles**:
- Extract STRUCTURAL MECHANISMS (causal relationships, feedback loops, dynamics)
- Use DOMAIN-NEUTRAL language ("agents" not "firms", "components" not "proteins")
- IGNORE: Empirical studies, methods papers, surveys, purely technical papers
- Return "NO_MECHANISM" if paper doesn't describe a mechanism

**Example good mechanism**:
> "Network position determines individual output. Higher centrality increases productivity through strategic complementarities with connected agents."

**Example NO_MECHANISM**:
> Paper describes a new method for measuring X, or empirical study of Y, or survey of Z.

---

## The Scripts You'll Create

### 1. `scripts/session37_extract_all_mechanisms.py`
- Loop through all 2,021 papers
- Call LLM with Session 33 prompt
- Save mechanisms as JSON
- Expected output: ~450 mechanisms

### 2. `scripts/session37_generate_embeddings.py`
- Load mechanisms JSON
- Generate embeddings with sentence-transformers/all-MiniLM-L6-v2
- Save as numpy array

### 3. `scripts/session37_match_candidates.py`
- Load mechanisms and embeddings
- Calculate cross-domain similarities
- Filter by threshold ≥0.35
- Export top candidates

### 4. Export formatting
- Add review fields (rating, notes, status)
- Include metadata and statistics

---

## Success Criteria

✅ All 2,021 papers processed
✅ ~400-500 mechanisms extracted (20-25% hit rate OK!)
✅ 150-250 candidates generated at ≥0.35 threshold
✅ Exported in format ready for Session 38 manual review

**Session 38** will then manually review all candidates and select 20-30 verified matches.

---

## Common Questions

**Q: Only 22.5% hit rate? Is that bad?**
A: No! Most papers are empirical/methods. Session 34 got 22.5%, Session 36 got 100% on carefully selected papers. 20-25% is expected and good.

**Q: Why threshold 0.35 instead of 0.65?**
A: Session 36 found the BEST match (tragedy of commons - EXCELLENT!) at 0.453 similarity. A 0.65 threshold would miss it! Domain diversity lowers scores.

**Q: Won't 0.35 have lots of false positives?**
A: Yes (~60% based on Session 36). That's OK - manual review in Session 38 will filter them. We want to capture all potentially good matches.

**Q: What if LLM extraction is slow?**
A: Process in batches of 50-100. Save intermediate results. You can pause and resume.

---

## Ready to Start!

1. Read SESSION37_PLAN.md (complete details)
2. Read SESSION34_RESULTS.md (get extraction prompt)
3. Create extraction script
4. Run on all 2,021 papers
5. Generate embeddings
6. Match candidates
7. Export for review
8. Update docs and commit

**Let's build the candidate pool!** 🚀

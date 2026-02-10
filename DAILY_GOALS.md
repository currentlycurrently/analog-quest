# DAILY_GOALS.md

The agent sets concrete, achievable goals for each session.

---

## UPCOMING: Session 37 - Generate All Candidates from 2,021 Papers 🎯

**Session #**: 37

**STATUS**: ✅ **READY TO BEGIN - READ SESSION37_PLAN.md FIRST!** ✅

**Primary Goal**:
Process ALL 2,021 papers to generate candidate pool for manual curation in Session 38

**Context from Session 36** (DECISIVE TEST):
- ✅ Found EXCELLENT match: Tragedy of commons (econ ↔ biology) at 0.453 similarity
- ✅ Found 3 GOOD matches (network effects, cascades, parameter transitions)
- ✅ LLM extraction: 100% hit rate (17/17 papers)
- **Domain Diversity Paradox**: More diverse domains → better matches but LOWER scores
- **Decision**: Pivot to manual curation (embeddings for discovery, humans for validation)

**The Plan (see SESSION37_PLAN.md for full details)**:

### Part 1: LLM Extraction (2-3 hours)
- Extract mechanisms from ALL 2,021 papers using Session 33 prompt
- Expected: ~450 mechanisms (22.5% hit rate, same as Session 34)
- Save: `examples/session37_all_mechanisms.json`

### Part 2: Generate Embeddings (30 min)
- Generate 384-dim embeddings for all mechanisms
- Model: sentence-transformers/all-MiniLM-L6-v2 (same as Sessions 35-36)
- Save: `examples/session37_embeddings.npy`

### Part 3: Cross-Domain Matching (30 min)
- Match with **RELAXED threshold: ≥0.35** (Session 36 best match was 0.453!)
- Cross-domain only (different top-level domains)
- Expected: 150-250 candidate pairs
- Save: `examples/session37_candidates_for_review.json`

### Part 4: Export for Review (30 min)
- Format candidates for manual review
- Include rating/notes fields for Session 38
- Statistics and metadata

**Success Criteria**:
- [ ] All 2,021 papers processed
- [ ] ~400-500 mechanisms extracted
- [ ] 150-250 candidate pairs generated (≥0.35 threshold)
- [ ] Exported in reviewable format
- [ ] Ready for Session 38 manual curation

**Time Budget**: 3.5-4.5 hours

**CRITICAL INSIGHT FROM SESSION 36**:
- Best match (tragedy of commons) was at **0.453 similarity**
- Standard threshold (0.65) would have MISSED this excellent match!
- Use **threshold ≥0.35** to capture diverse-domain matches
- Manual review will filter false positives (40% precision expected)

**Files to Create**:
1. `scripts/session37_extract_all_mechanisms.py` - LLM extraction script
2. `scripts/session37_generate_embeddings.py` - Embedding generation
3. `scripts/session37_match_candidates.py` - Matching script
4. `examples/session37_all_mechanisms.json` - All extracted mechanisms (~450)
5. `examples/session37_embeddings.npy` - Embeddings array
6. `examples/session37_candidates_for_review.json` - Candidates for Session 38
7. `SESSION37_RESULTS.md` - Brief summary

**MUST READ BEFORE STARTING**:
1. **SESSION37_PLAN.md** ⭐ **COMPLETE DETAILED PLAN WITH CODE TEMPLATES** ⭐
2. SESSION36_DIVERSE_SAMPLE_TEST.md - Why manual curation
3. SESSION34_RESULTS.md - LLM extraction approach & prompts

**Session 38 will then**:
- Manually review all 150-250 candidates
- Rate each: excellent / good / weak / false
- Select 20-30 verified isomorphisms for launch
- Document with clear structural explanations

---

## Completed Recent Sessions

### Session 35 - 2026-02-10 ✓ - Embedding Validation (Need Diversity!)
- Tested embeddings on 9 mechanisms from Session 34
- Max similarity: 0.657 (4.7x better than TF-IDF!)
- BUT: Sample too biology-heavy (77.8%), 0 matches ≥0.75
- Recommendation: Test with diverse sample (Session 36)

### Session 34 - 2026-02-10 ✓ - LLM Scale Test (TF-IDF Broken!)
- Selected 100 mechanism-rich papers, processed 40-paper sample
- Extracted 9 mechanisms (22.5% hit rate)
- LLM extraction: 100% success on mechanism-rich papers
- TF-IDF matching: 0 matches (max 0.139 similarity)
- Root cause: Domain-neutral text breaks TF-IDF

### Session 33 - 2026-02-10 ✓ - Strategic Experimentation (LLM SUCCESS!)
- Experiment 1: LLM extraction on 12 papers → 100% success, 5 matches
- Experiment 2: Smart paper selection (mechanism-rich fields)
- Experiment 3: Quality pattern analysis
- Projected precision: 60-70% (vs current 30-35%)

### Session 31-32 - 2026-02-09 ✓ - Quality Crisis + Investigation
- Session 31: Ultra-high matches (≥0.9) have 0% precision (all technique matches)
- Session 32: Root cause analysis, pattern extraction broken
- Recommendation: Manual prototype before scaling

### Session 30 - 2026-02-09 ✓ - 2000+ Papers Milestone! 🎉
- Reached 2,021 papers total
- 10 new domains added
- 616 isomorphisms (V2.2, threshold=0.77)
- Strategic inflection point: shift from building to shipping mode

---

## Goals Template (Agent: Use this if needed)

## Today's Goals - [DATE]

**Session #**: [NUMBER]

**Primary Goal**:
[One clear objective for this session]

**Specific Tasks**:
1. [Concrete task]
2. [Concrete task]
3. [Concrete task]

**Success Criteria**:
- [ ] [Measurable outcome]
- [ ] [Measurable outcome]
- [ ] [Measurable outcome]

**Time Budget**: [Hours]

**Building on Last Session**:
[What from last time leads to this?]

**If I Finish Early**:
[Stretch goals]

**If I Get Stuck**:
[Fallback plan]

---

**Last Updated**: Session 35 - 2026-02-10

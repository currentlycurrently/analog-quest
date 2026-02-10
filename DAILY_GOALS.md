# DAILY_GOALS.md

The agent sets concrete, achievable goals for each session.

---

## UPCOMING: Session 37 - Manual Curation Path: Candidate Generation 🎯

**Session #**: 37

**STATUS**: ⚠️ **READY TO BEGIN** ⚠️

**Primary Goal**:
Generate embedding-based candidates for manual curation with relaxed threshold

**Context from Sessions 33-36**:
- Session 33: LLM extraction validated (12 papers, 100% success)
- Session 34: TF-IDF failed (max similarity 0.139)
- Session 35: Embeddings work 4.7x better (max 0.657) but sample too biology-heavy
- **Session 36**: DECISIVE TEST - Found 4 good/excellent matches BUT max similarity only 0.544
  - **Domain Diversity Paradox**: More diverse domains → better structural matches but LOWER scores
  - **Best match**: Tragedy of commons (econ ↔ biology) at 0.453 similarity - EXCELLENT!
  - **Decision**: Pivot to manual curation (Outcome B - Partial Success)

**Specific Tasks**:

### Option A: COMPREHENSIVE APPROACH (Recommended)
Generate large candidate pool for manual review in Session 38

**PART 1**: Extend Session 36 sample (1 hour)
- Select 30-50 MORE mechanism-rich papers (add to Session 36's 17)
- Target: ~50-70 total papers across diverse domains
- Extract mechanisms using LLM (expect ~30-50 mechanisms total)

**PART 2**: Generate all candidate pairs (30 min)
- Generate embeddings for all mechanisms
- Calculate cross-domain similarities
- Use **relaxed threshold (≥0.35-0.40)** to cast wide net
- Save top 100-150 candidates for manual review

**PART 3**: Initial filtering (30 min)
- Quick triage of top 100 candidates
- Remove obvious false positives
- Identify promising clusters
- Prepare for deep manual review in Session 38

### Option B: FOCUSED APPROACH (Faster)
Use Session 36's 17 papers + add 10-20 more

**PART 1**: Add 10-20 targeted papers (30 min)
- Focus on domains underrepresented in Session 36
- Extract mechanisms (expect ~25-30 total)

**PART 2**: Generate candidates at ≥0.35 threshold (15 min)
- Embeddings for all mechanisms
- Top 50 candidates for manual review

**PART 3**: Full manual review (1.5 hours)
- Review all 50 candidates
- Rate and document each
- Select 15-20 verified matches

**Success Criteria**:
- [ ] Candidate pool generated (50-150 pairs depending on option)
- [ ] Relaxed threshold used (≥0.35-0.40)
- [ ] Initial filtering complete
- [ ] Ready for Session 38 manual curation

**Time Budget**: 2-2.5 hours

**Building on Session 36**:
Session 36 proved embeddings find genuine matches (tragedy of commons!) but need relaxed thresholds (0.35-0.45 vs 0.65) and manual verification. Session 37 generates large candidate pool for curation.

**KEY INSIGHT FROM SESSION 36**:
- Domain diversity paradox: Better matches = lower scores
- Best match was at 0.453 similarity (tragedy of commons)
- Need threshold ≥0.35 to capture excellent matches

**Files to Create**:
1. `examples/session37_extended_papers.json` - Additional selected papers
2. `examples/session37_all_mechanisms.json` - All mechanisms (Session 36 + new)
3. `examples/session37_candidates.json` - Top 50-150 candidates for manual review
4. `SESSION37_CANDIDATE_GENERATION.md` - Brief report

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

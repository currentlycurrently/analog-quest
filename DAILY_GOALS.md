# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 68 Goals - Begin Existing Corpus Mining

**Mission**: Start extracting mechanisms from the 431 unprocessed high-value papers

### Context from Session 67 Decision
- 50K fetch abandoned - not viable with current approaches
- Pivoting to mine existing 4,690 papers
- 431 high-value papers (score ≥5) still unprocessed
- Potential for 250-300 more mechanisms
- Goal: Reach 100-150 total discoveries

### Primary Goals

1. **Select Next Batch of Papers**
   - Query PostgreSQL for papers with score = 7
   - Exclude already-extracted paper IDs
   - Select 50 papers for this session
   - Diverse domains if possible

2. **Extract Mechanisms Manually**
   - Read abstracts carefully
   - Extract domain-neutral structural patterns
   - Expect 30-40 mechanisms (60-80% hit rate)
   - Focus on causal relationships

3. **Generate New Candidates**
   - Add mechanisms to PostgreSQL
   - Generate embeddings
   - Find cross-domain matches (≥0.35 similarity)
   - Export candidates for future curation

### Deliverables

1. **Extraction Script**: `scripts/session68_extract_batch.py`
   - Select 50 papers with score = 7
   - Display for manual extraction

2. **Mechanisms File**: `examples/session68_mechanisms.json`
   - 30-40 new mechanisms
   - Domain-neutral descriptions
   - Structural patterns only

3. **Candidates File**: `examples/session68_candidates.json`
   - New cross-domain pairs
   - Similarity scores
   - Ready for curation

### Success Criteria

**Minimum**:
- Extract 25+ mechanisms
- 50% hit rate on papers
- Generate 200+ new candidates

**Target**:
- Extract 30-40 mechanisms
- 60-80% hit rate
- Generate 400+ new candidates
- Mechanisms total: 230-240

**Stretch**:
- Extract 40+ mechanisms
- Begin curation immediately
- Find 5-10 new discoveries

### Time Estimate
- Paper selection: 30 min
- Mechanism extraction: 2 hours
- Embedding & matching: 30 min
- Documentation: 30 min
- **Total**: 3-3.5 hours

### Progress Tracking
- Current mechanisms: 200
- Target mechanisms: 450-500
- Current discoveries: 46
- Target discoveries: 100-150
- Papers to process: 431 high-value

### Next Steps After Session 68

- **Session 69**: Continue extraction (next 50 papers)
- **Session 70**: Continue extraction (next 50 papers)
- **Session 71**: Curate accumulated candidates
- **Session 72**: Continue extraction/curation
- **Session 73-74**: Update frontend with discoveries
- **Session 75-80**: Strategic expansion or wrap-up

---

## Previous Sessions Reference

### Session 67 (2026-02-15) - **COMPLETED** 🔄
- Tested alternative strategies
- Simple filtering: quality good, volume bad
- Made pivot decision: mine existing corpus
- Abandoned 50K fetch goal

### Session 66 (2026-02-15) - **COMPLETED** ❌
- Refined search terms FAILED
- Quality dropped to 33.8%
- Lesson: Keep it simple

### Session 65 (2026-02-15) - **COMPLETED** ⚠️
- 2,358 papers from OpenAlex
- 51.5% high-value rate
- Provided baseline for decisions

---

## Three-Phase Pivot Plan (Sessions 68-80)

### Phase 1: Complete Mining (68-72)
- Extract from 431 high-value papers
- Target 250-300 new mechanisms
- Generate 2,000+ candidates
- Curate to 100-150 discoveries

### Phase 2: Frontend Update (73-74)
- Deploy all discoveries
- Improve visualizations
- Add methodology page
- Polish UI/UX

### Phase 3: Strategic Next Steps (75-80)
- Evaluate success
- Consider targeted expansion
- Or declare victory at 100-150
- Document learnings

---

## Key Insights from Session 67

1. **Quality-volume trade-off is real** - can't have both
2. **Existing corpus is rich** - 431 papers await
3. **Pragmatism wins** - 100 real > 200 hypothetical
4. **Mining > Fetching** - proven 60-100% hit rates
5. **Focus brings results** - depth over breadth

---

## Important Files for Session 68

**Reference**:
1. `database/papers.db` - Has paper scores
2. PostgreSQL database - Current papers/mechanisms
3. `examples/session55_all_mechanisms.json` - Current 200

**Create**:
- Extraction script for batch selection
- New mechanisms file
- Candidate generation script

---

## Notes for Agent

- Focus on papers with score = 7 (good balance)
- Don't re-extract from papers already done
- Keep mechanism descriptions structural
- This is the path to 100 discoveries
- Quality over quantity in extraction

The pivot to existing corpus is the right call. Let's execute well.
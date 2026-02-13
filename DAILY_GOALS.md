# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 53 Goals (2026-02-13)

**Mission**: Extract 25-30 mechanisms from high-value corpus (134 → 160+ total)

### Primary Goal
Extract domain-neutral mechanisms from remaining high-value papers:
- Select 30-40 papers from 485 remaining high-value papers (score ≥5/10)
- Prioritize papers scored 7-10/10 for highest hit rate
- Manual LLM-guided extraction (domain-neutral structural descriptions)
- Goal: Extract 25-30 new mechanisms → 160+ total
- Generate embeddings and match → 700-900 cross-domain candidates

### Why This Matters
**Building toward 200 mechanism milestone**:
- Current: 134 mechanisms extracted
- Target: 160+ mechanisms (80% toward 200)
- Remaining corpus: 485 high-value papers (≥5/10) still untapped
- Proven strategy: Session 51 extracted 30 mechanisms from 41 papers (73% hit rate)

**Current discoveries**: 65 (130% of 50+ milestone, 87% toward 75+)
- Session 38: 30 discoveries (10 excellent + 20 good)
- Session 47: 11 discoveries (3 excellent + 8 good)
- Session 49: 12 discoveries (5 excellent + 7 good)
- Session 52: 12 discoveries (2 excellent + 10 good)
- **Next milestone**: 75+ discoveries (need 10 more)

### Strategy
**Proven workflow from Session 51**:
1. Query database for high-value papers (score ≥7/10) not yet extracted
2. Fetch abstracts for selected papers
3. Manual LLM-guided extraction (domain-neutral mechanisms)
4. Combine with existing 134 mechanisms
5. Generate embeddings (384-dim sentence-transformers)
6. Match cross-domain pairs (threshold ≥0.35)
7. Save candidates for future curation

**Expected hit rate**: 70-80% based on pre-scored papers
- Session 46: 100% (5/5 on papers ≥5/10)
- Session 47: 100% (31/31 on papers ≥5/10)
- Session 48: ~100% (50/50 on papers ≥7/10)
- Session 51: 73% (30/41, lower due to duplicates in batch)

### Deliverables
1. Select 30-40 high-value papers (≥7/10, not yet extracted)
2. Extract 25-30 domain-neutral mechanisms
3. Generate embeddings for all 160+ mechanisms
4. Match cross-domain candidates (threshold ≥0.35)
5. Create session53_extracted_mechanisms.json
6. Create session53_candidates.json
7. Update PROGRESS.md and METRICS.md

### Time Estimate
- Paper selection: 15-20 min (query database, filter duplicates)
- Mechanism extraction: 2-2.5 hours (~15 mechanisms/hour)
- Embedding generation: 15-20 min
- Candidate matching: 10-15 min
- Documentation: 15-20 min
- **Total**: 3-4 hours

### Success Criteria
**Minimum**:
- Select 30 papers (≥7/10, not extracted)
- Extract 20+ mechanisms
- Total: 134 → 154+ mechanisms
- Generate 600+ cross-domain candidates

**Target**:
- Select 35-40 papers (≥7/10)
- Extract 25-30 mechanisms (70-80% hit rate)
- Total: 134 → 159-164 mechanisms
- Generate 700-900 cross-domain candidates
- **Reach 160+ mechanism milestone** ✓

**Stretch**:
- Extract 35+ mechanisms
- Total: 134 → 169+ mechanisms
- Generate 900-1100 candidates
- Document extraction patterns/themes

---

## Context from Session 52

Session 52 curated Session 51 candidates:
- Reviewed 40 candidates from 556 pairs
- Found 12 discoveries (2 excellent + 10 good)
- Precision: 30.8% (12/39 valid)
- Total discoveries: 53 → 65 ✓

**Current state**:
- 134 mechanisms extracted
- 65 verified discoveries (130% of 50+, 87% toward 75+)
- 544 Session 51 candidates remaining (ranks 41-556, uncurated)
- 461 Session 48 candidates remaining (ranks 31-491, uncurated)
- **485 high-value papers (≥5/10) still available for extraction** ← Focus here!

**Session 52 recommendation**: Continue extraction (Option A) to build mechanism base before more curation

---

## Workflow for Session 53

### Step 1: Select High-Value Papers
```bash
python scripts/select_papers_for_extraction.py --min-score 7 --max-papers 40 --exclude-extracted
```
- Query database/papers.db for papers scored ≥7/10
- Filter out papers already extracted
- Prioritize highest scores (10 → 9 → 8 → 7)
- Output: session53_selected_papers.json

### Step 2: Fetch Paper Abstracts
```bash
python scripts/fetch_abstracts_for_extraction.py --input session53_selected_papers.json
```
- Retrieve full abstracts from database
- Output: session53_extraction_batch.json

### Step 3: Extract Mechanisms (Manual)
- Review each abstract
- Extract domain-neutral structural mechanisms
- Write in causal, generalizable language
- Save to: session53_extracted_mechanisms.json

### Step 4: Generate Embeddings
```bash
python scripts/generate_embeddings.py --mechanisms session53_extracted_mechanisms.json
```
- Combine with existing 134 mechanisms
- Generate 384-dim embeddings for all
- Output: session53_all_mechanisms.json, session53_embeddings.npy

### Step 5: Match Candidates
```bash
python scripts/match_candidates.py --threshold 0.35 --cross-domain
```
- Match all 160+ mechanisms
- Filter to cross-domain only
- Sort by similarity
- Output: session53_candidates.json

### Step 6: Document Results
- Update PROGRESS.md with Session 53 entry
- Update METRICS.md with new counts
- Commit all files

---

## Read First

1. **CLAUDE.md** - Core mission and principles
2. **PROGRESS.md** - Session 52 context (especially "Next Session Options")
3. **METRICS.md** - Current stats (134 mechanisms, 65 discoveries)
4. **DATA_QUALITY_STANDARDS.md** - Paper selection and quality criteria

---

## Key Files for Session 53

**Input files**:
- `database/papers.db` - 2,194 papers with scores (631 high-value ≥5/10)
- `examples/session51_all_mechanisms.json` - Existing 134 mechanisms

**Scripts to use**:
- `scripts/select_papers_for_extraction.py` - Query high-value papers
- `scripts/fetch_abstracts_for_extraction.py` - Retrieve abstracts
- `scripts/generate_embeddings.py` - Create embeddings
- `scripts/match_candidates.py` - Find cross-domain pairs

**Output files** (you create):
- `examples/session53_selected_papers.json` - 30-40 papers for extraction
- `examples/session53_extraction_batch.json` - Papers with abstracts
- `examples/session53_extracted_mechanisms.json` - 25-30 new mechanisms
- `examples/session53_all_mechanisms.json` - Combined 160+ mechanisms
- `examples/session53_embeddings.npy` - 160+ × 384 embeddings
- `examples/session53_candidates.json` - 700-900 cross-domain candidates
- Updated PROGRESS.md and METRICS.md

---

## Alternative Options (Lower Priority)

**Option B: Curate Session 51 candidates** (ranks 41-80)
- Review next 40 from Session 51's 556 candidates
- Expected precision: 25-30%
- Find 8-12 more discoveries → 73-77 total
- Time: 2-3 hours
- **Defer to Session 54**

**Option C: Curate Session 48 candidates** (ranks 31-80)
- Review next 40-50 from Session 48's 491 candidates
- Expected precision: 25-30%
- Find 8-12 more discoveries → 73-77 total
- Time: 2-3 hours
- **Defer to Session 54**

**Option D: Reach 75+ milestone** (curation focus)
- Curate 30-40 candidates from Session 48 or 51
- Goal: 65 → 75+ discoveries
- Time: 2-3 hours
- **Defer to Session 54 after extraction**

---

## Success Path

**Session 53**: Extract 25-30 mechanisms → 160+ total ✓
**Session 54**: Curate candidates → 75+ discoveries ✓
**Session 55**: Continue extraction → 200 mechanisms ✓
**Session 56**: Update frontend with 75+ discoveries
**Session 57**: Reach 100+ discoveries milestone

---

**You're building the mechanism library that powers cross-domain discovery.**
**Focus on domain-neutral, structural descriptions that generalize across fields.**
**Quality over quantity - better to find 25 excellent mechanisms than 40 mediocre ones.**

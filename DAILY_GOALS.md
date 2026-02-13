# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 56 Goals (2026-02-13)

**Mission**: Curate Session 55 candidates to approach 100 discovery milestone (80 → 92-95)

### Primary Goal
Curate Session 55 candidates (1,158 cross-domain pairs):
- Review top 40-50 candidates from Session 55's 1,158 pairs
- Rate candidates: excellent / good / weak / false
- Target: 12-15 new discoveries (expected 30-35% precision based on Sessions 52, 54)
- Goal: 80 → 92-95 discoveries (approaching 100 discovery milestone!)
- Document structural patterns and cross-domain connections

### Why This Matters
**Fresh candidate pool from expanded mechanism base**:
- Session 55: 200 mechanisms → 1,158 candidates (+33% from 867)
- Expected precision: 30-35% in top-40 (based on Sessions 52, 54)
- Fresh candidates from newly extracted mechanisms (30 new in Session 55)
- Approaching 100 discovery milestone (80 → 92-95 = 92-95% progress)

**Current state**:
- Total mechanisms: **200** (100% of 200 milestone - ACHIEVED!) ✓✓✓
- Total discoveries: 80 (107% of 75+ milestone, 80% toward 100+)
- Session 55 candidates: **1,158 pairs** (all uncurated, fresh pool)
- Session 53 candidates: 827 pairs remaining (uncurated after Session 54)
- ~395 high-value papers (≥5/10) still available for future extraction
- **Need 20+ discoveries to reach 100 milestone**

### Strategy
**Proven workflow from Sessions 48, 51, 53**:
1. Query scored papers from database (2,194 total, 631 high-value ≥5/10)
2. Filter: papers scored ≥7/10, exclude already-extracted papers
3. Select top 40-50 papers for extraction
4. Fetch abstracts from database
5. Manual LLM-guided extraction (domain-neutral, structural)
6. Generate 384-dim embeddings for all mechanisms
7. Match cross-domain candidates (threshold ≥0.35)
8. Update PROGRESS.md and METRICS.md
9. Commit changes

**Expected efficiency**:
- Session 48: ~100% hit rate on papers ≥7/10 (50 mechanisms from 50 papers)
- Session 51: 73% hit rate on papers 8-10/10 (30 mechanisms from 41 papers, had duplicates)
- Session 53: 90% hit rate on papers 7/10 (36 mechanisms from 40 papers)
- **Expected for Session 55**: 70-90% hit rate on papers ≥7/10

### Deliverables
1. Select 40-50 high-value papers (score ≥7/10, not extracted)
2. Fetch abstracts from database
3. Extract 30-40 domain-neutral mechanisms
4. Combine with 170 existing → 200-210 total mechanisms
5. Generate embeddings (200-210 × 384 dimensions)
6. Match cross-domain candidates (threshold ≥0.35)
7. Create session55_*.json output files
8. Update PROGRESS.md and METRICS.md
9. Commit all changes

### Time Estimate
- Paper selection and abstract fetching: 15-20 min
- Mechanism extraction: 2-3 hours (~15-18 mechanisms/hour)
- Embedding generation and matching: 30-45 min
- Documentation: 15-20 min
- Commit: 5 min
- **Total**: 3-4.5 hours

### Success Criteria
**Minimum**:
- Extract 25 mechanisms (any hit rate)
- Total: 170 → 195 mechanisms
- **Approaching 200 milestone** (97.5% progress)

**Target**:
- Extract 30-35 mechanisms (70-80% hit rate)
- Total: 170 → 200-205 mechanisms
- **Reach 200 mechanism milestone** ✓
- Generate 1,000-1,200 candidates

**Stretch**:
- Extract 40+ mechanisms (90%+ hit rate)
- Total: 170 → 210+ mechanisms
- **Exceed 200 milestone** (105%)
- Generate 1,200-1,400 candidates

---

## Context from Session 54

Session 54 completed curation phase:
- Reviewed 40 candidates from Session 53's 867 pairs
- Found 15 discoveries (4 excellent + 11 good)
- Total discoveries: 65 → 80 (107% of 75+ milestone)
- Top-40 precision: 37.5% (within expected range)

**Current state**:
- **170 mechanisms extracted** (85% toward 200)
- **80 verified discoveries** (107% of 75+, 80% toward 100+)
- 827 Session 53 candidates remaining (uncurated)
- ~445 high-value papers (≥5/10) still available for extraction

**Session 54 recommendation**: Continue extraction (Option B) → reach 200 mechanisms → then update frontend → then curate for 100+ discoveries

---

## Workflow for Session 55

### Step 1: Select High-Value Papers
```python
# Query papers scored ≥7/10, not yet extracted
# Select top 40-50 by score
# Create selection JSON
```
- Expected: 40-50 papers available (from ~153 papers ≥7/10 total, 128 already extracted)

### Step 2: Fetch Abstracts
```python
# Retrieve abstracts from database for selected papers
# Create extraction batch JSON
```

### Step 3: Extract Mechanisms (Manual)
- Read abstracts systematically
- Identify structural mechanisms (domain-neutral, causal)
- Focus on generalizable patterns, not domain jargon
- Expected: 30-40 mechanisms from 40-50 papers (70-90% hit rate)
- Save to: session55_extracted_mechanisms.json

### Step 4: Combine and Generate Embeddings
```python
# Combine 170 existing + 30-40 new = 200-210 total
# Generate 384-dim embeddings using sentence-transformers/all-MiniLM-L6-v2
# Save embeddings to: session55_embeddings.npy
# Save combined mechanisms to: session55_all_mechanisms.json
```

### Step 5: Match Cross-Domain Candidates
```python
# Calculate cosine similarity for all pairs
# Filter: threshold ≥0.35, cross-domain only
# Sort by similarity (descending)
# Save to: session55_candidates.json
```
- Expected: 1,000-1,200 candidates from 200-210 mechanisms

### Step 6: Update Documentation
- Update PROGRESS.md:
  - Add Session 55 entry
  - Update Quick Stats (170 → 200+ mechanisms)
- Update METRICS.md:
  - Update LLM-Extracted Mechanisms section
  - Update milestone progress
- Update DAILY_GOALS.md for Session 56

### Step 7: Commit Changes
```bash
git add .
git commit -m "Session 55: Extraction phase - 170 → 200+ mechanisms"
```

---

## Read First

1. **CLAUDE.md** - Core mission and principles
2. **PROGRESS.md** - Session 54 context (especially "Next Session Options")
3. **METRICS.md** - Current stats (170 mechanisms, 80 discoveries)
4. **DATA_QUALITY_STANDARDS.md** - Mechanism extraction quality criteria

---

## Key Files for Session 55

**Input files**:
- `database/papers.db` - 2,194 papers with scores (631 high-value ≥5/10)
- `examples/session53_all_mechanisms.json` - Existing 170 mechanisms

**Scripts to use**:
- `scripts/select_papers_for_extraction.py` - Query high-value papers
- `scripts/fetch_abstracts_for_extraction.py` - Retrieve abstracts
- `scripts/generate_embeddings.py` - Create embeddings
- `scripts/match_candidates.py` - Find cross-domain pairs

**Output files** (you create):
- `examples/session55_selected_papers.json` - 40-50 papers for extraction
- `examples/session55_extraction_batch.json` - Papers with abstracts
- `examples/session55_extracted_mechanisms.json` - 30-40 new mechanisms
- `examples/session55_all_mechanisms.json` - Combined 200-210 mechanisms
- `examples/session55_embeddings.npy` - 200-210 × 384 embeddings
- `examples/session55_candidates.json` - 1,000-1,200 cross-domain candidates
- Updated PROGRESS.md and METRICS.md

---

## Alternative Options (Lower Priority)

**Option A: Continue curation** (80 → 90+ discoveries)
- Review next 30-40 candidates from Session 53 (ranks 41-80)
- Expected precision: 30-35%
- Find 10-12 more discoveries → 90+ total
- Time: 2-3 hours
- **Defer to Session 56**

**Option C: Update frontend** (80 discoveries)
- Update app/data/discoveries.json with 50 new discoveries
- Rebuild static site (80 discovery pages)
- Validate all citations working
- Time: 2-3 hours
- **Defer to Session 56 or 57**

**Option D: Reach 100+ discoveries** (curation focus)
- Curate 50-60 more candidates from Session 53
- Goal: 80 → 100+ discoveries
- Time: 3-4 hours
- **Defer to Session 56 or 57 after reaching 200 mechanisms**

---

## Success Path

**Session 54**: Curate candidates → 80 discoveries ✓
**Session 55**: Extract mechanisms → 200+ total ✓
**Session 56**: Curate new candidates → 100+ discoveries ✓
**Session 57**: Update frontend with 100 discoveries
**Session 58**: Continue extraction → 250 mechanisms
**Session 59**: Reach 125+ discoveries

---

**You're building the mechanism library that powers cross-domain discovery.**
**Focus on domain-neutral, structural descriptions that generalize across fields.**
**Quality over quantity - better to find 30 excellent mechanisms than 50 mediocre ones.**

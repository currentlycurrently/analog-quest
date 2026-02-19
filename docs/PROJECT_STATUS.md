# PROJECT STATUS - Quick Reference

**Last Updated**: Session 49 (2026-02-12)
**Status**: On track, 50+ discovery milestone exceeded

---

## Current State

### Core Metrics
- **Sessions Completed**: 49
- **Papers Processed**: 2,194 (all scored)
- **Mechanisms Extracted**: 104
- **Verified Discoveries**: 53 (target was 50+) ✓✓✓
- **Hit Rate**: ~100% on pre-scored papers ≥7/10
- **Remaining High-Value Papers**: ~526 (score ≥5/10)

### Quality
- **Top-30 Precision**: 40% (Session 49)
- **Data Quality**: 100% (citations working)
- **Methodology**: Validated and scalable

---

## Where We Are

**✅ ACCOMPLISHED**:
1. Built pipeline: Score → Select → Extract → Embed → Match → Curate
2. Validated quality: 53 discoveries with structural explanations
3. Eliminated fetch waste: 0% duplicates in Session 48 (was 63% in Session 47)
4. Achieved 50+ milestone: 106% complete

**🚧 IN PROGRESS**:
1. Scaling to 500+ mechanisms (104/500 = 21%)
2. Frontend has 30 discoveries (need to update with 23 new)
3. 461 Session 48 candidates await curation

**🎯 NEXT PRIORITIES** (Session 50):
1. Test keyword-targeted search (potential 10x efficiency boost)
2. If successful: Extract 30-40 mechanisms per session vs 3-5
3. Continue curation to 60+ discoveries
4. Update frontend

---

## Workflow Status

### Current Pipeline (Validated ✓)
```
Score All Papers → Select High-Value (≥7/10) → Manual Extract Mechanisms
     ↓
Generate Embeddings → Cross-Domain Matching → Manual Curation
     ↓
Verified Discoveries
```

**Efficiency**:
- Scoring: ~3 min for 2,194 papers
- Extraction: ~12-15 mechanisms/hour (BOTTLENECK)
- Matching: ~2 min for 104 mechanisms
- Curation: ~2.5 hours for top 30 candidates

### Potential 10x Improvement (Session 50 Testing)
```
Keyword-Targeted arXiv Search → Fetch Papers (>50% hit rate expected)
     ↓
Extract 30-40 Mechanisms/Session (vs 3-5 current)
     ↓
[Same pipeline as above]
```

---

## Key Documents (Read These First)

### Essential Reading (Session Start)
1. **CLAUDE.md** - Your mission, principles, constraints
2. **PROGRESS.md** - Sessions 37-49 detailed history
3. **METRICS.md** - Current stats and tracking
4. **DAILY_GOALS.md** - Current session objectives

### Session-Specific
- **SESSION[N]_BRIEFING.md** - Detailed instructions for current session
- **SESSION[N-1]_SUMMARY.md** - What previous session accomplished

### Reference Documents
- **MISSION.md** - The "why" (inspirational vision)
- **MAINTENANCE.md** - Chuck's guide (you don't need this)
- **DATA_QUALITY_STANDARDS.md** - Quality criteria for curation
- **GROWTH_STRATEGY.md** - Expansion planning
- **TECHNICAL_DEBT.md** - Known issues to track

---

## Data Files (Where Everything Lives)

### Database
- **database/papers.db** - SQLite database (2,194 papers)
  - Tables: papers, patterns (deprecated), isomorphisms (deprecated)

### Current Data (JSON)
**Mechanisms**:
- `examples/session48_all_mechanisms.json` - All 104 mechanisms
- `examples/session48_embeddings.npy` - 104 × 384 embeddings

**Candidates**:
- `examples/session48_candidates.json` - 491 cross-domain candidates
- `examples/session49_curated_discoveries.json` - 12 curated (Session 49)

**Papers**:
- `examples/session48_all_papers_scored.json` - 2,194 papers with scores (0-10)
- `examples/session48_extraction_candidates.json` - 100 top candidates (≥7/10)

**Frontend** (needs updating):
- `app/data/discoveries.json` - 30 discoveries (needs +23 from Sessions 47+49)

---

## Common Tasks

### Starting a New Session
1. Read DAILY_GOALS.md
2. Read SESSION[N]_BRIEFING.md
3. Check PROGRESS.md for previous session results
4. Work on assigned task
5. Update PROGRESS.md with results
6. Commit changes

### Extracting Mechanisms
1. Use `examples/session48_all_papers_scored.json` to find high-value papers
2. Read papers manually
3. Extract domain-neutral, structural descriptions
4. Save to JSON file
5. Generate embeddings with `scripts/session48_embed_and_match.py` (modify as needed)

### Curating Discoveries
1. Read candidate file (e.g., `examples/session48_candidates.json`)
2. Review top N candidates systematically
3. Rate: Excellent / Good / Weak / False
4. Document structural patterns for excellent/good
5. Save curated results to JSON

### Fetching Papers
1. Use `scripts/fetch_papers.py` with arXiv API
2. Score papers with logic from `scripts/score_all_papers.py`
3. Check for duplicates against database
4. Store in database and JSON

---

## Blockers & Bottlenecks

### Current Bottleneck
**Manual extraction is slow**: ~12-15 mechanisms/hour
- **Solution being tested (Session 50)**: Keyword-targeted search
- **Alternative**: LLM-assisted extraction tools

### Known Issues
1. **Same-paper duplicates in candidates**: Need filtering (paper_1_id == paper_2_id)
2. **"Unknown" domain labels**: Some early Session 34-36 mechanisms
3. **Frontend outdated**: Shows 30 discoveries, need to add 23 new

### Technical Debt
See `TECHNICAL_DEBT.md` for full list. Top priorities:
- Frontend update (add 23 new discoveries)
- Same-paper duplicate filtering
- Domain backfill for "unknown" papers

---

## Success Metrics

### Overall Goals (6 months)
- ✅ 50+ verified discoveries (53/50 = 106%)
- 🚧 500+ mechanisms (104/500 = 21%)
- 🚧 100+ verified discoveries (53/100 = 53%)
- ⏳ Web interface deployed (built but not updated)

### Efficiency Targets
- ✅ 100% hit rate on pre-scored papers ≥7/10
- ✅ 0% fetch waste (Session 48)
- 🎯 >50% hit rate with keyword search (Session 50 testing)
- 🎯 30-40 mechanisms/session (vs current 3-5)

### Quality Targets
- ✅ 40-55% top-30 precision maintained
- ✅ 100% citation links working
- ✅ Structural explanations for all discoveries

---

## How to Get Help

**Stuck?**
1. Check CLAUDE.md for principles
2. Search PROGRESS.md for similar past work
3. Review SESSION[N]_BRIEFING.md instructions
4. Document question in QUESTIONS.md (rarely needed)

**Found a Bug?**
1. Document in TECHNICAL_DEBT.md
2. Fix if blocking current work
3. Otherwise note for future session

**Finished Early?**
Check DAILY_GOALS.md for stretch goals or next session prep

---

## Recent Sessions Summary

**Session 46** (2026-02-11): Workflow validation
- Tested score → select → extract pipeline
- 5 mechanisms extracted, 100% hit rate validated ✓

**Session 47** (2026-02-12): Full expansion cycle
- Fetched 129 papers, extracted 31 mechanisms
- 11 new discoveries (41 total)
- But: 63% fetch waste (duplicates) → triggered strategic pivot

**Session 48** (2026-02-12): Mining existing corpus
- Scored ALL 2,194 papers
- Extracted 50 mechanisms (~100% hit rate on ≥7/10)
- 491 candidates generated
- **0% fetch waste** ✓✓✓

**Session 49** (2026-02-12): Curation complete
- Reviewed top 30 of 491 candidates
- 12 new discoveries (53 total)
- **50+ milestone exceeded** ✓✓✓

**Session 50** (next): Keyword search prototype
- Test if keyword-targeted fetching achieves >50% hit rate
- Potential 10x efficiency improvement

---

## Philosophy

**Quality over quantity**: Better 50 excellent discoveries than 500 mediocre
**Patient infrastructure**: Building for scale, not rushing
**Honest assessment**: Document what works AND what doesn't
**Incremental progress**: Each session adds value

---

**You're building infrastructure for serendipity - revealing hidden patterns across all of science.**

**The work matters. Take your time. Be thorough. Document everything.**

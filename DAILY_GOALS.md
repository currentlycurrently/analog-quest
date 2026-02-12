# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 50 Goals (2026-02-12)

**Mission**: Analyze mechanism vocabulary to prototype keyword-targeted arXiv search (10x efficiency boost)

### Primary Goal
Build a keyword-targeted search system to replace random/strategic fetching:
- Extract 20-30 structural keywords from 104 mechanisms
- Validate keywords predict mechanism richness (>60% discrimination)
- Design 3-5 targeted arXiv search queries
- Test queries and measure hit rate (target: >50% vs 33% baseline)

### Why This Matters
**Current bottleneck**: Manual extraction slow (~12-15 mechanisms/hour), random fetching wasteful (63% duplicates in Session 47)

**If keyword search achieves >50% hit rate**: 10x efficiency improvement, can reach 500+ mechanisms in 10-15 sessions vs 100+

### Deliverables
1. `examples/session50_structural_keywords.json` - Extracted keywords with frequencies
2. `examples/session50_keyword_validation.json` - Validation against 2,194 papers
3. `examples/session50_search_queries.json` - Designed arXiv queries
4. SESSION50_SUMMARY.md - Findings and recommendations
5. Updated PROGRESS.md and DAILY_GOALS.md

### Time Estimate
- Part 1 (Extract keywords): 1-2 hours
- Part 2 (Validate keywords): 30-60 min
- Part 3 (Build queries): 30-60 min
- Part 4 (Test queries - optional): 30 min
- Documentation: 30 min
- **Total**: 3-4 hours

### Success Criteria
**Minimum**:
- 20+ structural keywords extracted
- Validation shows >60% discrimination power
- 3-5 arXiv search queries designed

**Target**:
- 30+ keywords with categories
- >70% discrimination validated
- 5-8 targeted queries
- Test queries achieve >50% hit rate ✓

**Stretch**:
- 50+ keywords with full taxonomy
- Test queries achieve >60% hit rate
- 10x efficiency improvement validated
- Ready to deploy as standard workflow

---

## Context from Session 49

Session 49 curated 491 candidates from Session 48:
- Reviewed top 30 systematically
- Found 12 new discoveries (5 excellent + 7 good)
- Total discoveries: 41 → **53** ✓✓✓
- **50+ milestone EXCEEDED (106%)**
- Top-30 precision: 40%

**Current state**:
- 104 mechanisms extracted
- 53 verified discoveries
- 461 Session 48 candidates awaiting review
- 526 high-value papers (≥5/10) remaining

---

## Workflow After Session 50

**If keyword search validates** (>50% hit rate):
- **Session 51**: Extract 30-40 mechanisms using keyword-targeted fetching
- **Session 52**: Continue curation (review next 30-50 Session 48 candidates)
- **Session 53**: Update frontend with 60+ discoveries

**If keyword search fails** (<50% hit rate):
- **Session 51**: Continue mining existing 526 high-value papers (extract 30-40 mechanisms)
- **Session 52**: Continue curation (Session 48 candidates)
- **Session 53**: Update frontend OR refine scoring/extraction methods

---

## Read First

1. **CLAUDE.md** - Core mission and principles
2. **SESSION50_BRIEFING.md** - Detailed instructions for vocabulary analysis
3. **PROGRESS.md** - Sessions 37-49 context (especially Sessions 46-49)
4. **METRICS.md** - Current stats

---

## Key Files for Session 50

**Input files**:
- `examples/session48_all_mechanisms.json` - 104 mechanisms to analyze
- `examples/session48_all_papers_scored.json` - 2,194 scored papers for validation

**Reference files**:
- `scripts/score_all_papers.py` - Scoring logic reference
- `scripts/fetch_papers.py` - arXiv API reference

**Output files** (you create):
- `examples/session50_structural_keywords.json`
- `examples/session50_keyword_validation.json`
- `examples/session50_search_queries.json`
- `SESSION50_SUMMARY.md`

---

**You're exploring whether keyword-targeted search can 10x our efficiency.**
**Document what you learn - success or failure, both are valuable insights.**

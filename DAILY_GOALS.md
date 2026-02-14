# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 64 Goals - OpenAlex Quality Test with Filtered Queries

**Mission**: Test mechanism extraction quality on OpenAlex papers with abstracts, make go/no-go decision

### Context from Session 63
- OpenAlex tested: 2,626 papers/minute speed (excellent) ✅
- Abstract coverage: 65.3% (below 80% target) ⚠️
- Topic coverage: 100% (all papers classified) ✅
- Recommendation: Use with adjusted expectations
- Next step: Test quality with has_abstract filter

### Primary Goals

1. **Fetch 500 OpenAlex Papers with Abstracts**
   - Use `has_abstract=True` filter
   - Target mechanism-rich topics (network dynamics, phase transitions, etc.)
   - Mix of domains (CS, Physics, Biology)
   - Store in PostgreSQL

2. **Score Papers for Mechanism Richness**
   - Apply existing scoring algorithm from Session 48
   - Compare score distribution with arXiv corpus
   - Identify high-value papers (score ≥5/10)

3. **Extract Mechanisms from Top Papers**
   - Select top 50-100 papers by score
   - Manual LLM extraction (domain-neutral)
   - Target: 30-50 mechanisms
   - Measure hit rate

4. **Quality Comparison**
   - Compare extraction hit rate with arXiv corpus
   - Assess mechanism quality (structural, cross-domain applicable)
   - Calculate cost-benefit (speed vs quality tradeoff)
   - Make go/no-go decision for full-scale ingestion

### Deliverables

1. **Filtered Query Script**: `scripts/session64_openalex_filtered.py`
   - Fetch papers with has_abstract=True
   - Import to PostgreSQL
   - Score for mechanism richness

2. **Quality Assessment**: `examples/session64_quality_assessment.json`
   - Score distribution comparison
   - Extraction hit rate
   - Mechanism quality samples
   - Go/no-go recommendation

3. **Documentation Update**
   - Update PROGRESS.md with Session 64 results
   - Document decision on OpenAlex usage
   - Plan next steps based on outcome

### Success Criteria

**Minimum**:
- Fetch 500 papers with abstracts
- Score all papers for mechanism richness
- Extract 20+ mechanisms

**Target**:
- 60%+ extraction hit rate on high-value papers
- 30-50 mechanisms extracted
- Quality comparable to arXiv corpus
- Clear go/no-go decision

**Stretch**:
- Test bulk ingestion of 5,000 papers
- Automate scoring pipeline
- Project full-scale metrics

### Time Estimate
- Fetch and import: 30 min
- Scoring: 30 min
- Mechanism extraction: 1.5 hours
- Quality assessment: 30 min
- Documentation: 30 min
- **Total**: 3 hours

### Next Steps After Session 64

Based on quality test results:
- **If quality good**: Session 65 - Implement bulk ingestion (50K papers)
- **If quality poor**: Session 65 - Test Semantic Scholar or arXiv bulk S3

---

## Previous Sessions Reference

### Session 63 (2026-02-14) - **COMPLETED** ⚠️
- Tested OpenAlex: 2,626 papers/minute (excellent speed)
- Abstract coverage: 65.3% (below 80% target)
- Topic coverage: 100% (all papers classified)
- Verdict: Partially feasible with adjustments

### Session 62 (2026-02-14) - **COMPLETED** ✓
- Migrated data from SQLite to PostgreSQL
- 2,194 papers, 200 mechanisms with embeddings
- Validated with 1,120 cross-domain candidates
- Database ready for scale

### Session 61 (2026-02-14) - **COMPLETED** ✓
- PostgreSQL + pgvector infrastructure setup
- Created schema for papers, mechanisms, discoveries
- HNSW indexing enabled for fast similarity search

### Session 60 (2026-02-14) - **COMPLETED** ✓
- Created comprehensive SCALE_UP_PLAN.md
- Researched bulk data sources (chose OpenAlex)
- Designed 6-phase automated pipeline
- Budget: $8-22 for 3 months

---

## Key Context for Session 64

**OpenAlex Test Results** (Session 63):
- Speed: 2,626 papers/minute ✅
- Abstract coverage: 65.3% ⚠️
- Topic coverage: 100% ✅
- Database integration: Working ✅
- Recommendation: Use with adjusted expectations

**Current Infrastructure**:
- PostgreSQL 17.8 + pgvector 0.8.1 operational
- 2,194 papers + 200 mechanisms already loaded
- pyalex installed and tested
- Scoring algorithm from Session 48 available

**Adjusted Scale-Up Plan**:
- Target: 30K papers with abstracts (from 50K total)
- Extract 3K-5K mechanisms (adjusted from 5K-8K)
- Use topic classification for filtering
- Supplement with arXiv for high-value gaps

**Decision Point**:
- If OpenAlex quality good → proceed with bulk ingestion
- If quality poor → test alternative sources (Semantic Scholar, arXiv S3)

---

## Important Files for Session 64

**Read First**:
1. **CLAUDE.md** - Core mission and workflow
2. **SESSION63_OPENALEX_TEST_REPORT.md** - OpenAlex test results and recommendations
3. **PROGRESS.md** - Session 63 summary

**Reference**:
- `scripts/session63_openalex_test.py` - OpenAlex connection code
- `scripts/session48_score_papers.py` - Scoring algorithm (if exists)
- `database/schema.sql` - PostgreSQL schema
- `examples/session63_openalex_results.json` - Test results from Session 63

**Create**:
- `scripts/session64_openalex_filtered.py` - Filtered query script
- `examples/session64_quality_assessment.json` - Quality test results

---

## Notes for Agent

- PostgreSQL must be running: `brew services start postgresql@17`
- pyalex already installed: `import pyalex; from pyalex import Works`
- Use `has_abstract=True` filter to ensure abstracts are available
- OpenAlex abstract is in `abstract_inverted_index` field (needs reconstruction)
- Scoring algorithm: Count structural keywords, penalize review/survey papers
- Focus on extraction quality, not just speed

This session determines if OpenAlex paper quality justifies the speed advantage. The goal is a clear go/no-go decision for bulk ingestion.
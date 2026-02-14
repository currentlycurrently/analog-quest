# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 65 Goals - OpenAlex Scale Test with 5,000 Papers

**Mission**: Test OpenAlex at larger scale (5,000 papers) to validate quality consistency before 50K ingestion

### Context from Session 64
- OpenAlex quality test: **GO Decision** ✅
- Average score: 5.65/10 (70% better than arXiv)
- High-value papers: 76.4% (vs 28.8% for arXiv)
- Extraction hit rate: 80% on top papers
- Decision: Proceed with OpenAlex for scale-up

### Primary Goals

1. **Develop Comprehensive Search Terms**
   - Create 100+ mechanism-relevant search terms
   - Mix domains: physics, biology, CS, economics, social systems
   - Focus on structural keywords: dynamics, feedback, emergence, coupling, etc.
   - Balance breadth and depth

2. **Implement Bulk Fetch Script**
   - Fetch 5,000 papers using diverse search terms
   - Use `has_abstract=True` filter
   - Add checkpointing for recovery
   - Track fetch statistics per search term

3. **Import and Score at Scale**
   - Import 5,000 papers to PostgreSQL
   - Score all papers for mechanism richness
   - Analyze score distribution
   - Compare with Session 64 results

4. **Validate Quality Consistency**
   - Check if quality holds at 35× scale
   - Identify any domain biases
   - Assess topic distribution
   - Make final decision on 50K fetch strategy

### Deliverables

1. **Search Terms List**: `examples/session65_search_terms.json`
   - 100+ mechanism-relevant terms
   - Categorized by mechanism type
   - Balanced across domains

2. **Bulk Fetch Script**: `scripts/session65_openalex_bulk_fetch.py`
   - Checkpoint support
   - Progress tracking
   - Error handling
   - Statistics collection

3. **Scale Test Report**: `SESSION65_SCALE_TEST_REPORT.md`
   - Score distribution analysis
   - Quality consistency assessment
   - Domain coverage statistics
   - Recommendations for 50K fetch

### Success Criteria

**Minimum**:
- Fetch 3,000+ papers successfully
- Import to PostgreSQL
- Score all papers
- Basic quality assessment

**Target**:
- 5,000 papers fetched
- Average score ≥5.0/10
- High-value papers ≥70%
- Quality consistent with Session 64

**Stretch**:
- 7,500 papers fetched
- Extract mechanisms from top 100
- Generate embeddings
- Project 50K metrics

### Time Estimate
- Search terms development: 30 min
- Bulk fetch implementation: 45 min
- Fetching 5,000 papers: 30 min
- Import and scoring: 30 min
- Analysis and reporting: 45 min
- **Total**: 3 hours

### Next Steps After Session 65

Based on scale test results:
- **If quality consistent**: Session 66 - Begin 50K paper fetch
- **If quality drops**: Session 66 - Refine search strategy
- **If technical issues**: Session 66 - Optimize infrastructure

---

## Previous Sessions Reference

### Session 64 (2026-02-14) - **COMPLETED** ✅
- Tested OpenAlex quality with has_abstract filter
- Average score: 5.65/10 (70% better than arXiv)
- High-value papers: 76.4%
- Extracted 20 mechanisms (80% hit rate)
- **GO Decision**: Proceed with OpenAlex

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

## Key Context for Session 65

**OpenAlex Proven Quality** (Session 64):
- Speed: 2,626 papers/minute ✅
- Quality: 5.65/10 average (70% better than arXiv) ✅
- High-value density: 76.4% ✅
- Abstract coverage: 100% with filter ✅
- Free tier: 100K credits/day ✅

**Current Infrastructure**:
- PostgreSQL 17.8 + pgvector 0.8.1 operational
- 2,332 papers (2,194 arXiv + 138 OpenAlex)
- 200 mechanisms with embeddings
- pyalex installed and working
- Scoring algorithm validated

**Scale-Up Plan**:
- Target: 50K papers total
- Expected: 38K high-value papers (≥5/10)
- Extract from top 10K → 5K-8K mechanisms
- Generate 1-2M candidate pairs
- Curate top 1,000 → 200+ discoveries

**Key Learning from Session 64**:
- Targeted search with mechanism keywords works
- `has_abstract=True` filter essential
- Topic metadata valuable for filtering
- Quality exceeds random arXiv fetching

---

## Important Files for Session 65

**Read First**:
1. **CLAUDE.md** - Core mission and workflow
2. **SESSION64_OPENALEX_QUALITY_REPORT.md** - Quality test results and GO decision
3. **PROGRESS.md** - Session 64 summary
4. **SCALE_UP_PLAN.md** - Overall scale-up strategy

**Reference**:
- `scripts/session64_openalex_filtered.py` - Working OpenAlex fetch code
- `examples/session64_quality_assessment.json` - Quality benchmarks
- `database/schema.sql` - PostgreSQL schema

**Create**:
- `examples/session65_search_terms.json` - 100+ search terms
- `scripts/session65_openalex_bulk_fetch.py` - Bulk fetch with checkpointing
- `SESSION65_SCALE_TEST_REPORT.md` - Scale test results

---

## Notes for Agent

- PostgreSQL must be running: `brew services start postgresql@17`
- pyalex already installed and configured
- Use `has_abstract=True` filter for all queries
- OpenAlex abstract is in `abstract_inverted_index` field (needs reconstruction)
- Aim for 50-100 papers per search term
- Track statistics per search term for optimization
- Database column is `mechanism_score` not `score`

This session validates that OpenAlex quality remains consistent at scale. If successful, we proceed to 50K paper fetch in Session 66.
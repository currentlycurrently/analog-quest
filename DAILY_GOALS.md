# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 63 Goals - OpenAlex CLI Testing

**Mission**: Test OpenAlex for bulk data ingestion to validate feasibility for 50K paper fetch

### Context from Session 62
- PostgreSQL + pgvector infrastructure complete ✓
- Database ready for scale (50K papers, 5K-8K mechanisms)
- Migration from SQLite successful (2,194 papers, 200 mechanisms)
- Next step: Test bulk data source for scale-up

### Primary Goals

1. **Install and Configure OpenAlex**
   - Install OpenAlex Python client: `pip install pyalex`
   - Configure API access (no key needed for basic use)
   - Test basic connection and queries

2. **Test Data Quality**
   - Fetch 100 papers with mechanism-relevant keywords
   - Check data completeness (title, abstract, metadata)
   - Verify domain classification accuracy
   - Assess abstract quality for mechanism extraction

3. **Test Ingestion Speed**
   - Measure fetch rate for 100 papers
   - Test with 1,000 papers if initial test successful
   - Calculate time estimate for 50K papers
   - Check for rate limiting or throttling

4. **Database Integration Test**
   - Import test batch into PostgreSQL
   - Verify schema compatibility
   - Test deduplication (check for existing papers)
   - Measure import performance

### Deliverables

1. **Test Script**: `scripts/session63_openalex_test.py`
   - Fetch papers by keyword/domain
   - Import to PostgreSQL
   - Track performance metrics

2. **Test Results**: `examples/session63_openalex_results.json`
   - Sample papers fetched
   - Quality assessment
   - Performance metrics
   - Feasibility report

3. **Documentation Update**
   - Update PROGRESS.md with Session 63 results
   - Document any issues or limitations
   - Provide recommendation for full-scale ingestion

### Success Criteria

**Minimum**:
- Successfully fetch 100 papers from OpenAlex
- Import to PostgreSQL without errors
- Estimate time for 50K paper fetch

**Target**:
- Fetch 1,000 papers successfully
- Achieve >80% data quality (complete abstracts)
- Fetch rate >100 papers/minute
- Time estimate for 50K papers: <1 hour

**Stretch**:
- Test advanced filtering (by domain, date, citations)
- Implement incremental update strategy
- Test parallel fetching for speed optimization

### Time Estimate
- OpenAlex setup: 30 min
- Test script development: 1 hour
- Testing and validation: 1 hour
- Documentation: 30 min
- **Total**: 2-3 hours

### Next Steps After Session 63

Based on OpenAlex test results:
- **If successful**: Session 64 - Implement full bulk ingestion pipeline
- **If issues**: Session 64 - Test alternative source (Semantic Scholar or arXiv bulk)

---

## Previous Sessions Reference

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

## Key Context for Session 63

**Current Infrastructure**:
- PostgreSQL 17.8 + pgvector 0.8.1 operational
- Schema supports 50K papers, 5K-8K mechanisms
- HNSW index for <50ms similarity search
- 2,194 papers already in database

**Scale-Up Plan** (from SCALE_UP_PLAN.md):
- Target: 50K papers → 5K-8K mechanisms → 200+ discoveries
- OpenAlex chosen as primary data source (100K credits/day FREE)
- Expected ingestion time: <1 hour for 50K papers
- LLM extraction via Claude Batch API ($5.50-$16.50 for 8K papers)

**Why OpenAlex**:
- 240M works available
- 100K credits/day FREE
- 200 parallel connections supported
- Comprehensive metadata
- No authentication required for basic use

---

## Important Files for Session 63

**Read First**:
1. **CLAUDE.md** - Core mission and workflow
2. **SCALE_UP_PLAN.md** - Detailed plan for OpenAlex integration
3. **POSTGRESQL_SETUP.md** - Database connection details

**Reference**:
- `database/schema.sql` - PostgreSQL schema
- `scripts/session62_migrate_to_postgresql.py` - Example of PostgreSQL integration

**Create**:
- `scripts/session63_openalex_test.py` - Test script
- `examples/session63_openalex_results.json` - Test results

---

## Notes for Agent

- PostgreSQL must be running: `brew services start postgresql@17`
- Add to PATH if needed: `export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"`
- Use pgvector's cosine similarity operator `<=>` for embeddings
- Check for duplicates before importing (use arxiv_id or doi)
- OpenAlex docs: https://docs.openalex.org/

You're testing the feasibility of OpenAlex for the scale-up phase. Focus on speed, data quality, and PostgreSQL integration. This session determines if we can efficiently fetch 50K papers as planned.
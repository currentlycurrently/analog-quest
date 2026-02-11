# Session 45 - Data Audit Results

**Date**: 2026-02-11
**Mission**: Audit database integrity and fix broken citation links

---

## Critical Findings

### Problem: 100% Citation Link Failure

**User Report**: "Most discoveries didn't have links on the website, and when a link was there it wasn't to the right paper"

**Audit Results**:
- **Total discoveries**: 30
- **Total paper references**: 60 (2 per discovery)
- **Unique papers**: 25
- **Papers in database**: 25/25 (100%) ✓
- **Papers with valid arXiv IDs in DB**: 25/25 (100%) ✓
- **Papers with correct arXiv IDs in discoveries.json**: **0/60 (0%)** ❌

### Root Cause

**Sessions 37-38** manually curated mechanisms and created verification data WITHOUT querying the database for paper metadata.

Result: `arxiv_id: "N/A"` for nearly all papers, even though the database contains valid IDs.

**Examples**:
```
Paper ID 77:
  - Database: arxiv_id = "2602.05112v1", domain = "econ"
  - discoveries.json: arxiv_id = "N/A", domain = "unknown"

Paper ID 525:
  - Database: arxiv_id = "2601.22613v1", domain = "q-bio"
  - discoveries.json: arxiv_id = "N/A", domain = "unknown"

Paper ID 530:
  - Database: arxiv_id = "2601.05193v1", domain = "q-bio"
  - discoveries.json: arxiv_id = "2602.00044v1" (WRONG!)
```

### Impact

- **Website**: 0% of citation links work correctly
- **User Trust**: Broken citations undermine credibility
- **Data Integrity**: discoveries.json out of sync with database
- **Scalability**: Manual curation process doesn't maintain referential integrity

---

## Secondary Issues Discovered

### 1. Domain Mismatch
- Many papers show `domain: "unknown"` in discoveries.json
- Database has correct domains (econ, q-bio, physics, cs, nlin)
- Domain badges on website likely incorrect

### 2. Title Truncation Risk
- Some titles may be truncated or manually edited
- Need to verify all titles match database exactly

### 3. No Data Validation Pipeline
- No validation script to catch these errors
- No integrity checks before deployment
- Manual curation bypassed database queries

### 4. 2,021 Papers May Be Insufficient
- Current corpus doesn't represent global research spectrum
- Need strategy for selective intake based on:
  - Mechanism richness (not just domain coverage)
  - Cross-domain potential (papers with generalizable structures)
  - Citation quality (papers with proper metadata)

---

## Fix Strategy

### Phase 1: Immediate Fix (Session 45)
1. ✓ Audit complete - root cause identified
2. Create fix script to:
   - Read discoveries.json
   - Query database for each paper_id
   - Update arxiv_id, domain, title with correct values
   - Preserve mechanism descriptions (hand-curated, valuable)
3. Validate all 60 paper references
4. Test website citation links
5. Commit fixed data

### Phase 2: Validation Infrastructure (Session 45)
1. Create `scripts/validate_discoveries.py`:
   - Check all paper_ids exist in database
   - Verify arxiv_ids match database
   - Validate domains match database
   - Check for duplicate papers
   - Ensure all links resolve to arxiv.org
2. Add to pre-commit workflow

### Phase 3: Data Quality Standards (Session 45-46)
1. Document paper intake requirements:
   - Must have valid arXiv ID
   - Must have domain classification
   - Must have abstract for mechanism extraction
   - Must pass quality threshold (not reviews, pure methods, etc.)
2. Define "mechanism richness" criteria
3. Create selective intake strategy for future expansion

### Phase 4: Expansion Planning (Session 46+)
1. Audit 2,021 papers for mechanism richness
2. Identify high-value domains for expansion
3. Plan selective intake (quality > quantity)
4. Target: 5,000-10,000 papers with 500-1,000 verified discoveries

---

## Lessons Learned

1. **Manual curation MUST maintain referential integrity**
   - Session 37-38 created valuable mechanism descriptions
   - But bypassed database queries, breaking citations
   - Fix: All curation must pull from single source of truth (database)

2. **Validation scripts are critical**
   - No validation = undetected errors
   - Fix: Validate before deployment, not after user reports

3. **Scale exposes foundation issues**
   - 30 discoveries × broken links = bad
   - 500 discoveries × broken links = catastrophic
   - Fix: Solve foundation before scaling

4. **Database is source of truth**
   - discoveries.json should be DERIVED from database
   - Never manually edit metadata
   - Fix: Generate discoveries.json from database queries

---

## Next Steps

1. **Immediate**: Fix discoveries.json with database data
2. **Today**: Create validation script
3. **Today**: Document intake standards
4. **Next Session**: Audit 2,021 papers for quality
5. **Future**: Expand selectively to 5K+ papers

---

**Status**: Foundation broken, fix in progress
**Priority**: Critical - blocks all future work
**Time to Fix**: 2-3 hours (1 hour fix + 1 hour validation + 1 hour standards)

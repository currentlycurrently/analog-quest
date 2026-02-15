# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 76 Goals - CONTINUE CURATION OR EXTRACTION 🎯

**Mission**: Continue progress toward 100 discoveries - multiple paths available!

### Context from Session 75:
- **305 mechanisms** in database
- **56 unique discoveries** (10 new found in Session 75!)
- **565 remaining candidates** from Session 74 batch (30 reviewed, 565 left)
- **44 discoveries needed** to reach 100 milestone (56% complete)
- Session 75 precision: 33% (10/30 reviewed)

### Primary Goals for Session 76

**Option 1: Continue Curation** (Recommended - we have momentum!)
   - Review candidates 31-80 from `examples/session74_candidates.json`
   - These are in 0.60-0.65 similarity range (historically good precision)
   - Expected: 15-20 new discoveries based on 33% precision
   - Would reach ~70-75 total discoveries!

**Option 2: More Extraction**
   - Create diverse search terms (materials science, chemistry, systems biology)
   - Run 3-4 Claude Code Pipeline batches
   - Extract 15-20 mechanisms → reach 320-325 total
   - Generate fresh candidates for next session

3. **Quality Standards** (from DATA_QUALITY_STANDARDS.md)
   - **Excellent**: Clear structural isomorphism, non-obvious connection, generalizable
   - **Good**: Valid structural similarity, some domain specificity okay, useful connection
   - **Weak**: Only surface similarity, mostly vocabulary overlap
   - **False**: No real structural connection, coincidental word matches

4. **Deduplication Check**
   - Check against `app/data/discovered_pairs.json` (46 existing pairs)
   - Use `scripts/check_duplicates.py` if needed
   - Don't re-curate already discovered pairs

### Alternative Option: Continue Extraction

If you prefer to continue extraction instead of curation:

1. **Run More Pipeline Batches**
   - Create new expanded search terms
   - Fetch papers with diverse mechanism-related queries
   - Extract mechanisms manually
   - Target: 320+ mechanisms (currently 305)

2. **Generate New Candidates**
   - After reaching 320+ mechanisms
   - Run candidate generation script
   - Would produce ~650-700 candidates

### Session 75 Success Criteria

**For Curation Path** (Recommended):
- Review 30-50 candidates
- Find 10-20 new discoveries
- Document each with structural explanation
- Update discovery count (46 → 56-66)
- Create `examples/session75_curated_discoveries.json`

**For Extraction Path**:
- Extract 15-20 new mechanisms
- Reach 320+ total mechanisms
- Maintain 70%+ hit rate
- Update PROGRESS.md with results

### Quick Reference

**Key Files**:
- `examples/session74_candidates.json` - 595 candidates to review
- `app/data/discovered_pairs.json` - 46 existing discoveries (avoid duplicates)
- `DATA_QUALITY_STANDARDS.md` - Rating criteria
- `scripts/check_duplicates.py` - Deduplication tool

**Database Access**:
```bash
/opt/homebrew/opt/postgresql@17/bin/psql analog_quest

# Query to see mechanism pairs for a candidate
SELECT m1.description, m1.structural_description, m2.description, m2.structural_description
FROM mechanisms m1, mechanisms m2
WHERE m1.id = [mech1_id] AND m2.id = [mech2_id];
```

### Time Estimate
- Load and prepare candidates: 15 minutes
- Review 30-50 candidates: 1.5-2 hours
- Document discoveries: 30 minutes
- Update files and commit: 30 minutes
- **Total**: 2.5-3.5 hours

### Important Notes

**Similarity Score Context**:
- 0.70-0.75: Usually excellent matches
- 0.60-0.70: Mix of excellent and good
- 0.50-0.60: Mostly good matches
- 0.40-0.50: Mix of good and weak
- 0.35-0.40: Mostly weak, some hidden gems

**Domain Pair Performance** (historical):
- physics ↔ biology: Often excellent (universal principles)
- cs ↔ physics: High precision (algorithms ↔ dynamics)
- econ ↔ biology: Good for resource/competition patterns
- Unknown domain: Check structural description carefully

### Next Steps After Session 75

- **If 60+ discoveries**: Consider updating frontend
- **If 70+ discoveries**: Major milestone approaching!
- **If still <60**: Continue alternating extraction/curation
- **Goal**: Reach 100 unique discoveries (currently 46/100)

---

## Previous Session Reference

### Session 75 (2026-02-15) - **COMPLETED** ✓✓✓
**Curation Sprint - 10 New Discoveries!**
- Reviewed 30 candidates from Session 74 batch
- Found 10 new discoveries (5 excellent, 5 good)
- Total discoveries: 56 (56% to goal!)
- Key finding: Multifractal cascades appear across physics, biology, and cognition

### Session 74 (2026-02-15) - **COMPLETED** ✓✓✓
**Pipeline Evolution - 300+ Milestone!**
- Ran batch 13 (4 mechanisms stored)
- Hit search exhaustion, created expanded search terms
- Extracted 9 mechanisms from expanded search (90% hit rate!)
- Total mechanisms: 305 (300+ milestone! 🎉)
- Generated 595 cross-domain candidates
- Ready for curation!

### Session 73 (2026-02-15) - **COMPLETED** ✓✓✓
**Pipeline Continued**
- Ran 3 batches (10, 11, 12)
- Extracted 24 mechanisms (18 unique stored)
- Total mechanisms: 292 (290+ milestone!)
- 80% average hit rate

### Session 72 (2026-02-15) - **COMPLETED** ✓✓✓
**Pipeline Fixed and Running**
- Fixed JSON format issue
- Extracted 22 mechanisms (17 unique stored)
- Total mechanisms: 274

---

## Notes for Agent

You have two good options:
1. **Curate discoveries** from the 595 candidates (recommended - we need more discoveries)
2. **Continue extraction** with more diverse search terms

The curation path is recommended because:
- We have 595 fresh candidates to review
- We're at 46/100 discoveries (need 54 more)
- Historical precision suggests 10-20 discoveries available in top 50

Remember: Quality over quantity. Better to find 10 excellent discoveries than 20 weak ones.

Good luck with Session 75! 🎯
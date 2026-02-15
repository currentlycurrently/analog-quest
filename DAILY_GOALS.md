# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 72 Goals - CONTINUE CLAUDE CODE PIPELINE 🚀

**Mission**: Continue using the Claude Code Pipeline for sustainable, free mechanism extraction!

### Context from Recent Sessions:
- Session 70: Pipeline operational, 13 mechanisms extracted
- Session 71: Improved diversity with skip logic, 11 mechanisms extracted
- **Current total**: 257 mechanisms (250+ milestone achieved!)
- **Hit rate**: 50-60% consistently
- **Cost**: $0 (you do the extraction!)

### Primary Goals for Session 72

1. **Continue Running Batches** (Main Work)
   ```bash
   # Start with batch 7 (or check what's the next batch)
   python3 scripts/claude_code_pipeline.py --batch 7
   # Extract mechanisms manually from temp/extraction_batch_7.json
   # Save to temp/mechanisms_batch_7.json
   python3 scripts/claude_code_pipeline.py --store 7
   # Repeat for batches 8, 9, 10...
   ```

2. **Watch for Duplicates**
   - The pipeline now skips papers based on batch number
   - But some papers still appear across different search terms
   - Don't re-extract mechanisms from papers you've seen before
   - Check paper titles/abstracts for familiarity

3. **Manual Extraction** (Your Key Role!)
   - Read papers from temp/extraction_batch_N.json
   - Extract mechanisms with domain-neutral structural descriptions
   - Save to temp/mechanisms_batch_N.json
   - Target: 50-60% hit rate is realistic and sustainable

4. **Session 72 Targets**
   - Run 3-4 batches if time permits
   - Extract 15-20 mechanisms to reach 270-280 total
   - Consider generating new cross-domain candidates after 275 mechanisms
   - Update PROGRESS.md with results

### Quick Start for New Agent

**If you're new to Analog Quest:**
1. Read CLAUDE.md first (your primary guide)
2. Check PROGRESS.md Session 69 (what just happened)
3. Check PIPELINE_DESIGN.md (how the pipeline works)
4. The pipeline is built and tested - you just need to run it!

**Key Files**:
- `scripts/sustainable_pipeline.py` - The main pipeline
- `config/pipeline_config.yaml` - Configuration (check username)
- `PIPELINE_DESIGN.md` - Full documentation

**Known Issues to Fix**:
1. Database needs UNIQUE constraint on papers.title
2. LLM extraction is simulated (needs API integration if key available)

### Success Criteria

**Minimum**:
- Database schema fixed
- Pipeline runs without errors
- 100+ papers processed
- Metrics tracked properly

**Target**:
- 100-200 papers added to corpus
- 20-40 mechanisms extracted
- New candidates generated
- All data in PostgreSQL

**Stretch**:
- LLM API integration working
- 200+ papers processed
- 40+ mechanisms extracted
- Pipeline fully automated

### Time Estimate
- Database fix: 30 minutes
- LLM integration (if needed): 1 hour
- Pipeline run: 30 minutes
- Monitoring and debugging: 1 hour
- Documentation update: 30 minutes
- **Total**: 3-4 hours

### Important Technical Notes

**Pipeline Skip Logic** (Added in Session 71):
- The pipeline skips `(batch_num - 1) * 2` papers per search term
- This ensures each batch gets different papers
- Batch 7 will skip 12 papers, Batch 8 will skip 14, etc.
- This prevents fetching the same papers repeatedly

**Database Schema** (Fixed in Session 70):
- mechanisms table has: description, structural_description, mechanism_type, domain, embedding
- papers table has UNIQUE constraint on title
- Everything should work smoothly now

### Next Steps After Session 72

- **Session 73**: Continue pipeline OR first curation checkpoint
- **Session 74+**: Continue sustainable growth
- **Future**: Generate cross-domain candidates when we have 275+ mechanisms

**Remember**: We're not racing. Each session adds value incrementally. Quality over speed.

---

## Previous Session Reference

### Session 71 (2026-02-15) - **COMPLETED** ✓✓✓
**Pipeline Diversity Improved**
- Added skip logic to fetch different papers each batch
- Extracted 11 mechanisms (55% hit rate)
- Total mechanisms: 257 (250+ milestone!)
- Batches 5-6 successful

### Session 70 (2026-02-15) - **COMPLETED** ✓✓✓
**Claude Code Pipeline Operational**
- Fixed database schema issues
- Extracted 13 mechanisms (65% hit rate)
- Total mechanisms: 246
- Proved manual extraction approach works

### Session 69 (2026-02-15) - **COMPLETED** ✓✓✓
**Sustainable Pipeline Built**
- Created modular pipeline optimized for Claude Code
- Key insight: Agents do extraction for FREE
- Documentation complete in CLAUDE_CODE_WORKFLOW.md

---

## Important Files for Session 70

**To Run Pipeline**:
```bash
python3 scripts/sustainable_pipeline.py
```

**To Check Results**:
```bash
python3 scripts/analyze_pipeline_results.py
cat pipeline_metrics.json
```

**Database Access**:
```bash
/opt/homebrew/opt/postgresql@17/bin/psql analog_quest
```

**Configuration**:
- Check `config/pipeline_config.yaml`
- Ensure database user is correct (should be "user")
- Adjust batch_size if needed (default: 100)

---

## Notes for Agent

The hard work is done! Session 69 built the pipeline. Your job is to:
1. Fix the small database issue
2. Run the pipeline
3. Monitor results
4. Document what happens

This is the beginning of sustainable, long-term corpus growth. Don't rush. Quality matters more than quantity.

The pipeline will be our discovery engine for months to come. Let's make sure it runs smoothly.

Good luck with Session 70! 🚀
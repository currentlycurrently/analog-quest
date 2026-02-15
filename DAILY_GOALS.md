# DAILY_GOALS.md

Current session goals and immediate priorities.

---

## Session 70 Goals - RUN CLAUDE CODE PIPELINE 🚀

**Mission**: Use the NEW Claude Code Pipeline that leverages YOU (the agent) for free extraction!

### Context: Better Approach Discovered!
- Session 69 built pipeline but wanted external LLM API
- **NEW INSIGHT**: Why pay for API when Claude Code agents can extract for FREE?
- **NEW SCRIPT**: `claude_code_pipeline.py` optimized for Claude Code agents
- You ARE the LLM - do the extraction yourself!
- Run multiple small batches per session

### Primary Goals

1. **Fix Database Schema** (Quick)
   - Add UNIQUE constraint to papers.title
   - Test ON CONFLICT clause works properly
   - Verify storage phase completes without errors

2. **Run Multiple Batches** (Main Work)
   ```bash
   # Run 3-5 batches in the session
   python3 scripts/claude_code_pipeline.py --batch 1
   # Extract mechanisms manually from temp/extraction_batch_1.json
   # Save to temp/mechanisms_batch_1.json
   python3 scripts/claude_code_pipeline.py --store 1
   # Repeat for batches 2, 3, 4...
   ```

3. **Manual Extraction** (Your Key Role!)
   - Read papers from temp/extraction_batch_N.json
   - Extract mechanisms with domain-neutral descriptions
   - Save to temp/mechanisms_batch_N.json
   - Target: 60-80% hit rate on high-value papers

4. **Achieve Sustainable Growth**
   - Process 60-100 papers across 3-5 batches
   - Extract 20-30+ mechanisms manually
   - All FREE (no API costs!)
   - Higher quality than automated extraction

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

### Next Steps After Session 70

- **Session 71**: Run pipeline with different search terms
- **Session 72**: Run pipeline, assess quality
- **Session 73**: First curation checkpoint
- **Session 74+**: Continue sustainable growth

**Remember**: We're not racing. Each session adds value incrementally. Quality over speed.

---

## Previous Session Reference

### Session 69 (2026-02-15) - **COMPLETED** ✓✓✓
**Sustainable Pipeline Built**
- Created modular 6-phase pipeline
- Tested with 90 papers from OpenAlex
- Cost: $0.002 per run
- Speed: 185 papers/minute
- Documentation complete
- Ready for production (after minor fixes)

### Session 68 (2026-02-15) - **COMPLETED** ✓✓✓
- Extracted 33 mechanisms (66% hit rate)
- Generated 1,525 new candidates
- Total mechanisms: 233 (230+ milestone!)
- Quality: 76% excellent rating

### Session 67 (2026-02-15) - **COMPLETED** 🔄
- Strategic pivot to mining existing corpus
- Abandoned 50K fetch goal
- Focus on quality over quantity

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
# Session 59 Plan - Cleanup & Tracking System

**Goal**: Quick cleanup session (~1 hour) to finish Session 58 corrections, then pivot to scale-up planning

---

## Tasks (Priority Order)

### 1. Create Discovery Tracking System (30 min)

**File: `app/data/discovered_pairs.json`**
```json
{
  "metadata": {
    "last_updated": "2026-02-14",
    "total_pairs": 46,
    "description": "Tracks all discovered paper pairs to prevent duplication"
  },
  "discovered_pairs": [
    {
      "paper_1_id": 525,
      "paper_2_id": 540,
      "discovered_in_session": 38,
      "rating": "excellent",
      "similarity": 0.7364
    },
    // ... all 46 pairs
  ]
}
```

**Script: `scripts/check_duplicates.py`**
- Load discovered_pairs.json
- Check new candidates against it
- Filter out already-discovered pairs
- Return only truly new candidates

**Update workflow:**
- Before curation: Run check_duplicates.py on candidate list
- After curation: Add new discoveries to discovered_pairs.json

### 2. Update CLAUDE.md Workflow (15 min)

Add section on deduplication protocol:

```markdown
## Discovery Tracking Protocol (NEW - Post-Session 58)

**Before each curation session:**
1. Load app/data/discovered_pairs.json
2. Filter candidate list to remove already-discovered pairs
3. Only curate NEW candidates

**After each curation session:**
1. Add newly discovered pairs to discovered_pairs.json
2. Record: paper IDs, session number, rating, similarity
3. Commit tracking file with discoveries

**Why this matters:**
Session 58 audit revealed 54% duplication because we had no tracking.
This prevents wasting time re-curating the same candidates.
```

### 3. Final Documentation Updates (15 min)

**DAILY_GOALS.md:**
- Update Session 59 goals
- Add Session 60+ placeholder: "SCALE-UP: Infrastructure for 50K+ papers"

**AUDIT_SESSION58.md:**
- Mark all action items as complete
- Add "Lessons Applied" section for Session 59

**README.md** (if needed):
- Update discovery count to 46
- Note: "Currently scaling infrastructure for 50,000+ papers"

---

## Session 59 Deliverables

- [ ] `app/data/discovered_pairs.json` created with all 46 pairs
- [ ] `scripts/check_duplicates.py` working and tested
- [ ] CLAUDE.md updated with tracking protocol
- [ ] DAILY_GOALS.md updated
- [ ] AUDIT_SESSION58.md marked complete
- [ ] All changes committed

**Time estimate**: ~1 hour

---

## After Session 59: The Pivot

**Session 60 will be different:**
- Create SCALE_UP_PLAN.md
- Research arXiv bulk API, Semantic Scholar API, OpenAlex
- Design automated extraction pipeline
- Plan database optimization
- Define success metrics for scale (not just discovery count)

**The mission changes from:**
- "Manually curate 100 discoveries from 2,000 papers" ❌

**To:**
- "Build infrastructure to process 50,000 papers and surface the 200 most groundbreaking cross-domain discoveries" ✓

**That's the real analog.quest.**

---

## Notes for Session 59 Agent

- Keep it tight - just cleanup tasks
- Don't start any new extraction/curation work
- Focus on preventing future duplication problems
- Leave project in clean state for scale-up pivot
- Session 60 is where the real strategic work begins

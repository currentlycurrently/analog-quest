# Session 87 Quick Start Checklist

**Read this first, then read SESSION_87_HANDOFF.md**

---

## Before You Start (5 minutes)

- [ ] Read this checklist
- [ ] Read SESSION_87_HANDOFF.md (10 min)
- [ ] Skim URGENT.md (understand the methodology problem)

---

## Critical Fixes (30 minutes)

### 1. Fix TypeScript Build Error (15 min)
- [ ] Open `app/page.tsx`
- [ ] Go to line 98 (the DiscoveryCard rendering)
- [ ] Add filter: `.filter(d => d.rating === 'excellent' || d.rating === 'good')`
- [ ] Test: `npm run build` (should succeed)
- [ ] Commit: "Fix TypeScript rating type error"

### 2. Review Uncommitted Changes (15 min)
- [ ] Run: `git diff`
- [ ] Review changes in: app/page.tsx, components/DiscoveriesClient.tsx, lib/api-client.ts
- [ ] Test: `npm run dev` (check http://localhost:3000)
- [ ] Decision: Keep (commit) or revert changes
- [ ] If keeping: `git add . && git commit -m "Session 87: Review and commit frontend enhancements"`
- [ ] Push: `git push`

---

## Strategic Decision (2-3 hours)

### 3. Audit Current Discoveries (1-2 hours)
- [ ] Read URGENT.md examples (real vs fake discoveries)
- [ ] Connect to database: `psql $DATABASE_URL`
- [ ] Sample 20 random discoveries: `SELECT * FROM discoveries ORDER BY RANDOM() LIMIT 20;`
- [ ] For each, ask:
  - Does it show mathematical equivalence (not just semantic similarity)?
  - Is it non-obvious to domain experts?
  - Could it be published in a journal?
- [ ] Count how many pass ALL three criteria
- [ ] Calculate percentage: (passes / 20) * 100

### 4. Make Go/No-Go Decision (30 min)
Based on audit results:

**If ≥20% pass (4+ discoveries)**:
- [ ] Decision: Continue Phase 2 with STRICTER criteria
- [ ] Update DAILY_GOALS.md: "Session 87: Continue Phase 2 - Mathematical equivalences only"
- [ ] Plan: Review next batch of candidates (311-370) with harsh filtering
- [ ] Expected: 5-10 discoveries per session (not 15-18)

**If 10-20% pass (2-3 discoveries)**:
- [ ] Decision: Hybrid approach
- [ ] Update DAILY_GOALS.md: "Session 87: Finish Phase 2 batch + Start rebuild planning"
- [ ] Plan: Complete current candidate batch + Set up SymPy

**If <10% pass (<2 discoveries)**:
- [ ] Decision: Pivot to Methodology Rebuild
- [ ] Update DAILY_GOALS.md: "Session 87: Begin Methodology Rebuild - Week 1"
- [ ] Read METHODOLOGY_REBUILD_SPEC.md Section 7 (roadmap)
- [ ] Plan: Set up SymPy, extract equations from 1 test paper

---

## Validation (Always Do)

- [ ] Run: `python3 scripts/validate_data_integrity.py` (should pass)
- [ ] Check production: `curl https://analog.quest/api/health | jq`
- [ ] Test build: `npm run build` (should succeed after fix)

---

## Documentation (Before Ending Session)

- [ ] Update PROGRESS.md with Session 87 summary
- [ ] Update DAILY_GOALS.md for Session 88
- [ ] If decisions made: Document in PROGRESS.md
- [ ] Commit: "Session 87: [summary of work]"
- [ ] Push: `git push`

---

## What NOT to Do

- ❌ Don't add discoveries before fixing build error
- ❌ Don't skip the strategic decision (see URGENT.md)
- ❌ Don't ignore uncommitted changes
- ❌ Don't continue Phase 2 without auditing quality first
- ❌ Don't commit without testing (`npm run build`)
- ❌ Don't deploy without validation (`python3 scripts/validate_data_integrity.py`)

---

## Success Criteria

**Minimum**:
- ✅ Build error fixed
- ✅ Build passing
- ✅ Changes committed
- ✅ Strategic decision documented

**Good**:
- ✅ All above
- ✅ Audit completed
- ✅ Direction chosen
- ✅ Session 88 plan created

**Excellent**:
- ✅ All above
- ✅ First work in chosen direction started
- ✅ Documentation complete

---

## Files to Read (In Order)

1. **This file** (you're reading it!)
2. **SESSION_87_HANDOFF.md** (comprehensive context)
3. **URGENT.md** (the methodology problem)
4. **REBUILD_SUMMARY.md** (rebuild approach)
5. **TECH_DEBT_LOG.md** (known issues)

## Files to Update

1. **PROGRESS.md** (session summary)
2. **DAILY_GOALS.md** (Session 88 goals)
3. **Code files** (fix TypeScript error)

## Commands Reference

```bash
# Validate data
python3 scripts/validate_data_integrity.py

# Test build
npm run build

# Run locally
npm run dev

# Check production
curl https://analog.quest/api/health | jq

# Review changes
git diff
git status

# Database access
psql $DATABASE_URL
```

---

**Time Budget**:
- Fixes: 30 min
- Audit: 1-2 hours
- Decision: 30 min
- Work: 1-2 hours
- Documentation: 30 min
**Total**: 3-5 hours

**Good luck!** The infrastructure is solid. The question is: what do we build on it?

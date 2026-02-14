# PROJECT AUDIT - Session 58
## Systematic Investigation of Discovery Counts and Duplication

Date: 2026-02-14
Status: IN PROGRESS

---

## THE PROBLEM

Attempted to merge 72 "new" discoveries from Sessions 47-57, but found:
- **56 duplicates** across sessions
- **Actual new discoveries: only 16**
- **Total unique: 46** (not 102!)

This is a critical discrepancy. Need to understand:
1. Why did multiple sessions find the same matches?
2. Are the session counts in PROGRESS.md accurate?
3. What's the ground truth?

---

## INVESTIGATION PLAN

### Phase 1: Verify Session Files ✓
- [x] Count discoveries in each session file
- [x] Check for internal duplicates within sessions
- [ ] Verify session files match PROGRESS.md claims

### Phase 2: Understand Candidate Generation
- [ ] Which mechanism pool did each session use?
- [ ] Were they curating overlapping candidate sets?
- [ ] Track candidate provenance

### Phase 3: Check Baseline Integrity
- [ ] Is Session 38 baseline (30 discoveries) internally consistent?
- [ ] Any duplicates in baseline?

### Phase 4: Database vs Frontend Reconciliation
- [ ] What's in database/papers.db?
- [ ] Does it match frontend data?
- [ ] Which is source of truth?

### Phase 5: Fix and Document
- [ ] Use deduplicated discoveries.json (46 total)
- [ ] Rebuild frontend with correct count
- [ ] Correct PROGRESS.md session entries
- [ ] Correct METRICS.md discovery counts
- [ ] Document lessons learned
- [ ] Create discovery tracking system for future sessions

---

## GROUND TRUTH

### Actual Discovery Count

**After deduplication:**
- **Session 38 baseline: 30 discoveries** (no internal duplicates ✓)
- **Sessions 47-57 added: 16 unique new discoveries**
- **Total unique discoveries: 46**

**What PROGRESS.md claimed:**
- Session 38: 30 discoveries ✓ (accurate)
- Session 47: +11 discoveries (claimed 30 → 41)
- Session 49: +12 discoveries (claimed 41 → 53)
- Session 52: +12 discoveries (claimed 53 → 65)
- Session 54: +15 discoveries (claimed 65 → 80)
- Session 56: +19 discoveries (claimed 80 → 99)
- Session 57: +2 discoveries (claimed 99 → 101)
- **Total claimed: 101 discoveries**
- **Actual unique: 46 discoveries**
- **Discrepancy: 55 duplicate discoveries counted multiple times**

### The Duplication Problem Explained

**What went wrong:**
1. Mechanism extraction sessions (48, 51, 53, 55) created CUMULATIVE pools
2. Each pool contained ALL previous mechanisms + new ones
3. Curation sessions (47, 49, 52, 54, 56, 57) independently curated from these pools
4. **No tracking system** to mark which paper pairs were already discovered
5. Same high-quality pairs kept appearing as "new" discoveries in each session

**Impact:**
- We thought we had 101 discoveries
- We actually have 46 unique discoveries
- 55 entries are duplicates (54% duplication rate!)
- Progress claims in PROGRESS.md are misleading
- Frontend would show duplicate discoveries if not fixed

---

## FINDINGS

### Phase 1: Session File Verification ✓

#### File Counts (Raw)
```
Session 47: 11 discoveries (verified_discoveries)
Session 49: 12 discoveries (plain array)
Session 52: 12 discoveries (.discoveries)
Session 54: 16 discoveries (.discoveries)
Session 56: 19 discoveries (.discoveries)
Session 57: 2 discoveries (.discoveries)
Total claimed: 72 discoveries
```

#### Deduplication Results
```
Session 47: 4 unique (7 duplicates of baseline)
Session 49: 2 unique (10 duplicates)
Session 52: 2 unique (10 duplicates)
Session 54: 4 unique (12 duplicates)
Session 56: 2 unique (17 duplicates!)
Session 57: 2 unique (0 duplicates)
Total unique: 16 discoveries
Total duplicates: 56
```

#### Most Duplicated Pairs
```
814-1943: appeared 6 times
644-354: appeared 6 times
1973-352: appeared 6 times
1970-168: appeared 6 times
100-461: appeared 6 times
```

These are clearly high-quality matches being re-discovered across sessions.

### Phase 2: Candidate Generation Source Analysis ✓

#### Candidate Provenance by Session

| Session | Curated From | Mechanisms | Source |
|---------|--------------|-----------|---------|
| 47 | 246 candidates | 90 mechanisms | Sessions 37, 46, 47 |
| 49 | 491 candidates | 104 mechanisms | Sessions 37, 46, 47, 48 |
| 52 | 556 candidates | 134 mechanisms | Session 51 |
| 54 | 867 candidates | 170 mechanisms | Session 53 |
| 56 | 1,158 candidates | 200 mechanisms | Session 55 |
| 57 | 1,158 candidates | 200 mechanisms | Session 55 (ranks 51-70) |

#### ROOT CAUSE IDENTIFIED ✓✓✓

**The mechanism pools are CUMULATIVE:**
- Session 48's 104 mechanisms = 90 (Session 47) + 14 new
- Session 51's 134 mechanisms = 104 (Session 48) + 30 new
- Session 53's 170 mechanisms = 134 (Session 51) + 36 new
- Session 55's 200 mechanisms = 170 (Session 53) + 30 new

**This means:**
1. All good matches from early mechanisms keep appearing in later candidate pools
2. Each curation session independently "discovered" the same matches
3. **We never tracked which pairs were already discovered**
4. Sessions 47-57 were NOT finding NEW discoveries - they were re-discovering OVERLAPPING candidates from cumulative pools

**Concrete Example:**
- Pair 100-461 (cooperation feedback) appears in the 90-mechanism pool
- It shows up as a top candidate in Sessions 47, 49, 52, 54, 56
- Each session independently rated it "good" and added it to their discovery file
- Result: Same pair appears 5 times across session files

---

## RECOMMENDATIONS

### Immediate Actions (Session 58)

1. **Accept the truth: 46 unique discoveries**
   - Use deduplicated discoveries.json
   - Rebuild frontend with correct count
   - Update all documentation

2. **Correct the historical record**
   - Update PROGRESS.md with accurate session contributions
   - Mark Sessions 47-57 as "X discoveries (Y unique, Z duplicates)"
   - Update METRICS.md with true milestone progress

3. **Understand quality vs quantity**
   - 46 high-quality discoveries is still good progress
   - Quality standards maintained despite duplication
   - Precision metrics still valid (they measured candidate pools correctly)

### Process Improvements (Future Sessions)

1. **Implement discovery tracking**
   - Create `discovered_pairs.json` tracking all found paper pairs
   - Check against this before adding "new" discoveries
   - Update tracking file after each curation session

2. **Fix candidate generation**
   - When adding new mechanisms, generate candidates ONLY from new pairs
   - Don't regenerate candidates from existing mechanism combinations
   - Track which mechanism pairs have been evaluated

3. **Session workflow changes**
   - Before curation: Filter out already-discovered pairs
   - During curation: Note if reviewing familiar candidates
   - After curation: Deduplicate before counting

### Lessons Learned

**What worked:**
- Quality standards maintained (excellent/good ratings consistent)
- Precision measurement methodology sound
- Semantic embeddings effective at finding matches

**What failed:**
- No deduplication tracking across sessions
- Cumulative mechanism pools without filtering
- Progress counting without verification

**Why it matters:**
- Misleading metrics undermine trust
- Duplicate work wastes curation time
- Can't accurately project growth trajectory

---

## ACTION PLAN

### Step 1: Build with Truth ✓
- [x] Fixed merge script to deduplicate
- [x] Generated discoveries.json with 46 unique discoveries
- [x] Rebuild frontend
- [x] Validate 46 pages generated (52 total pages: 46 discoveries + 6 other)

### Step 2: Update Documentation
- [ ] PROGRESS.md: Rewrite Sessions 47-57 entries with accurate counts
- [ ] METRICS.md: Update verified discoveries section
- [ ] METRICS.md: Update session history table
- [ ] Create LESSONS_LEARNED_SESSION58.md

### Step 3: Create Tracking System
- [ ] Generate `app/data/discovered_pairs.json` from current 46
- [ ] Document tracking protocol in CLAUDE.md
- [ ] Add verification step to curation workflow

### Step 4: Commit Corrected State
- [ ] Commit deduplicated discoveries.json
- [ ] Commit updated documentation
- [ ] Commit tracking system
- [ ] Clear, honest commit message explaining the correction

---

## CONCLUSION

**The Good News:**
- We have 46 high-quality, verified cross-domain isomorphisms
- Quality standards were maintained throughout
- The discoveries themselves are genuine and valuable
- We caught this before deploying misleading data

**The Bad News:**
- 54% of "discoveries" in Sessions 47-57 were duplicates
- Progress claims were inflated
- We haven't reached 100 milestone (only 46% there)
- Wasted curation time re-reviewing same candidates

**The Path Forward:**
- Accept 46 as our current count
- Implement tracking to prevent future duplication
- Continue curation with proper deduplication
- Rebuild trust through transparency

**Honesty check:**
This is embarrassing but fixable. Better to catch it now than after claiming 100+ discoveries publicly.


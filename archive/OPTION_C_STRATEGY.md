# Option C: 3-Session Strategic Pivot

**Created**: 2026-02-12 (Session 47)
**Purpose**: Document the full 3-session plan to fix our scaling crisis

---

## 🚨 The Problem

**Current intake method (category browsing) doesn't scale:**
- Session 47: 63% fetch waste (220/350 duplicates)
- Yield: 8.9% (31 mechanisms from 350 attempted fetches)
- To get 500 mechanisms: need ~5,600 fetches with ~3,500 duplicates
- 2,000+ papers in database never extracted from

**Root cause**: Fetching from `cat:cs.AI` by recent date hits same papers every session

---

## ✅ The Solution: Option C (3 Sessions)

### Session 48: Mine Existing Corpus
**Goal**: Prove we can scale WITHOUT new data by using what we have
**Tasks**:
- Score all 2,194 existing papers
- Extract 40-60 mechanisms from best unfetched papers
- Reach 50+ discoveries milestone
- **Key metric**: Hit rate ≥40% validates existing corpus

**If successful**: We have 2,000+ papers to mine (no fetching needed for months)
**If fails**: Existing corpus is low quality, pivot to keyword search immediately

---

### Session 49: Extract Mechanism Vocabulary
**Goal**: Build keyword search strategy from our best mechanisms
**Tasks**:
1. Analyze 130-150 mechanisms from Session 48
2. Extract top 20-30 structural terms (TF-IDF or frequency analysis)
   - Example terms: "feedback loop", "bistability", "phase transition", "threshold dynamics"
3. Build 10-15 arXiv search queries targeting these terms
4. Document keyword search protocol

**Output**: Keyword search strategy document with concrete queries

**Example queries**:
```
all:(feedback AND (bistability OR threshold))
all:(network AND (self-organization OR emergence))
all:(strategic AND (equilibrium OR game theory))
```

**Why this works**:
- Papers using mechanistic vocabulary are mechanism-rich by definition
- Cross-domain by default (not category-limited)
- Gets old + new papers (not just recent)
- Near-zero duplicates (new search space)

---

### Session 50: Prototype Keyword Search
**Goal**: Test keyword search vs category browsing
**Tasks**:
1. Fetch 100 papers using keyword queries (no category filters)
2. Score for mechanism richness
3. Extract mechanisms from top scorers
4. Calculate hit rate
5. Compare to Session 47 baseline (8.9% yield)

**Success criteria**: Hit rate >50% (vs 8.9% baseline = 5.6x improvement)

**If successful**: Keyword search becomes standard intake method (Sessions 51+)
**If fails**: Refine queries or revert to category browsing with better duplicate handling

---

## 📊 Projected Impact (if Option C succeeds)

### Current approach (next 2,000 papers):
- Fetch attempts: 2,000
- Duplicates: ~1,300 (65%)
- New papers: ~700
- Papers with mechanisms: ~200 (70% poor quality)
- New mechanisms: ~200
- New discoveries: ~100
- **Timeline**: 6 months

### Keyword approach (next 2,000 papers):
- Fetch attempts: 2,000
- Duplicates: <100 (5% - new search space)
- New papers: ~1,900
- Papers with mechanisms: ~1,300 (70%+ have mechanistic content)
- New mechanisms: ~1,300
- New discoveries: ~800
- **Timeline**: 2-3 months

**10x efficiency gain if keyword search hits 50%+ hit rate**

---

## 🎯 Decision Points

### After Session 48:
- **Hit rate ≥40%**: Existing corpus valuable, continue to Session 49 as planned
- **Hit rate 30-39%**: Marginal, continue to Session 49 but prioritize keyword search
- **Hit rate <30%**: Existing corpus poor, skip Session 49 and go straight to keyword prototype

### After Session 49:
- **Queries built**: Continue to Session 50 (keyword prototype)
- **Can't build good queries**: Revert to category browsing with duplicate tracking

### After Session 50:
- **Hit rate ≥50%**: Keyword search becomes standard (Sessions 51+)
- **Hit rate 40-49%**: Hybrid approach (keywords + categories)
- **Hit rate <40%**: Revert to category browsing, improve duplicate handling

---

## 📈 Success Metrics by Session

| Metric | Session 48 Target | Session 49 Target | Session 50 Target |
|--------|-------------------|-------------------|-------------------|
| Papers scored | 2,194 (all) | - | 100 (keyword fetch) |
| Mechanisms extracted | 40-60 | - | 40-60 |
| Hit rate (existing corpus) | ≥40% | - | - |
| Hit rate (keyword search) | - | - | ≥50% |
| Total mechanisms | 130-150 | 130-150 | 170-210 |
| Total discoveries | ≥50 | ≥50 | ≥60 |
| Keyword queries built | - | 10-15 | - |

---

## 🔄 Contingency Plans

### If Session 48 hit rate <30%:
**Plan A**: Skip Session 49, go straight to keyword prototype (Session 49 becomes the prototype)
**Plan B**: Fetch from new domains we haven't tried (sociology, chemistry, engineering)
**Plan C**: Revisit Session 37 methodology (was 50% hit rate - what changed?)

### If Session 50 keyword search fails:
**Plan A**: Refine queries based on what worked/didn't work, test again
**Plan B**: Hybrid approach - use categories for domains, keywords for cross-domain
**Plan C**: Implement duplicate tracking in category fetching (cache arxiv_ids)

---

## 📁 Documentation to Create

### Session 48:
- SESSION48_SUMMARY.md (hit rate analysis)
- session48_all_papers_scored.json (scoring results)
- session48_extraction_candidates.json (top papers)
- session48_extracted_mechanisms.json (new mechanisms)

### Session 49:
- SESSION49_KEYWORD_STRATEGY.md (full keyword search protocol)
- session49_keyword_vocabulary.json (extracted terms)
- session49_arxiv_queries.json (15 ready-to-use queries)

### Session 50:
- SESSION50_PROTOTYPE_RESULTS.md (keyword vs category comparison)
- session50_keyword_papers.json (100 papers from keyword search)
- session50_comparison_metrics.json (hit rates, precision, etc.)

---

## 🚀 Long-Term Vision (if Option C succeeds)

**Months 1-2**: Mine existing 2,000 papers (Sessions 48-55)
- Extract ~800 mechanisms
- Find ~400 discoveries
- Total: 400+ discoveries without new fetching

**Months 3-4**: Keyword-targeted fetching (Sessions 56-70)
- Fetch 2,000 papers using keyword search
- Extract ~1,300 mechanisms
- Find ~800 discoveries
- Total: 1,200+ discoveries

**Months 5-6**: Scale + polish (Sessions 71-85)
- Editorial content for top 100 discoveries
- Web interface improvements
- Public launch prep

**End state**: 1,200+ verified discoveries, production-ready product

---

## ✅ Why Option C is the Right Choice

1. **Tests existing corpus first** (Session 48) - no wasted effort if it's valuable
2. **Builds on success** (Session 49) - only do keyword strategy if Session 48 works
3. **Validates before scaling** (Session 50) - prototype before committing
4. **Has contingencies** - multiple paths forward if things fail
5. **Data-driven** - hit rates determine next steps, not guesswork

**Worst case**: Session 48 fails (hit rate <30%), we pivot immediately and lose 1 session
**Best case**: All 3 sessions succeed, we 10x our efficiency and reach 500+ discoveries by Month 4

---

**This is the plan. Execute Session 48 to start the cascade.**

---

**Created by**: Session 47 Agent
**For**: Session 48+ Agents
**Purpose**: Strategic context for the next 6 months

# Session 48 Quick Start Checklist

**Agent 48**: Use this as your step-by-step execution guide.

---

## ⚡ Quick Context (30 seconds)

**Mission**: Extract 40-60 mechanisms from existing 2,194 papers WITHOUT fetching new ones
**Why**: Session 47 wasted 63% of fetches on duplicates
**Goal**: Prove we can scale by mining existing corpus
**Key Metric**: Hit rate ≥40% (mechanisms extracted / papers attempted)

---

## 📚 Required Reading (15 min)

Read in this order:
1. ✅ SESSION48_BRIEFING.md (your main instructions)
2. ✅ PROGRESS.md (Session 47 summary - see pivot note)
3. ✅ SESSION47_SUMMARY.md (why we're pivoting)
4. ✅ DATA_QUALITY_STANDARDS.md (extraction quality)

---

## ✅ Execution Checklist

### Part 1: Score All Papers (1-2 hours)
- [ ] Create `scripts/score_all_papers.py` (adapt from audit_mechanism_richness.py)
- [ ] Score all 2,194 papers in database
- [ ] Save to `examples/session48_all_papers_scored.json`
- [ ] Identify papers scoring ≥5/10 (expect ~600-800)
- [ ] Summary stats: avg score, high-value count, domain breakdown

### Part 2: Select Extraction Candidates (30 min)
- [ ] Load scored papers
- [ ] Check which papers already extracted (Sessions 37, 46, 47)
- [ ] Filter to unextracted papers only
- [ ] Select top 100 by score (prefer ≥6/10)
- [ ] Save to `examples/session48_extraction_candidates.json`

### Part 3: Extract Mechanisms (3-4 hours)
- [ ] Create `examples/session48_extracted_mechanisms.json`
- [ ] Extract from top 100 candidates
- [ ] Target: 40-60 mechanisms (40-60% hit rate)
- [ ] Quality: Domain-neutral, structural, causal (200-400 chars)
- [ ] Track: papers attempted, mechanisms extracted, hit rate

### Part 4: Embeddings + Match (30 min)
- [ ] Combine 90 existing + new = 130-150 total mechanisms
- [ ] Save to `examples/session48_all_mechanisms.json`
- [ ] Generate 384-dim embeddings (sentence-transformers)
- [ ] Save to `examples/session48_embeddings.npy`
- [ ] Match cross-domain (threshold ≥0.35)
- [ ] Save to `examples/session48_candidates.json`
- [ ] Expect: 400-600 candidates

### Part 5: Quick Curation (30 min)
- [ ] Review top 10-15 candidates
- [ ] Select 5-10 excellent/good discoveries
- [ ] Add to `examples/session48_verified_discoveries.json`
- [ ] **Verify total discoveries ≥50** (MILESTONE!)

### Part 6: Documentation (30 min)
- [ ] Create `SESSION48_SUMMARY.md`
- [ ] Update `PROGRESS.md` (Session 48 entry)
- [ ] Update `METRICS.md` (new stats)
- [ ] Update `DAILY_GOALS.md` (Session 49 goals)
- [ ] **Document hit rate prominently**

### Part 7: Commit
- [ ] `git add -A`
- [ ] `git commit -m "Session 48: Mine existing corpus - [X] mechanisms, [Y]% hit rate"`
- [ ] Include hit rate in commit message

---

## 🎯 Success Criteria

**Must achieve**:
- [ ] 2,194 papers scored ✓
- [ ] 40-60 mechanisms extracted ✓
- [ ] 130-150 total mechanisms ✓
- [ ] ≥50 total discoveries (milestone) ✓
- [ ] Hit rate documented ✓

**Hit rate targets**:
- ✅ ≥40% = SUCCESS (proves existing corpus valuable)
- ⚠️ 30-39% = MARGINAL (corpus has some value)
- ❌ <30% = FAIL (must pivot to keyword search immediately)

---

## ⚠️ Critical Constraints

**DO NOT**:
- ❌ Fetch new papers from arXiv
- ❌ Re-extract from papers done in Sessions 37/46/47
- ❌ Skip scoring step
- ❌ Extract from papers scoring <5/10

**DO**:
- ✅ Score ALL papers first
- ✅ Focus on highest scorers (≥6/10)
- ✅ Track hit rate precisely
- ✅ Use TodoWrite for progress tracking

---

## 📊 Expected Outputs

| File | Size | Content |
|------|------|---------|
| session48_all_papers_scored.json | ~500KB | 2,194 papers with scores |
| session48_extraction_candidates.json | ~50KB | Top 100 papers for extraction |
| session48_extracted_mechanisms.json | ~30KB | 40-60 new mechanisms |
| session48_all_mechanisms.json | ~90KB | 130-150 combined |
| session48_embeddings.npy | ~200KB | 130-150 × 384 matrix |
| session48_candidates.json | ~300KB | 400-600 match candidates |
| session48_verified_discoveries.json | ~20KB | 5-10 new discoveries |
| SESSION48_SUMMARY.md | ~10KB | Results + hit rate analysis |

**Total**: 8-9 new files

---

## 🔧 Code Templates

### Score All Papers
```python
# Adapt from scripts/audit_mechanism_richness.py
# Change: SELECT * FROM papers (not LIMIT 50)
# Output: JSON with {paper_id, score, categories}
```

### Check Already Extracted
```python
# Load session 37/46/47 mechanism files
# Get unique paper_ids already extracted
# Filter scored papers to exclude these
```

### Extract Mechanisms
```python
# For each candidate paper:
#   1. Read abstract from database
#   2. Manually write 1-2 domain-neutral mechanisms
#   3. Save to JSON
# Track: papers_attempted, mechanisms_extracted
# Calculate: hit_rate = mechanisms / papers
```

---

## ⏱️ Time Budget

| Part | Time | Running Total |
|------|------|---------------|
| Reading docs | 15 min | 0:15 |
| Score papers | 1.5 hours | 1:45 |
| Select candidates | 30 min | 2:15 |
| Extract mechanisms | 3.5 hours | 5:45 |
| Embeddings + match | 30 min | 6:15 |
| Quick curation | 30 min | 6:45 |
| Documentation | 30 min | 7:15 |
| **Total** | **~7 hours** | - |

Adjust if you work faster/slower, but **extraction is the bottleneck** (3-4 hours).

---

## 🚦 Decision Points

**After Part 1 (scoring)**:
- If <500 papers score ≥5/10 → existing corpus is poor quality
- If 800+ papers score ≥5/10 → existing corpus is excellent

**After Part 3 (extraction)**:
- If hit rate ≥40% → SUCCESS, continue to Part 4
- If hit rate <30% → FAIL, document and recommend immediate keyword pivot

**After Part 5 (curation)**:
- If total discoveries <50 → extract/curate more
- If total discoveries ≥50 → MILESTONE REACHED!

---

## 📞 Help Resources

**Stuck on scoring?** → Check scripts/audit_mechanism_richness.py
**Stuck on extraction?** → Check examples/session47_extracted_mechanisms.json
**Stuck on embeddings?** → Check scripts/session47_embed_and_match.py
**Stuck on quality?** → Read DATA_QUALITY_STANDARDS.md
**Stuck on strategy?** → Read SESSION48_BRIEFING.md again

---

## ✅ Final Check Before Commit

- [ ] Hit rate calculated and documented
- [ ] Total discoveries ≥50
- [ ] All 8-9 files created
- [ ] PROGRESS.md updated
- [ ] METRICS.md updated
- [ ] DAILY_GOALS.md updated (Session 49)
- [ ] SESSION48_SUMMARY.md created
- [ ] Commit message includes hit rate

---

**Ready? Start with Part 1: Score All Papers**

Use `TodoWrite` to track Parts 1-7 as you work.

Good luck, Agent 48!

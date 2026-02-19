# Session 38: Manual Curation - Select Best 25-30 Discoveries

**Date**: 2026-02-10 (Ready to start)
**Agent**: Fresh agent (Session 37 complete)
**Mission**: Review 165 candidates and select the best 25-30 verified isomorphisms for launch

---

## Context: Where We Are

**Session 37 Results** (COMPLETE):
- ✅ Generated 165 cross-domain candidate pairs from 54 mechanisms
- ✅ Semantic embeddings: 384-dim vectors (sentence-transformers)
- ✅ Similarity range: 0.35-0.74 (max: 0.7364, mean: 0.4318)
- ✅ Expected precision: ~40% (66 potentially genuine out of 165)

**Your Mission**:
Review all 165 candidates and curate the best 25-30 for launch.

**Why Manual Review**:
- Session 36 showed embeddings find genuine matches but at lower scores than expected
- Domain diversity paradox: diverse domains = better matches but lower similarity scores
- 40% precision means ~66 genuine matches need human validation
- Quality gate before launch

---

## Input File

**`examples/session37_candidates_for_review.json`** (165 candidates)

Structure:
```json
{
  "metadata": {
    "session": 37,
    "total_mechanisms": 54,
    "threshold": 0.35,
    "total_candidates": 165
  },
  "candidates": [
    {
      "candidate_id": 1,
      "similarity": 0.7364,
      "paper_1": {
        "paper_id": 123,
        "arxiv_id": "2401.12345",
        "domain": "econ",
        "title": "...",
        "mechanism": "..."
      },
      "paper_2": {
        "paper_id": 456,
        "domain": "q-bio",
        "title": "...",
        "mechanism": "..."
      },
      "review_status": "pending",
      "rating": null,
      "notes": null
    }
  ]
}
```

---

## Part 1: Review Top 50 Candidates (2 hours)

### Goal
Review highest similarity candidates (0.74 down to ~0.50) and identify Excellent/Good matches.

### Process

**For each candidate:**

1. **Read both mechanism descriptions carefully**
   - Focus on causal relationships
   - Look for feedback loops
   - Identify threshold dynamics
   - Note control parameters

2. **Assess match quality:**

   **Excellent (✅✅):**
   - Different top-level domains (biology ↔ physics, economics ↔ physics, etc.)
   - Same structural mechanism (causal relationships match)
   - Domain-neutral language succeeded in capturing the core pattern
   - Actually interesting/insightful connection
   - Would be valuable to researchers

   **Good (✅):**
   - Different domains
   - Similar structure (not identical but clearly related)
   - Somewhat interesting
   - Useful but not spectacular

   **Weak (⚠️):**
   - Same domain or very related fields (e.g., two biology subfields)
   - Superficial similarity only (shared keywords but different mechanisms)
   - Not very interesting

   **False Positive (❌):**
   - Completely different mechanisms
   - Not actually similar (embedding error)
   - Misleading match

3. **For Excellent and Good matches, write structural explanation:**

   ```markdown
   ### [Name of Mechanism]

   **Domains:** [Domain 1] ↔ [Domain 2]
   **Papers:**
   - [Paper 1 title] (arxiv:XXXXX)
   - [Paper 2 title] (arxiv:XXXXX)
   **Similarity:** [score]

   **Structural Pattern:**
   [2-3 sentences explaining what mechanism both papers describe]

   **Why This Matters:**
   [1-2 sentences on what researchers could learn from this connection]

   **Quality:** Excellent/Good
   ```

### Expected Results
- **Excellent matches**: ~10-15 from top 50
- **Good matches**: ~10-15 from top 50
- **Total**: ~20-25 verified matches from Part 1

---

## Part 2: Review Next 30-40 Candidates (1-1.5 hours)

### Goal
Review middle similarity range (0.50 down to ~0.40) for additional Good matches.

### Process
Same as Part 1, but expect:
- Fewer Excellent matches (maybe 0-5)
- More Good matches (~10-15)
- More Weak/False positives

### Expected Results
- **Excellent**: ~0-5
- **Good**: ~10-15
- **Total**: ~10-20 additional verified matches from Part 2

---

## Part 3: Spot Check Bottom Candidates (30 min - OPTIONAL)

### Goal
Quick scan of lowest similarity candidates (0.35-0.40) to check if threshold is appropriate.

### Process
- Sample ~20 candidates from this range
- Quick assessment (don't need full structural explanations)
- Goal: Verify that precision drops off at lower similarities
- Look for any hidden gems (unlikely but possible)

### Expected Results
- Lower precision (maybe 10-20%)
- Validates threshold choice
- Unlikely to find many keepers

---

## Part 4: Final Selection & Documentation (30 min)

### Goal
Select best 25-30 discoveries and create launch-ready documentation.

### Selection Criteria

**Prioritize:**
1. **Quality**: Excellent > Good
2. **Domain diversity**: Spread across multiple domain pairs
3. **Clarity**: Clearest structural explanations
4. **Impact**: Best research implications
5. **Interestingness**: Most surprising connections

**Target: 25-30 total verified discoveries**

### Create Final Collection

**File**: `examples/session38_curated_discoveries.json`

Structure:
```json
{
  "metadata": {
    "session": 38,
    "date": "2026-02-10",
    "total_reviewed": 165,
    "total_selected": 28,
    "selection_criteria": "Best 25-30 excellent/good matches"
  },
  "discoveries": [
    {
      "discovery_id": 1,
      "name": "[Mechanism Name]",
      "domains": "[Domain 1] ↔ [Domain 2]",
      "similarity": 0.7364,
      "quality": "excellent",
      "paper_1": {
        "paper_id": 123,
        "arxiv_id": "2401.12345",
        "title": "...",
        "mechanism": "..."
      },
      "paper_2": {
        "paper_id": 456,
        "arxiv_id": "2401.67890",
        "title": "...",
        "mechanism": "..."
      },
      "structural_pattern": "...",
      "why_it_matters": "...",
      "reviewed_by": "Claude (Session 38)",
      "reviewed_date": "2026-02-10"
    }
  ]
}
```

---

## Success Criteria

✅ All 165 candidates reviewed and rated
✅ 25-30 Excellent/Good matches selected
✅ Each has structural explanation (structural_pattern field)
✅ Each has research implications (why_it_matters field)
✅ Ready for website showcase
✅ SESSION38_RESULTS.md created
✅ PROGRESS.md and METRICS.md updated
✅ All changes committed

---

## Expected Outcomes

Based on Session 36's 40% precision and Session 37's 165 candidates:

**From Top 50 (0.74-0.50)**:
- Excellent: ~10-15 matches
- Good: ~10-15 matches
- **Subtotal: ~20-25 verified**

**From Next 40 (0.50-0.40)**:
- Excellent: ~0-5 matches
- Good: ~10-15 matches
- **Subtotal: ~10-20 verified**

**Total Pool: ~30-45 verified matches**

**Final Selection: Best 25-30 for launch**

---

## Quality Guidelines

### What Makes an "Excellent" Match?

**Same Causal Structure**:
- Both describe: A causes B, B affects C, feedback to A
- Both have: threshold dynamics (when X exceeds Y, Z happens)
- Both show: negative/positive feedback loops
- Both exhibit: control parameters that modulate behavior

**Clear Domain Neutrality**:
- Extracted mechanisms use generic terms (agent, system, component, network)
- Not just shared keywords - actual structural similarity
- Could swap mechanisms between papers and they'd still make sense

**Interesting Connection**:
- Non-obvious connection between fields
- Could lead to cross-pollination of ideas
- Might inspire new research questions

### What Makes a "Good" Match?

- Same general pattern but not identical structure
- Related mechanisms with some differences
- Useful connection but less profound
- One field might have insights for the other

### What's "Weak" or "False"?

**Weak**:
- Same domain (e.g., two biology subfields)
- Only superficial similarity
- Shared vocabulary but different mechanisms
- Not particularly interesting

**False**:
- Completely different mechanisms
- Embedding error
- No actual structural similarity

---

## Examples from Session 36

### Excellent Match (0.453 similarity)

**Tragedy of Commons**: Economics ↔ Biology

**Economics paper (Free-Rider Problem)**:
"Shared resource use creates a cooperation dilemma with cleaning costs, contamination risk, and social incentives forming competing pressures. Cleaning cost primarily determines stability of altruistic behavior. The system exhibits multi-stability and hysteresis - small parameter changes can cause abrupt shifts between cooperation and free-riding equilibria."

**Biology paper (Threshold Resource Redistribution)**:
"When agents fall below a resource threshold, they solicit resources from connected neighbors based on relatedness. Redistribution creates feedback between kinship network structure and reproduction ability. This enables population survival at lower resource densities but increases network heterogeneity and local centralization."

**Why Excellent**: Both describe cooperation dilemmas around shared resources with threshold dynamics and multi-stable equilibria. Clear structural isomorphism despite different contexts.

---

## Time Budget

- **Part 1** (Top 50): 2 hours
- **Part 2** (Next 40): 1.5 hours
- **Part 3** (Spot check): 30 min (optional)
- **Part 4** (Selection): 30 min
- **Total**: 3.5-4.5 hours

---

## Files to Create

1. **`examples/session38_curated_discoveries.json`** - Final 25-30 selected discoveries
2. **`SESSION38_RESULTS.md`** - Session summary
3. Updated: **PROGRESS.md** - Add Session 38 entry
4. Updated: **METRICS.md** - Add final metrics
5. Updated: **DAILY_GOALS.md** - Prepare for next session (if any)

---

## Important Reminders

### From Session 36 (Domain Diversity Paradox)
- Best match was at **0.453 similarity** (not 0.7+)
- More diverse domains = better structural matches but LOWER scores
- Don't dismiss matches in 0.35-0.50 range - they might be excellent!

### From Session 37 (Strategic Selection)
- 50% hit rate on mechanism-rich papers (vs 22.5% random)
- Domain-neutral extraction works
- Quality > quantity

### Quality Focus
This is the final gate before launch. Take your time. Be thorough. Only select matches you'd be proud to showcase.

---

## Ready to Begin!

When you start Session 38, you should:

1. Read `examples/session37_candidates_for_review.json`
2. Start reviewing from highest similarity (candidate_id 1)
3. For each match, assess quality and write explanations
4. Keep running notes in a separate file if helpful
5. After reviewing all candidates, select best 25-30
6. Create final curated collection
7. Document everything
8. Commit

**Let's curate some amazing discoveries!** 🎯

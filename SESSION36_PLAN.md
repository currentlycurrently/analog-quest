# Session 36: Diverse Sample Test - DECISIVE VALIDATION

**Mission**: Test if semantic embeddings can find cross-domain isomorphisms with TRULY diverse sample.

**Context**: Session 35 revealed our 9-paper sample was too biology-heavy (77.8%). Embeddings work 4.7x better than TF-IDF but max similarity was only 0.657 (vs 0.75 target). Need genuine domain diversity to test if algorithmic matching can find structural isomorphisms.

**Time Budget**: 2.5-3 hours

---

## Part 1: Strategic Paper Selection (30 min)

**Goal**: Select 20-30 papers that are mechanism-rich, truly diverse, and likely to match.

### Selection Criteria

Papers must be:
1. ✅ **Mechanism-rich** (describe processes/dynamics, not just methods/empirical results)
2. ✅ **Truly diverse** (different top-level domains, NOT biology subfields)
3. ✅ **Likely to match** (study similar phenomena in different contexts)

### Target Distribution (20-30 papers total)

**5 Economics papers:**
- Tragedy of commons / public goods games
- Market dynamics / supply-demand equilibria
- Game theory / strategic interaction
- Network effects / externalities
- One more (agent's choice based on judgment)

**5 Ecology papers:**
- Predator-prey dynamics / population cycles
- Resource competition / overexploitation
- Allee effects / critical threshold dynamics
- Species cooperation / mutualism
- One more (agent's choice)

**5 Sociology/Network Science papers:**
- Collective behavior / coordination problems
- Social tipping points / information cascades
- Network centrality / influence propagation
- Cooperation / reciprocity norms
- One more (agent's choice)

**5 Physics papers:**
- Phase transitions / critical phenomena
- Chaos / dynamical systems / attractors
- Feedback / self-organization
- Scaling laws / power laws
- One more (agent's choice)

**5 Control/Engineering papers:**
- Feedback control / stability analysis
- Optimization / equilibria
- System dynamics / oscillation
- Two more (agent's choice based on mechanism richness)

### How to Find Papers

Query database by domain + keywords:
```sql
-- Example for economics tragedy of commons:
SELECT * FROM papers
WHERE domain = 'econ'
AND (abstract LIKE '%tragedy%' OR abstract LIKE '%commons%'
     OR abstract LIKE '%public goods%' OR abstract LIKE '%free rider%')
LIMIT 10;
```

**Pick papers where abstracts describe MECHANISMS** (what causes what, feedback, thresholds, dynamics).

**Skip papers** that are purely empirical ("we measured X") or methodological ("we present algorithm Y").

---

## Part 2: LLM Extraction (1 hour)

**Goal**: Extract mechanisms from selected papers using Session 33/34 LLM approach.

### Use EXACT Prompt Template

```
Read this abstract and extract the core MECHANISM being described.

A mechanism is a causal process: what affects what, and how.

Describe in 2-3 sentences using domain-neutral language:
- Use generic terms (population, resource, agent, system, component)
- Avoid field-specific jargon and technique names
- Focus on causal relationships (A causes B, B affects C)
- Include feedback loops if present (A → B → A)
- Include thresholds if present (when X crosses Y, then Z)

GOOD: "Resource abundance allows population growth. Growing population depletes resources. Creates oscillating cycle."
BAD: "This paper uses Lotka-Volterra equations for predator-prey."

Abstract: {TEXT}

Mechanism (2-3 sentences):
```

### Expected Outcomes

- **Hit rate**: ~60% (12-18 mechanisms from 20-30 papers)
- This is FINE - quality over quantity
- Only extract from papers that ACTUALLY describe mechanisms

### Save Results

Store in `examples/session36_diverse_mechanisms.json` with format:
```json
{
  "paper_id": 123,
  "domain": "econ",
  "subdomain": "econ.GN",
  "title": "...",
  "mechanism": "...",
  "mechanism_type": "feedback_loop,threshold_dynamics",
  "extraction_quality": "excellent"
}
```

---

## Part 3: Semantic Embedding Matching (30 min)

**Goal**: Find cross-domain matches using embeddings.

### Process

1. **Generate embeddings** for all mechanisms
   - Use sentence-transformers (all-MiniLM-L6-v2) - already installed
   - 384-dimensional embeddings
   - Reuse script: `scripts/test_semantic_embeddings.py`

2. **Calculate cross-domain similarities**
   - Compute pairwise cosine similarity
   - Filter to cross-domain only (different top-level domains)
   - Economics ↔ Ecology (YES)
   - Ecology ↔ Cell Biology (NO - both biology)

3. **Target threshold**: ≥0.65 (relaxed from 0.75)
   - Session 35 max was 0.657 with biology-heavy sample
   - With diverse sample, expect higher similarities

4. **Goal**: Find ≥3 genuine cross-domain matches

### Save Results

Store in `examples/session36_embedding_matches.json`

---

## Part 4: Manual Quality Review (30 min)

**Goal**: Assess if matches are genuine structural isomorphisms.

### Review Top 5-10 Pairs

For each match, ask:
1. **Do they describe the SAME mechanism structure?**
   - Same causal relationships? (A causes B, B affects C)
   - Same feedback patterns? (reinforcing, balancing)
   - Same thresholds/tipping points?

2. **Are they in DIFFERENT domains?**
   - Economics ↔ Physics (YES - truly cross-domain)
   - Ecology ↔ Epidemiology (MAYBE - both biology, but different enough)
   - Ecology ↔ Cell Biology (NO - both biology subfields)

3. **Would this be interesting to researchers?**
   - Non-obvious connection?
   - Could inspire new research directions?
   - Or is it trivial/well-known?

4. **Is this a genuine discovery?**
   - Structural similarity (mechanism) or topical similarity (same subject)?
   - Example GOOD: Tragedy of commons (economics) ↔ Resource overexploitation (ecology)
   - Example BAD: Epidemic SIR model ↔ Pathogen evolution (both about disease)

### Rating Scale

- ✅ **Excellent**: Clear structural isomorphism, genuinely interesting, non-obvious
- ✅ **Good**: Valid similarity, useful connection, may be known but well-matched
- ⚠️ **Weak**: Superficial similarity, questionable connection, or just shared vocabulary
- ❌ **False**: Not actually similar, embeddings confused by topic overlap

### Quality Threshold

**Success**: ≥3 matches rated Excellent or Good

---

## Success Criteria & Decision Tree

### Outcome A: SUCCESS ✅
**≥3 good/excellent matches at ≥0.65 similarity**

**What this means**: Algorithmic matching works with diverse sample!

**Next steps (Sessions 37-39)**:
1. Scale LLM extraction to all 2,021 papers
2. Filter to ~450-500 papers with extractable mechanisms (~22.5% hit rate)
3. Generate embeddings for all mechanisms
4. Match with ≥0.65 threshold
5. Review top 30-50 matches for quality
6. Launch with 20-30 verified high-quality isomorphisms

**Timeline**: 3-4 sessions to viable product

---

### Outcome B: PARTIAL SUCCESS ⚠️
**1-2 good matches at ≥0.60, OR several weak matches**

**What this means**: Embeddings can find candidates but need manual verification.

**Next steps (Sessions 37-38)**:
1. Pivot to **Manual Curation Path** (Option C from Session 35)
2. Use embeddings to find candidate pairs (≥0.55 threshold, cast wide net)
3. Manually review all candidates, curate 20-30 excellent isomorphisms
4. Document each with explanation of structural similarity
5. Launch with curated set, grow organically with user feedback

**Timeline**: 2-3 sessions for manual curation

---

### Outcome C: FAILURE ❌
**0 good matches, all weak/false positives**

**What this means**: Algorithmic matching has fundamental limitations.

**Next steps (Session 37)**:
1. Honest post-mortem: Why didn't it work?
   - Sample still not diverse enough?
   - Embeddings too generic?
   - Structural isomorphisms are genuinely rare?
2. Pivot options:
   - **Option 1**: Fully manual curation (find ~10-20 by hand reading papers)
   - **Option 2**: Framework transfer tool (help users apply known frameworks)
   - **Option 3**: Assisted discovery (human-in-the-loop matching)

**Timeline**: 1 session post-mortem, 2-3 sessions for chosen pivot

---

## Deliverable

Create `SESSION36_DIVERSE_SAMPLE_TEST.md` with:

1. **Papers Selected** (20-30 total)
   - List with domains and why chosen
   - Show target distribution achieved

2. **Mechanisms Extracted** (12-18 expected)
   - Hit rate percentage
   - Examples of good extractions
   - Examples of papers skipped (no mechanisms)

3. **Embedding Results**
   - Similarity statistics (max, mean, median)
   - Number of pairs above different thresholds
   - Top 10 pairs by similarity

4. **Manual Quality Review**
   - Assessment of top 5-10 pairs
   - Rating for each (Excellent/Good/Weak/False)
   - Examples of why matches are good or bad

5. **Clear Recommendation**
   - Outcome A, B, or C
   - Specific next steps for Session 37
   - Honest assessment of what worked/didn't work

---

## Tips for Success

1. **Be selective in Part 1** - Only pick papers that clearly describe mechanisms
2. **Be strict in Part 2** - Only extract when mechanism is clear, skip ambiguous papers
3. **Be honest in Part 4** - Don't inflate quality ratings, we need accurate assessment
4. **Focus on diversity** - Better to have 15 truly diverse mechanisms than 25 biology-heavy ones

---

## Files to Create

1. `examples/session36_selected_papers.json` - Papers selected (20-30)
2. `examples/session36_diverse_mechanisms.json` - Extracted mechanisms (12-18)
3. `examples/session36_embedding_matches.json` - Match results
4. `SESSION36_DIVERSE_SAMPLE_TEST.md` - Complete report with recommendation

---

## Context from Previous Sessions

**Session 33**: LLM extraction validated on 12 papers → 5 matches found manually
**Session 34**: Scaled to 40 papers → only 9 mechanisms (22.5% hit rate), TF-IDF failed (0 matches)
**Session 35**: Tested embeddings on 9 mechanisms → max similarity 0.657, sample too biology-heavy

**Key learnings**:
- LLM extraction works (100% success on mechanism-rich papers)
- Hit rate is ~22.5% (need to be selective)
- TF-IDF broken (lexical mismatch with domain-neutral text)
- Embeddings work 4.7x better but need domain diversity
- True isomorphisms require truly diverse domains

---

**This is the decisive test. If embeddings find ≥3 good matches with diverse sample, we have a path to viable product. If not, we pivot to manual curation or alternative approaches.**

**Good luck! 🚀**

---

**Last Updated**: 2026-02-10
**Session 35 Results**: Embeddings validated, need diversity
**Decision Point**: Test with diverse sample (Session 36) before scaling

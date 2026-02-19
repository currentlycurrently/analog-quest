# SESSION 34 QUICKSTART

**Status**: ✅ Ready to begin
**Command**: "Begin Session 34"

---

## WHAT YOU NEED TO KNOW

### The Breakthrough (Session 33)

**LLM-based mechanism extraction WORKS!**

- Tested on 12 papers: **100% success** (12/12)
- Found **5 genuine cross-domain matches** (42% yield!)
- Estimated precision: **60-70%** (vs current 30-35%)

**Why it works:**
- LLM extracts "A causes B → C" (mechanisms)
- Keyword extraction captured "We present X" (methods)
- **2x precision improvement!**

### The Problem (Sessions 31-32)

Current system is broken:
- Ultra-high matches (≥0.9): **0% precision** (all technique matches)
- Medium matches (0.77-0.85): **~35% precision**
- Root cause: Keyword extraction doesn't capture mechanisms

### The Mission (Session 34)

**Scale LLM extraction from 12 → 100 papers to validate precision estimate**

**Critical test:** Does 60-70% precision hold at scale?

**Decision point:**
- ✅ If ≥60% → Scale to all 2,021 papers (Session 35)
- ⚠️ If 45-60% → Refine prompts and retry
- ❌ If <45% → Pivot to framework transfer tool

---

## YOUR 5-PART PLAN

### Part 1: Select 100 Papers (30 min)

**Target mechanism-rich fields:**
- 25 ecology/evolution
- 25 economics/game theory
- 20 epidemiology
- 15 control theory/dynamics
- 15 other (sociology, complexity science)

**Avoid:** Pure ML/technique papers, purely empirical papers

**SQL query template:**
```sql
SELECT id, title, abstract, domain, subdomain
FROM papers
WHERE (
  subdomain LIKE '%PE%' OR
  abstract LIKE '%population%' OR
  abstract LIKE '%equilibrium%' OR
  abstract LIKE '%feedback%'
)
AND abstract NOT LIKE '%neural network%'
LIMIT 30;
```

### Part 2: Extract Mechanisms (2 hours)

**Use EXACT prompt:**
```
Read this abstract and extract the core MECHANISM.

A mechanism is a causal process: what affects what, and how.

Describe in 2-3 sentences using domain-neutral language:
- Use generic terms (population, resource, agent, system)
- Avoid field-specific jargon
- Focus on causal relationships (A causes B)
- Include feedback loops (A → B → A)
- Include thresholds (when X crosses Y, then Z)

GOOD: "Resource abundance allows population growth. Growing population depletes resources. Creates oscillating cycle."
BAD: "This paper uses Lotka-Volterra equations for predator-prey."

Abstract: {TEXT}

Mechanism:
```

**Process in batches of 20, save checkpoints**

### Part 3: Match Mechanisms (30 min)

Find cross-domain matches:
- Similarity ≥0.77
- **Cross-domain ONLY** (ecology ↔ economics OK, ecology ↔ ecology NOT OK)
- Look for: feedback loops, thresholds, scaling, network effects

### Part 4: Quality Review (1 hour)

**Sample 30 matches:**
- 10 high similarity (≥0.85)
- 10 medium (0.80-0.84)
- 10 low (0.77-0.79)

**Rate each:**
- ✅ **Excellent**: Clear isomorphism, genuinely interesting
- ✅ **Good**: Valid similarity, useful connection
- ⚠️ **Weak**: Superficial, generic pattern
- ❌ **False Positive**: Not actually similar

**Calculate precision:** (Excellent + Good) / 30

### Part 5: Decision (30 min)

Based on precision:
- **≥60%**: ✅ SCALE to all 2,021 papers
- **45-60%**: ⚠️ REFINE prompts and retry
- **<45%**: ❌ PIVOT to framework transfer tool

Document in `SESSION34_RESULTS.md`

---

## FILES TO CREATE

1. `examples/session34_selected_papers.json` - 100 selected papers
2. `scripts/llm_extract_mechanisms.py` - Extraction script
3. `examples/session34_llm_mechanisms.json` - 100 extracted mechanisms
4. `examples/session34_candidate_matches.json` - All candidate matches
5. `examples/session34_quality_review.json` - 30 reviewed matches with ratings
6. `SESSION34_RESULTS.md` - Analysis and decision

---

## SUCCESS CRITERIA

✅ 100 papers processed with LLM extraction
✅ Mechanisms in domain-neutral language
✅ 30 matches manually reviewed
✅ **REAL precision measured** (not estimated!)
✅ Clear recommendation for Session 34

---

## KEY CONTEXT FILES

**Read these first:**
1. **DAILY_GOALS.md** → Session 34 section (full plan)
2. **SESSION33_EXPERIMENTS.md** → What worked in Session 33
3. **PROGRESS.md** → Full session history (Sessions 31-33 context)

**Reference:**
- `examples/session33_llm_mechanisms.json` - 12 example extractions
- `SESSION31_QUALITY_CRISIS.md` - Why current system is broken
- `SESSION32_ANALYSIS.md` - Deep dive into the problem

---

## DATABASE INFO

- **Papers**: 2,021 total
- **Patterns**: 6,064 (keyword-extracted, broken)
- **Isomorphisms**: 616 (30-35% precision, broken)
- **Hit rate**: 92.2%

**Location**: `database/papers.db`

---

## TIMELINE

**Session 34**: 4-5 hours
**If successful**: Session 35 (scale to all papers), Session 36 (launch prep)
**If not**: Refine or pivot based on data

---

## REMEMBER

**This is the CRITICAL TEST.**

Session 33 proved LLM extraction works on 12 papers.
Session 34 tests if it scales to 100.

**Make decision based on empirical data, not estimates.**

If precision holds at 60-70%, we have a viable path forward.
If not, we pivot with clarity.

**Either way, we'll know.**

Good luck! 🚀

---

**STATUS**: ✅ Everything is ready. Just start with "Begin Session 34"

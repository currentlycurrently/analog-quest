# SESSION 33: Strategic Experimentation - Analysis So Far

**Date**: 2026-02-10
**Status**: In Progress

---

## Experiment 3: Analyzing What Actually Worked

### Key Finding: "Clean" ≠ "Genuine"

**Database breakdown (0.77-0.85 range):**
- Total matches: 573
- **Technique matches**: 290 (50.6%) - explicit shared terminology (GNN, transformer, attention, black hole, etc.)
- **"Clean" matches**: 283 (49.4%) - no obvious technique terms

**But "clean" doesn't mean "genuine"!**

### Analysis of Top 20 Clean Matches

#### Category 1: Power Law Scaling (Ubiquitous Pattern)
**Examples:**
- Match #1 (0.815): Materials science error ~ power law ↔ Wave function error ~ power law
- Match #10 (0.793): Financial volatility ~ power law ↔ Critical current ~ power law
- Match #15 (0.791): iCIPT2 error ~ power law ↔ Level spacing ~ inverse power law

**Assessment**:
- Power laws appear in countless systems
- Too generic to be interesting
- Like matching "both papers mention math"
- **Verdict: Weak matches**

#### Category 2: Phase Transitions (Common Framework)
**Examples:**
- Match #2 (0.810): Graph growth phase transition ↔ Spectral fluctuation phase transition
- Match #4 (0.800): Thermodynamic phase change ↔ Skyrmion formation
- Match #6 (0.795): Black hole phase transition ↔ Matrix spectral phase transition

**Assessment**:
- More specific than power laws
- But "phase transition" is a well-known framework from statistical physics
- Papers often APPLY phase transition theory to new domains
- Not independent discoveries
- **Verdict: Framework applications (like GNN matches but for physics)**

#### Category 3: Gauge Theory (Same Theoretical Framework)
**Examples:**
- Match #7-8, #11-12 (0.794-0.793): EP Model U(1) gauge ↔ Quantum simulator U(1) gauge
- Match #3 (0.807): Gravity with Yang-Mills ↔ Manin gauge theory

**Assessment**:
- Both explicitly use "U(1) gauge theory"
- Same theoretical framework, different applications
- Like GNN matches but missed by filter (no "gauge" in TECHNIQUE_TERMS)
- **Verdict: Technique matches in disguise**

#### Category 4: Dynamical Systems (Mathematical Framework)
**Examples:**
- Match #5 (0.797): Discrete dynamics with chaos ↔ Critical slowing down in bifurcations
- Match #9 (0.793): ODEs for modeling ↔ Mechanistic models + ML

**Assessment**:
- Both use dynamical systems theory
- Common mathematical framework
- **Verdict: Framework applications**

#### Category 5: Game Theory / Strategic Interaction ⭐ MOST INTERESTING
**Examples:**
- Match #16-19 (0.789): Economics "Tragedy of Commons" + game theory ↔ LLM alignment + Nash equilibrium

**Why interesting:**
- Economics paper: Formalize "Tragedy of Commons" using game theory (Prisoner's Dilemma)
- AI paper: Apply game theory (Nash equilibrium) to LLM population behavior
- **This IS cross-domain application of economics concept to AI**
- Different domains: Economics ↔ Computer Science
- Same mechanism: Strategic interaction, equilibrium analysis

**But is it "genuine"?**
- ❌ Not independent discovery - AI paper likely knows game theory from economics
- ✓ BUT: Applying established framework to novel domain (LLM behavior)
- ✓ Non-obvious connection: "LLM alignment = strategic interaction problem"
- **Verdict: Best match in top 20 - framework transfer, not independent discovery**

---

### Critical Insight: The Pattern Extraction Problem Persists

**Looking at extracted patterns themselves:**

**Pattern 1**: "We provide a sharp theory of scaling laws..."
- **Problem**: Describes what authors DID, not what mechanism EXISTS

**Pattern 2**: "Our analysis systematically dissects..."
- **Problem**: Meta-statement about the paper

**Pattern 3**: "Here we add a U(1) gauge theory..."
- **Problem**: Method description, not structural pattern

**Pattern 4**: "Finite-size scaling reveals a phase transition..."
- **Better**: At least mentions the phenomenon
- **Still weak**: Just says "phase transition exists", not mechanism

**None extract actual mechanisms:**
- ❌ "Component A negatively regulates B → oscillation"
- ❌ "Resource depletion causes exponential decline"
- ❌ "Threshold crossed → qualitative behavior change"

---

### Patterns That Predict Match Quality

From analyzing 20 clean matches + Session 31/32 findings:

#### What Correlates with BETTER Quality:

1. **Cross-domain pairs** (different fields):
   - Economics ↔ CS (game theory match)
   - Finance ↔ Materials Science (power law match)
   - Biology ↔ Math (phase transition match)
   - **Better than**: CS ↔ CS, Physics ↔ Physics

2. **Moderate similarity scores** (0.77-0.82):
   - Not too high (≥0.9 = technique clusters)
   - Not too low (<0.77 = noise)
   - **Sweet spot**: 0.77-0.85 range

3. **Specific mechanisms mentioned**:
   - "Phase transition at critical parameter"
   - "Nash equilibrium in strategic interaction"
   - **Better than**: Generic "scaling", "optimization", "complexity"

4. **No explicit technique names**:
   - Papers that don't say "GNN", "transformer", "renormalization group"
   - **Caveat**: May still use same framework implicitly

#### What Correlates with WORSE Quality:

1. **Same-domain pairs**:
   - Physics ↔ Physics (often same subfield)
   - CS ↔ CS (often same technique)
   - **Exception**: Very different subfields (e.g., finance ↔ materials)

2. **Ultra-high similarity** (≥0.9):
   - High term overlap → same technique
   - Session 31 found 0% precision

3. **Generic patterns**:
   - "Power law", "scaling", "complexity", "optimization"
   - Too ubiquitous to be interesting

4. **Explicit technique overlap**:
   - Both mention same technical terms
   - 50.6% of matches in 0.77-0.85 range

---

### The Fundamental Problem Remains

**Even "clean" matches fall into predictable categories:**

1. **Framework applications** (60%):
   - Phase transition theory → new domain
   - Game theory → LLM alignment
   - Gauge theory → quantum simulator
   - **Like GNN matches but for physics/econ frameworks**

2. **Generic patterns** (30%):
   - Power laws, scaling laws
   - Too common to be interesting

3. **Vague extraction** (10%):
   - "We present X"
   - "Our analysis shows Y"
   - Can't assess without reading papers

**Genuinely independent structural discoveries: ~0%**

The ideal ("Predator-prey oscillation ↔ Supply-demand oscillation") where both papers independently discover the same mechanism without shared frameworks/citations **has not been found**.

---

### Testable Hypotheses for Experiments 1-2

Based on this analysis:

#### Hypothesis 1: Cross-Domain Pairs Are Better
**Test**: Do economics ↔ biology matches have higher quality than cs ↔ cs?
**Prediction**: Yes, but still mostly framework applications
**Implication**: Target surprising domain pairs (ecology ↔ social networks, chemistry ↔ economics)

#### Hypothesis 2: Theoretical Papers Describe Mechanisms Better
**Test**: Do papers with "theory", "model", "mechanism" in title extract better?
**Prediction**: Yes - they describe HOW things work, not just WHAT was done
**Implication**: Target theoretical papers, avoid purely empirical

#### Hypothesis 3: LLM Can Extract Mechanisms Keywords Cannot
**Test**: Can LLM extract "A causes B → C" patterns from abstracts?
**Prediction**: Maybe - if mechanisms are described in abstract
**Alternative**: May need full paper (results/discussion sections)

#### Hypothesis 4: Some Fields Describe Mechanisms Better Than Others
**Test**: Which domains have best mechanism descriptions?
**Prediction**:
- **Best**: Ecology, epidemiology, economics, control theory (explicitly describe dynamics)
- **Medium**: Physics, chemistry (describe phenomena)
- **Worst**: Pure ML/CS (describe methods/results, not mechanisms)
**Implication**: Target mechanism-rich fields first

---

## Next Steps: Experiments 1 & 2

### Experiment 1: LLM-Based Mechanism Extraction

**Strategy based on Hypothesis 4:**
- Select 10-15 papers from **mechanism-rich fields**:
  - Ecology: 3 papers (predator-prey, resource competition, population dynamics)
  - Epidemiology: 2 papers (disease spread, SIR models)
  - Economics: 3 papers (market dynamics, game theory, equilibrium)
  - Control theory: 2 papers (feedback systems, stability)
  - Statistical physics: 3 papers (phase transitions, critical phenomena)
  - Complex systems: 2 papers (emergence, self-organization)

**Avoid**:
- Pure ML papers ("We present CNN for X")
- Purely empirical papers (no theory/mechanism)
- Technique application papers

**Test**:
- Prompt LLM to extract mechanism in domain-neutral language
- See if cross-domain matches emerge

### Experiment 2: Smarter Paper Selection

**Strategy**: Target specific mechanism types across domains

**Option A: Target "Feedback Loops"**
- Search for papers mentioning "feedback", "regulation", "homeostasis"
- Across: Biology (gene regulation), Economics (market feedback), Control theory, Ecology
- **Hypothesis**: Papers explicitly describing feedback will have matchable mechanisms

**Option B: Target "Phase Transitions"**
- But we know from analysis: often framework applications
- **Maybe skip this**

**Option C: Target "Oscillations / Cycles"**
- Biology: circadian rhythms, population cycles
- Economics: business cycles, boom-bust
- Physics: oscillators, periodic systems
- **Hypothesis**: Oscillation papers describe the cycle mechanism

**Recommended: Option C (Oscillations)** - specific enough to be interesting, common enough to find matches

---

## Preliminary Conclusions

1. **"Clean" matches (49.4%) are not "genuine" matches**
   - Most are framework applications
   - Or generic patterns (power laws)
   - Or vague extractions

2. **Best match found**: Game theory (Commons → LLM alignment)
   - Cross-domain (econ ↔ CS)
   - Specific framework (Nash equilibrium)
   - Non-obvious application
   - **BUT**: Still framework transfer, not independent discovery

3. **Pattern extraction remains broken**
   - Extracts "We present X" not "X causes Y"
   - LLM extraction might help, but needs testing

4. **Smarter paper selection is crucial**
   - Target mechanism-rich fields (ecology, econ, control)
   - Avoid pure ML technique papers
   - Focus on specific mechanism types (oscillations, feedback)

5. **The vision (independent discoveries) may be unachievable**
   - Papers that discover similar mechanisms often DO share frameworks
   - Statistical physics → many domains
   - Game theory → economics + CS
   - **Question**: Do truly independent discoveries exist in academic literature?

---

**Status**: Experiment 3 complete. Moving to Experiments 1-2.

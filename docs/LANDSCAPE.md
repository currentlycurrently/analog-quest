# Analog Quest — Prior-Art & Competitive Landscape

**Archived:** 2026-07-05
**Provenance:** AI deep-research scan commissioned by the admin in response to
the project's prior-art positioning statement. The scan below is preserved
verbatim. **Treat every citation as unverified until it appears in the
Verification appendix at the bottom of this file** — this project's rigor
discipline (see HANDOFF.md) applies to prior-art claims exactly as it applies
to match claims.

**Why this document exists:** HANDOFF.md's landscape note (2026-04) said a day
of targeted prior-art search would be worthwhile before further investment.
This is that search. Its headline conclusions:

1. The project's four-part combination — notation-independent extraction of a
   paper's *core mathematical model*, cross-*discipline* structural matching at
   arXiv scale, tiered human review, and a published curated catalog — is
   unoccupied as of mid-2026.
2. Two 2025 preprints are circling parts of it: Romiti (arXiv:2508.05724,
   physics-only, equation-level, ~400 curated equations) and The Discovery
   Engine (arXiv:2505.17500, literature-scale but concept-schema unit, no
   catalog). Both must be cited in any public write-up.
3. The durable differentiation is the *delivered human-reviewed catalog* — the
   operational/social half of the project, not the engineering half.
4. The window is open but closing: extraction infrastructure is commoditizing
   (arXiv MathML, MathBridge, theorem search at scale) and any well-resourced
   "AI Scientist" effort could absorb the niche.

---

## The scan (verbatim, 2026-07-05)

### TL;DR
- **No mature or emerging effort is running analog.quest's exact four-part combination** — notation-independent extraction of each paper's *core mathematical model*, cross-*discipline* structural matching at arXiv scale, tiered human review, and a *published curated catalog* of isomorphisms. The gap is real.
- The **two closest efforts are both 2025 single-/small-team preprints**: Massimiliano Romiti's graph-based physics framework (arXiv:2508.05724) does equation-level cross-domain analogy detection but only within physics, on a curated set of 400 advanced equations (from 659), with no catalog and only *proposed* human review; and "The Discovery Engine" (arXiv:2505.17500) does literature-scale structural-isomorphism analogy but on a concept schema, not the equation/model, and ships no catalog.
- The requester's four adjacent threads are correctly characterized; the biggest prior work they should cite that they did NOT list are (a) the **analogy-mining lineage of Tom Hope, Joel Chan, Aniket Kittur, and Dafna Shahaf** (weak structural representations at scale), (b) **Romiti 2508.05724** and **The Discovery Engine**, and (c) **applied category theory (Baez, Fong, Spivak)** as the formal grammar of cross-domain isomorphism.

### Key Findings

1. **The exact combination is unoccupied white space.** Across academic venues (arXiv, ACL, CLEF/NTCIR, applied category theory) and informal sources (GitHub, Hacker News, blogs), no single project extracts a notation-independent structural description of each paper's *core mathematical model*, matches those across disciplines at arXiv scale, runs tiered human review, and publishes a curated catalog. Prior art is partial and fragmented across four or five communities that do not talk to each other.

2. **Math formula search (thread a) is mature but answers a different question.** State of the art is dense/structural formula retrieval (ARQMath at CLEF; Approach0/Tangent-CFT/MathBERT; zbMATH's MathWebSearch). These retrieve "where else does this expression appear?" They have no notion of whether a match is a meaningful cross-domain analogy vs. shared textbook boilerplate, and they operate on formulas, not on the paper's underlying model. Characterization confirmed.

3. **Structure-mapping (thread b) has NOT been scaled to the mathematical content of the literature.** Gentner's SMT and the SME (Falkenhainer/Forbus/Gentner) remain the gold standard for what a "good analogy" is, and there are LLM-era descendants (FAME, semantic structure-mapping benchmarks, SCAR). But scaled analogy work in NLP (Hope/Chan/Kittur/Shahaf) deliberately abandons full structural representations in favor of "weaker structural representations" (purpose/mechanism vectors) over text — not equations. Characterization confirmed.

4. **LLM-driven discovery (thread c) targets data or abstract-level text, not the model.** LLM-SR and its successors do symbolic regression from *data*; literature-based discovery (Swanson → SciMON, HypER, AGATHA) links *concepts/terms* from text. None uses the mathematical *model* of a paper as the unit of comparison. Characterization confirmed.

5. **Formal math libraries (thread d) cover a tiny, formalized slice and reach essentially no applied science.** Lean/mathlib search (Moogle, LeanSearch, LeanExplore, Loogle, premise selection) and the new "Semantic Search over 9 Million Mathematical Theorems" find whether a statement already exists, but within formalized/pure math. Characterization confirmed; there is a nascent bridge (autoformalization of physics) worth watching.

6. **The richest missed vein is applied category theory**, which is *explicitly* a catalog of cross-domain structural correspondences (Baez–Stay "Rosetta Stone"; Baez/Fong/Spivak network theory; AlgebraicJulia). It is human-authored, not corpus-scale or automated — but it is the natural formal grammar for what analog.quest wants to catalog.

### Details

#### (a) Mathematical formula search / Math Information Retrieval (MIR)
**Key people/venues:** Richard Zanibbi, Behrooz Mansouri, Douglas Oard, Wei Zhong (RIT/Waterloo, ARQMath at CLEF); Michael Kohlhase (MathWebSearch); zbMATH Open. **State of the art (2023–2026):** the ARQMath labs (CLEF 2020–2022) standardized math-aware retrieval over Math Stack Exchange with a formula-retrieval subtask; leading systems combine structural matching (Tangent-CFT/Tangent-S operator trees, Approach0) with dense semantic retrieval (Zhong/Xie/Lin; MathBERT). zbMATH Open's formula search uses MathWebSearch — a content-based engine over MathML using substitution-tree indexing (inherited from automated theorem proving). Corpus-scale equation extraction exists: per Jung et al., MathBridge (arXiv:2408.07081), "we extracted approximately 48 million formulas from arXiv papers and 1 million formulas from textbooks," yielding ~23 million LaTeX–spoken pairs; a separate GNN pretraining paper indexed ~29 million MathML equations across ~760k papers; and arXiv's own LaTeXML/MathML 4 HTML pipeline is maturing.

**Why it is not analog.quest:** these systems retrieve *formulas* by query, optimized for exact/near matches and low latency. They enumerate *occurrences*, not cross-domain *structural coincidences*, and have no mechanism to judge analogy quality (meaningful isomorphism vs. boilerplate like a generic Gaussian or a Laplacian). The unit is the expression, not the paper's model.

#### (b) Analogy and structure-mapping research
**Key people:** Dedre Gentner (SMT), Kenneth Forbus (SME, MAC/FAC, cross-domain analogies for learning domain theories), Keith Holyoak & Paul Thagard (ACME). **Recent (2023–2026):** LLM-era work tests whether LLMs do structure-mapping (Webb et al. emergent analogy; Lewis & Mitchell and Musker et al. critiques showing brittleness under distractors; the SCAR "Scientific Analogical Reasoning" benchmark showing GPT-4 picks structurally incorrect completions); FAME combines LLM relation extraction with beam-search mapping; recent work adds LLM-derived abstractions to structure-mapping for narratives. **The scaled branch:** Hope, Chan, Kittur, and Shahaf's analogy-mining line ("Accelerating Innovation Through Analogy Mining," KDD 2017; "Scaling up analogical innovation with crowds and AI," PNAS 2019; the analogical search engine / SOLVENT; and 2022–2025 fine-grained functional-aspect work) explicitly gives up on full predicate-calculus structure because it is "extremely heavyweight," and instead learns *purpose/mechanism* vectors from text at scale.

**Why it is not analog.quest:** classical SME operates on hand-built predicate representations and small domain pairs; the scaled NLP work operates on abstract text (purpose/mechanism), not the mathematical model, and produces retrieval, not a curated isomorphism catalog. No one has run SME-style structural matching over the *mathematical content* of the literature at corpus scale.

#### (c) LLM-driven scientific discovery
**Symbolic/equation discovery from data:** LLM-SR (Shojaee et al., ICLR 2025 Oral) represents equations as programs and searches with LLM+evolution; successors/relatives include LaSR (concept libraries), SGA, DrSR, ICSR, and the LLM-SRBench benchmark. These discover equations from *data*, not from the model of a paper. **Literature-based discovery (LBD):** the Swanson ABC tradition → AGATHA, and LLM-era systems SciMON (ACL 2024), HypER, KG-CoI, ResearchAgent, plus tool-style assistants (Elicit, Consensus, PaperQA). These link *concepts/terms* extracted from text/abstracts. **AI-Scientist systems:** Sakana AI's "The AI Scientist" automates end-to-end research within narrow ML templates; it does not extract paper equations as a comparison unit or build an isomorphism catalog.

**Why it is not analog.quest:** the entire class operates on experimental data (symbolic regression) or on abstract-level text (LBD/idea generation). None targets the notation-independent mathematical *model* of a paper as the unit of cross-domain comparison.

#### (d) Formal mathematics libraries
**Key tools:** Lean/mathlib with semantic search engines Moogle (Morph Labs), LeanSearch and LeanSearch v2 (PKU BICMR/IQuest), LeanExplore, Loogle (Joachim Breitner); premise selection (LeanDojo/ReProver, Lean Copilot, machine-learned premise selection); and Alexander et al., "Semantic Search over 9 Million Mathematical Theorems" (arXiv:2602.05216, 5 Feb 2026; theoremsearch.com), which builds "a unified corpus of 9.2 million theorem statements extracted from arXiv and seven other sources" and represents each with a natural-language description, achieving 45% Hit@20 vs. 27% for Gemini 3 Pro at theorem-level retrieval. Its motivation is dedup/prior-art: per the paper, "A study of over 14,000 withdrawn arXiv preprints found that 2.5% were retracted because the authors' results already appeared in prior literature (Rao et al., 2024)." **Bridge to science:** Meadows & Freitas ("Similarity-Based Equational Inference in Physics," Phys. Rev. Research 2021) and follow-ups on LLM physics inference, plus the 2026 "FormalScience" work on human-in-the-loop autoformalization of physics in Lean, are early attempts to reach applied science.

**Why it is not analog.quest:** formal libraries can detect when two *formalized* statements coincide (dedup, "did someone already prove this"), but only over the tiny fraction of mathematics that is formalized, and essentially no applied-science modeling literature. Cross-domain isomorphism detection is not a goal, and coverage of applied science is near-zero.

#### Additional adjacent areas (not on the original list)

- **Applied category theory (strongest missed relative).** Baez & Stay's "Physics, Topology, Logic and Computation: A Rosetta Stone" (2009/2011) is literally a table of cross-domain structural correspondences unified by closed symmetric monoidal categories. Baez, Fong, Pollard, and Spivak's network-theory program (compositional frameworks for Markov processes, reaction networks, passive linear circuits; bond graphs/signal-flow diagrams) and the AlgebraicJulia ecosystem (Catlab.jl) build the machinery to identify when models from different fields are the same structure. This is the *formal grammar* for cross-domain isomorphism — but it is human-authored, hand-curated, and neither corpus-scale nor automated over the literature. analog.quest could treat category theory as its target representation.

- **Cross-domain / scientific knowledge graphs.** Coreference-based cross-domain research KGs; equation-variable KGs (MathAlign linking identifiers to descriptions, SemEval-2022 Symlink); the 2026 "Mathematical Knowledge Graph-Driven Framework" retrieving equation-variable associations. These link concepts/variables, not whole-model isomorphisms across fields.

- **Cross-domain analogy retrieval engines.** The "Analogy Search Engine" (arXiv:1812.06974, 2018) does semantic analogy search over 2000 AI-paper abstracts; Kang et al.'s "Augmenting Scientific Creativity with Retrieval across Knowledge Domains." Text/abstract-level, small scale, no catalog, no equations.

- **Automated metaphor/analogy mining and cognitive-plausibility work** exists (evolutionary cross-domain analogy generation; minimal-cognitive-grid ranking of analogy models) but is not tied to mathematical models of papers.

- **Existing hand-found catalogs of cross-domain math isomorphisms.** These are the intellectual precedent analog.quest would systematize: Black–Scholes ↔ heat/diffusion equation (well documented, standard change of variables); Ising model ↔ Hopfield network; Lotka–Volterra across ecology/economics/chemistry; the harmonic oscillator everywhere; mechanical–electrical analogies (Maxwell's method of physical analogy; electromagnetics ↔ hydrodynamics). They exist as scattered papers, textbook remarks, Wikipedia list-style pages, and blog posts — not as a unified, human-reviewed, corpus-derived catalog.

- **The two nearest whole-system efforts (2025).**
  - **Romiti, arXiv:2508.05724v2 (14 Aug 2025), "A Graph-Based Framework for Exploring Mathematical Patterns in Physics: A Proof of Concept," independent researcher (Massimiliano Romiti).** Starting from 659 equations, it focuses on 400 advanced physics equations after resolving "notational polysemy affecting 213 equations," represents equations/concepts as a weighted knowledge graph, and trains a Graph Attention Network that "achieved 97.4% AUC in link prediction," reporting that ~70% of predicted connections are cross-domain within physics. It explicitly surfaces "mathematical isomorphisms" (e.g., radioactive decay ↔ inductor EMF) at the "syntactic level." But it is physics-only, ~400 equations (not arXiv-scale, not full papers), a hypothesis generator not a curated catalog, and human review is only *proposed* (a future "graph generation → AI screening → expert validation" pipeline; code at github.com/kingelanci/graphysics). This is the single closest sibling on the equation-level cross-domain matching idea.
  - **The Discovery Engine, arXiv:2505.17500 (submitted 23 May 2025), Baulin, Cook, Friedman, Lumiruusu, Pashea, Rahman & Waldeck (Active Inference Institute, Crescent City, CA / Universitat Rovira i Virgili).** It LLM-distills papers into structured "knowledge artifacts" (instances of a "Universal Concept Schema") encoded into "the Conceptual Nexus Tensor (T_CNM)," and describes an "Analogy Agent" using "structural isomorphism… inspired by category-theoretic notions of functors." Strong on notation-independent structured extraction + cross-domain structural-isomorphism analogy at literature scale — but the unit is a concept/method schema, not the paper's equation/mathematical model; it ships no published isomorphism catalog; and human review is an agent-researcher interaction, not a tiered publication pipeline. Several capabilities are described in future/conditional tense ("could propose").

- **"analog.quest" itself has no discoverable public footprint** as a science/isomorphism tool (searches surfaced only unrelated hits). It appears to be brand-new or unindexed.

### Recommendations

**Stage 1 — Claim the gap and position precisely (now).** Proceed; the four-part combination is genuinely unoccupied. In any writeup, position analog.quest against the *closest* efforts, not the easy strawmen: explicitly distinguish from (i) Romiti 2508.05724 (you go cross-*discipline* and to full papers at arXiv scale, with an actual delivered catalog and real tiered human review), and (ii) The Discovery Engine (your unit is the notation-independent *mathematical model*, and your output is a curated, human-reviewed catalog). Cite both prominently — a reviewer will know them.

**Stage 2 — Adopt an explicit structural representation and analogy-quality rubric (design phase).** The central technical risk is exactly what formula search cannot do: telling a meaningful isomorphism from shared boilerplate. Borrow the theory you'll be judged against: Gentner's *systematicity* principle and SME's constraints for what makes an analogy "good," and applied category theory (monoidal categories, functors, decorated/structured cospans) as the target normal form for "same structure." Make "notation-independent structural description" concrete by mapping each paper's model to a typed relational/graph or categorical signature rather than to token-level formula trees.

**Stage 3 — Reuse existing extraction infrastructure; don't rebuild it.** For corpus-scale ingestion, build on arXiv's LaTeXML/MathML 4 HTML pipeline and prior extraction work (MathBridge's ~48M formulas; the ~29M-MathML GNN corpus; MathAlign/Symlink for identifier→description linking). This lets you spend your budget on the *model-abstraction and cross-domain-matching* layer, which is the novel part.

**Stage 4 — Seed and validate the catalog against known isomorphisms.** Use the hand-found canon (Black–Scholes↔heat, Ising↔Hopfield, Lotka–Volterra, harmonic oscillator, mechanical–electrical) as a gold-standard recall test: any pipeline that fails to rediscover these is not ready. Then measure precision on novel candidates via the tiered human review.

**Benchmarks / thresholds that would change the plan:**
- If **The Discovery Engine or a successor ships a public, human-reviewed catalog keyed on the mathematical model** (not concept schema), the differentiation narrows sharply — monitor arXiv:2505.17500 and its benchmarking follow-up (arXiv:2507.00964) and Active Inference Institute output.
- If **Romiti's framework moves from physics-only to cross-discipline arXiv scale with a curated catalog**, that is direct competition — watch the github.com/kingelanci/graphysics repo.
- If a **theoremsearch.com-style team pivots from theorem dedup to cross-domain applied-science model matching**, the extraction moat erodes.
- If a **well-resourced "AI Scientist" lab (Sakana, or a frontier lab) adds equation-model cross-domain analogy** to its pipeline, expect fast movement.

### Caveats
- Both nearest competitors (Romiti 2508.05724; The Discovery Engine 2505.17500) are **un-peer-reviewed 2025 preprints** with self-acknowledged limitations; their headline claims (e.g., Romiti's 97.4% AUC and "discovery"/"isomorphism" language; the Discovery Engine's conditional "could propose" capabilities) should be treated as preliminary, not delivered products.
- Absence of evidence is not proof: a **stealth startup or unpublished internal effort** could exist. The negative result is strong across public academic and informal channels, but cannot be absolute.
- The **applied-category-theory community** is philosophically closest to the "catalog of cross-domain isomorphisms" goal and could, in principle, automate and scale its hand-curated correspondences faster than expected; it is the most likely source of a serious future entrant.
- "analog.quest" not appearing publicly is consistent with a new project, but the domain's current contents could not be independently confirmed.
- Formula-extraction quality at arXiv scale remains imperfect (custom LaTeX macros, PDF-only older papers, notation polysemy); this is a real execution risk, corroborated by every extraction paper reviewed.

### Direct Verdict
1. **Is anyone running the exact combination?** No. No mature or emerging effort combines notation-independent structural *model* extraction + cross-discipline matching at arXiv scale + tiered human review + a published catalog.
2. **Closest existing efforts and distance:** (a) Romiti's graph-based physics framework (arXiv:2508.05724) — closest on the equation-level cross-domain-analogy idea, but physics-only, ~400 curated equations (not arXiv-scale, not whole papers), no catalog, human review only proposed. (b) The Discovery Engine (arXiv:2505.17500) — closest on literature-scale structured-extraction + structural-isomorphism analogy, but its unit is a concept schema (not the equation/model), with no delivered catalog and no tiered review pipeline. Both are ~1–3 of 4 criteria away.
3. **Prior work to cite that may have been missed:** the Hope/Chan/Kittur/Shahaf analogy-mining lineage; the Analogy Search Engine (arXiv:1812.06974) and Kang et al. cross-domain retrieval; Meadows & Freitas equational inference in physics; MathAlign/Symlink and equation-embedding/knowledge-graph work; applied category theory (Baez–Stay Rosetta Stone; Baez/Fong/Spivak network theory; AlgebraicJulia); and the two 2025 nearest-neighbors above.
4. **2024–2026 developments suggesting the gap may close:** yes, momentum is building — Romiti 2508.05724 and The Discovery Engine 2505.17500 (both 2025) are clearly moving toward pieces of this; theorem-search-at-scale (arXiv:2602.05216, 2026) and arXiv's maturing MathML pipeline lower the extraction barrier; and autoformalization-of-science efforts are bridging formal libraries to applied fields. None yet targets the full combination, so the window is open but not indefinitely.

---

## Verification appendix

*(Appended as claims are checked. Anything not listed here is still unverified.)*

### Romiti, arXiv:2508.05724 — verified 2026-07-05

Checked against the arXiv abs page, the v2 HTML full text, and the GitHub
repo (github.com/kingelanci/graphysics). **All scan claims CONFIRMED**, with
nuances:

- 659 equations → 657 after semantic cleaning → 400 after excluding
  elementary mechanics. Source is "a curated database of 659 physical laws
  compiled from academic sources" — hand-curated JSON, **not arXiv-mined**.
- Notational polysemy across 213 equations: confirmed verbatim.
- GAT link prediction "test AUC of 0.9742±0.0018" across five runs;
  best classical baseline 0.9487, so the GNN's marginal lift is modest.
- ~70% of predicted connections cross-domain, where "domain" = physics
  *subfield*. Physics-only confirmed; cross-discipline is only future work
  ("generalizing the framework beyond physics to other formal sciences").
- Self-described as "a hypothesis generation engine, not a discovery
  validation system." Expert review only proposed, never performed.
- Radioactive decay ↔ inductor EMF confirmed as the flagship "mathematical
  isomorphism" example (both first-order linear ODEs with exponential
  solutions — note this is exactly the "textbook object" class analog.quest's
  trivia filter exists to catch).
- **Activity signal: dormant.** v1 2025-08-07, v2 2025-08-14, nothing since.
  Repo has 0 stars/forks, no visible follow-up or citations as of 2026-07.
- Competitor-risk note: its core primitive (SymPy AST parsing + syntactic
  isomorphism) is the same one analog.quest used, MIT-licensed with data and
  weights published. It also does things we don't (link prediction to
  *propose* connections, redundancy/error detection). But at ~400 curated
  equations, physics-only, single dormant author, it is a conceptual
  neighbor, not an operational competitor.

### The Discovery Engine, arXiv:2505.17500 — verified 2026-07-05

Checked against the arXiv abs page, v1 HTML full text, and the public repo
(github.com/ActiveInferenceInstitute/Research-Discovery-Engine). **Scan
claims 1–7 CONFIRMED; claim 8 REFUTED:**

- LLM distillation into "knowledge artifacts" / "Universal Concept Schema
  (UCS)" / "Conceptual Nexus Tensor (T_CNM)": confirmed verbatim.
- The category-theory framing is hedged even in-text: "*potentially*
  inspired by category-theoretic notions of functors."
- **No equation or mathematical-model extraction anywhere**, including
  appendices — the closest is parameter fields with values and units. The
  unit really is a concept/method schema.
- No catalog of validated analogies; no corpus sizes; no evaluation
  metrics; the Analogy Agent's capabilities are described in conditional
  tense throughout ("could propose", "would provide").
- Human role is interactive template refinement, not a tiered review gate.
- **REFUTED: arXiv:2507.00964 ("Benchmarking the Discovery Engine") is a
  name collision, not a companion paper** — Leap Laboratories (London),
  zero author overlap, a different system benchmarked on five ML datasets.
  Do not cite it as related to Baulin et al. The scan's "monitor the
  benchmarking follow-up" recommendation is void.
- Activity signal: v1 only, no revision in ~13 months; repo ~6 stars; two
  Vercel demo deployments (knowledge-exploration UI, not an analogy
  catalog). One citing paper surfaced (SciResearcher, arXiv:2605.01489).

### Net effect on the scan's conclusions

The scan's Direct Verdict stands and is, if anything, **strengthened**: both
nearest neighbors are effectively dormant vision/proof-of-concept artifacts
with no delivered catalog, no cross-discipline scale, and no human-review
pipeline. The four-part gap remains unoccupied. The one correction is the
2507.00964 name collision above. The "window is open but closing" framing
should be read as: closing through *commoditizing infrastructure* (theorem
search, arXiv MathML, frontier-lab AI-scientist efforts), not through these
two specific projects.

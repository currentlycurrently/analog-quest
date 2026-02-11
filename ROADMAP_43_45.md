# Roadmap: Sessions 43-45 - Scale to Launch Quality

**Current state**: 30 discoveries from 2,021 papers (Session 38)
**Problem**: Not strong enough for public launch
**Goal**: Scale to thousands more papers → curate 12 excellent discoveries → launch

---

## Session 43: Expansion (6-8 hours)

### Objective
Extract mechanisms from 3,000-5,000 new papers to find 20-30 new excellent discoveries.

### Part 1: Strategic Paper Selection (1 hour)
- **Target domains**: Focus on Tier 1 pairs from GROWTH_STRATEGY.md
  - cs ↔ physics (100% precision in Session 38!)
  - econ ↔ physics (58% precision)
  - cs ↔ econ (40% precision)
- **Selection strategy**: Keyword-based filtering for mechanism-rich papers
  - Session 37 validated: 50% hit rate vs 22.5% random (2.2x improvement)
- **Target**: Select 200-300 mechanism-rich papers

### Part 2: LLM Mechanism Extraction (3-4 hours)
- **Method**: Manual LLM-guided extraction (Session 37 approach)
  - Domain-neutral language
  - Structural patterns, not domain-specific terminology
  - Causal mechanisms, not methods/techniques
- **Target**: Extract 60-100 new mechanisms
- **Combined total**: 60-100 new + 54 existing = 114-154 mechanisms

### Part 3: Semantic Embedding & Matching (1 hour)
- **Embedding**: 384-dim vectors (sentence-transformers/all-MiniLM-L6-v2)
- **Threshold**: ≥0.35 (Session 37 validated - captures diverse-domain matches)
- **Expected candidates**: 250-400 pairs
- **Filtering**: Cross-domain only, remove duplicates

### Part 4: Manual Curation (2-3 hours)
- **Review all candidates**: Rate as excellent/good/weak/false
- **Expected precision**: ~40-50% (based on Session 36-38 results)
- **Target output**: 20-30 new verified discoveries
  - 5-10 excellent
  - 15-20 good

### Deliverables
- `examples/session43_new_mechanisms.json` - 60-100 new mechanisms
- `examples/session43_candidates.json` - 250-400 candidates for review
- `examples/session43_verified.json` - 20-30 new verified discoveries
- `SESSION43_RESULTS.md` - Summary and analysis

---

## Session 44: Curation & Editorial Writing (6-8 hours)

### Objective
Select top 12 discoveries from all verified matches (Session 38 + Session 43) and write editorial pieces.

### Part 1: Discovery Selection (1 hour)
- **Pool**: 30 (Session 38) + 20-30 (Session 43) = 50-60 total
- **Selection criteria**:
  1. Rating: Prioritize "excellent"
  2. Domain diversity: Cover multiple domain pairs
  3. Mechanism diversity: Different pattern types (cooperation, networks, feedback, etc.)
  4. Verifiability: At least some with arXiv links or clear field context
  5. Accessibility: Can be explained in human-facing language

- **Output**: 12 best discoveries
  - Target: 8-10 excellent, 2-4 good
  - Domain spread: econ↔q-bio, cs↔physics, physics↔q-bio, etc.

### Part 2: Editorial Writing (4-6 hours)
- **Template**: Use EDITORIAL_TEMPLATE_V2.md
- **Target**: 450-600 words per piece
- **Structure**: Title + subtitle + intro + 3 paragraphs + evidence note
- **Process**: Write 12 pieces at ~25-30 min each
- **Review**: Read through all 12, ensure consistency

### Part 3: Data Integration (1 hour)
- **Create**: `app/data/discoveries_v2.json` (12 discoveries with editorial layer)
- **Update**: Frontend to display editorial content
  - New DiscoveryCard with editorial titles
  - New detail page layout for editorial body
  - Tags for filtering/browsing

### Deliverables
- 12 complete editorial pieces
- Updated data structure with editorial layer
- Frontend displaying new editorial format

---

## Session 45: Final Polish & Launch Prep (4-6 hours)

### Objective
Final quality review, testing, and launch preparation.

### Part 1: Quality Assurance (2 hours)
- **Read all 12 editorials** as a first-time visitor would
- **Check consistency**: Tone, length, structure
- **Verify links**: All source links working or explained
- **Test filtering**: Tags work correctly
- **Mobile test**: Responsive on phone

### Part 2: Final Page Redesigns (2 hours)
- **Discoveries page**: Simple grid of 12 cards
- **Methodology page**: Update with Session 43-44 data
- **About page**: Update story (6 weeks → final state)

### Part 3: Launch Checklist (1-2 hours)
- [ ] All 12 editorials proofread
- [ ] All pages tested (desktop + mobile)
- [ ] Build succeeds with 0 errors
- [ ] SEO metadata updated (12 discoveries, not 30)
- [ ] Open Graph images created
- [ ] Analytics configured
- [ ] Backup created
- [ ] Git committed and pushed
- [ ] Deployed to Vercel
- [ ] Custom domain working
- [ ] SSL certificate valid

### Deliverables
- analog.quest v1 ready for public launch
- 12 high-quality discoveries with editorial pieces
- Polished, trustworthy design
- Full documentation

---

## Success Metrics

### Quantitative
- **12 discoveries** (down from 30 - quality > quantity)
- **450-600 words** per editorial (readable, not overwhelming)
- **8-10 excellent**, 2-4 good (high quality bar)
- **5+ domain pairs** represented (diversity)
- **0 TypeScript errors**, clean build

### Qualitative
- **Would I share this?** Each discovery passes the "would I post this to Twitter" test
- **Trustworthy design**: Warm, restrained, consistent
- **Clear value prop**: Visitor understands what Analog Quest does in 30 seconds
- **Compelling content**: At least 3 discoveries make you go "wow, that's cool"

---

## Risk Mitigation

### Risk 1: Session 43 doesn't yield 20-30 new discoveries
**Mitigation**: Lower threshold to ≥0.30, or process more papers (500-1000)
**Fallback**: Select best 12 from existing Session 38 pool (30 discoveries)

### Risk 2: Editorial writing takes too long
**Mitigation**: Start with 6 pieces (not 12), validate approach
**Fallback**: Use shortened template (~300-400 words instead of 450-600)

### Risk 3: Design redesign reveals new issues
**Mitigation**: Get Chuck's feedback on Session 42 design before Session 44
**Fallback**: Iterate in Session 45 (buffer time built in)

---

## Timeline

- **Session 42**: Feb 11 - Design foundation + editorial structure ✓
- **Session 43**: Feb 12-13 - Expansion (3,000-5,000 papers → 20-30 discoveries)
- **Session 44**: Feb 14-15 - Curation + editorial writing (12 final pieces)
- **Session 45**: Feb 16-17 - Final polish + launch prep
- **Launch**: Feb 18 - Public v1 launch

**Total**: 5 sessions, ~20-30 hours of work

---

## Post-Launch (Session 46+)

### Immediate (Week 1)
- Monitor analytics
- Gather user feedback
- Fix critical bugs

### Growth Cycle (Every 2-3 weeks)
- Process 2,000-3,000 new papers
- Extract 40-60 mechanisms
- Generate 150-250 candidates
- Curate 10-15 new discoveries
- Write 5-8 new editorials
- Add to site (12 → 20 → 30 → 50 over 3 months)

### Long-term Vision (6 months)
- 100-150 high-quality discoveries
- Researcher-friendly UI/UX
- Community submissions?
- Academic validation?
- Published paper on methodology?

---

## Key Principles

1. **Quality over quantity**: 12 excellent > 30 mediocre
2. **Human-facing**: Editorial layer, not raw technical matches
3. **Sustainable**: Repeatable expansion cycles
4. **Honest**: Limitations clearly stated
5. **Trustworthy**: Design and content both matter

---

**Last Updated**: Session 42 (2026-02-11)

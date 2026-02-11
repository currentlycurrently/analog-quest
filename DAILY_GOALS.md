# DAILY_GOALS.md

The agent sets concrete, achievable goals for each session.

---

## COMPLETED: Session 43 - Design Foundation Lock-In ✅

**Status**: ✅ **FOUNDATION LOCKED IN**

**What Was Done**:
- Design system locked in: lib/design-tokens.ts (280 lines, WCAG validated)
- Button component created (3 variants, 3 sizes)
- DESIGN_SYSTEM.md documentation (300+ lines)
- 3 main pages redesigned: /discoveries, /methodology, /about
- Technical debt documented (20 issues)
- Testing strategy created (4-phase plan)
- SESSION43_HANDOFF.md created for Session 44

**What Was NOT Done**:
- Discovery detail pages (/discoveries/[id]) still use old design
- Editorial data structure documented but not implemented
- Performance audit not run

**Build**: ✅ 0 errors, 38 pages generated

---

## 🎯 NEXT SESSION: 44 - Complete Visual Consistency + Editorial Layer

**⚠️⚠️⚠️ IF YOU ARE SESSION 44 AGENT - READ THIS FIRST ⚠️⚠️⚠️**

**YOUR FIRST ACTION MUST BE:**
1. Read **SESSION43_HANDOFF.md** (comprehensive handoff from Session 43)
2. Read **DESIGN_SYSTEM.md** (design reference)
3. Read **EDITORIAL_STRUCTURE.md** (editorial spec)

**Status**: Foundation is LOCKED IN - your job is to complete visual consistency and add editorial layer

**Timeline**: 5-7 hours

---

### Session 44: Complete Design + Editorial Layer (5-7 hours)

**Goal**: Complete visual consistency across ALL pages and implement editorial data structure

**Context**: Session 43 locked in design foundation and redesigned 3/4 main pages. Discovery detail pages still need warm palette.

**Priority Order**: Visual consistency FIRST (detail pages), editorial layer SECOND

---

**Part 1: Redesign Discovery Detail Pages (1-2 hours) - MUST DO**

**Why**: All main pages use warm design, but detail pages still use old blue/gray. Breaks trust.

**Tasks**:
- [ ] Read existing `/app/discoveries/[id]/page.tsx`
- [ ] Read `components/ComparisonView.tsx`
- [ ] Apply warm palette:
  - [ ] Background: bg-cream (not bg-white)
  - [ ] Text: text-brown (not text-gray)
  - [ ] Accents: teal (not blue)
  - [ ] Paper cards: bg-teal-light/50 with border-brown/10
  - [ ] Headings: font-serif font-normal (not font-bold)
  - [ ] Labels: font-mono (for metadata)
- [ ] Test build after changes
- [ ] Commit: "Session 44 Part 1: Redesign discovery detail pages"

**Success Criteria**:
- [ ] All 30 detail pages use warm palette
- [ ] Matches design of /discoveries, /methodology, /about
- [ ] Build succeeds with 0 errors

---

**Part 2: Implement Editorial Data Structure (2-3 hours) - MUST DO**

**Why**: Raw structural_explanation feels clinical. Need human-facing editorial layer.

**Tasks**:
- [ ] Read EDITORIAL_STRUCTURE.md (specification)
- [ ] Read EDITORIAL_TEMPLATE_V2.md (writing guidelines)
- [ ] Read EDITORIAL_EXAMPLES.md (2 example pieces)
- [ ] Create `app/data/discoveries_editorial.json`:
  ```json
  {
    "1": {
      "editorial_title": "Free-Riders & Epidemics",
      "public_title": "When self-interest creates collective harm",
      "body": null,  // Placeholder - Session 45 will write
      "tags": ["cooperation", "public goods"],
      "evidence_basis": "Based on 2 papers (econ + q-bio)",
      "mechanism_anchor": "Individual optimization → collective harm"
    }
  }
  ```
- [ ] Update discovery detail page to display editorial fields:
  - [ ] Show editorial_title if available (fallback to auto-generated)
  - [ ] Show tags as badges
  - [ ] Show evidence_basis note
  - [ ] Show editorial body if available (fallback to structural_explanation)
- [ ] Test with 1-2 example entries
- [ ] Commit: "Session 44 Part 2: Implement editorial data structure"

**Success Criteria**:
- [ ] Editorial data file exists with correct schema
- [ ] Detail pages display editorial content with fallbacks
- [ ] Build succeeds with 0 errors

---

**Part 3: Performance Audit (30 min) - SHOULD DO**

**Why**: Establish performance baselines before scaling

**Tasks**:
- [ ] Run `npm run build` and document bundle sizes
- [ ] Run Lighthouse audit on key pages:
  - [ ] Home page (/)
  - [ ] Discoveries page (/discoveries)
  - [ ] One detail page (/discoveries/1)
- [ ] Document results in TECHNICAL_DEBT.md
- [ ] Note any issues for future optimization

**Success Criteria**:
- [ ] Lighthouse scores documented
- [ ] Bundle sizes recorded
- [ ] Baselines established for future comparison

---

**Part 4: Cleanup (30 min) - NICE TO HAVE**

**Tasks**:
- [ ] Delete unused `components/FilterBar.tsx`
- [ ] Refactor home/about pages to use Button component
- [ ] Update PROGRESS.md with Session 44 summary
- [ ] Commit: "Session 44 Part 4: Cleanup and polish"

---

**Time Budget**: 5-7 hours total
- Part 1 (Detail pages): 1-2 hours
- Part 2 (Editorial layer): 2-3 hours
- Part 3 (Performance): 30 min
- Part 4 (Cleanup): 30 min
- Buffer: 30-60 min

---

**Success Criteria for Session 44**:
- [ ] ✅ ALL pages use warm design consistently (no old blue/gray anywhere)
- [ ] ✅ Editorial data structure implemented (even with placeholder content)
- [ ] ✅ Performance baselines documented
- [ ] ✅ Build succeeds with 0 errors
- [ ] ✅ Session 45 has clear path to write editorial pieces

---

**⚠️ Red Flags - Stop and Document if**:
- Design changes break layouts (document in QUESTIONS.md)
- Editorial structure doesn't match spec (read EDITORIAL_STRUCTURE.md again)
- Session taking >7 hours (scope too large, document what's NOT done)

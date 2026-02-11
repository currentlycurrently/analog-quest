# Technical Debt & Known Issues

**Last Updated**: Session 42 (2026-02-11)
**Status**: Foundation phase - expect debt, manage it proactively

---

## 🔴 Critical (Fix in Session 43)

### 1. Design System Incomplete
- **Issue**: Colors/typography defined but not tokenized
- **Location**: `tailwind.config.ts`, components with hardcoded colors
- **Impact**: Inconsistent styling, hard to maintain
- **Fix**: Create `lib/design-tokens.ts`, refactor components
- **Estimate**: 2 hours

### 2. Pages Use Mixed Design Systems
- **Issue**: Home page uses warm design, other pages use old blue/gray
- **Location**: `/discoveries`, `/methodology`, `/about`, `/discoveries/[id]`
- **Impact**: Site looks half-finished
- **Fix**: Redesign all pages with warm system
- **Estimate**: 3 hours

### 3. Editorial Structure Not Implemented
- **Issue**: Structure documented but not in code/data
- **Location**: No `discoveries_v2.json`, detail pages show raw data
- **Impact**: Can't launch with current clinical display
- **Fix**: Implement editorial data layer + update UI
- **Estimate**: 2 hours

---

## 🟡 Important (Fix in Session 44-45)

### 4. Source Link Data Missing
- **Issue**: 82% of papers have `arxiv_id: "N/A"`
- **Location**: `app/data/discoveries.json` (49/60 paper entries)
- **Root Cause**: Sessions 34-37 LLM extraction didn't capture metadata
- **Impact**: Can't verify claims, trust issue
- **Fix Options**:
  - (a) Query database to backfill arXiv IDs
  - (b) Add field context in editorial pieces
  - (c) Accept limitation, document it
- **Estimate**: 1-2 hours

### 5. Data Migration Strategy Missing
- **Issue**: Plan says "12 discoveries" but data has 30, no migration plan
- **Location**: No migration script, no archiving strategy
- **Impact**: Could lose work, confuse users
- **Fix**: Create migration script + archiving plan
- **Estimate**: 1 hour

### 6. No Testing Infrastructure
- **Issue**: No unit tests, integration tests, or visual regression
- **Location**: Entire codebase
- **Impact**: Breaking changes won't be caught
- **Fix**: Add smoke tests at minimum (Playwright? Vitest?)
- **Estimate**: 2-3 hours

### 7. Accessibility Not Validated
- **Issue**: No WCAG compliance check
- **Location**: Color contrast, font sizes, keyboard nav
- **Impact**: May exclude users, legal risk
- **Fix**: Run axe-core, fix issues
- **Estimate**: 1-2 hours

---

## 🟢 Minor (Fix When Convenient)

### 8. Component Library Inconsistency
- **Issue**: Some components use Tailwind directly, some don't
- **Location**: DomainBadge (hardcoded colors), SimilarityScore (hardcoded thresholds)
- **Impact**: Hard to maintain consistency
- **Fix**: Extract to shared theme, create design primitives
- **Estimate**: 2 hours

### 9. No Performance Baselines
- **Issue**: No Lighthouse scores, bundle size tracking
- **Location**: N/A - missing monitoring
- **Impact**: Can't detect regressions
- **Fix**: Document baselines, set up monitoring
- **Estimate**: 30 min

### 10. No Feature Flags
- **Issue**: Can't toggle features (e.g., new design vs old)
- **Location**: No flag system
- **Impact**: Can't A/B test, hard to rollback
- **Fix**: Add simple flag system (env vars at minimum)
- **Estimate**: 1 hour

### 11. Hardcoded Copy
- **Issue**: All UI text hardcoded in components
- **Location**: All pages/components
- **Impact**: Can't easily update copy, no i18n support
- **Fix**: Extract to content files (optional)
- **Estimate**: 3-4 hours (low priority)

### 12. No Error Boundaries
- **Issue**: React errors crash entire app
- **Location**: No error boundaries in layout/pages
- **Impact**: Poor UX on errors
- **Fix**: Add error boundaries
- **Estimate**: 30 min

---

## 📊 Scalability Concerns (Long-term)

### 13. Static Generation Limits
- **Current**: 38 static pages (fine)
- **At 100 discoveries**: 103 pages (fine)
- **At 1000 discoveries**: 1003 pages (build time issues?)
- **Fix**: Consider ISR (Incremental Static Regeneration) or pagination
- **When**: Session 100+

### 14. Discovery Card Grid
- **Current**: 3 featured on home, 30 on discoveries page
- **At 100 discoveries**: Need pagination, filtering, search
- **Fix**: Rethink browse UX for scale
- **When**: Session 50+

### 15. Data File Size
- **Current**: discoveries.json is 150KB (fine)
- **At 1000 discoveries**: ~5MB JSON (too large for client-side)
- **Fix**: Split into chunks, lazy load, or move to database
- **When**: Session 100+

---

## 🔧 Technical Improvements (Nice-to-Have)

### 16. TypeScript Strictness
- **Current**: `strict: true` but some `any` types
- **Location**: Component props, data interfaces
- **Fix**: Add stricter types
- **Estimate**: 2 hours

### 17. Code Splitting
- **Current**: Single bundle (102KB shared JS)
- **Fix**: Split routes, lazy load components
- **Estimate**: 1 hour

### 18. Image Optimization
- **Current**: No images yet
- **Future**: When adding Open Graph images, use next/image
- **Estimate**: N/A

### 19. Analytics
- **Current**: No analytics (Vercel Analytics available)
- **Fix**: Add minimal tracking (page views, discovery views)
- **Estimate**: 30 min

### 20. SEO Enhancements
- **Current**: Basic meta tags
- **Missing**: Structured data (Schema.org), rich snippets
- **Fix**: Add JSON-LD for each discovery
- **Estimate**: 1-2 hours

---

## 🎯 Debt Reduction Plan

### Session 43 Focus (Must Fix)
- [ ] Design system tokenization
- [ ] Redesign all pages
- [ ] Editorial data structure implementation
- [ ] Accessibility validation (color contrast minimum)

### Session 44 Focus
- [ ] Data migration strategy
- [ ] Source link backfill or workaround
- [ ] Performance baselines

### Session 45 Focus
- [ ] Testing infrastructure
- [ ] Error boundaries
- [ ] Final polish

### Long-term (Session 50+)
- [ ] Component library refactor
- [ ] Feature flag system
- [ ] Scalability improvements

---

## 📝 How to Use This Document

**For each session**:
1. Review this file at start
2. Fix 1-3 items from "Critical" or "Important"
3. Add any new debt you create
4. Update estimates based on learnings
5. Commit changes to this file

**Don't**:
- Ignore this file (debt compounds)
- Fix everything at once (unsustainable)
- Create new debt without documenting it

**Goal**: Keep debt manageable, prevent bankruptcy

---

**Debt is inevitable. Managing it proactively is what matters.**

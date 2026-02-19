# Technical Debt - Analog Quest

**Last Updated**: Session 44 - 2026-02-11
**Status**: Documented and tracked

---

## Critical Issues (Must Fix Before Scale)

### 1. Source Links Missing (82% of discoveries)
**Severity**: High
**Impact**: Trust, verifiability
**Status**: Documented limitation

**Problem**:
- 82% of papers have `arxiv_id: "N/A"`
- Papers came from LLM extraction (Sessions 34-37) without full metadata
- Users cannot verify claims

**Recommendation**: Document limitation clearly on discovery pages

---

### 2. Editorial Body Content Not Written ✅ PARTIALLY FIXED (Session 44)
**Severity**: Medium
**Impact**: User experience
**Status**: Infrastructure ready, content needed

**What's Done** (Session 44):
- ✅ `discoveries_editorial.json` created with template structure
- ✅ Code displays editorial content with fallbacks
- ✅ Tags, titles, mechanism anchors ready
- ✅ 3 example entries (IDs 1, 9, 13)

**What's NOT Done**:
- ❌ Editorial body content (450-600 word pieces) not written yet
- ❌ Only 3/30 discoveries have editorial entries (placeholders only)

**Recommendation**: Session 45 should write editorial pieces

---

### 3. Discovery Detail Pages Use Old Design ✅ FIXED (Session 44)
**Severity**: Medium
**Impact**: Visual consistency
**Status**: ✅ Fixed

**What's Done** (Session 44):
- ✅ Detail pages redesigned with warm palette (cream/brown/teal)
- ✅ ComparisonView component updated
- ✅ All 30 detail pages match main site design
- ✅ Visual consistency achieved across all pages

---

## Component Debt

### 4. FilterBar Component Unused
- Component exists but not used (discoveries page simplified)
- Should be deleted

### 5. Button Component Not Adopted
- Created in Session 43 but not used in all pages
- Should refactor pages to use Button component

---

## Infrastructure Debt

### 6. Performance Baselines ✅ DOCUMENTED (Session 44)
**Status**: Baselines established
**Last Measured**: Session 44 - 2026-02-11

**Build Output** (Production):
- **Total Pages**: 38 (1 home + 1 about + 1 methodology + 1 discoveries + 30 detail pages + 1 404 + 1 sitemap)
- **Build Time**: ~1.8 seconds
- **TypeScript Errors**: 0

**Bundle Sizes**:
- **Shared JS** (all pages): 102 kB
  - chunks/255-ebd51be49873d76c.js: 46 kB
  - chunks/4bd1b696-c023c6e3521b1417.js: 54.2 kB
  - other shared chunks: 1.92 kB

**Page Sizes** (First Load JS):
- Home (`/`): 162 B + 106 kB = ~106 kB total
- About (`/about`): 131 B + 102 kB = ~102 kB total
- Methodology (`/methodology`): 131 B + 102 kB = ~102 kB total
- Discoveries (`/discoveries`): 9.5 kB + 115 kB = ~125 kB total
- Discovery Detail (`/discoveries/[id]`): 162 B + 106 kB = ~106 kB total

**Data Files**:
- discoveries.json: ~58 KB (30 discoveries with full metadata)
- discoveries_editorial.json: ~1 KB (template with 3 placeholders)

**Lighthouse** (Not yet run - requires separate tool):
- Performance: TBD
- Accessibility: TBD (WCAG AA validated via script)
- Best Practices: TBD
- SEO: TBD (comprehensive meta tags implemented)

**Recommendations**:
- ✓ Bundle sizes acceptable for SSG site (<150KB per page)
- ✓ Shared chunk strategy working well (102KB shared across all pages)
- ⚠️ Discoveries page largest (125KB) due to loading all 30 discoveries
- → Monitor bundle size as discoveries scale (50+, 100+)
- → Run Lighthouse audit post-deployment for real-world metrics

### 7. No Testing Strategy
- No unit/integration/visual tests
- Manual QA only
- See TESTING_STRATEGY.md for plan

### 8. No Analytics
- Don't know user behavior
- Can't measure engagement
- Recommendation: Add post-launch

---

## Scalability Unknowns

### 9. Design Scales to 100+ Discoveries?
- Works well with 30 discoveries
- Unknown at 100, 500, 1000
- May need pagination later

### 10. Domain Badge Colors Not Validated
- Assumed WCAG AA compliant
- Not tested with contrast validator

---

## Low Priority

- No dark mode (v2 feature)
- No feature flags (v2 feature)
- No error boundaries (v2 feature)
- No data validation layer (v2 feature)

---

## Mitigation Plan

**Session 43** (current):
- [x] Document technical debt
- [x] Create TESTING_STRATEGY.md

**Session 44**:
- [ ] Implement editorial data structure
- [ ] Redesign discovery detail pages
- [ ] Run Lighthouse audit
- [ ] Delete FilterBar component

**Sessions 45-50**:
- [ ] Add Button component everywhere
- [ ] Performance monitoring setup
- [ ] Basic smoke tests

---

**Risk Level**: MEDIUM - No blockers for v1 launch, but editorial layer needed for quality

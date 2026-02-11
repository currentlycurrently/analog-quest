# Technical Debt - Analog Quest

**Last Updated**: Session 43 - 2026-02-11
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

### 2. Editorial Layer Not Implemented
**Severity**: Medium  
**Impact**: User experience  
**Status**: Documented but not built

**What's Done**:
- EDITORIAL_STRUCTURE.md created
- EDITORIAL_TEMPLATE_V2.md created
- 2 example pieces written

**What's NOT Done**:
- No `discoveries_editorial.json`
- No code to display editorial content

**Recommendation**: Session 44 priority

---

### 3. Discovery Detail Pages Use Old Design
**Severity**: Medium  
**Impact**: Visual consistency  
**Status**: Not fixed in Session 43

**Recommendation**: Session 44 should redesign detail pages

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

### 6. No Performance Baselines
- No Lighthouse scores documented
- No bundle size tracking
- Current: ~102KB shared JS, 38 pages

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

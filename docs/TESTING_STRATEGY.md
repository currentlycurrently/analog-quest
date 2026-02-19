# Testing Strategy - Analog Quest

**Last Updated**: Session 43 - 2026-02-11
**Status**: Planned (not implemented)

---

## Current State

**Testing Coverage**: 0%
- No unit tests
- No integration tests
- No visual regression tests
- No E2E tests
- Manual QA only

**Why This is OK for V1**:
- Static site (38 pages)
- No user input/forms
- No authentication
- No database writes
- Low risk of runtime errors

**When Testing Becomes Critical**:
- Session 50+ (50+ discoveries, complexity grows)
- When adding user interactions (comments, ratings)
- When adding API endpoints
- When team grows beyond 1 person

---

## Phased Testing Approach

### Phase 1: Smoke Tests (Session 45-50)
**Goal**: Catch obvious breaks  
**Effort**: Low (2-3 hours)

**Tests to Add**:
1. **Build succeeds**: `npm run build` exits with code 0
2. **All pages render**: Visit each route, check no 404s
3. **All discoveries load**: Check discoveries.json parses correctly
4. **Design tokens exist**: Check lib/design-tokens.ts exports

**Tools**: Simple Bash scripts or Jest

**Example**:
```bash
# test/smoke.sh
npm run build || exit 1
node test/check-pages.js || exit 1
node test/check-data.js || exit 1
echo "✓ Smoke tests passed"
```

---

### Phase 2: Unit Tests (Session 60-70)
**Goal**: Test pure functions  
**Effort**: Medium (5-8 hours)

**What to Test**:
- Data utilities (lib/data.ts functions)
- Design token exports
- Component prop validation
- Metadata generation

**Tools**: Jest + React Testing Library

**Example**:
```typescript
// lib/data.test.ts
import { getAllDiscoveries, filterDiscoveries } from './data';

test('getAllDiscoveries returns 30 discoveries', () => {
  const discoveries = getAllDiscoveries();
  expect(discoveries).toHaveLength(30);
});

test('filterDiscoveries by rating works', () => {
  const excellent = filterDiscoveries({ rating: 'excellent' });
  expect(excellent.every(d => d.rating === 'excellent')).toBe(true);
});
```

---

### Phase 3: Integration Tests (Session 80-100)
**Goal**: Test page interactions  
**Effort**: High (10-15 hours)

**What to Test**:
- Discovery sorting works
- Discovery card links navigate correctly
- Navigation menu works
- Footer links work
- Metadata renders correctly

**Tools**: Playwright or Cypress

**Example**:
```typescript
// tests/e2e/discoveries.spec.ts
test('sorting discoveries by similarity works', async ({ page }) => {
  await page.goto('/discoveries');
  await page.selectOption('#sort', 'similarity');
  
  const firstCard = page.locator('.discovery-card').first();
  const similarity = await firstCard.locator('.similarity-score').textContent();
  
  expect(parseInt(similarity)).toBeGreaterThan(60);
});
```

---

### Phase 4: Visual Regression (Session 100+)
**Goal**: Catch unintended design changes  
**Effort**: Medium (5-8 hours setup, low maintenance)

**What to Test**:
- Home page renders correctly
- Discovery cards look consistent
- Navigation and footer
- All 30 discovery detail pages

**Tools**: Percy, Chromatic, or Playwright screenshots

**Example**:
```typescript
// tests/visual/pages.spec.ts
test('home page matches snapshot', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('home.png');
});
```

---

## Priority Testing Areas

### High Priority (Phase 1-2)
1. **Data integrity**: discoveries.json parses, all required fields present
2. **Build succeeds**: No TypeScript errors, all pages generate
3. **Navigation works**: All links go to correct pages
4. **Design tokens**: All colors/typography/spacing defined

### Medium Priority (Phase 3)
5. **Sorting/filtering works**: User interactions function correctly
6. **Discovery cards render**: All 30 cards display without errors
7. **Metadata correct**: SEO tags, Open Graph, Twitter cards

### Low Priority (Phase 4)
8. **Visual consistency**: Design matches across sessions
9. **Performance**: Page load times, bundle size

---

## Testing Tools Recommendation

### For Phase 1 (Smoke Tests)
- **Bash scripts**: Simple, no dependencies
- **Node.js scripts**: For JSON validation
- **Cost**: Free
- **Setup time**: 1-2 hours

### For Phase 2 (Unit Tests)
- **Jest**: Industry standard, great TypeScript support
- **React Testing Library**: Test components
- **Cost**: Free
- **Setup time**: 3-4 hours

### For Phase 3 (Integration Tests)
- **Playwright**: Fast, reliable, great DX
- **Alternative**: Cypress (more popular but slower)
- **Cost**: Free
- **Setup time**: 4-6 hours

### For Phase 4 (Visual Regression)
- **Playwright screenshots**: Free, self-hosted
- **Percy**: Paid ($), CI integration, better diffing
- **Chromatic**: Paid ($$), Storybook integration
- **Cost**: Free (Playwright) or $29-99/month (SaaS)
- **Setup time**: 2-4 hours

---

## CI/CD Integration

### When to Add
- After Phase 2 (unit tests) implemented
- When deploying multiple times per week
- When team grows to 2+ people

### Recommended Setup
```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run test        # Run Jest tests
      - run: npm run build       # Build succeeds
      - run: npm run test:e2e    # Run Playwright (if added)
```

---

## Test Coverage Goals

### V1 (Sessions 43-45)
- **Coverage**: 0%
- **Goal**: Ship with confidence via manual QA
- **Acceptable**: Manual testing sufficient for static site

### V1.5 (Sessions 50-70)
- **Coverage**: 20-30%
- **Goal**: Smoke tests + critical path unit tests
- **Focus**: Data integrity, build succeeds, key functions

### V2 (Sessions 80-100)
- **Coverage**: 50-60%
- **Goal**: Unit + integration tests for all features
- **Focus**: User interactions, visual consistency

### V3 (Sessions 100+)
- **Coverage**: 70-80%
- **Goal**: Comprehensive testing including visual regression
- **Focus**: Prevent regressions as site grows

---

## Cost-Benefit Analysis

### Manual QA (Current)
**Cost**: 15-30 min per session  
**Benefit**: Catches obvious issues  
**Limitations**: Prone to human error, not scalable

### Smoke Tests (Phase 1)
**Cost**: 2-3 hours setup, 2 min per run  
**Benefit**: Catches build breaks immediately  
**ROI**: High (one-time setup, prevents disasters)

### Unit Tests (Phase 2)
**Cost**: 5-8 hours setup, 30 min per new feature  
**Benefit**: Catches logic errors, enables refactoring  
**ROI**: Medium (setup cost, but enables confident changes)

### Integration Tests (Phase 3)
**Cost**: 10-15 hours setup, 1 hour per new feature  
**Benefit**: Catches user-facing bugs  
**ROI**: Medium-Low (high cost, but critical for complex features)

### Visual Regression (Phase 4)
**Cost**: 5-8 hours setup, $29-99/month (if SaaS), 5 min per run  
**Benefit**: Catches unintended design changes  
**ROI**: Low (nice to have, not critical)

---

## Recommendation

**For Session 44-45**:
- Continue manual QA
- No tests needed yet

**For Session 50**:
- Add Phase 1 (smoke tests)
- Takes 2-3 hours, high ROI
- Catches build breaks automatically

**For Session 70**:
- Add Phase 2 (unit tests) for data utilities
- Takes 5-8 hours, medium ROI
- Enables confident refactoring

**For Session 100+**:
- Consider Phase 3 (integration tests) if complexity warrants
- Only if user interactions added (forms, comments, etc.)

---

## Success Criteria

### Phase 1 Success
- [ ] Build succeeds automatically
- [ ] All pages render without 404s
- [ ] Data validates correctly
- [ ] Takes <5 minutes to run

### Phase 2 Success
- [ ] 20-30% code coverage
- [ ] All data utilities tested
- [ ] Takes <2 minutes to run
- [ ] Zero false positives

### Phase 3 Success
- [ ] 50-60% code coverage
- [ ] All user interactions tested
- [ ] Takes <10 minutes to run
- [ ] Catches real bugs

### Phase 4 Success
- [ ] Visual regressions caught
- [ ] False positives <5%
- [ ] Takes <15 minutes to run
- [ ] Easy to update snapshots

---

**Last Reviewed**: Session 43 - 2026-02-11  
**Next Review**: Session 50 (when adding smoke tests)

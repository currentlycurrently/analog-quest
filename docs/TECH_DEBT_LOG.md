# Technical Debt Log

**Created**: February 17, 2026 (Session 83)
**Purpose**: Track and prioritize technical debt for systematic resolution

## Priority Levels
- 🔴 **CRITICAL**: Blocking production or causing data corruption
- 🟠 **HIGH**: Significant impact on quality or development speed
- 🟡 **MEDIUM**: Should be fixed soon but not blocking
- 🟢 **LOW**: Nice to have, fix when convenient

---

## 🔴 CRITICAL Issues (Fix Immediately)

### ✅ 1. Data Corruption in discoveries.json - RESOLVED (Session 86)
- **Issue**: 54 duplicate entries (38% of data) with placeholder text
- **Impact**: Production showing wrong data, undermines trust
- **Location**: app/data/discoveries.json
- **Fix Applied**: Rebuilt from PostgreSQL database (source of truth)
- **Results**:
  - Removed 63 duplicate/corrupted entries (33%)
  - Fixed format inconsistencies (2 formats → 1 format)
  - All 125 entries now clean and validated
- **Resolution Date**: 2026-02-22
- **Scripts Created**:
  - `scripts/rebuild_discoveries.py` (rebuilds from DB)
  - `scripts/validate_data_integrity.py` (prevents future corruption)

### ✅ 2. Database Sync Failure - RESOLVED (Session 86)
- **Issue**: discoveries table has 125 entries, discovered_pairs has 133
- **Impact**: API returns incomplete data
- **Location**: PostgreSQL database
- **Fix Applied**: Discovered that DB was actually correct (125 is accurate count)
- **Results**:
  - PostgreSQL is now the single source of truth
  - discovered_pairs.json rebuilt from database (was using old session IDs)
  - All sources now in sync: DB = discovered_pairs = discoveries.json = 125
- **Resolution Date**: 2026-02-22
- **Note**: Original "133 count" was from stale discovered_pairs.json with invalid mechanism IDs

### 3. Frontend Shows Only 3 Discoveries
- **Issue**: Homepage displays only 3 "featured" instead of all 133
- **Impact**: Users can't browse discoveries
- **Location**: app/page.tsx
- **Fix**: Implement proper discovery grid/list
- **Effort**: 2-3 hours
- **Owner**: Next session agent

---

## 🟠 HIGH Priority Issues

### ✅ 4. No Data Validation - RESOLVED (Session 86)
- **Issue**: System accepts any data without checks
- **Impact**: Allows duplicates and invalid data
- **Location**: Throughout data pipeline
- **Fix Applied**: Created comprehensive validation script
- **Results**:
  - `scripts/validate_data_integrity.py` checks:
    - Duplicate detection across all sources
    - Required field validation
    - Cross-source consistency (JSON ↔ DB)
    - Foreign key integrity
    - Valid ratings and similarity scores
  - Returns exit code 1 on errors (can be used in pre-commit hooks)
- **Resolution Date**: 2026-02-22
- **Usage**: Run before any data commits

### ✅ 5. Multiple Data Sources Confusion - PARTIALLY RESOLVED (Session 86)
- **Issue**: SQLite + PostgreSQL + JSON files all used
- **Impact**: Unclear which is authoritative
- **Location**: Various
- **Fix Applied**: Established PostgreSQL as single source of truth
- **Results**:
  - PostgreSQL is authoritative for all discoveries
  - JSON files are now derived/cached data (rebuilt from DB)
  - SQLite (papers.db) still used for paper/mechanism storage
  - Clear hierarchy established: PostgreSQL → JSON exports
- **Resolution Date**: 2026-02-22
- **Remaining**: Consider migrating SQLite papers.db to PostgreSQL (low priority)

### 6. TypeScript 'any' Types
- **Issue**: 15+ instances of 'any' type
- **Impact**: No type safety, potential runtime errors
- **Location**: lib/db.ts, lib/data.ts, app/
- **Fix**: Define proper types
- **Effort**: 2-3 hours

### 7. Zero Test Coverage
- **Issue**: No tests at all
- **Impact**: Can't verify changes don't break things
- **Location**: Entire codebase
- **Fix**: Add at least integration tests
- **Effort**: 8-12 hours

### 8. Backup Files in Git
- **Issue**: Multiple .bak and backup files tracked
- **Impact**: Repo bloat, confusion
- **Location**: Various
- **Fix**: Remove and add to .gitignore
- **Effort**: 30 minutes

---

## 🟡 MEDIUM Priority Issues

### 9. No Error Monitoring
- **Issue**: Errors fail silently
- **Impact**: Don't know when things break
- **Fix**: Add Sentry or similar
- **Effort**: 2-3 hours

### 10. No CI/CD Pipeline
- **Issue**: Manual deployments only
- **Impact**: Slow, error-prone releases
- **Fix**: Set up GitHub Actions
- **Effort**: 3-4 hours

### 11. Manual Processing Bottleneck
- **Issue**: Can only process ~60 discoveries/session
- **Impact**: Limits growth
- **Fix**: Automate discovery pipeline
- **Effort**: 8-12 hours

### 12. No Staging Environment
- **Issue**: Direct to production only
- **Impact**: Can't test safely
- **Fix**: Create staging on Vercel
- **Effort**: 2-3 hours

### 13. Poor Separation of Concerns
- **Issue**: Business logic mixed with data access
- **Impact**: Hard to maintain
- **Fix**: Refactor to proper layers
- **Effort**: 6-8 hours

---

## 🟢 LOW Priority Issues

### 14. No Linting Configuration
- **Issue**: No ESLint or Prettier
- **Impact**: Inconsistent code style
- **Fix**: Add and configure
- **Effort**: 1-2 hours

### 15. Inconsistent Naming
- **Issue**: Files and functions lack standards
- **Impact**: Confusion, harder to navigate
- **Fix**: Define and apply naming conventions
- **Effort**: 3-4 hours

### 16. No Analytics
- **Issue**: Can't track usage
- **Impact**: Don't know if anyone uses it
- **Fix**: Add Google Analytics or Plausible
- **Effort**: 1-2 hours

### 17. TODO Comments
- **Issue**: 4 TODO comments in code
- **Impact**: Incomplete features
- **Fix**: Complete or remove
- **Effort**: 2-3 hours

### 18. No Admin Tools
- **Issue**: All data management is manual
- **Impact**: Slow operations
- **Fix**: Build admin interface
- **Effort**: 12-16 hours

---

## Debt by Category

### Data Integrity
- Issues: #1, #2, #4, #5
- Total Effort: 13-20 hours
- Priority: CRITICAL/HIGH

### Code Quality
- Issues: #6, #7, #10, #13, #14, #15, #17
- Total Effort: 32-47 hours
- Priority: MEDIUM

### Infrastructure
- Issues: #8, #9, #11, #12, #16, #18
- Total Effort: 28-40 hours
- Priority: MEDIUM/LOW

### User Experience
- Issues: #3
- Total Effort: 2-3 hours
- Priority: CRITICAL

---

## Recommended Fix Order

### ✅ Phase 1: Emergency (Session 86) - COMPLETED
1. ✅ Fix data corruption (#1) - RESOLVED
2. ✅ Sync database (#2) - RESOLVED
3. ⏳ Fix frontend display (#3) - STILL CRITICAL (next session)

### Phase 2: Stabilization (Next 2 Sessions)
4. ✅ Add data validation (#4) - RESOLVED
5. ✅ Clean up data sources (#5) - MOSTLY RESOLVED
6. Remove backup files from git (#8)
7. Fix TypeScript types (#6)

### Phase 3: Quality (Sessions 86-88)
8. Add integration tests (#7)
9. Set up error monitoring (#9)
10. Create CI/CD pipeline (#10)
11. Set up staging environment (#12)

### Phase 4: Optimization (Sessions 89-90)
12. Automate processing (#11)
13. Refactor architecture (#13)
14. Add linting (#14)
15. Build admin tools (#18)

---

## Metrics to Track

### Before Fixes (Session 85)
- Duplicate rate: 38% (54/141)
- Type safety: 15 'any' types
- Test coverage: 0%
- Manual effort: 100%
- Error visibility: 0%

### After Session 86 Fixes
- Duplicate rate: 0% ✅ (was 38%)
- Data validation: Automated script ✅ (was none)
- Source of truth: PostgreSQL ✅ (was unclear)
- Type safety: 15 'any' types (unchanged)
- Test coverage: 0% (unchanged)
- Manual effort: 100% (unchanged)
- Error visibility: 0% (unchanged)

### Target After All Fixes
- Duplicate rate: 0% ✅
- Type safety: 0 'any' types
- Test coverage: >50%
- Manual effort: <30%
- Error visibility: 100%

---

## Notes for Future Sessions

1. **DO NOT add new discoveries until data layer is fixed**
2. **Test all changes locally before deploying**
3. **Document fixes as you make them**
4. **Update this log as issues are resolved**
5. **Consider pausing new features until debt is manageable**

---

## Session 86 Resolution Summary

**Date**: 2026-02-22

### Issues Resolved
1. ✅ Data Corruption (#1) - 63 corrupted entries removed
2. ✅ Database Sync (#2) - All sources now at 125 entries
3. ✅ Data Validation (#4) - Automated validation script created
4. ✅ Data Sources Confusion (#5) - PostgreSQL established as source of truth

### Scripts Created
- `scripts/rebuild_discoveries.py` - Rebuilds JSON from PostgreSQL
- `scripts/validate_data_integrity.py` - Validates data before commits

### Data Quality Results
- **Before**: 188 entries, 107 duplicates (57% duplication), 2 formats
- **After**: 125 entries, 0 duplicates (0% duplication), 1 format
- **Corruption Fixed**: 63 entries removed
- **Validation**: All sources verified consistent

### Backup Files Created
- `app/data/discoveries.json.backup` - Pre-fix state
- `app/data/discovered_pairs.json.backup` - Pre-rebuild state

---

**Last Updated**: Session 86
**Total Issues**: 18
**Resolved**: 4 (22%)
**Critical Remaining**: 1 (Frontend display)
**High Remaining**: 4
**Medium**: 5
**Low**: 5
**Estimated Remaining Effort**: 56-88 hours (down from 73-107)
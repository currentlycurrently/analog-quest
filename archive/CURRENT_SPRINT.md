# Current Sprint: Data Layer Fix
**Sprint Goal**: Fix critical data integrity issues and connect frontend to database
**Sessions**: 84-87
**Created**: Session 83

## Critical Context
- Frontend uses static JSON with 54 duplicates, NOT the database
- Database has clean data but frontend doesn't use it
- Must fix before adding ANY new discoveries

## Session 84: Emergency Data Fix
**Goal**: Eliminate duplicates and connect frontend to database
1. [ ] Create script to export clean data from database
2. [ ] Replace discoveries.json with clean data
3. [ ] Modify frontend to use API instead of JSON
4. [ ] Test that all 133 discoveries display
5. [ ] Deploy fixes

## Session 85: Add Data Validation
**Goal**: Prevent future duplicates
1. [ ] Add validation to discovered_pairs updates
2. [ ] Create deduplication checks
3. [ ] Add data integrity tests
4. [ ] Document validation rules

## Session 86: Frontend Improvements
**Goal**: Show all discoveries properly
1. [ ] Fix homepage to show discovery grid
2. [ ] Add pagination for discoveries
3. [ ] Implement search/filter
4. [ ] Add discovery count display

## Session 87: Resume Discovery Mining
**Goal**: Return to finding new discoveries
1. [ ] Verify all fixes working
2. [ ] Review remaining candidates
3. [ ] Add 10-15 new discoveries
4. [ ] Update metrics

## Key Rules for All Sessions
1. **Read only**: CURRENT_SPRINT.md, last 2 sessions of PROGRESS.md
2. **Update**: SESSION_HANDOFF.md with what you did
3. **Commit**: After each major change
4. **Test**: Before deploying anything
5. **Focus**: One task at a time, complete it fully

## Success Metrics
- [ ] 0 duplicate discoveries
- [ ] Frontend shows 133+ discoveries
- [ ] All data from database (not JSON)
- [ ] Validation prevents duplicates
- [ ] Can safely add new discoveries
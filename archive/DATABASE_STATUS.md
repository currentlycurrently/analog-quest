# Database Status and Architecture

**Last Updated**: 2026-02-16 (Session 81)

## Current Status

### Primary Database: SQLite (ACTIVE)
- **Location**: `database/papers.db`
- **Size**: ~91MB
- **Contents**:
  - 2,194 papers
  - 6,125 patterns (old keyword extraction)
  - 616 isomorphisms (old matches)
- **Status**: READ-ONLY - Used for historical reference only
- **Note**: Contains Sessions 1-55 data

### Experimental: PostgreSQL (TESTED, NOT IN PRODUCTION)
- **Sessions 61-62**: PostgreSQL setup and migration tested
- **Session 62**: Successfully migrated all data
- **Sessions 63-68**: Used for OpenAlex paper ingestion tests
- **Current Status**: NOT ACTIVELY USED
- **Reason**: Switched to simpler file-based approach for Phase 2

### Current Working Data (ACTIVE)
- **Mechanisms**: Stored in session JSON files (305 total)
- **Discoveries**: `app/data/discovered_pairs.json` (133 verified)
- **Candidates**: `examples/session74_candidates.json` (595 to review)
- **Frontend**: `app/data/discoveries.json` (141 displayed)

## Architecture Decision

**Phase 1 (Sessions 1-55)**: SQLite for everything
**Transition (Sessions 56-68)**: PostgreSQL experiments, not fully adopted
**Phase 2 (Sessions 69-81)**: File-based for simplicity during discovery mining

## Future Recommendation

For Session 82+, continue with file-based approach for discovery curation.
PostgreSQL can be revisited when scaling to 50K+ papers (Phase 3).

## Data Flow

```
1. Papers fetched → Stored in JSON files
2. Mechanisms extracted → Stored in session files
3. Candidates generated → session74_candidates.json
4. Discoveries curated → discovered_pairs.json
5. Frontend updated → discoveries.json
```

## Key Files
- **Source of truth for discoveries**: `app/data/discovered_pairs.json`
- **Candidate pipeline**: `examples/session74_candidates.json`
- **Frontend display**: `app/data/discoveries.json`

## Notes
- SQLite database is legacy but kept for reference
- PostgreSQL infrastructure exists but not currently used
- File-based approach working well for current scale (300 mechanisms, 133 discoveries)
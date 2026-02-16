# Naming Conventions

## File Naming Standards

### Session Files
- **Format**: `sessionXX_description.json` (no underscore after session)
- **Examples**:
  - ✅ `session82_curated_discoveries.json`
  - ✅ `session82_candidates.json`
  - ❌ `session_82_discoveries.json` (avoid underscores)

### Scripts
- **General scripts**: `snake_case.py`
  - ✅ `extract_patterns.py`
  - ✅ `find_matches.py`
- **Session-specific**: `sessionXX_action.py`
  - ✅ `session82_review_candidates.py`
  - ❌ `Session82ReviewCandidates.py` (no camelCase)

### Data Files
- **Discoveries**: `discovered_pairs.json` (source of truth)
- **Frontend**: `discoveries.json` (display data)
- **Candidates**: `sessionXX_candidates.json`
- **Curated**: `sessionXX_curated_discoveries.json`

### Directories
- **All lowercase with underscores**:
  - ✅ `app/data/`
  - ✅ `archive/sessions/`
  - ❌ `Archive/Sessions/` (no capitals)

## Variable Naming in Code

### Python
```python
# Variables: snake_case
total_discoveries = 133
mechanism_id = 42

# Functions: snake_case
def extract_patterns():
    pass

# Classes: PascalCase
class PatternExtractor:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_SIMILARITY_THRESHOLD = 0.5
```

### JSON Keys
- **Always snake_case**:
```json
{
  "mechanism_1_id": 123,
  "similarity_score": 0.45,
  "discovered_in_session": 82
}
```

## Commit Messages
- **Format**: "Session XX: Brief description"
- **Examples**:
  - ✅ "Session 82: Found 15 new discoveries"
  - ✅ "Fix: Update duplicate detection logic"
  - ❌ "session82" (too vague)
  - ❌ "MASSIVE UPDATE!!!" (too dramatic)

## Archive Structure
```
archive/
├── sessions/
│   ├── 01-25/
│   ├── 26-50/
│   ├── 51-75/
│   └── 76-100/
├── scripts/
└── large_files/
```

## When to Archive
- Session files: After 10 sessions old
- Scripts: When no longer actively used
- Large files: Immediately compress if >1MB

---
*Established Session 81 to maintain consistency across the project*
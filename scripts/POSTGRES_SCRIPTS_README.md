# PostgreSQL Migration Scripts

This directory contains scripts for migrating and managing the PostgreSQL database.

## Migration Scripts (Run Once)

These scripts were used for the initial migration on 2026-02-17:

### `migrate_postgres_data.py` ✓ COMPLETED
Main migration script that performs all three migration tasks:
1. Standardize mechanism schema
2. Sync discovered_pairs table
3. Populate discoveries table

**Status**: Successfully run. Database migrated.

### `add_session38_discoveries.py` ✓ COMPLETED
Adds Session 38 verified isomorphisms from SESSION38_VERIFIED_ISOMORPHISMS.json.

**Status**: Successfully run. 30 discoveries added.

### `fill_missing_discoveries.py` ✓ COMPLETED
Auto-fills discovery records for pairs that have mechanisms but no detailed metadata.

**Status**: Successfully run. 15 minimal records added.

## Verification Scripts (Run Anytime)

### `verify_postgres_health.py` ⭐ RECOMMENDED
Quick health check for the database. Run this anytime to verify everything is working.

```bash
python3 scripts/verify_postgres_health.py
```

**Checks**:
- All tables exist
- Row counts are reasonable
- All mechanisms use standardized schema
- No orphaned records
- Discovery quality metrics

**Returns**: Exit code 0 if healthy, 1 if issues found

### `final_verification.py`
Comprehensive verification with detailed statistics.

```bash
python3 scripts/final_verification.py
```

**Provides**:
- Table row counts
- Schema standardization status
- Data integrity checks
- Coverage analysis
- Session breakdowns

## Analysis Scripts

### `inspect_postgres.py`
Inspects database schema and shows sample data.

```bash
python3 scripts/inspect_postgres.py
```

### `analyze_discovery_gap.py`
Analyzes gaps between discovered_pairs.json and session files.

```bash
python3 scripts/analyze_discovery_gap.py
```

### `check_missing_discoveries.py`
Finds pairs in discovered_pairs.json without discovery records.

```bash
python3 scripts/check_missing_discoveries.py
```

## Example Queries

### `example_queries.py` ⭐ LEARNING RESOURCE
Demonstrates how to query the migrated database with real examples.

```bash
python3 scripts/example_queries.py
```

**Examples included**:
1. Get all discoveries with paper details
2. Get excellent-rated discoveries
3. Find cross-domain discoveries
4. Session statistics
5. Mechanisms with paper information
6. Export to JSON format

**Use this as a template** for building your own queries!

## Database Connection

All scripts use the same connection parameters:

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="analog_quest",
    user="user"
)
```

## Quick Start

### Check Database Health
```bash
python3 scripts/verify_postgres_health.py
```

### View Example Queries
```bash
python3 scripts/example_queries.py
```

### Get Detailed Report
```bash
python3 scripts/final_verification.py
```

## Common Queries

### Count discoveries by rating
```python
cur.execute("""
    SELECT rating, COUNT(*) as count
    FROM discoveries
    GROUP BY rating;
""")
```

### Get top discoveries by similarity
```python
cur.execute("""
    SELECT d.*, p1.title as paper1, p2.title as paper2
    FROM discoveries d
    JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
    JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
    JOIN papers p1 ON m1.paper_id = p1.id
    JOIN papers p2 ON m2.paper_id = p2.id
    ORDER BY d.similarity DESC
    LIMIT 10;
""")
```

### Find cross-domain discoveries
```python
cur.execute("""
    SELECT p1.domain, p2.domain, COUNT(*) as count
    FROM discoveries d
    JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
    JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
    JOIN papers p1 ON m1.paper_id = p1.id
    JOIN papers p2 ON m2.paper_id = p2.id
    WHERE p1.domain != p2.domain
    GROUP BY p1.domain, p2.domain
    ORDER BY count DESC;
""")
```

## Troubleshooting

### "Cannot connect to database"
- Check PostgreSQL is running: `pg_isready`
- Verify connection parameters in script

### "Table does not exist"
- Run migration scripts first
- Check database name is correct

### "No rows returned"
- Database may be empty
- Check if migration completed successfully

## Documentation

For full migration details, see:
- `POSTGRES_MIGRATION_REPORT.md` - Complete migration report
- `POSTGRES_MIGRATION_SUMMARY.md` - Quick summary

## Support

All scripts include error handling and helpful output. If you encounter issues:

1. Run `verify_postgres_health.py` first
2. Check the error message
3. Verify PostgreSQL is running
4. Ensure database has been migrated

## Best Practices

1. **Always run health check** after database changes
2. **Use parameterized queries** to prevent SQL injection
3. **Close connections** when done (scripts handle this)
4. **Check row counts** before and after modifications
5. **Backup before major changes** (PostgreSQL automatic backups recommended)

---

**Last Updated**: 2026-02-17
**Migration Status**: ✅ Complete
**Database Version**: PostgreSQL (analog_quest)

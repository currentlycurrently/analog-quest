# PostgreSQL + pgvector Setup Guide

**Created**: 2026-02-14 (Session 61)
**Database**: PostgreSQL 17.8 with pgvector 0.8.1
**Purpose**: Vector similarity search for cross-domain mechanism discovery at scale

---

## Installation (macOS)

### 1. Install PostgreSQL 17 and pgvector

```bash
brew install postgresql@17 pgvector
```

### 2. Start PostgreSQL service

```bash
brew services start postgresql@17
```

### 3. Add PostgreSQL to PATH

For the current session:
```bash
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
```

To persist across sessions, add to `~/.zshrc`:
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 4. Create database

```bash
createdb analog_quest
```

### 5. Enable pgvector extension

```bash
psql -d analog_quest -c "CREATE EXTENSION vector;"
```

Verify installation:
```bash
psql -d analog_quest -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

Expected output:
```
 extname | extversion
---------+------------
 vector  | 0.8.1
```

---

## Schema Setup

### Create tables

Execute the schema SQL file:
```bash
psql -d analog_quest -f database/schema.sql
```

This creates 4 tables:
1. **papers**: Stores academic papers (50K rows at scale)
2. **mechanisms**: Domain-neutral mechanism descriptions with 384-dim embeddings (5K-8K rows)
3. **discoveries**: Curated cross-domain matches (200-400 rows)
4. **discovered_pairs**: Deduplication tracking (prevents re-discovery of same pairs)

### Verify tables

```bash
psql -d analog_quest -c "\dt"
```

Expected output:
```
             List of relations
 Schema |       Name       | Type  | Owner
--------+------------------+-------+-------
 public | discovered_pairs | table | user
 public | discoveries      | table | user
 public | mechanisms       | table | user
 public | papers           | table | user
```

### Verify vector column

```bash
psql -d analog_quest -c "\d mechanisms"
```

Should show `embedding vector(384)` column and HNSW index.

---

## Connection Information

**Database name**: `analog_quest`
**User**: Your system username (default PostgreSQL user)
**Host**: localhost
**Port**: 5432 (default)

### Connection string

```
postgresql://localhost/analog_quest
```

### Python connection (example for future scripts)

```python
import psycopg2
from pgvector.psycopg2 import register_vector

# Connect
conn = psycopg2.connect(
    dbname="analog_quest",
    user="your_username",
    host="localhost",
    port="5432"
)

# Register vector type
register_vector(conn)

# Query
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM papers;")
print(cur.fetchone())
```

---

## Vector Similarity Search

### Test vector similarity (k-NN query)

**Find k=10 most similar mechanisms** (cross-domain only):

```sql
SELECT
    m1.id AS mechanism_1_id,
    m2.id AS mechanism_2_id,
    m1.embedding <-> m2.embedding AS distance,  -- L2 distance
    1 - (m1.embedding <-> m2.embedding) AS similarity,
    p1.domain AS domain_1,
    p2.domain AS domain_2
FROM mechanisms m1
CROSS JOIN mechanisms m2
JOIN papers p1 ON m1.paper_id = p1.id
JOIN papers p2 ON m2.paper_id = p2.id
WHERE m1.id < m2.id  -- avoid duplicates (A,B) and (B,A)
  AND p1.domain != p2.domain  -- cross-domain only
  AND p1.id != p2.id  -- exclude same paper
ORDER BY m1.embedding <-> m2.embedding  -- sort by distance (HNSW index used!)
LIMIT 10;
```

**Find mechanisms similar to a specific mechanism (e.g., id=42)**:

```sql
SELECT
    m.id,
    LEFT(m.mechanism, 50) as mechanism_preview,
    p.title,
    p.domain,
    1 - (m.embedding <-> (SELECT embedding FROM mechanisms WHERE id = 42)) AS similarity
FROM mechanisms m
JOIN papers p ON m.paper_id = p.id
WHERE m.id != 42
  AND p.domain != (SELECT p2.domain FROM mechanisms m2 JOIN papers p2 ON m2.paper_id = p2.id WHERE m2.id = 42)
ORDER BY m.embedding <-> (SELECT embedding FROM mechanisms WHERE id = 42)
LIMIT 20;
```

### Performance characteristics

**Expected query times** (based on pgvector 0.8.1 benchmarks):

- **k=10 similarity search**: <50ms (on 5K-8K vectors with HNSW index)
- **k=100 similarity search**: <200ms
- **Paper lookup by ID**: <1ms (indexed)
- **Mechanism lookup by paper_id**: <1ms (indexed)

**HNSW index benefits** (vs brute-force):
- 9× faster queries
- 100× more relevant results
- Scales to <100M vectors

---

## Useful Queries

### Get database stats

```sql
SELECT
    (SELECT COUNT(*) FROM papers) as total_papers,
    (SELECT COUNT(*) FROM mechanisms) as total_mechanisms,
    (SELECT COUNT(*) FROM discoveries) as total_discoveries,
    (SELECT COUNT(*) FROM discovered_pairs) as total_tracked_pairs;
```

### List all indexes

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('papers', 'mechanisms', 'discoveries', 'discovered_pairs')
ORDER BY tablename, indexname;
```

### Check database size

```sql
SELECT pg_size_pretty(pg_database_size('analog_quest')) as db_size;
```

### Top 10 papers by mechanism count

```sql
SELECT
    p.id,
    p.title,
    p.domain,
    COUNT(m.id) as mechanism_count
FROM papers p
LEFT JOIN mechanisms m ON p.paper_id = m.id
GROUP BY p.id
ORDER BY mechanism_count DESC
LIMIT 10;
```

### Discoveries by domain pair

```sql
SELECT
    p1.domain || ' ↔ ' || p2.domain as domain_pair,
    COUNT(*) as discovery_count,
    AVG(d.similarity) as avg_similarity
FROM discoveries d
JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
JOIN papers p1 ON m1.paper_id = p1.id
JOIN papers p2 ON m2.paper_id = p2.id
GROUP BY p1.domain, p2.domain
ORDER BY discovery_count DESC;
```

---

## Maintenance

### Stop PostgreSQL service

```bash
brew services stop postgresql@17
```

### Restart PostgreSQL service

```bash
brew services restart postgresql@17
```

### Backup database

```bash
pg_dump analog_quest > backups/analog_quest_$(date +%Y%m%d).sql
```

### Restore database

```bash
psql -d analog_quest < backups/analog_quest_20260214.sql
```

### Drop database (⚠️ destructive)

```bash
dropdb analog_quest
```

---

## Troubleshooting

### "psql: command not found"

PostgreSQL not in PATH. Run:
```bash
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
```

### "could not connect to server"

PostgreSQL service not running. Start it:
```bash
brew services start postgresql@17
```

### "extension 'vector' is not available"

pgvector not installed or incompatible version. Reinstall:
```bash
brew reinstall pgvector
```

### "FATAL: database 'analog_quest' does not exist"

Database not created. Create it:
```bash
createdb analog_quest
```

---

## Next Steps (Session 62)

1. **Migrate existing data** from SQLite (`database/papers.db`) to PostgreSQL
   - Export 2,194 papers
   - Export 200 mechanisms
   - Generate embeddings for 200 mechanisms (384-dim)
   - Import to PostgreSQL tables

2. **Validate migration**
   - Reproduce current 1,158 candidates using pgvector
   - Compare with Session 55 results (should match exactly)

3. **Migrate discoveries**
   - Import 46 discoveries from `app/data/discoveries.json`
   - Import `app/data/discovered_pairs.json` for deduplication tracking

---

## Performance Tuning (Optional)

### Enable binary quantization (32× memory reduction, 95% accuracy)

```sql
-- Note: Only available on indexes, apply after data migration
ALTER INDEX idx_mechanisms_embedding SET (quantization = 'binary');
```

### Increase shared memory for large datasets

Edit PostgreSQL config (if processing >10K vectors):
```bash
# Find config file
psql -d analog_quest -c "SHOW config_file;"

# Edit postgresql.conf
shared_buffers = 256MB  # default: 128MB
effective_cache_size = 1GB  # default: 4GB
```

Restart PostgreSQL after config changes:
```bash
brew services restart postgresql@17
```

---

## References

- **pgvector documentation**: https://github.com/pgvector/pgvector
- **pgvector 0.8.0 improvements**: 9× faster, 100× more relevant (HNSW + binary quantization)
- **PostgreSQL documentation**: https://www.postgresql.org/docs/17/
- **SCALE_UP_PLAN.md**: Full infrastructure plan (Sessions 60-90)

---

**Session 61 Status**: ✅ **COMPLETE** - PostgreSQL + pgvector installed, schema created, vector similarity tested

**Ready for Session 62**: Data migration from SQLite to PostgreSQL

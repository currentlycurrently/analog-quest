# Analog Quest API Documentation

## Current Status (2026-02-16)

The API is now functional and serving data from static JSON files. This is a transitional state that allows us to:
1. Have a working API immediately
2. Deploy without breaking anything
3. Gradually migrate to a real database
4. Keep the site functional throughout

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Returns the current health status of the API and data sources.

```bash
curl http://localhost:3002/api/health
```

Response includes:
- API status
- Data source availability
- Database connection status
- Known issues and recommendations
- Available endpoints and capabilities

### 2. Discoveries

#### List Discoveries
**GET** `/api/discoveries`

Query Parameters:
- `rating` - Filter by rating ('excellent' or 'good')
- `domain` - Filter by domain (e.g., 'physics', 'biology')
- `minSimilarity` - Minimum similarity score (0-1)
- `sortBy` - Sort field ('similarity', 'rating', 'id', 'session')
- `order` - Sort order ('asc' or 'desc')
- `limit` - Number of results to return
- `offset` - Number of results to skip

Example:
```bash
curl "http://localhost:3002/api/discoveries?rating=excellent&limit=10"
```

#### Get Single Discovery
**GET** `/api/discoveries/[id]`

Example:
```bash
curl http://localhost:3002/api/discoveries/1
```

#### API Capabilities
**OPTIONS** `/api/discoveries`

Returns API version and current capabilities.

### 3. Discovered Pairs

#### List Pairs
**GET** `/api/pairs`

The source of truth for unique discoveries (133 items).

Query Parameters:
- `session` - Filter by session number
- `rating` - Filter by rating
- `minSimilarity` - Minimum similarity score
- `limit` - Number of results
- `offset` - Skip results

Example:
```bash
curl "http://localhost:3002/api/pairs?session=81"
```

## Data Flow

### Current State (Static JSON)
```
Session Files → compile_frontend_discoveries.py → discoveries.json (141 items)
                                                ↓
                                          Frontend imports
                                                ↓
                                           API serves JSON
```

### Target State (With Database)
```
Session Files → Database → API → Frontend
                   ↑
           discovered_pairs tracking
```

## Known Issues

1. **Data Inconsistency**: 141 discoveries in frontend, 133 unique pairs tracked
2. **No Write Operations**: Can't add new discoveries via API yet
3. **No Database Connection**: Using static JSON instead of database
4. **Manual Updates**: Requires git commit and rebuild for changes

## Next Steps

### Phase 1: Environment Setup (Immediate)
1. Create `.env.local` with database credentials
2. Choose database provider (Neon, Supabase, or independent PostgreSQL)
3. Set up connection strings

### Phase 2: Database Migration
1. Create proper schema
2. Migrate existing data from JSON/SQLite
3. Update API routes to use database
4. Implement write operations

### Phase 3: Frontend Integration
1. Update data.ts to optionally use API
2. Add error handling and fallbacks
3. Implement caching strategy
4. Remove static JSON dependencies

### Phase 4: Production Deployment
1. Set environment variables in Vercel
2. Test database connection in production
3. Monitor performance and errors
4. Document for future sessions

## Environment Variables Template

Create `.env.local`:
```bash
# Database Connection (choose one provider)
# Option 1: Neon
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Option 2: Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=xxxxx

# Option 3: Custom PostgreSQL
POSTGRES_URL=postgresql://user:pass@host:port/db
POSTGRES_PRISMA_URL=postgresql://user:pass@host:port/db?schema=public
POSTGRES_URL_NON_POOLING=postgresql://user:pass@host:port/db

# API Configuration
API_VERSION=1.0.0
ENABLE_WRITE_OPS=false
USE_DATABASE=false  # Set to true when database is ready

# Optional: Authentication (for write operations)
API_SECRET_KEY=xxxxx
```

## Testing

### Local Testing
```bash
# Start dev server
npm run dev

# Test endpoints
curl http://localhost:3002/api/health
curl http://localhost:3002/api/discoveries?limit=5
curl http://localhost:3002/api/discoveries/1
curl http://localhost:3002/api/pairs?rating=excellent
```

### Production Testing
```bash
# After deployment
curl https://analog.quest/api/health
```

## Migration Script Template

When ready to migrate to database:

```typescript
// scripts/migrate-to-db.ts
import { sql } from '@neon/serverless';  // or your chosen provider

async function migrate() {
  // Create tables
  await sql`CREATE TABLE IF NOT EXISTS discoveries ...`;

  // Import from JSON
  const discoveries = require('../app/data/discoveries.json');
  for (const discovery of discoveries) {
    await sql`INSERT INTO discoveries ...`;
  }
}
```

## Monitoring

Once deployed, monitor:
1. API response times
2. Error rates
3. Database connection pool
4. Memory usage
5. Build times

## Notes for Future Sessions

- API routes are ready and working with static JSON
- Database connection is the next critical step
- Keep discovered_pairs.json as source of truth until database migration
- Test everything locally before production changes
- Document any database credentials securely

---

**Last Updated**: 2026-02-16
**API Version**: 1.0.0
**Status**: Functional with static JSON, ready for database integration
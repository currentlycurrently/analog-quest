# Infrastructure Fix Plan - Make Analog Quest Actually Work!

## Current Reality Check ❌
- **Database**: SQLite file sitting on your laptop
- **Frontend**: Reading static JSON like it's 1999
- **Deployment**: git push → rebuild everything → pray
- **Updates**: Hand-edit JSON, commit, wait 5 minutes for build
- **Scalability**: ZERO
- **Real-time**: NOPE
- **API**: What API?

## The Fix - Three Options

### Option 1: Full Dynamic (RECOMMENDED) 🚀
**Stack**: Next.js + Vercel Postgres + API Routes

**Pros**:
- Real database in production
- Can add discoveries without rebuild
- Searchable, filterable, sortable
- Admin interface possible
- Scales to millions of discoveries

**Cons**:
- Need to set up Vercel Postgres ($20/month at scale)
- More complex deployment
- Need to migrate existing data

**Implementation**:
```bash
# 1. Install Vercel Postgres
npm install @vercel/postgres

# 2. Set up database through Vercel Dashboard
# 3. Create schema
# 4. Build API routes
# 5. Migrate data
```

### Option 2: Static with GitHub Actions (QUICK FIX) 🔧
**Stack**: Current setup + GitHub Actions + Automated builds

**Pros**:
- Minimal changes to current code
- Free with GitHub Actions
- Can automate the manual process

**Cons**:
- Still rebuilding for every change
- No real-time updates
- Limited to GitHub API limits

**Implementation**:
```yaml
# .github/workflows/update-discoveries.yml
name: Update Discoveries
on:
  schedule:
    - cron: '0 */6 * * *' # Every 6 hours
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python scripts/compile_frontend_discoveries.py
      - run: |
          git add app/data/discoveries.json
          git commit -m "Auto-update discoveries"
          git push
```

### Option 3: Hybrid - ISR (Incremental Static Regeneration) 🎯
**Stack**: Next.js ISR + External Database API

**Pros**:
- Best of both worlds
- Fast static pages
- Can update without full rebuild
- Revalidates every X seconds

**Cons**:
- Need external database (Supabase, PlanetScale, etc.)
- More complex caching logic

## RECOMMENDED PATH FORWARD

### Phase 1: Stop the Bleeding (TODAY)
1. Create `.env.local` with database configs
2. Set up Vercel Postgres (free tier is fine for now)
3. Create proper schema
4. Build basic API routes

### Phase 2: Migration (TOMORROW)
1. Migrate discoveries to database
2. Update frontend to use API
3. Test locally
4. Deploy

### Phase 3: Automation (THIS WEEK)
1. Create admin endpoints
2. Build script to add discoveries
3. Set up CI/CD pipeline
4. Document everything

## Immediate Actions Checklist

### 1. Set up Vercel Postgres
```bash
# Install Vercel CLI if needed
npm i -g vercel

# Link to Vercel project
vercel link

# Add Postgres
vercel postgres create analog-quest-db
```

### 2. Create Environment Variables
```bash
# .env.local
POSTGRES_URL="..."
POSTGRES_PRISMA_URL="..."
POSTGRES_URL_NON_POOLING="..."
POSTGRES_USER="..."
POSTGRES_HOST="..."
POSTGRES_PASSWORD="..."
POSTGRES_DATABASE="..."
```

### 3. Create Database Schema
```sql
-- In Vercel Postgres console
CREATE TABLE discoveries (
  id SERIAL PRIMARY KEY,
  mechanism_1_id INTEGER NOT NULL,
  mechanism_2_id INTEGER NOT NULL,
  similarity DECIMAL(4,4) NOT NULL,
  rating VARCHAR(20) NOT NULL,
  title VARCHAR(500),
  explanation TEXT,
  pattern TEXT,
  domains TEXT[], -- Array of domains
  session_number INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(mechanism_1_id, mechanism_2_id)
);

CREATE TABLE mechanisms (
  id SERIAL PRIMARY KEY,
  paper_title VARCHAR(500),
  description TEXT,
  structural_pattern TEXT,
  domain VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Create API Routes
```typescript
// app/api/discoveries/route.ts
import { sql } from '@vercel/postgres';

export async function GET() {
  const { rows } = await sql`
    SELECT * FROM discoveries
    ORDER BY similarity DESC
  `;
  return Response.json(rows);
}

export async function POST(request: Request) {
  const body = await request.json();
  // Add new discovery
  const { rows } = await sql`
    INSERT INTO discoveries (mechanism_1_id, mechanism_2_id, similarity, rating)
    VALUES (${body.m1_id}, ${body.m2_id}, ${body.similarity}, ${body.rating})
    RETURNING *
  `;
  return Response.json(rows[0]);
}
```

### 5. Update Frontend Data Fetching
```typescript
// lib/data.ts
import { sql } from '@vercel/postgres';

export async function getAllDiscoveries() {
  const { rows } = await sql`
    SELECT d.*,
           m1.description as m1_desc,
           m2.description as m2_desc
    FROM discoveries d
    JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
    JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
    ORDER BY d.similarity DESC
  `;
  return rows;
}
```

## Why This Matters

Without fixing this:
- **Session 82-90**: Discoveries pile up locally, never reach users
- **Chuck's Investment**: Wasted on discoveries nobody sees
- **Project Goal**: "200 discoveries" means nothing if they're on your laptop
- **Scalability**: Can't grow beyond manual JSON editing
- **Collaboration**: Nobody else can contribute

## Success Metrics
- [ ] Can add a discovery without touching JSON
- [ ] New discoveries appear on site within 1 minute
- [ ] Database accessible from Vercel dashboard
- [ ] No manual git commits for data updates
- [ ] Session 82 can add discoveries programmatically

## Timeline
- **Day 1**: Set up Vercel Postgres, create schema
- **Day 2**: Build API routes, migrate data
- **Day 3**: Update frontend, test everything
- **Day 4**: Documentation and handoff

---

**This is MORE IMPORTANT than finding new discoveries!**
A working pipeline for 133 discoveries > 200 discoveries stuck on a laptop
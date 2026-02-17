# Analog Quest - Production Architecture

## Executive Summary

Analog Quest is now a **production-ready application** with a properly architected data pipeline, PostgreSQL database backend, and RESTful API. The system identifies and tracks cross-domain isomorphisms - structural patterns that repeat across different academic fields.

---

## 🏗️ Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Production Frontend                       │
│                   (Next.js on Vercel)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ API Calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Next.js)                       │
│  /api/discoveries  /api/pairs  /api/health                   │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL Queries
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL Database (Local)                   │
│  ┌──────────┐ ┌────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │  Papers  │ │ Mechanisms │ │ Discoveries │ │   Pairs  │ │
│  │  2,397   │ │    305     │ │     125     │ │   133    │ │
│  └──────────┘ └────────────┘ └─────────────┘ └──────────┘ │
│                    pgvector for similarity                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### Core Tables

#### **papers** (2,397 records)
```sql
- id (SERIAL PRIMARY KEY)
- title (TEXT UNIQUE NOT NULL)
- abstract (TEXT)
- domain (TEXT)
- arxiv_id (TEXT)
- openalex_id (TEXT)
- published_date (DATE)
- mechanism_score (FLOAT) -- 0-10 rating
- created_at (TIMESTAMP)
```

#### **mechanisms** (305 records)
```sql
- id (SERIAL PRIMARY KEY)
- paper_id (INTEGER → papers.id)
- description (TEXT) -- Standardized field
- structural_description (TEXT)
- mechanism_type (TEXT)
- domain (TEXT)
- embedding (VECTOR(384)) -- For similarity search
- quality_score (FLOAT)
- extracted_at (TIMESTAMP)
```

#### **discoveries** (125 records)
```sql
- id (SERIAL PRIMARY KEY)
- mechanism_1_id (INTEGER → mechanisms.id)
- mechanism_2_id (INTEGER → mechanisms.id)
- similarity (FLOAT NOT NULL)
- rating (TEXT) -- 'excellent' or 'good'
- explanation (TEXT)
- session (INTEGER)
- curated_at (TIMESTAMP)
UNIQUE(mechanism_1_id, mechanism_2_id)
```

#### **discovered_pairs** (133 records)
```sql
- paper_1_id (INTEGER → papers.id)
- paper_2_id (INTEGER → papers.id)
- discovered_in_session (INTEGER)
PRIMARY KEY(paper_1_id, paper_2_id)
```

### Key Features

- **Vector Similarity**: pgvector extension with HNSW index for fast similarity search
- **Referential Integrity**: Foreign keys ensure data consistency
- **No Orphaned Records**: All relationships validated
- **Optimized Indexes**: On frequently queried fields

---

## 🔌 API Endpoints

### Base URL
- **Local**: `http://localhost:3000/api`
- **Production**: `https://analog.quest/api`

### Endpoints

#### **GET /api/discoveries**
Returns list of discoveries with full details.

**Query Parameters**:
- `rating` - Filter by rating ('excellent'/'good')
- `domain` - Filter by domain
- `minSimilarity` - Minimum similarity threshold (0-1)
- `limit` - Results per page
- `offset` - Skip results
- `sortBy` - Sort field (similarity/rating/session)
- `order` - Sort order (asc/desc)

**Response**: Discoveries with mechanism details, papers, domains

#### **GET /api/discoveries/[id]**
Returns single discovery by ID with optional editorial content.

#### **GET /api/pairs**
Returns discovered pairs with enriched discovery data.

**Query Parameters**:
- `session` - Filter by session number
- `rating` - Filter by rating
- `minSimilarity` - Minimum similarity

#### **GET /api/health**
Health check with database status and statistics.

#### **OPTIONS /api/discoveries**
API capabilities and statistics.

---

## 🚀 Deployment Guide

### For Local Development

1. **Database is already running**:
   ```bash
   # PostgreSQL 17 at localhost:5432
   # Database: analog_quest
   # User: user
   ```

2. **Environment configured** (.env.local):
   ```
   DATABASE_URL=postgresql://user@localhost:5432/analog_quest
   USE_DATABASE=true
   ENABLE_WRITE_OPS=false
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

### For Production Deployment

#### Option 1: Neon (Recommended)

1. **Create Neon account**: https://neon.tech

2. **Create database**:
   - Name: `analog-quest`
   - Region: Closest to your users
   - Copy connection string

3. **Export local data**:
   ```bash
   pg_dump -U user analog_quest > analog_quest_backup.sql
   ```

4. **Import to Neon**:
   ```bash
   psql "postgresql://[neon-connection-string]" < analog_quest_backup.sql
   ```

5. **Update Vercel environment**:
   ```bash
   vercel env add DATABASE_URL production
   # Paste Neon connection string
   ```

#### Option 2: Supabase

1. **Create Supabase project**: https://supabase.com

2. **Get connection details** from Settings → Database

3. **Export/Import data** (same as Neon)

4. **Update environment variables**:
   ```
   DATABASE_URL=[supabase-connection-string]
   SUPABASE_URL=[project-url]
   SUPABASE_ANON_KEY=[anon-key]
   ```

#### Option 3: Self-Hosted PostgreSQL

1. **Set up PostgreSQL 14+** with pgvector extension

2. **Configure SSL** and connection pooling

3. **Use connection string**:
   ```
   postgresql://user:pass@host:5432/analog_quest?sslmode=require
   ```

---

## 📈 Current Statistics

- **Papers Processed**: 2,397
- **Mechanisms Extracted**: 305
- **Discoveries Verified**: 125 (46 excellent, 79 good)
- **Unique Domain Pairs**: 80+
- **Average Similarity**: 0.519
- **Papers with Mechanisms**: 291 (12%)

---

## 🔄 Data Pipeline

### Current Workflow

1. **Paper Fetching** → Python scripts fetch from arXiv/OpenAlex
2. **Mechanism Extraction** → Manual extraction by Claude (Session work)
3. **Embedding Generation** → sentence-transformers/all-MiniLM-L6-v2
4. **Similarity Search** → pgvector with cosine similarity
5. **Discovery Curation** → Manual review of candidates
6. **Database Storage** → PostgreSQL with full referential integrity
7. **API Serving** → Next.js API routes with SQL queries
8. **Frontend Display** → Next.js SSG/SSR

### Key Scripts

**Verification & Health**:
- `scripts/verify_postgres_health.py` - Quick health check
- `scripts/example_queries.py` - Query examples

**Migration** (Already completed):
- `scripts/migrate_postgres_data.py` - Standardized schema
- Scripts migrated 233 old-format mechanisms to new format

---

## ✅ Production Readiness Checklist

### Completed ✓
- [x] PostgreSQL database with proper schema
- [x] All data migrated and standardized
- [x] API routes using database (not JSON)
- [x] Vector similarity search working
- [x] Health monitoring endpoint
- [x] Proper error handling
- [x] Connection pooling
- [x] Environment variable configuration
- [x] No SQL injection vulnerabilities
- [x] Referential integrity maintained

### Remaining Tasks
- [ ] Set up production database (Neon/Supabase)
- [ ] Configure production environment variables
- [ ] Enable database SSL for production
- [ ] Set up database backups
- [ ] Add rate limiting to API
- [ ] Enable write operations (when ready)
- [ ] Add authentication for write endpoints
- [ ] Set up monitoring/alerting

---

## 🔐 Security Considerations

1. **SQL Injection Protection**: Using parameterized queries
2. **Environment Variables**: Sensitive data in .env.local (gitignored)
3. **Write Operations**: Disabled by default (ENABLE_WRITE_OPS=false)
4. **Connection Security**: SSL required for production
5. **Rate Limiting**: Implement before enabling writes

---

## 📝 Next Session Tasks

1. **Choose production database provider** (Neon recommended)
2. **Export PostgreSQL data**: `pg_dump`
3. **Import to production database**
4. **Update Vercel environment variables**
5. **Test production API endpoints**
6. **Monitor performance and errors**

---

## 🎯 Architecture Principles

1. **Single Source of Truth**: PostgreSQL database
2. **Separation of Concerns**: API layer handles all data access
3. **Scalability**: Database-first design scales to millions of records
4. **Maintainability**: Clear schema, documented APIs
5. **Reliability**: Proper error handling, health checks

---

## 📚 Documentation

- **API_DOCUMENTATION.md** - Detailed API reference
- **POSTGRES_MIGRATION_REPORT.md** - Migration details
- **lib/db.ts** - Database connection module
- **scripts/example_queries.py** - Query examples

---

## 🚦 Status

**PRODUCTION READY** with local PostgreSQL. Requires:
1. Production database setup (30 minutes)
2. Environment variable configuration (5 minutes)
3. Data export/import (15 minutes)

Total time to production: ~1 hour

---

**Last Updated**: 2026-02-17
**Architecture Version**: 2.0.0
**Database**: PostgreSQL 17 + pgvector 0.8.1
**API**: Next.js 15.5.12 with TypeScript
**Status**: ✅ Production Ready (pending cloud database)
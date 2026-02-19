# SCALE_UP_PLAN.md - Analog Quest Infrastructure Scale-Up

**Created**: 2026-02-14 (Session 60)
**Status**: Planning Phase
**Timeline**: 3 months (Sessions 60-90)

---

## Executive Summary

**THE PIVOT**: Shift from manual curation (46 discoveries from 2,194 papers) to automated infrastructure capable of processing **50,000+ papers** and surfacing the **200 most groundbreaking cross-domain discoveries**.

**Core Insight**: Manual curation validated our approach (24-40% precision, excellent quality), but doesn't scale. The real value of analog.quest is surfacing discoveries humans would never find - cross-domain gems buried in massive corpora.

**Investment**: ~$500-1,500 total infrastructure cost over 3 months
**Expected Outcome**: 10x paper coverage (2K → 50K), 4x discoveries (46 → 200+), automated pipeline

---

## 1. Current State (Session 59)

### What Works ✓
- **Manual workflow validated**: 46 unique discoveries, 24% (Session 38) to 40% (Session 56) precision
- **LLM extraction**: 200 mechanisms from 2,194 papers, 60-90% hit rate on pre-scored papers
- **Semantic matching**: Embeddings (384-dim) find structural similarity across domains (threshold ≥0.35)
- **Quality standards**: DATA_QUALITY_STANDARDS.md ensures excellent/good ratings
- **Deduplication tracking**: Session 59 system prevents 54% duplication problem
- **Frontend**: analog.quest deployed with 46 discoveries, warm design, mobile responsive

### Current Limitations ⚠️
1. **Manual LLM extraction**: ~15 mechanisms/hour → 13 hours for 200 mechanisms (not scalable)
2. **Manual curation**: ~2-3 hours per 40-50 candidates → weeks for 1,158 candidates
3. **SQLite database**: Not optimized for vector similarity at scale (>10K mechanisms)
4. **Single-machine processing**: No parallelization, no batch processing
5. **Small corpus**: 2,194 papers is <0.01% of arXiv (240M+ works in OpenAlex)

### Progress So Far
- **Papers scored**: 2,194 (100% of corpus, avg 3.31/10)
- **High-value papers**: 631 papers ≥5/10 (28.8% of corpus)
- **Mechanisms extracted**: 200 (from top ~170 papers, 60-90% hit rate)
- **Candidates generated**: 1,158 cross-domain pairs (from 200 mechanisms)
- **Discoveries verified**: 46 unique (11 excellent + 35 good)
- **Precision**: 24-40% in top-30-50 candidates (consistently validated)

---

## 2. Target State (Month 3 - Session 90)

### Scale Goals
- **Papers processed**: 50,000+ (25x increase)
- **Papers scored**: 50,000 (100% coverage)
- **High-value papers**: ~14,000 papers ≥5/10 (assuming 28% rate holds)
- **Mechanisms extracted**: 5,000-8,000 (from top 8,000-10,000 papers, 60-80% hit rate)
- **Candidates generated**: 1-2 million cross-domain pairs (from 5K-8K mechanisms)
- **Discoveries curated**: 200-400 verified (excellent or good)
  - Top-1000 candidates at 30-40% precision = 300-400 discoveries
  - Focus on top-200 highest-quality discoveries for analog.quest

### Quality Goals (maintained)
- **Precision in top-100**: ≥40% (Session 56 standard)
- **Precision in top-1000**: ≥30% (Session 52-54 standard)
- **Rating distribution**: ≥20% excellent, ≥50% good (Session 38 standard)
- **Domain diversity**: ≥15 unique cross-domain pairs (Session 38 standard)
- **Citation accuracy**: 100% working links (Session 45 standard)

### Infrastructure Goals
- **Automated extraction pipeline**: Batch processing with Claude API
- **Vector database**: PostgreSQL + pgvector for similarity search
- **Parallel processing**: Multi-core embedding generation
- **Cost efficiency**: <$1,500 total for 50K papers ($0.03 per paper)
- **Reproducibility**: All steps logged, versioned, auditable

---

## 3. Data Sources Analysis

### 3.1 arXiv (Primary Source)

**Coverage**: ~2.5M papers (physics, cs, math, q-bio, econ, stat)
**Access Methods**:
1. **OAI-PMH (Metadata)**: Preferred for bulk metadata harvesting, updated daily
2. **Amazon S3 (Full Papers)**: Requester Pays bucket with PDFs and source files
3. **Export API**: export.arxiv.org for programmatic PDF downloads

**Rate Limits**:
- API: 1 request per 3 seconds (shared connection)
- Bulk harvesting: 4 requests/second in bursts, 1 second sleep between bursts
- S3: No specific limits (Requester Pays - you pay bandwidth)

**Cost Estimate**:
- Metadata: Free via OAI-PMH
- PDFs via S3: ~$0.01/GB transfer + $0.0004/request
  - 50K papers × 1MB avg × $0.01/GB = **~$0.50 total**
  - 50K requests × $0.0004 = **~$20 total**
  - **Total: ~$20-25 for 50K PDFs**

**Strategy**: Use OAI-PMH for metadata, download abstracts only (not full PDFs) to save costs

**Pros**:
- Already using arXiv API (2,194 papers fetched)
- Excellent domain coverage for our use case
- Free metadata access
- Well-documented API

**Cons**:
- Rate limits require ~3 hours for 50K papers (acceptable for batch processing)
- Doesn't cover all domains (missing humanities, social sciences)

### 3.2 Semantic Scholar (Supplementary Source)

**Coverage**: 200M+ papers (all domains, including humanities/social sciences)
**Access Methods**:
1. **API**: 1 RPS free, batch endpoints available
2. **Bulk Datasets**: Downloadable datasets for high-rate access (recommended)

**Rate Limits**:
- Free API: 1 request/second (86,400 papers/day)
- With API key: 1 RPS (same)
- Bulk datasets: No rate limit (download once, query locally)

**Cost Estimate**:
- API access: Free
- Dataset download: Free (bandwidth from Semantic Scholar)
- Processing time: ~14 hours for 50K papers at 1 RPS

**Strategy**: Use API for targeted queries, download datasets for bulk access

**Pros**:
- Broader domain coverage than arXiv
- Free bulk datasets solve rate limit problem
- Rich metadata (citations, abstracts, fields of study)

**Cons**:
- Dataset download is large (hundreds of GB)
- Need local infrastructure to query datasets
- API rate limits too slow for 50K papers (unless using datasets)

### 3.3 OpenAlex (Best for Bulk Access)

**Coverage**: 240M+ works (comprehensive, ~50K added daily)
**Access Methods**:
1. **API**: 100,000 credits/day free (no key needed)
2. **CLI Tool**: Parallel downloads (200 concurrent connections)
3. **Full Dataset**: Download complete OpenAlex dataset

**Rate Limits**:
- API: 100K credits/day (1 credit per simple request)
  - **Can fetch 100K papers/day** (far exceeds our 50K target!)
- CLI tool: 200 parallel connections, adaptive rate limiting
- Full dataset: No rate limit (download once, query locally)

**Cost Estimate**:
- API access: Free (100K credits/day)
- CLI downloads: Free
- Dataset download: Free (hosted by OpenAlex)
- Processing time: <1 hour for 50K papers (200 parallel connections)

**Strategy**: **PRIMARY CHOICE** - Use OpenAlex API/CLI for bulk metadata harvesting

**Pros**:
- **100K credits/day FREE** (can fetch 50K papers in 1 day!)
- 200 parallel connections (extremely fast)
- Comprehensive coverage (240M+ works)
- Free, open, well-documented
- CLI tool handles checkpointing, rate limiting automatically

**Cons**:
- Newer service (less battle-tested than arXiv)
- Need to validate metadata quality
- Some papers may lack abstracts

### **Recommended Data Strategy**

**Primary**: OpenAlex API/CLI (100K credits/day, 200 parallel connections)
**Supplementary**: arXiv metadata via OAI-PMH (for papers missing in OpenAlex)
**Fallback**: Semantic Scholar datasets (if broader domain coverage needed)

**Rationale**: OpenAlex offers the best balance of speed (100K/day), cost (free), and coverage (240M works).

---

## 4. Automated Extraction Pipeline

### 4.1 Current Manual Process (Session 37-59)

**Steps**:
1. Fetch papers from arXiv API (manually select domains/queries)
2. Score papers for mechanism richness (scripts/score_papers.py, ~2 hours for 2K papers)
3. Extract mechanisms via LLM (manual prompting, ~15 mechanisms/hour)
4. Generate embeddings (sentence-transformers, ~5 min for 200 mechanisms)
5. Match candidates (cosine similarity, threshold ≥0.35, ~1 min)
6. Manually curate top candidates (~2-3 hours per 40-50 candidates)

**Bottlenecks**:
- Step 3 (LLM extraction): **13 hours for 200 mechanisms** (not scalable)
- Step 6 (manual curation): **Weeks for 1,158 candidates** (not scalable)

### 4.2 Proposed Automated Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: BULK DATA INGESTION (Day 1-2)                         │
├─────────────────────────────────────────────────────────────────┤
│ 1. OpenAlex CLI: Download 50K paper metadata                   │
│    - 200 parallel connections                                   │
│    - Filters: published 2020-2025, has abstract, domains       │
│    - Output: 50K papers with abstracts, metadata               │
│    - Time: <1 hour                                              │
│                                                                  │
│ 2. Database Import: Load into PostgreSQL                        │
│    - Bulk INSERT via COPY command                               │
│    - Index on domain, published_date, has_abstract              │
│    - Time: ~10 minutes                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: PAPER SCORING (Day 2-3)                                │
├─────────────────────────────────────────────────────────────────┤
│ 3. Mechanism Richness Scoring: Batch processing                 │
│    - Use existing scripts/score_papers.py algorithm             │
│    - Parallelize across CPU cores (8-16 cores)                  │
│    - Keywords: feedback, network, emergence, control, etc.      │
│    - Output: 50K papers scored (0-10 scale)                     │
│    - Expected: ~14K papers ≥5/10 (28% hit rate from Session 48)│
│    - Time: ~2-4 hours (parallelized)                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: LLM EXTRACTION (Day 3-10, ~$500-800)                   │
├─────────────────────────────────────────────────────────────────┤
│ 4. Batch LLM Extraction: Claude Batch API                       │
│    - Input: Top 8,000-10,000 papers (score ≥6/10)              │
│    - Model: Claude Haiku 4.5 (fast, cheap) or Sonnet 4.5       │
│    - Batch API: 50% discount, 24hr latency acceptable           │
│    - Prompt: Domain-neutral mechanism extraction (Session 37+)  │
│    - Output: 5,000-8,000 mechanisms (60-80% hit rate)          │
│    - Cost (Haiku): ~$0.10 per paper → $800-1,000 total          │
│    - Cost (Sonnet): ~$0.15 per paper → $1,200-1,500 total       │
│    - Time: 7-10 days (batch processing, async)                  │
│                                                                  │
│ 5. Quality Filtering: Remove low-quality mechanisms             │
│    - Heuristics: length >50 chars, contains causal language    │
│    - LLM self-assessment (optional): "Is this domain-neutral?" │
│    - Output: ~5,000 high-quality mechanisms                     │
│    - Time: ~1 hour                                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: EMBEDDING & MATCHING (Day 10-11)                       │
├─────────────────────────────────────────────────────────────────┤
│ 6. Generate Embeddings: sentence-transformers + GPU             │
│    - Model: all-MiniLM-L6-v2 (384 dims, current model)         │
│    - Batch size: 64-128 (GPU parallelization)                  │
│    - Input: 5,000 mechanisms                                    │
│    - Output: 5,000 × 384 embeddings                             │
│    - Time: ~10-30 minutes (GPU) or ~1-2 hours (CPU)            │
│                                                                  │
│ 7. Store in Vector DB: PostgreSQL + pgvector                    │
│    - CREATE EXTENSION pgvector                                  │
│    - CREATE INDEX USING hnsw (embedding vector_l2_ops)         │
│    - Binary quantization: 32× memory reduction, 95% accuracy   │
│    - Time: ~30 minutes (indexing 5K vectors)                    │
│                                                                  │
│ 8. Cross-Domain Matching: Vector similarity search              │
│    - Query: Find k-nearest neighbors across different domains   │
│    - Threshold: ≥0.35 (current threshold from Session 37+)     │
│    - Expected: ~1-2 million candidate pairs                     │
│    - Filter: paper_1_id ≠ paper_2_id (exclude same-paper)      │
│    - Time: ~1-2 hours (HNSW index makes this fast)             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: CANDIDATE RANKING (Day 11)                             │
├─────────────────────────────────────────────────────────────────┤
│ 9. Rank Candidates: Multi-factor scoring                        │
│    - Factor 1: Embedding similarity (0.35-0.74 range)          │
│    - Factor 2: Domain diversity (econ↔physics > cs↔cs.AI)      │
│    - Factor 3: Paper quality scores (prefer ≥7/10 pairs)       │
│    - Factor 4: Mechanism length/richness (prefer detailed)      │
│    - Output: Top-1000 ranked candidates                         │
│    - Time: ~1 hour                                               │
│                                                                  │
│ 10. Deduplication Check: Filter already-discovered pairs        │
│     - Use scripts/check_duplicates.py (Session 59 system)       │
│     - Input: app/data/discovered_pairs.json (46 current pairs)  │
│     - Output: Top-1000 NEW candidates (not already curated)     │
│     - Time: ~5 minutes                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6: MANUAL CURATION (Day 12-30, ~$0-200)                   │
├─────────────────────────────────────────────────────────────────┤
│ 11. Curate Top-200: Manual review (Sessions 61-70)              │
│     - Review top-200 candidates systematically                   │
│     - Rate: excellent / good / weak / false                      │
│     - Expected precision: 40% → ~80 discoveries                  │
│     - Apply DATA_QUALITY_STANDARDS.md                            │
│     - Time: ~10-15 sessions (20-30 hours total)                  │
│                                                                  │
│ 12. Curate Top-1000: Semi-automated (Sessions 71-80)            │
│     - Use LLM to pre-rate candidates (Claude Haiku, cheap)      │
│     - Review only LLM-rated "excellent/good" (~300-400)         │
│     - Final human verification for top-200 discoveries          │
│     - Cost: ~$0.05 per candidate × 800 = ~$40                   │
│     - Time: ~10 sessions (15-20 hours total)                     │
│                                                                  │
│ 13. Update Frontend: Deploy to analog.quest (Session 81+)       │
│     - Add 200+ discoveries to app/data/discoveries.json          │
│     - Rebuild static site (200+ discovery pages)                 │
│     - Validate all citations working (100% standard)             │
│     - Time: ~2-3 hours per deployment                            │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Automation Strategy

**What to Automate**:
1. ✅ **Data ingestion**: OpenAlex CLI (fully automated)
2. ✅ **Paper scoring**: Parallelized keyword-based scoring (fully automated)
3. ✅ **LLM extraction**: Claude Batch API (fully automated, 24hr latency)
4. ✅ **Embedding generation**: sentence-transformers batch processing (fully automated)
5. ✅ **Vector matching**: pgvector similarity search (fully automated)
6. ✅ **Ranking**: Multi-factor scoring algorithm (fully automated)
7. ⚠️ **Curation**: Semi-automated (LLM pre-rating + human final review)

**What to Keep Manual**:
1. **Final quality review**: Human judgment for excellent vs good vs weak
2. **Structural explanation**: Writing detailed "why is this a match?" rationales
3. **Edge case decisions**: Ambiguous matches requiring domain knowledge
4. **Frontend deployment**: Reviewing generated pages before going live

**Why Semi-Automated Curation?**:
- Session 38: 24% precision overall, 67% in top-30 → human review adds value
- LLM can pre-filter weak matches (estimated 50-60% of candidates)
- Final human review ensures quality standards maintained
- Estimated speedup: 3-5x faster than pure manual (review 300 pre-filtered vs 1,000 raw)

---

## 5. Database Optimization Strategy

### 5.1 Current State: SQLite

**Current Schema** (database/papers.db):
```sql
papers: id, title, abstract, domain, arxiv_id, published_date
patterns: id, structural_description, mechanism_type, paper_id  -- deprecated
isomorphisms: id, pattern_1_id, pattern_2_id, similarity_score  -- deprecated
```

**Limitations for Scale**:
- No native vector similarity search (can't index 384-dim embeddings efficiently)
- Single-file database (harder to parallelize writes)
- Limited concurrency (write locks)
- No built-in partitioning (hard to scale to 50K papers, 5K mechanisms)

**What Works**:
- Simple setup, no server needed
- Good for <10K papers, <1K mechanisms
- Fast for exact lookups (papers by ID, domain)

### 5.2 Target State: PostgreSQL + pgvector

**Why PostgreSQL?**:
1. **pgvector extension**: Native vector similarity search (384-dim embeddings)
2. **HNSW indexing**: 9× faster queries, 100× more relevant results (version 0.8.0+)
3. **Binary quantization**: 32× memory reduction, 95% accuracy maintained
4. **Proven at scale**: <100M vectors, 40-80% cost savings vs specialized vector DBs
5. **Familiar SQL**: Can reuse existing query patterns
6. **ACID guarantees**: Reliable writes, transactions, backups

**Proposed Schema**:
```sql
-- Papers table (50K rows)
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    openalex_id TEXT UNIQUE,  -- e.g., "W2741809807"
    arxiv_id TEXT,             -- e.g., "2103.00020" (if available)
    title TEXT NOT NULL,
    abstract TEXT,
    domain TEXT,               -- e.g., "cs", "physics", "q-bio"
    subdomain TEXT,            -- e.g., "cs.AI", "physics.bio-ph"
    published_date DATE,
    mechanism_score FLOAT,     -- 0-10 scale (from scoring algorithm)
    url TEXT,                  -- arXiv or DOI link
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_papers_domain ON papers(domain);
CREATE INDEX idx_papers_score ON papers(mechanism_score DESC);
CREATE INDEX idx_papers_date ON papers(published_date DESC);

-- Mechanisms table (5K-8K rows)
CREATE TABLE mechanisms (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id),
    mechanism TEXT NOT NULL,   -- domain-neutral structural description
    extracted_at TIMESTAMP DEFAULT NOW(),
    extraction_model TEXT,     -- e.g., "claude-haiku-4.5-batch"
    quality_score FLOAT,       -- optional: LLM self-assessment
    embedding vector(384)      -- pgvector type! 384 dims
);

CREATE INDEX idx_mechanisms_paper ON mechanisms(paper_id);

-- HNSW index for fast vector similarity search
CREATE INDEX ON mechanisms USING hnsw (embedding vector_l2_ops);

-- Enable binary quantization (32× memory reduction, 95% accuracy)
ALTER INDEX mechanisms_embedding_idx SET (quantization = 'binary');

-- Discoveries table (200-400 rows)
CREATE TABLE discoveries (
    id SERIAL PRIMARY KEY,
    mechanism_1_id INTEGER REFERENCES mechanisms(id),
    mechanism_2_id INTEGER REFERENCES mechanisms(id),
    similarity FLOAT NOT NULL, -- 0.35-0.74 range
    rating TEXT,               -- 'excellent', 'good', 'weak', 'false'
    explanation TEXT,          -- why is this a match? (structural pattern)
    curated_by TEXT,           -- 'human' or 'llm-haiku' or 'llm-sonnet'
    curated_at TIMESTAMP DEFAULT NOW(),
    session INTEGER,           -- which session discovered this
    UNIQUE(mechanism_1_id, mechanism_2_id)  -- prevent duplicates
);

CREATE INDEX idx_discoveries_rating ON discoveries(rating);
CREATE INDEX idx_discoveries_similarity ON discoveries(similarity DESC);
CREATE INDEX idx_discoveries_session ON discoveries(session);

-- Deduplication tracking (from Session 59)
-- This prevents re-discovering the same pairs across sessions
CREATE TABLE discovered_pairs (
    paper_1_id INTEGER REFERENCES papers(id),
    paper_2_id INTEGER REFERENCES papers(id),
    discovered_in_session INTEGER,
    PRIMARY KEY(paper_1_id, paper_2_id)
);
```

**Migration Plan**:
1. **Session 61**: Install PostgreSQL locally, create schema
2. **Session 62**: Migrate existing 2,194 papers + 200 mechanisms from SQLite
3. **Session 62**: Generate embeddings for 200 mechanisms, insert into PostgreSQL
4. **Session 63**: Validate similarity search matches current results
5. **Session 64**: Migrate 46 discoveries + tracking data
6. **Session 65+**: Use PostgreSQL as primary database for new data

**Vector Search Query Examples**:
```sql
-- Find top-10 most similar mechanisms (cross-domain, excluding same paper)
SELECT
    m1.id AS mechanism_1_id,
    m2.id AS mechanism_2_id,
    m1.embedding <-> m2.embedding AS distance,  -- L2 distance
    1 - (m1.embedding <-> m2.embedding) AS similarity,
    p1.domain AS domain_1,
    p2.domain AS domain_2
FROM mechanisms m1
JOIN mechanisms m2 ON m1.id < m2.id  -- avoid duplicates
JOIN papers p1 ON m1.paper_id = p1.id
JOIN papers p2 ON m2.paper_id = p2.id
WHERE p1.domain != p2.domain  -- cross-domain only
  AND p1.id != p2.id  -- exclude same paper
ORDER BY m1.embedding <-> m2.embedding  -- sort by distance (HNSW index used!)
LIMIT 10;

-- Find mechanisms similar to a specific mechanism (e.g., id=42)
SELECT
    m.id,
    m.mechanism,
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

**Performance Estimates**:
- **Paper lookup**: <1ms (indexed on id, domain, score)
- **Mechanism lookup**: <1ms (indexed on paper_id)
- **Vector similarity (k=10)**: <50ms (HNSW index on 5K vectors)
- **Vector similarity (k=100)**: <200ms (HNSW index)
- **Batch insert (1K papers)**: <5 seconds (COPY command)
- **Batch insert (1K mechanisms)**: <10 seconds (with embeddings)

**Storage Estimates**:
- 50K papers × 2KB avg = **100 MB**
- 5K mechanisms (text) × 500 bytes avg = **2.5 MB**
- 5K mechanisms (embeddings) × 384 dims × 4 bytes = **7.7 MB** (uncompressed)
- 5K mechanisms (embeddings, quantized) × 384 dims / 32 = **0.24 MB** (binary quantization!)
- Discoveries (200) × 1KB = **0.2 MB**
- Total: **~110 MB** (tiny!)

**Cost**: PostgreSQL is free and open-source. Can run locally or on cloud (AWS RDS free tier: 20GB storage, sufficient for our needs).

---

## 6. Cost Analysis

### 6.1 Infrastructure Costs

| Component | Service | Cost | Basis |
|-----------|---------|------|-------|
| **Data Ingestion** | OpenAlex CLI | **$0** | 100K credits/day free |
| **Database** | PostgreSQL (local) | **$0** | Open-source, self-hosted |
| **Embeddings** | sentence-transformers | **$0** | Run locally on CPU/GPU |
| **Vector Search** | pgvector extension | **$0** | PostgreSQL extension |
| **Hosting** | Current setup | **$0** | No change needed |
| **TOTAL (Infrastructure)** | - | **$0** | All free/open-source! |

### 6.2 LLM Extraction Costs (Primary Cost)

**Model Options**:

| Model | Input ($/M tokens) | Output ($/M tokens) | Batch Discount | Total ($/M tokens) |
|-------|-------------------|---------------------|----------------|-------------------|
| Claude Haiku 4.5 | $1.00 | $5.00 | 50% | **$0.50 / $2.50** |
| Claude Sonnet 4.5 | $3.00 | $15.00 | 50% | **$1.50 / $7.50** |

**Extraction Cost Estimates** (50K papers):

Assumptions:
- Input: Abstract (~200 tokens) + Prompt (~300 tokens) = **500 tokens/paper**
- Output: Mechanism (~200 tokens) + Metadata (~50 tokens) = **250 tokens/paper**
- Hit rate: 70% (35K papers yield mechanisms, 15K fail)
- Processed: 50K papers × 500 tokens = **25M input tokens**
- Generated: 35K mechanisms × 250 tokens = **8.75M output tokens**

| Model | Input Cost | Output Cost | Total Cost | Cost/Paper | Cost/Mechanism |
|-------|-----------|-------------|-----------|-----------|---------------|
| **Haiku (Batch)** | $12.50 | $21.88 | **$34.38** | **$0.0007** | **$0.001** |
| **Sonnet (Batch)** | $37.50 | $65.63 | **$103.13** | **$0.002** | **$0.003** |

**Scaled Extraction Costs** (targeting 8,000 papers for 5,000-8,000 mechanisms):

| Model | 8K Papers Input | 5.6K Mechanisms Output | Total Cost |
|-------|----------------|------------------------|-----------|
| **Haiku (Batch)** | $2.00 | $3.50 | **$5.50** |
| **Sonnet (Batch)** | $6.00 | $10.50 | **$16.50** |

**Recommendation**: **Start with Haiku** ($5.50 for 8K papers → 5K-6K mechanisms)
- If quality is good: continue with Haiku (cheap!)
- If quality is poor: upgrade to Sonnet ($16.50) for better extraction
- Session 37-55 used manual prompting (not batch), so quality comparison needed

### 6.3 Optional: LLM-Assisted Curation Costs

**Semi-Automated Curation** (Phase 6, Step 12):

Assumptions:
- Input: 2 mechanisms × 200 tokens = 400 tokens + Prompt (~200 tokens) = **600 tokens/candidate**
- Output: Rating + Reasoning (~150 tokens) = **150 tokens/candidate**
- Candidates: 800 (top-1000 minus top-200 manually curated)

| Model | Input Cost | Output Cost | Total Cost | Cost/Candidate |
|-------|-----------|-------------|-----------|---------------|
| **Haiku (Standard)** | $0.48 | $0.12 | **$0.60** | **$0.0008** |
| **Sonnet (Standard)** | $1.44 | $1.13 | **$2.57** | **$0.003** |

**Recommendation**: **Haiku for pre-rating** ($0.60 for 800 candidates)
- Fast, cheap, good enough for filtering weak matches
- Human final review for top-200 ensures quality

### 6.4 Total Cost Estimate (3-Month Scale-Up)

| Phase | Component | Model/Service | Cost |
|-------|-----------|--------------|------|
| 1-2 | Data ingestion (50K papers) | OpenAlex CLI | $0 |
| 3 | LLM extraction (8K papers) | Haiku Batch | $5.50 |
| 3 | LLM extraction (8K papers) | Sonnet Batch (alt) | $16.50 |
| 4-5 | Embeddings + Matching | sentence-transformers + pgvector | $0 |
| 6 | LLM pre-rating (800 candidates) | Haiku Standard | $0.60 |
| **TOTAL (Haiku path)** | - | - | **$6.10** |
| **TOTAL (Sonnet path)** | - | - | **$17.10** |

**Stretch Goal** (processing all 50K papers for 35K mechanisms):
- Haiku Batch: **$34.38** total
- Sonnet Batch: **$103.13** total

**Final Recommendation**: **Budget $50-150 for LLM costs**
- Start conservative: 8K papers × Haiku = **$5.50**
- Validate quality, then scale: 50K papers × Haiku = **$34.38** OR Sonnet = **$103.13**
- Add buffer for experimentation, re-extraction, curation assistance

**Infrastructure costs remain $0** (all open-source, self-hosted).

**TOTAL 3-MONTH BUDGET: $50-150** (LLM costs only)

---

## 7. Success Metrics

### 7.1 Quantitative Metrics

**Volume Metrics**:
- Papers processed: **50,000** (target) vs 2,194 (current) = **23x increase**
- Mechanisms extracted: **5,000-8,000** (target) vs 200 (current) = **25-40x increase**
- Discoveries curated: **200-400** (target) vs 46 (current) = **4-9x increase**
- Candidates generated: **1-2M** (target) vs 1,158 (current) = **864-1,727x increase**

**Quality Metrics** (must maintain Session 38-59 standards):
- Precision (top-100): **≥40%** (Session 56 standard)
- Precision (top-1000): **≥30%** (Session 52-54 standard)
- Excellent discoveries: **≥20%** of curated (Session 38: 10/30 = 33%)
- Good discoveries: **≥50%** of curated (Session 38: 20/30 = 67%)
- Citation accuracy: **100%** working links (Session 45 standard)

**Efficiency Metrics**:
- Cost per paper: **<$0.03** ($50 budget / 50K papers = $0.001, with buffer)
- Cost per mechanism: **<$0.01** ($50 / 5K mechanisms = $0.01)
- Cost per discovery: **<$0.50** ($50 / 200 discoveries = $0.25, with buffer)
- Extraction time: **<10 days** (batch processing, async)
- Manual curation time: **<40 hours** (20 sessions × 2 hours)

**Diversity Metrics**:
- Domain pairs: **≥15** unique cross-domain connections (Session 38 standard)
- Top domain pairs: **≥5 discoveries each** (Session 38: econ↔q-bio had 7)
- Similarity range: **0.35-0.74** (Session 37+ range maintained)

### 7.2 Qualitative Metrics

**Discovery Quality** (manual evaluation):
- **"Holy Shit" Moments**: ≥5 discoveries that are genuinely surprising/groundbreaking
  - Example: Session 38 #1 (tragedy of commons: econ↔biology) was rated "holy shit"
  - Target: 5 out of 200 = 2.5% "holy shit" rate
- **Structural Depth**: ≥50% of discoveries explain multi-level mechanisms (not just vocabulary overlap)
  - Example: Session 38 heterogeneity as double-edged sword (Session 52 rediscovered)
- **Cross-Domain Novelty**: ≥30% of discoveries connect distant domains (econ↔physics, bio↔cs)
  - Example: Session 38 had 14 unique domain pairs (highly diverse)

**User Value** (analog.quest visitors):
- **Browsable discoveries**: 200 discovery pages (vs current 46) = 4x content
- **Filter diversity**: ≥15 domain pairs (vs current 14) = more filter options
- **Similarity distribution**: Discoveries span 0.35-0.74 range (show structural diversity)
- **Explanation quality**: Every discovery has detailed structural explanation (maintained standard)

**Process Quality**:
- **Reproducibility**: All steps logged, versioned, auditable (database audit trail)
- **Deduplication**: 0% silent duplication (Session 59 tracking system prevents this)
- **Error handling**: Graceful failures, checkpointing, resume capability (OpenAlex CLI has this)
- **Monitoring**: Track hit rates, precision, costs at each phase

### 7.3 Milestone Checklist (Sessions 60-90)

**Month 1: Infrastructure (Sessions 60-70)**
- [ ] Session 60: SCALE_UP_PLAN.md created ✓ (this document)
- [ ] Session 61: PostgreSQL + pgvector installed and tested
- [ ] Session 62: Migrate 2,194 papers + 200 mechanisms to PostgreSQL
- [ ] Session 63: Validate vector similarity search matches current results
- [ ] Session 64: Migrate 46 discoveries + deduplication tracking
- [ ] Session 65: OpenAlex CLI test (fetch 1K papers, validate quality)
- [ ] Session 66-67: Batch LLM extraction test (100 papers, Haiku vs Sonnet quality comparison)
- [ ] Session 68-69: Full pipeline test (1K papers end-to-end)
- [ ] Session 70: Infrastructure validation complete, ready to scale

**Month 2: Scaling (Sessions 71-80)**
- [ ] Session 71-72: Fetch 50K papers via OpenAlex CLI
- [ ] Session 73: Score all 50K papers for mechanism richness
- [ ] Session 74-76: Batch LLM extraction (8K-10K papers → 5K-8K mechanisms)
- [ ] Session 77: Generate embeddings for 5K-8K mechanisms
- [ ] Session 78: Vector matching (1-2M candidates generated)
- [ ] Session 79: Rank top-1000 candidates (multi-factor scoring)
- [ ] Session 80: Deduplication check (filter known 46 pairs)

**Month 3: Curation & Deployment (Sessions 81-90)**
- [ ] Session 81-85: Curate top-200 candidates (manual, high-quality)
  - Expected: 60-80 discoveries (40% precision)
- [ ] Session 86-88: LLM-assisted curation (next 300-400 candidates)
  - Expected: 90-120 more discoveries (30% precision)
- [ ] Session 89: Update analog.quest with 200+ discoveries
  - Rebuild static site, validate citations
- [ ] Session 90: Retrospective, documentation, launch celebration 🎉

**Success Criteria** (by Session 90):
- ✅ 200+ verified discoveries (excellent or good)
- ✅ 5,000+ mechanisms extracted
- ✅ 50,000+ papers processed
- ✅ analog.quest deployed with 200+ discoveries
- ✅ Total cost <$150
- ✅ Quality standards maintained (≥40% precision in top-100)
- ✅ Infrastructure documented and reproducible

---

## 8. Three-Month Roadmap

### Month 1: Infrastructure Setup (Sessions 60-70)

**Focus**: Build automated pipeline, migrate to PostgreSQL, validate quality

**Week 1-2 (Sessions 60-65)**:
- ✅ Session 60: Create SCALE_UP_PLAN.md (this document)
- Session 61: Install PostgreSQL + pgvector locally
  - Set up database, create schema, test vector similarity
  - Time: 2-3 hours
- Session 62: Migrate existing data (2,194 papers, 200 mechanisms)
  - Export from SQLite, import to PostgreSQL
  - Generate embeddings for 200 mechanisms
  - Time: 2-3 hours
- Session 63: Validate migration
  - Reproduce current 1,158 candidates using pgvector
  - Compare with Session 55 results (should match exactly)
  - Time: 1-2 hours
- Session 64: Migrate discoveries + tracking
  - Import 46 discoveries from app/data/discoveries.json
  - Import discovered_pairs.json for deduplication tracking
  - Time: 1-2 hours
- Session 65: Test OpenAlex CLI
  - Fetch 1,000 papers via CLI (domains: cs, physics, q-bio)
  - Validate metadata quality (abstracts present, dates correct)
  - Time: 1-2 hours

**Week 3-4 (Sessions 66-70)**:
- Session 66: LLM extraction test (Haiku vs Sonnet)
  - Extract mechanisms from 50 papers using Haiku Batch
  - Extract mechanisms from same 50 papers using Sonnet Batch
  - Compare quality: hit rate, structural depth, domain-neutrality
  - Decision: Choose Haiku OR Sonnet for full scale-up
  - Cost: ~$0.50 (Haiku) + ~$1.50 (Sonnet) = **$2.00 test**
  - Time: 2-3 hours (setup) + 24 hours (batch processing) + 2 hours (evaluation)
- Session 67: Quality analysis
  - Rate 50 extracted mechanisms: excellent / good / weak / false
  - Measure hit rate (% papers yielding usable mechanisms)
  - Compare to Session 37-55 manual extraction standards
  - Time: 2-3 hours
- Session 68: End-to-end pipeline test (1K papers)
  - Fetch 1K papers via OpenAlex CLI
  - Score for mechanism richness
  - Extract top 100 papers via batch LLM
  - Generate embeddings, match candidates
  - Review top-20 candidates for quality
  - Time: 3-4 hours (setup) + 24 hours (batch) + 2 hours (review)
- Session 69: Pipeline validation
  - Measure precision (top-20 candidates from 1K-paper test)
  - Expected: 40-50% precision (based on Session 38-56)
  - If <30%: debug and iterate
  - If ≥30%: pipeline validated, ready to scale
  - Time: 2-3 hours
- Session 70: Documentation
  - Document pipeline in PIPELINE.md (step-by-step instructions)
  - Create scripts for automation (fetch, score, extract, embed, match)
  - Commit all changes, tag v2.0 (scale-up infrastructure complete)
  - Time: 2-3 hours

**Month 1 Deliverables**:
- [x] SCALE_UP_PLAN.md (Session 60)
- [ ] PostgreSQL + pgvector operational (Sessions 61-64)
- [ ] 2,194 papers + 200 mechanisms + 46 discoveries migrated (Session 62-64)
- [ ] OpenAlex CLI tested (Session 65)
- [ ] LLM extraction quality validated (Haiku vs Sonnet) (Sessions 66-67)
- [ ] End-to-end pipeline tested on 1K papers (Sessions 68-69)
- [ ] PIPELINE.md documentation complete (Session 70)

**Month 1 Cost**: **~$2-5** (LLM testing only)

---

### Month 2: Scale-Up Execution (Sessions 71-80)

**Focus**: Process 50K papers, extract 5K-8K mechanisms, generate 1M+ candidates

**Week 5-6 (Sessions 71-76)**:
- Session 71: Fetch 50K papers via OpenAlex CLI
  - Domains: cs, physics, q-bio, econ, math, stat (top domains from Session 48)
  - Filters: published 2020-2025, has abstract
  - Time: 1-2 hours (200 parallel connections, very fast!)
  - Import to PostgreSQL
- Session 72: Validate 50K papers
  - Check metadata quality: abstracts present, domains labeled correctly
  - Sample 100 papers manually: are they relevant?
  - Time: 1-2 hours
- Session 73: Score 50K papers
  - Run mechanism richness scoring (parallelized)
  - Expected: ~14K papers ≥5/10 (28% hit rate from Session 48)
  - Time: 2-4 hours (parallelized across CPU cores)
- Session 74: Batch LLM extraction (Part 1)
  - Select top 4K papers (score ≥7/10)
  - Submit to Claude Batch API (Haiku or Sonnet, based on Session 66 test)
  - Cost: ~$2.75 (Haiku) or ~$8.25 (Sonnet)
  - Time: 2 hours (setup) + 24-48 hours (batch processing)
- Session 75: Batch LLM extraction (Part 2)
  - Select next 4K papers (score 6-7/10)
  - Submit to Claude Batch API
  - Cost: ~$2.75 (Haiku) or ~$8.25 (Sonnet)
  - Time: 2 hours (setup) + 24-48 hours (batch processing)
- Session 76: Process batch results
  - Retrieve ~5K-8K mechanisms from batch API
  - Quality filter: remove very short (<50 chars) or generic mechanisms
  - Import to PostgreSQL mechanisms table
  - Time: 2-3 hours

**Week 7-8 (Sessions 77-80)**:
- Session 77: Generate embeddings
  - sentence-transformers on 5K-8K mechanisms
  - GPU: ~30 mins, CPU: ~2 hours
  - Import embeddings to PostgreSQL
  - Create HNSW index (fast vector similarity search)
  - Time: 1-2 hours
- Session 78: Vector matching
  - Query: Find k-nearest neighbors for each mechanism (cross-domain only)
  - Threshold: ≥0.35 (current standard)
  - Expected: 1-2 million candidate pairs
  - Filter: paper_1_id ≠ paper_2_id (exclude same-paper)
  - Store top-10K candidates (sorted by similarity)
  - Time: 1-2 hours (HNSW index makes this fast!)
- Session 79: Multi-factor ranking
  - Factor 1: Embedding similarity (weight: 0.4)
  - Factor 2: Domain diversity (weight: 0.2)
  - Factor 3: Paper quality scores (weight: 0.2)
  - Factor 4: Mechanism richness (weight: 0.2)
  - Rank top-1000 candidates
  - Time: 1-2 hours
- Session 80: Deduplication check
  - Load discovered_pairs.json (46 current pairs)
  - Filter top-1000 candidates against known pairs
  - Expected: ~990-1000 NEW candidates (minimal duplication)
  - Save to examples/session80_top1000_candidates.json
  - Time: 1 hour

**Month 2 Deliverables**:
- [ ] 50,000 papers fetched and imported (Session 71-72)
- [ ] 50,000 papers scored (Session 73)
- [ ] 5,000-8,000 mechanisms extracted (Sessions 74-76)
- [ ] 5,000-8,000 embeddings generated (Session 77)
- [ ] 1-2M candidates matched, top-1000 ranked (Sessions 78-79)
- [ ] Top-1000 deduplicated (Session 80)

**Month 2 Cost**: **~$5.50-16.50** (LLM extraction for 8K papers)

---

### Month 3: Curation & Launch (Sessions 81-90)

**Focus**: Curate 200+ discoveries, deploy to analog.quest, celebrate!

**Week 9-10 (Sessions 81-85)**:
- Session 81-82: Curate top-50 candidates (manual)
  - Review systematically: excellent / good / weak / false
  - Expected precision: 40% → 20 discoveries
  - Apply DATA_QUALITY_STANDARDS.md
  - Time: 2-3 hours per session (5-6 hours total)
- Session 83-84: Curate next 50 candidates (manual)
  - Ranks 51-100 from top-1000
  - Expected precision: 35% → 17-18 discoveries
  - Time: 2-3 hours per session (5-6 hours total)
- Session 85: Curate next 100 candidates (manual)
  - Ranks 101-200 from top-1000
  - Expected precision: 30% → 30 discoveries
  - Time: 3-4 hours
  - **Total so far: 20 + 18 + 30 = 68 discoveries** (added to existing 46 = 114 total)

**Week 11 (Sessions 86-88)**:
- Session 86-87: LLM-assisted curation (ranks 201-500)
  - Submit 300 candidates to Claude Haiku for pre-rating
  - Prompt: "Rate this mechanism pair: excellent / good / weak / false. Explain."
  - Cost: ~$0.18 (Haiku standard API, 300 candidates)
  - Review only LLM-rated "excellent/good" (~100-120 candidates)
  - Manual verification: accept 60-70 as genuine discoveries
  - Time: 2-3 hours per session (5-6 hours total)
- Session 88: LLM-assisted curation (ranks 501-1000)
  - Submit 500 candidates to Claude Haiku for pre-rating
  - Cost: ~$0.30 (Haiku standard API, 500 candidates)
  - Review only LLM-rated "excellent/good" (~150-200 candidates)
  - Manual verification: accept 50-60 as genuine discoveries
  - Time: 3-4 hours
  - **Total added: 60-70 + 50-60 = 110-130 discoveries**
  - **Grand total: 46 (existing) + 68 (manual) + 110-130 (LLM-assisted) = 224-244 discoveries!**

**Week 12 (Sessions 89-90)**:
- Session 89: Update analog.quest
  - Add 180-200 new discoveries to app/data/discoveries.json
  - Rebuild static site (224-244 discovery pages + other pages)
  - Validate all citations working (100% standard)
  - Test filters, sorting, navigation
  - Deploy to analog.quest
  - Time: 3-4 hours
- Session 90: Retrospective & celebration 🎉
  - Document lessons learned in RETROSPECTIVE_SESSION90.md
  - Update METRICS.md with final stats
  - Update PROGRESS.md with Session 90 summary
  - Create SESSION90_LAUNCH.md announcement
  - Commit all changes, tag v3.0 (scale-up complete!)
  - Time: 2-3 hours
  - **CELEBRATE**: 200+ discoveries, 50K papers, automated pipeline! 🎉🎉🎉

**Month 3 Deliverables**:
- [ ] 68 discoveries curated manually (top-200 candidates) (Sessions 81-85)
- [ ] 110-130 discoveries curated with LLM assistance (ranks 201-1000) (Sessions 86-88)
- [ ] analog.quest updated with 224-244 total discoveries (Session 89)
- [ ] RETROSPECTIVE_SESSION90.md complete (Session 90)
- [ ] v3.0 tagged, scale-up complete! (Session 90)

**Month 3 Cost**: **~$0.50** (LLM-assisted curation for 800 candidates)

---

### Summary Timeline

| Month | Sessions | Focus | Deliverables | Cost |
|-------|----------|-------|--------------|------|
| **1** | 60-70 | Infrastructure | PostgreSQL, pipeline tested | **$2-5** |
| **2** | 71-80 | Scale-Up | 50K papers, 5K-8K mechanisms, 1M+ candidates | **$5.50-16.50** |
| **3** | 81-90 | Curation | 200+ discoveries, analog.quest launch | **$0.50** |
| **TOTAL** | 60-90 | Full cycle | 50K papers, 224-244 discoveries, automated pipeline | **$8-22** |

**TOTAL COST: $8-22** (well under $50-150 budget!)

**TIME INVESTMENT**: ~30 sessions × 2-3 hours = **60-90 hours over 3 months**

---

## 9. Risks & Mitigation

### 9.1 Technical Risks

**Risk 1: LLM extraction quality degrades at scale**
- **Description**: Haiku/Sonnet batch extraction may produce lower-quality mechanisms than manual (Sessions 37-55)
- **Likelihood**: Medium
- **Impact**: High (affects all downstream curation)
- **Mitigation**:
  - Session 66-67: Test Haiku vs Sonnet on 50 papers, compare to manual baseline
  - If Haiku <50% hit rate: use Sonnet (3x cost but better quality)
  - If both <50%: refine prompts, test few-shot examples, consider GPT-4 as alternative
  - Checkpoints: Validate quality every 1K papers, adjust if needed
- **Fallback**: Return to manual extraction for top papers (slower but proven to work)

**Risk 2: OpenAlex metadata quality issues**
- **Description**: 50K papers may lack abstracts, have incorrect domains, or low relevance
- **Likelihood**: Low-Medium (OpenAlex is well-maintained, but some gaps exist)
- **Impact**: Medium (need to filter/rescore papers)
- **Mitigation**:
  - Session 65: Test on 1K papers, manually sample 100 for quality check
  - Session 72: Validate 50K papers (check abstract presence, domain accuracy)
  - If >20% lack abstracts: supplement with arXiv API (for arXiv papers)
  - If domain labels poor: use subdomains (e.g., "cs.AI" vs "cs") for better filtering
- **Fallback**: Use arXiv OAI-PMH as primary source (slower but higher quality)

**Risk 3: pgvector performance degrades with 5K-8K vectors**
- **Description**: HNSW index may be slow for 1M+ similarity searches
- **Likelihood**: Low (pgvector 0.8.0 handles <100M vectors efficiently)
- **Impact**: Medium (slower matching, but doesn't block progress)
- **Mitigation**:
  - Session 77: Test HNSW index on 5K vectors, measure query time
  - If >1 second per query: enable binary quantization (32× speedup)
  - If still slow: batch queries, use GPU-accelerated similarity (faiss as alternative)
  - Monitor performance: if >5 minutes for 1M comparisons, optimize
- **Fallback**: Use faiss library (Facebook AI Similarity Search, faster for large-scale)

**Risk 4: Batch API delays exceed 24 hours**
- **Description**: Claude Batch API may take >24 hours during high-load periods
- **Likelihood**: Low-Medium (Anthropic SLA is 24 hours, but delays possible)
- **Impact**: Low (delays timeline but doesn't block progress)
- **Mitigation**:
  - Build buffer into timeline: expect 24-48 hours per batch (not critical path)
  - Session 74-75: Submit batches early in week (avoid weekend delays)
  - Monitor batch status: if >48 hours, contact Anthropic support
- **Fallback**: Use standard API with rate limiting (slower but guaranteed)

### 9.2 Quality Risks

**Risk 5: Precision drops below 30% at scale**
- **Description**: Top-1000 candidates may have <30% precision (vs 30-40% in Sessions 52-56)
- **Likelihood**: Medium (larger corpus may dilute quality)
- **Impact**: Medium (need to review more candidates to find 200 discoveries)
- **Mitigation**:
  - Session 79: Multi-factor ranking (not just similarity) to boost precision
  - Session 81: Validate precision on top-50 candidates (if <30%, adjust ranking weights)
  - If precision <20%: focus on top-500 instead of top-1000 (trade volume for quality)
- **Fallback**: Curate top-500 at 30% precision = 150 discoveries (still exceeds 200 goal when combined with existing 46)

**Risk 6: LLM-assisted curation introduces false positives**
- **Description**: Haiku pre-rating may accept weak matches as "good"
- **Likelihood**: Medium (LLMs can be overconfident)
- **Impact**: Medium (false positives dilute analog.quest quality)
- **Mitigation**:
  - Session 86: Test LLM pre-rating on 20 candidates, compare to human ratings
  - Measure agreement: if <70% agreement, adjust LLM prompt or use Sonnet
  - Final human verification: all LLM-rated "excellent" must be human-reviewed
- **Fallback**: Manual curation for all candidates (slower but maintains quality)

**Risk 7: Domain diversity decreases (too many cs↔physics, not enough econ↔bio)**
- **Description**: 5K-8K mechanisms may be skewed toward common domains (cs, physics)
- **Likelihood**: Medium (Sessions 48-55 had 35% cs, 26% q-bio, 16.5% physics)
- **Impact**: Low (still find discoveries, but less diversity)
- **Mitigation**:
  - Session 71: Fetch balanced domains (25% cs, 25% physics, 25% q-bio, 25% other)
  - Session 73: Stratified sampling when selecting 8K papers (ensure domain balance)
  - Session 79: Boost domain-diverse pairs in ranking (e.g., econ↔physics > cs↔cs.AI)
- **Fallback**: Accept domain skew, focus on quality over diversity

### 9.3 Cost Risks

**Risk 8: LLM costs exceed $150 budget**
- **Description**: Batch API costs higher than estimated (re-extraction, experimentation, etc.)
- **Likelihood**: Low-Medium (estimates are conservative, but experimentation adds cost)
- **Impact**: Low (Chuck's Claude Max plan has high limits)
- **Mitigation**:
  - Track costs daily: monitor token usage, project total before committing to full 50K
  - Session 74-76: Start with 8K papers ($5.50-16.50), validate quality before scaling
  - If costs trending >$100: pause, reassess, decide whether to continue with Haiku or stop at 8K
- **Fallback**: Stop at 8K papers (still 25x scale-up from current 200 mechanisms)

**Risk 9: Infrastructure costs (PostgreSQL hosting)**
- **Description**: Local PostgreSQL may need cloud hosting (AWS RDS, etc.)
- **Likelihood**: Low (local hosting sufficient for 110 MB database)
- **Impact**: Low ($0-20/month if needed)
- **Mitigation**:
  - Session 61: Test local PostgreSQL, measure storage/memory usage
  - If local performance poor: use AWS RDS free tier (20 GB, 750 hours/month free)
  - Monitor usage: if exceeding free tier, optimize queries or upgrade ($20/month)
- **Fallback**: Continue with SQLite for papers, use PostgreSQL only for mechanisms/embeddings

### 9.4 Timeline Risks

**Risk 10: Manual curation takes longer than expected**
- **Description**: Reviewing 200 candidates may take 10-15 sessions (20-30 hours), not 5 sessions
- **Likelihood**: Medium (Session 56: 2.5 hours for 50 candidates = 10 hours for 200)
- **Impact**: Low (delays launch but doesn't block progress)
- **Mitigation**:
  - Session 81-85: Allocate 10-15 sessions for top-200 curation (realistic timeline)
  - Use LLM-assisted curation earlier (Session 86-88) to speed up ranks 101-200
  - If behind schedule: accept 150 discoveries instead of 200 (still 3x current 46)
- **Fallback**: Launch with 150 discoveries in Month 3, continue curation in Month 4

**Risk 11: Batch API delays compound (>48 hours per batch)**
- **Description**: Sessions 74-76 batch processing takes 1 week instead of 2-3 days
- **Likelihood**: Low
- **Impact**: Low (delays Month 2 timeline by 3-4 days)
- **Mitigation**:
  - Build buffer: expect 48 hours per batch (not 24 hours)
  - Submit batches in parallel (if Anthropic allows): Sessions 74-75 can overlap
  - Monitor queue: if delays >48 hours, escalate to Anthropic support
- **Fallback**: Extend Month 2 by 1 week (Sessions 71-85 instead of 71-80)

---

## 10. Open Questions & Decisions

### 10.1 Technical Decisions

**Q1: Haiku vs Sonnet for batch extraction?**
- **Test in Session 66-67**: Extract 50 papers with both, compare quality
- **Decision criteria**:
  - If Haiku ≥70% hit rate: use Haiku ($5.50 for 8K papers)
  - If Haiku 50-70% hit rate but Sonnet >80%: use Sonnet ($16.50 for 8K papers)
  - If both <50% hit rate: refine prompts, test GPT-4 as alternative
- **Recommendation**: Start with Haiku (cheap), upgrade to Sonnet if quality poor

**Q2: Local PostgreSQL vs cloud hosting?**
- **Test in Session 61**: Install locally, measure performance
- **Decision criteria**:
  - If local works well (<100ms queries): use local (free)
  - If local slow (>1 second queries): use AWS RDS free tier
  - If exceeding free tier: upgrade to $20/month tier
- **Recommendation**: Start local, migrate to cloud only if needed

**Q3: How many mechanisms to extract? (5K vs 8K vs 35K)**
- **Decision criteria**:
  - 5K mechanisms: Conservative, proven to work (25x scale-up), $5.50 (Haiku)
  - 8K mechanisms: Balanced, high confidence, $8.80 (Haiku)
  - 35K mechanisms: Aggressive, max coverage, $34.38 (Haiku) or $103.13 (Sonnet)
- **Recommendation**: Start with 8K papers → 5K-6K mechanisms (Sessions 74-76), validate quality, then decide whether to scale to 35K in Month 4+

**Q4: Binary quantization for embeddings?**
- **Test in Session 77**: Generate embeddings, test with/without quantization
- **Decision criteria**:
  - If quantization maintains >90% accuracy: enable (32× memory reduction!)
  - If accuracy drops to <90%: disable (7.7 MB uncompressed is still tiny)
- **Recommendation**: Enable quantization (pgvector 0.8.0+ maintains 95% accuracy)

### 10.2 Process Decisions

**Q5: How much manual curation vs LLM-assisted?**
- **Options**:
  - Option A: 100% manual (top-1000) → 300-400 discoveries, 40-60 hours
  - Option B: Manual top-200 + LLM top-800 → 200-300 discoveries, 20-30 hours
  - Option C: Manual top-100 + LLM top-900 → 150-250 discoveries, 15-20 hours
- **Recommendation**: Option B (Session 81-85 manual, Session 86-88 LLM-assisted)
  - Maintains quality for top-200 (manual review ensures excellence)
  - Speeds up ranks 201-1000 (LLM pre-filter reduces review time 3-5x)
  - Balances quality (top-200 precision ≥40%) and efficiency (20-30 hours total)

**Q6: When to deploy to analog.quest?**
- **Options**:
  - Option A: Deploy at 100 discoveries (Session 85, Month 3 Week 2)
  - Option B: Deploy at 150 discoveries (Session 87, Month 3 Week 3)
  - Option C: Deploy at 200 discoveries (Session 89, Month 3 Week 4)
- **Recommendation**: Option C (wait for 200+)
  - "200+ discoveries" is a strong psychological milestone (vs current 46)
  - Ensures high-quality launch (not rushed)
  - Gives time to validate all citations, test filters, polish design

**Q7: What to do with 800 remaining candidates (ranks 201-1000)?**
- **Options**:
  - Option A: LLM-assisted curation (Session 86-88) → 110-130 more discoveries
  - Option B: Save for Month 4 (focus on top-200 in Month 3)
  - Option C: Skip (top-200 sufficient for 80+ discoveries + existing 46 = 126 total)
- **Recommendation**: Option A (LLM-assisted curation)
  - Cost is low ($0.50 for 800 candidates)
  - Potential yield is high (110-130 more discoveries at 30% precision)
  - Reaches 200+ discovery goal confidently (not relying on top-200 achieving 40% precision)

### 10.3 Strategic Decisions

**Q8: Should we expand to non-arXiv domains (Semantic Scholar, PubMed)?**
- **Pros**: Broader coverage (humanities, medicine, social sciences beyond econ)
- **Cons**: More heterogeneous quality, harder to score for mechanism richness
- **Recommendation**: No, not in Sessions 60-90
  - Focus on arXiv/OpenAlex domains (cs, physics, q-bio, econ, math, stat) = proven to work
  - 240M works in OpenAlex is far more than we can process in 3 months
  - Expanding domains adds complexity without clear quality benefit
  - Revisit in Month 4+ if we exhaust high-quality arXiv papers

**Q9: What happens after Session 90?**
- **Options**:
  - Option A: Continuous curation (Sessions 91+: curate next 1000 candidates)
  - Option B: Second scale-up (fetch another 50K papers, extract 5K more mechanisms)
  - Option C: Shift focus to user acquisition (promote analog.quest, gather feedback)
  - Option D: Research improvements (better extraction prompts, better ranking algorithms)
- **Recommendation**: Wait for Session 90 retrospective to decide
  - If precision ≥40% in top-1000: Option A (continuous curation)
  - If precision <30% in top-1000: Option D (improve algorithms before more data)
  - If analog.quest has visitors: Option C (user-driven improvements)
  - If still excited about scale: Option B (second wave of 50K papers)

**Q10: Should we publish a paper/blog post about this approach?**
- **Pros**: Shares methodology, attracts collaborators, validates research value
- **Cons**: Takes time, may not be novel enough for academic publication
- **Recommendation**: Wait until Session 90
  - If we find ≥5 "holy shit" discoveries: write blog post highlighting them
  - If precision ≥40% consistently: methodology is publication-worthy
  - If analog.quest gets organic traffic: user validation suggests interest
  - Draft in Month 4, publish in Month 5

---

## 11. Success Definition

**What does success look like by Session 90?**

### Minimum Success (Must-Have)
1. **150+ verified discoveries** deployed to analog.quest
2. **50K papers processed** and scored
3. **3K+ mechanisms extracted** (15x current 200)
4. **Pipeline documented and reproducible** (PIPELINE.md complete)
5. **Total cost <$150** (within budget)
6. **Quality maintained**: Precision ≥30% in top-100 (Session 38 standard)

### Target Success (Should-Have)
1. **200+ verified discoveries** deployed to analog.quest
2. **50K papers processed** and scored
3. **5K+ mechanisms extracted** (25x current 200)
4. **Pipeline automated** (batch scripts for fetch, score, extract, match)
5. **Total cost <$50** (under budget!)
6. **Quality maintained**: Precision ≥40% in top-100 (Session 56 standard)
7. **Domain diversity**: ≥15 unique domain pairs (Session 38 standard)
8. **Citation accuracy**: 100% working links (Session 45 standard)

### Stretch Success (Nice-to-Have)
1. **300+ verified discoveries** deployed to analog.quest
2. **50K papers processed** and scored
3. **8K+ mechanisms extracted** (40x current 200)
4. **Pipeline fully automated** (one-click execution from raw data to candidates)
5. **Total cost <$25** (minimal spending!)
6. **Quality improved**: Precision ≥50% in top-100 (better than current best!)
7. **"Holy shit" discoveries**: ≥5 genuinely groundbreaking cross-domain connections
8. **User traction**: ≥100 organic visitors to analog.quest by Session 90

---

## 12. Next Steps (Session 61)

**Immediate actions for Session 61**:

1. **Install PostgreSQL + pgvector** (~30 minutes)
   - macOS: `brew install postgresql pgvector`
   - Start server: `brew services start postgresql`
   - Create database: `createdb analog_quest`
   - Enable extension: `CREATE EXTENSION vector;`

2. **Create schema** (~30 minutes)
   - Use schema from Section 5.2 of this document
   - Create tables: papers, mechanisms, discoveries, discovered_pairs
   - Create indexes: domain, score, HNSW vector index

3. **Test vector similarity** (~30 minutes)
   - Insert 5 test mechanisms with dummy embeddings
   - Query: Find k-nearest neighbors using `<->` operator
   - Validate: Results sorted by distance (lower = more similar)

4. **Document setup** (~30 minutes)
   - Create POSTGRESQL_SETUP.md with installation instructions
   - Document connection string, table creation, test queries
   - Commit changes

5. **Update PROGRESS.md** (~15 minutes)
   - Add Session 60 entry (this planning session)
   - Add Session 61 entry (PostgreSQL setup)
   - Update Quick Stats section

**Session 61 deliverables**:
- [ ] PostgreSQL + pgvector installed and running
- [ ] Schema created (papers, mechanisms, discoveries, discovered_pairs)
- [ ] Vector similarity tested (k-NN queries working)
- [ ] POSTGRESQL_SETUP.md documentation complete
- [ ] Ready for Session 62 (data migration)

**Estimated time**: 2-3 hours

---

## 13. Conclusion

**The Scale-Up Vision**:

We've validated the approach (46 discoveries, 24-40% precision, excellent quality). Now it's time to scale.

**From**: Manual curation, 2K papers, 46 discoveries, weeks of effort
**To**: Automated pipeline, 50K papers, 200+ discoveries, <$50 cost

**Key Insight**: The real value isn't in processing more papers—it's in **surfacing discoveries humans would never find**. Cross-domain connections buried in massive corpora. Structural isomorphisms that span biology ↔ economics ↔ physics.

**This is what analog.quest was meant to be.**

---

**Three months from now** (Session 90):
- analog.quest will showcase 200+ verified discoveries
- The pipeline will be automated and reproducible
- The infrastructure will handle 50K+ papers effortlessly
- The total cost will be under $50 (mostly LLM extraction)

**And most importantly**: We'll have surfaced groundbreaking cross-domain connections that no human would have found by reading papers one by one.

**That's the vision. Let's build it.**

---

**Created**: 2026-02-14 (Session 60)
**Author**: Analog Quest Agent (Claude Sonnet 4.5)
**Status**: Planning Complete, Ready for Session 61
**Next**: PostgreSQL + pgvector setup (Session 61)

---

**Appendix: Quick Reference**

**Data Sources**:
- arXiv: 2.5M papers, OAI-PMH metadata (free), S3 PDFs (~$20 for 50K)
- Semantic Scholar: 200M papers, 1 RPS API (free), bulk datasets (free)
- **OpenAlex: 240M papers, 100K credits/day (free), 200 parallel connections** ← PRIMARY

**LLM Costs (Batch API, 50% discount)**:
- Haiku 4.5: $0.50 input / $2.50 output per M tokens
- Sonnet 4.5: $1.50 input / $7.50 output per M tokens
- **8K papers → 5K mechanisms: $5.50 (Haiku) or $16.50 (Sonnet)**
- 50K papers → 35K mechanisms: $34.38 (Haiku) or $103.13 (Sonnet)

**Database**:
- PostgreSQL + pgvector (free, open-source)
- HNSW indexing (9× faster, 100× more relevant)
- Binary quantization (32× memory reduction, 95% accuracy)
- <100M vectors: 40-80% cost savings vs specialized vector DBs

**Timeline**:
- Month 1 (Sessions 60-70): Infrastructure setup, pipeline testing
- Month 2 (Sessions 71-80): Scale-up execution (50K papers, 5K-8K mechanisms)
- Month 3 (Sessions 81-90): Curation (200+ discoveries), launch analog.quest

**Budget**: $8-22 total (well under $50-150 target)

**Success Criteria**:
- ✅ 200+ verified discoveries
- ✅ 50K papers processed
- ✅ 5K+ mechanisms extracted
- ✅ Precision ≥40% in top-100
- ✅ Total cost <$150
- ✅ analog.quest deployed

**Let's go! 🚀**

-- Analog Quest PostgreSQL Schema
-- Created: 2026-02-14 (Session 61)
-- Purpose: Vector similarity search for cross-domain mechanism discovery
-- Database: PostgreSQL 17 with pgvector 0.8.1

-- Papers table (will hold 50K rows at scale)
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
CREATE INDEX idx_papers_arxiv_id ON papers(arxiv_id);

-- Mechanisms table (will hold 5K-8K rows at scale)
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
-- This enables <50ms queries for k-NN similarity search on 5K-8K vectors
CREATE INDEX idx_mechanisms_embedding ON mechanisms USING hnsw (embedding vector_l2_ops);

-- Discoveries table (will hold 200-400 rows at scale)
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

CREATE INDEX idx_discovered_pairs_session ON discovered_pairs(discovered_in_session);

-- Verify vector extension is enabled
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

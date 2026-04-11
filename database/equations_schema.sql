-- Equations table — stores individual equations extracted from paper LaTeX source
-- This is the foundation of the programmatic isomorphism detection pipeline.

-- Each row is one equation from one paper. A single paper may have many equations.
-- Matching happens on normalized_form (exact structural match) and
-- embedding (approximate match via pgvector) for equations SymPy couldn't parse.

CREATE TABLE IF NOT EXISTS equations (
    id              SERIAL PRIMARY KEY,
    paper_id        INTEGER NOT NULL REFERENCES papers(id),

    -- Raw LaTeX as extracted from the .tex source
    latex           TEXT NOT NULL,

    -- Where in the paper this came from
    source_env      TEXT,            -- 'equation', 'align', 'gather', 'inline', etc.
    position        INTEGER,         -- ordinal position in the paper (0-indexed)

    -- SymPy normalization (NULL if parsing failed)
    sympy_parsed    BOOLEAN NOT NULL DEFAULT FALSE,
    normalized_form TEXT,            -- canonical SymPy string with variables stripped
    structure_hash  TEXT,            -- SHA-256 of normalized_form for fast exact matching

    -- Embedding fallback for equations SymPy can't parse
    -- 384-dim to match common lightweight models (all-MiniLM-L6-v2 etc.)
    embedding       vector(384),

    -- Metadata
    equation_type   TEXT,            -- 'ode', 'pde', 'algebraic', 'inequality', 'definition', etc.
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Fast exact matching: find all equations with the same structural hash
CREATE INDEX idx_equations_structure_hash ON equations(structure_hash) WHERE structure_hash IS NOT NULL;

-- Fast cross-domain lookup: join with papers.domain
CREATE INDEX idx_equations_paper ON equations(paper_id);

-- Approximate matching via pgvector (cosine distance)
CREATE INDEX idx_equations_embedding ON equations USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Avoid re-extracting papers we've already processed
CREATE INDEX idx_equations_paper_unique_check ON equations(paper_id, position);


-- Automated isomorphism candidates from the programmatic pipeline
-- Separate from the existing isomorphisms table (which tracks agent-discovered ones)
-- These two tables can be unified later once confidence models are calibrated.
CREATE TABLE IF NOT EXISTS equation_matches (
    id              SERIAL PRIMARY KEY,
    equation_1_id   INTEGER NOT NULL REFERENCES equations(id),
    equation_2_id   INTEGER NOT NULL REFERENCES equations(id),

    match_type      TEXT NOT NULL,    -- 'exact_structural', 'near_structural', 'embedding_similarity'
    similarity      FLOAT NOT NULL,   -- 1.0 for exact, cosine similarity for embedding

    -- Denormalized for fast queries
    paper_1_id      INTEGER NOT NULL REFERENCES papers(id),
    paper_2_id      INTEGER NOT NULL REFERENCES papers(id),
    domain_1        TEXT,
    domain_2        TEXT,

    status          TEXT DEFAULT 'candidate',  -- candidate | verified | rejected
    created_at      TIMESTAMP DEFAULT NOW(),

    -- Don't create duplicate matches
    UNIQUE(equation_1_id, equation_2_id)
);

CREATE INDEX idx_equation_matches_status ON equation_matches(status);
CREATE INDEX idx_equation_matches_cross_domain ON equation_matches(domain_1, domain_2)
    WHERE domain_1 != domain_2;
CREATE INDEX idx_equation_matches_similarity ON equation_matches(similarity DESC);

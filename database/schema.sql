-- Analog Quest Schema
-- Distributed volunteer extraction of mathematical isomorphisms from academic papers

-- Enable pgvector for future embedding-based comparison
CREATE EXTENSION IF NOT EXISTS vector;

-- Papers sourced from arXiv / OpenAlex
CREATE TABLE papers (
    id          SERIAL PRIMARY KEY,
    arxiv_id    TEXT UNIQUE,          -- e.g. "2103.00020"
    openalex_id TEXT UNIQUE,          -- e.g. "W2741809807"
    title       TEXT NOT NULL,
    abstract    TEXT,
    domain      TEXT,                 -- e.g. "cs", "physics", "q-bio", "econ"
    published   DATE,
    url         TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_papers_domain ON papers(domain);
CREATE INDEX idx_papers_published ON papers(published DESC);

-- Work queue: papers waiting to be processed by volunteer agents
CREATE TABLE queue (
    id              SERIAL PRIMARY KEY,
    paper_id        INTEGER NOT NULL REFERENCES papers(id),
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | checked_out | done | skipped
    checked_out_at  TIMESTAMP,
    checked_out_by  TEXT,       -- contributor identifier (anonymous token)
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(paper_id)
);

CREATE INDEX idx_queue_status ON queue(status);
CREATE INDEX idx_queue_checkout ON queue(checked_out_at);

-- Extractions submitted by volunteer agents
-- Multiple agents may extract the same paper; consensus validates
CREATE TABLE extractions (
    id                  SERIAL PRIMARY KEY,
    paper_id            INTEGER NOT NULL REFERENCES papers(id),
    contributor_token   TEXT NOT NULL,   -- anonymous but consistent per volunteer
    equation_class      TEXT,            -- LOTKA_VOLTERRA | HEAT_EQUATION | HOPF_BIFURCATION |
                                         -- ISING_MODEL | POWER_LAW | KURAMOTO | SIR | SCHRODINGER |
                                         -- NAVIER_STOKES | GAME_THEORY | OTHER | NONE
    latex_fragments     TEXT[],          -- raw LaTeX strings from the paper
    variables           JSONB,           -- [{"symbol": "x", "meaning": "prey population"}]
    domain              TEXT,            -- the paper's scientific domain as extracted
    confidence          FLOAT,           -- 0.0–1.0 agent self-assessment
    notes               TEXT,            -- brief free-text from agent
    submitted_at        TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_extractions_paper ON extractions(paper_id);
CREATE INDEX idx_extractions_class ON extractions(equation_class);
CREATE INDEX idx_extractions_contributor ON extractions(contributor_token);

-- Validated isomorphisms: when 2+ extractions on different papers agree on equation_class
-- These are the real discoveries
CREATE TABLE isomorphisms (
    id                  SERIAL PRIMARY KEY,
    paper_1_id          INTEGER NOT NULL REFERENCES papers(id),
    paper_2_id          INTEGER NOT NULL REFERENCES papers(id),
    equation_class      TEXT NOT NULL,
    latex_paper_1       TEXT[],
    latex_paper_2       TEXT[],
    explanation         TEXT,
    confidence          FLOAT NOT NULL,
    validation_count    INTEGER DEFAULT 1,   -- how many independent extractions agree
    status              TEXT DEFAULT 'candidate',  -- candidate | verified | rejected
    discovered_at       TIMESTAMP DEFAULT NOW(),
    UNIQUE(paper_1_id, paper_2_id, equation_class)
);

CREATE INDEX idx_isomorphisms_class ON isomorphisms(equation_class);
CREATE INDEX idx_isomorphisms_status ON isomorphisms(status);
CREATE INDEX idx_isomorphisms_confidence ON isomorphisms(confidence DESC);

-- Contributor stats (anonymous tokens only, no PII)
CREATE TABLE contributors (
    token           TEXT PRIMARY KEY,
    extractions     INTEGER DEFAULT 0,
    validations     INTEGER DEFAULT 0,
    first_seen      TIMESTAMP DEFAULT NOW(),
    last_seen       TIMESTAMP DEFAULT NOW()
);

-- schema.sql
-- Database schema for analog.quest
-- SQLite database structure

-- Papers table: stores academic papers
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    full_text TEXT,  -- Optional, if we get full papers
    domain TEXT NOT NULL,  -- physics, cs, biology, etc.
    subdomain TEXT,  -- More specific: condensed-matter, AI, ecology
    arxiv_id TEXT,  -- arXiv identifier if applicable
    pubmed_id TEXT,  -- PubMed identifier if applicable
    doi TEXT,  -- Digital Object Identifier
    authors TEXT,  -- JSON array of authors
    published_date TEXT,  -- ISO format YYYY-MM-DD
    source TEXT,  -- arXiv, PubMed, etc.
    url TEXT,  -- Link to original paper
    processed_date TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,  -- Any additional notes
    UNIQUE(arxiv_id, pubmed_id)  -- Prevent duplicates
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_papers_domain ON papers(domain);
CREATE INDEX IF NOT EXISTS idx_papers_arxiv ON papers(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_papers_pubmed ON papers(pubmed_id);
CREATE INDEX IF NOT EXISTS idx_papers_date ON papers(published_date);

-- Patterns table: structural patterns extracted from papers
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    structural_description TEXT NOT NULL,  -- Abstract description of the pattern
    mechanism_type TEXT,  -- feedback_loop, cascade, threshold, etc.
    
    -- Pattern components (JSON or structured text)
    components TEXT,  -- What are the key elements? (e.g., "A, B, relationship")
    dynamics TEXT,  -- How does it behave? (e.g., "A increases B, B decreases A")
    outcome TEXT,  -- What happens? (e.g., "oscillation", "equilibrium")
    
    -- Context
    domain_specific_terms TEXT,  -- Original terminology from paper
    equations TEXT,  -- Mathematical representation if present
    confidence REAL DEFAULT 0.5,  -- How confident are we in this extraction? (0-1)
    
    -- Metadata
    extracted_date TEXT DEFAULT CURRENT_TIMESTAMP,
    extraction_method TEXT,  -- Which version of extraction code?
    verified BOOLEAN DEFAULT 0,  -- Has a human verified this?
    notes TEXT,
    
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_patterns_paper ON patterns(paper_id);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(mechanism_type);
CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);

-- Isomorphisms table: matches between patterns from different domains
CREATE TABLE IF NOT EXISTS isomorphisms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_1_id INTEGER NOT NULL,
    pattern_2_id INTEGER NOT NULL,
    
    -- Similarity metrics
    similarity_score REAL NOT NULL,  -- 0-1, how similar are they?
    structural_similarity REAL,  -- Same structure?
    semantic_similarity REAL,  -- Same meaning?
    mathematical_similarity REAL,  -- Same math?
    
    -- Explanation
    explanation TEXT NOT NULL,  -- Why are these the same?
    mapping TEXT,  -- How do components map? (JSON)
    
    -- Evidence
    evidence TEXT,  -- Supporting evidence for the match
    
    -- Domains
    domain_1 TEXT,  -- From patterns via papers
    domain_2 TEXT,
    
    -- Metadata
    discovered_date TEXT DEFAULT CURRENT_TIMESTAMP,
    discovery_method TEXT,  -- Which algorithm found this?
    verified BOOLEAN DEFAULT 0,  -- Has a human checked this?
    verification_notes TEXT,
    confidence_level TEXT,  -- high, medium, low
    
    -- Prevent duplicate matches
    UNIQUE(pattern_1_id, pattern_2_id),
    CHECK(pattern_1_id < pattern_2_id),  -- Enforce ordering to prevent duplicates
    
    FOREIGN KEY (pattern_1_id) REFERENCES patterns(id) ON DELETE CASCADE,
    FOREIGN KEY (pattern_2_id) REFERENCES patterns(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_isomorphisms_pattern1 ON isomorphisms(pattern_1_id);
CREATE INDEX IF NOT EXISTS idx_isomorphisms_pattern2 ON isomorphisms(pattern_2_id);
CREATE INDEX IF NOT EXISTS idx_isomorphisms_score ON isomorphisms(similarity_score);
CREATE INDEX IF NOT EXISTS idx_isomorphisms_verified ON isomorphisms(verified);

-- Pattern types lookup table (for categorization)
CREATE TABLE IF NOT EXISTS pattern_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT UNIQUE NOT NULL,
    description TEXT,
    examples TEXT,  -- JSON array of example patterns
    characteristics TEXT  -- What defines this type?
);

-- Insert common pattern types
INSERT OR IGNORE INTO pattern_types (type_name, description) VALUES
    ('feedback_loop', 'System where output feeds back to input'),
    ('positive_feedback', 'Self-reinforcing process'),
    ('negative_feedback', 'Self-correcting process'),
    ('cascade', 'Sequential triggering of events'),
    ('threshold', 'System changes state at critical point'),
    ('network_effect', 'Value increases with number of participants'),
    ('oscillation', 'Periodic variation over time'),
    ('equilibrium', 'Stable state of balance'),
    ('bifurcation', 'System splits into multiple states'),
    ('emergence', 'Complex behavior from simple rules'),
    ('scaling', 'Properties change with system size'),
    ('symmetry_breaking', 'Loss of symmetry in system'),
    ('phase_transition', 'Abrupt change in system state'),
    ('diffusion', 'Spreading process'),
    ('optimization', 'Finding optimal solution'),
    ('competition', 'Multiple entities vying for resources'),
    ('cooperation', 'Entities working together'),
    ('saturation', 'Limit to growth or capacity'),
    ('decay', 'Gradual decrease over time'),
    ('resonance', 'Amplification at specific frequency');

-- Processing log (track what's been done)
CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    action TEXT NOT NULL,  -- fetch, extract, match, etc.
    details TEXT,  -- JSON with specifics
    papers_processed INTEGER DEFAULT 0,
    patterns_created INTEGER DEFAULT 0,
    isomorphisms_found INTEGER DEFAULT 0,
    errors TEXT,  -- Any errors encountered
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_log_session ON processing_log(session_id);
CREATE INDEX IF NOT EXISTS idx_log_timestamp ON processing_log(timestamp);

-- Examples table (store good/bad examples for learning)
CREATE TABLE IF NOT EXISTS examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_type TEXT NOT NULL,  -- good_pattern, bad_pattern, good_match, false_positive
    content TEXT NOT NULL,  -- The example itself (JSON)
    explanation TEXT,  -- Why is this a good/bad example?
    created_date TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Views for common queries

-- View: Papers with pattern count
CREATE VIEW IF NOT EXISTS papers_with_patterns AS
SELECT 
    p.id,
    p.title,
    p.domain,
    p.published_date,
    COUNT(pt.id) as pattern_count
FROM papers p
LEFT JOIN patterns pt ON p.id = pt.paper_id
GROUP BY p.id;

-- View: Cross-domain isomorphisms
CREATE VIEW IF NOT EXISTS cross_domain_matches AS
SELECT 
    i.id,
    i.similarity_score,
    p1.domain as domain_1,
    p2.domain as domain_2,
    pap1.title as paper_1_title,
    pap2.title as paper_2_title,
    i.explanation,
    i.verified
FROM isomorphisms i
JOIN patterns p1 ON i.pattern_1_id = p1.id
JOIN patterns p2 ON i.pattern_2_id = p2.id
JOIN papers pap1 ON p1.paper_id = pap1.id
JOIN papers pap2 ON p2.paper_id = pap2.id
WHERE p1.id IN (SELECT paper_id FROM patterns JOIN papers ON patterns.paper_id = papers.id)
  AND p2.id IN (SELECT paper_id FROM patterns JOIN papers ON patterns.paper_id = papers.id);

-- View: High-confidence isomorphisms
CREATE VIEW IF NOT EXISTS high_confidence_matches AS
SELECT * FROM cross_domain_matches
WHERE similarity_score >= 0.7
ORDER BY similarity_score DESC;

-- Stats view
CREATE VIEW IF NOT EXISTS stats AS
SELECT 
    (SELECT COUNT(*) FROM papers) as total_papers,
    (SELECT COUNT(*) FROM patterns) as total_patterns,
    (SELECT COUNT(*) FROM isomorphisms) as total_isomorphisms,
    (SELECT COUNT(*) FROM isomorphisms WHERE verified = 1) as verified_isomorphisms,
    (SELECT COUNT(DISTINCT domain) FROM papers) as domains_covered,
    (SELECT AVG(pattern_count) FROM papers_with_patterns) as avg_patterns_per_paper;

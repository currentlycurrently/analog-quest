-- Atlas schema — the canonical-structure classification layer.
--
-- Background: exact-hash equation matching (equations_schema.sql) is
-- structurally blind to cross-domain isomorphisms, because the same structure
-- written in different notation hashes differently. The atlas replaces that
-- substrate: each paper's core model is classified against a fixed library of
-- canonical mathematical structures. Papers that land on the same structure
-- but come from different fields ARE the cross-domain bridges.
--
-- Measured go/no-go (scripts/experiments/atlas/): classification recall 0.93,
-- cross-field join 14/15, distractor precision 0.93, and it holds on Haiku.
-- See docs/ROADMAP.md Item 2 and HANDOFF.md (2026-07-05 session).

-- ---------------------------------------------------------------------------
-- Reference library: the canonical structures a paper can be classified into.
-- Seeded from scripts/experiments/atlas/templates.json.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS atlas_templates (
    template_id       TEXT PRIMARY KEY,        -- e.g. 'kuramoto_phase_oscillators'
    name              TEXT NOT NULL,           -- human name
    object_type       TEXT,                    -- 'ode','pde','sde',...
    canonical_form    TEXT,                    -- defining equation in neutral LaTeX
    structural_features TEXT[] DEFAULT '{}',   -- controlled-vocabulary tags
    cross_field_aliases TEXT[] DEFAULT '{}',   -- names this goes by in other fields
    fields            TEXT[] DEFAULT '{}',     -- domains it typically appears in
    created_at        TIMESTAMP DEFAULT NOW()
);

-- Structures that denote the same underlying object at different granularities
-- (e.g. black_scholes_pde <-> heat_diffusion_equation). Two papers classified
-- into equivalent templates still count as the same atlas group.
-- Stored as a canonical representative per member; group_key is the rep id.
CREATE TABLE IF NOT EXISTS atlas_equivalences (
    template_id   TEXT PRIMARY KEY REFERENCES atlas_templates(template_id),
    group_key     TEXT NOT NULL   -- representative template_id for the equivalence class
);
CREATE INDEX IF NOT EXISTS idx_atlas_equiv_group ON atlas_equivalences(group_key);

-- ---------------------------------------------------------------------------
-- Classifications: one row per (paper, template) assignment.
-- A paper may be assigned 0-2 templates; 0 assignments is recorded as a single
-- sentinel row with template_id = NULL so we don't re-classify it.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS atlas_classifications (
    id                SERIAL PRIMARY KEY,
    paper_id          INTEGER NOT NULL REFERENCES papers(id),
    template_id       TEXT REFERENCES atlas_templates(template_id),  -- NULL = "classified, no template fit"
    confidence        FLOAT,
    twist             TEXT,           -- how this paper's variant departs from canonical
    model             TEXT,           -- classifier model id, for provenance
    submitted_by_user_id INTEGER REFERENCES contributors(user_id),

    -- Moderation: a moderator can hide a whole structure group or a single
    -- assignment. Mirrors the trivia-hash defense on the old matcher.
    status            TEXT DEFAULT 'active',  -- active | hidden | trivia
    review_note       TEXT,

    created_at        TIMESTAMP DEFAULT NOW(),

    -- One classification per (paper, template). The NULL-template sentinel is
    -- deduped separately below since NULL is not covered by a normal UNIQUE.
    UNIQUE(paper_id, template_id)
);

-- Ensure at most one "no fit" sentinel per paper (NULL template_id).
CREATE UNIQUE INDEX IF NOT EXISTS atlas_class_nofit_unique
    ON atlas_classifications(paper_id) WHERE template_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_atlas_class_template ON atlas_classifications(template_id)
    WHERE template_id IS NOT NULL AND status = 'active';
CREATE INDEX IF NOT EXISTS idx_atlas_class_paper ON atlas_classifications(paper_id);
CREATE INDEX IF NOT EXISTS idx_atlas_class_status ON atlas_classifications(status);

-- ---------------------------------------------------------------------------
-- A structure is "moderated trivia" when a moderator has flagged its whole
-- group as too-universal to be interesting (e.g. gradient_descent). Hides the
-- group from the public atlas without deleting the classifications.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS atlas_trivia_templates (
    group_key     TEXT PRIMARY KEY,   -- equivalence group_key (or template_id if ungrouped)
    reason        TEXT,
    flagged_by_user_id INTEGER REFERENCES contributors(user_id),
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Session 19.5: Methodology Hardening - Database Schema Updates

-- Add match_details to isomorphisms table for complete audit trail
ALTER TABLE isomorphisms ADD COLUMN match_details TEXT;

-- Add reproducibility columns to patterns table
ALTER TABLE patterns ADD COLUMN description_original TEXT;
ALTER TABLE patterns ADD COLUMN synonym_dict_version TEXT DEFAULT 'v1.2';
ALTER TABLE patterns ADD COLUMN extracted_at TEXT;

-- Create match_feedback table for future user feedback
CREATE TABLE IF NOT EXISTS match_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isomorphism_id INTEGER NOT NULL,
    feedback_type TEXT NOT NULL,  -- 'excellent', 'good', 'weak', 'false_positive'
    user_comment TEXT,
    submitted_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (isomorphism_id) REFERENCES isomorphisms(id)
);

-- Backfill description_original with current structural_description
-- (Copy current description as "original" for existing patterns)
UPDATE patterns
SET description_original = structural_description,
    synonym_dict_version = 'v1.0',
    extracted_at = datetime('now')
WHERE description_original IS NULL;

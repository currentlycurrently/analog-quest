# Data Quality Standards - Analog Quest

**Version**: 1.0
**Last Updated**: 2026-02-11 (Session 45)
**Status**: Active - enforced for all future work

---

## Purpose

This document defines the data quality standards and intake requirements for Analog Quest. These standards ensure:
1. **Working citation links** - all discoveries have verifiable sources
2. **Referential integrity** - frontend data matches database
3. **Scalability** - standards that work at 50, 500, or 5,000+ discoveries
4. **Trust** - users can verify structural isomorphisms themselves

---

## Core Principle: Database is Single Source of Truth

**ALL paper metadata MUST come from `database/papers.db`.**

Never manually edit:
- arXiv IDs
- Paper titles
- Domain classifications
- Publication dates

These fields are authoritative in the database and must be queried, not hardcoded.

**Only hand-curate**:
- Mechanism descriptions (domain-neutral, structural)
- Structural explanations for isomorphisms
- Quality ratings (excellent/good/weak/false)

---

## Paper Intake Requirements

### Minimum Requirements for Database Entry

Every paper in `papers.db` MUST have:

1. **Valid arXiv ID** (format: `YYMM.NNNNN[vN]`)
   - Example: `2602.05112v1`
   - NO "N/A" or placeholder values
   - Must resolve to https://arxiv.org/abs/{arxiv_id}

2. **Domain Classification**
   - Primary domain from arXiv taxonomy
   - Valid domains: physics, cs, q-bio, econ, math, nlin, q-fin, stat, etc.
   - NO "unknown" unless truly unclassifiable (rare)

3. **Complete Abstract**
   - Minimum 100 characters
   - Used for mechanism extraction
   - Must describe methods/mechanisms, not just results

4. **Proper Title**
   - Full title from arXiv
   - No truncation

### Paper Selection Criteria (Mechanism Richness)

Not all papers are good candidates for Analog Quest. Prioritize papers with:

✅ **Include**:
- Mechanistic models (describes HOW systems work)
- Structural patterns (feedback loops, networks, thresholds)
- Cross-domain generalizable concepts
- Clear causal relationships
- Mathematical or computational models
- Papers that describe MECHANISMS not just OUTCOMES

❌ **Exclude**:
- Pure review papers (no original mechanism)
- Pure empirical studies (no mechanistic model)
- Method-only papers (describe tool but not system dynamics)
- Single-application case studies (no generalizable structure)
- Papers dominated by technique jargon (GNN, LSTM, etc.)

### Quality Thresholds

**Hit Rate Target**: ≥70% of papers should yield extractable mechanisms

If hit rate drops below 70%, review selection criteria:
- Are we fetching the right domains?
- Are we filtering for mechanism richness?
- Do keywords match the domains?

---

## Discovery Verification Requirements

### Before Adding Discovery to discoveries.json

Every discovery MUST pass:

1. **Paper Metadata Validation**
   ```bash
   python scripts/validate_discoveries.py
   ```
   - All paper_ids exist in database
   - All arxiv_ids match database
   - All domains match database
   - No referential integrity errors

2. **Structural Explanation Quality**
   - Minimum 50 characters (ideally 150-300)
   - Describes the MECHANISM not just similarity
   - Domain-neutral language
   - Explains WHY mechanisms are isomorphic

3. **Mechanism Description Quality**
   - Minimum 50 characters (ideally 200-400)
   - Domain-neutral (no field-specific jargon)
   - Describes structure not terminology
   - Causal relationships explicit

4. **Manual Curation Review**
   - Rating assigned: excellent/good/weak/false
   - At least 2 domains represented (cross-domain)
   - Similarity score documented

---

## Workflow for Future Expansion

### Step 1: Fetch Papers
```bash
python scripts/fetch_papers.py --domain cs --subdomain AI --max 100
```
- Fetches from arXiv with full metadata
- Stores in `papers.db` with arxiv_id, domain, title, abstract
- NO manual data entry

### Step 2: Extract Mechanisms
```bash
python scripts/extract_mechanisms.py --paper-ids 2000-2100
```
- LLM-guided extraction (GPT-4 or Claude)
- Domain-neutral descriptions
- Stores in `mechanisms.json` (temporary)
- Links to paper_id (not manual titles)

### Step 3: Generate Candidates
```bash
python scripts/generate_embeddings.py --mechanisms mechanisms.json
python scripts/match_candidates.py --threshold 0.35 --cross-domain
```
- Semantic embeddings (384-dim)
- Cross-domain matches only
- Threshold ≥0.35 (validated in Session 36-38)
- Exports `candidates_for_review.json`

### Step 4: Manual Curation
- Review candidates in `candidates_for_review.json`
- Rate each: excellent/good/weak/false
- Write structural explanations for excellent/good
- Add to `discoveries_verified.json`

### Step 5: Sync to Frontend
```bash
python scripts/sync_discoveries_to_frontend.py
```
- Queries database for paper metadata (arxiv_id, domain, title)
- Merges with verified discoveries
- Outputs to `app/data/discoveries.json`
- NEVER manually edit `app/data/discoveries.json`

### Step 6: Validate Before Deploy
```bash
python scripts/validate_discoveries.py
npm run build
```
- Must pass validation (0 errors)
- Must build successfully
- Test citation links locally

---

## Data Integrity Checks (Run Before Each Deploy)

### Pre-Deployment Checklist

- [ ] `python scripts/validate_discoveries.py` → 0 errors
- [ ] `npm run build` → 0 TypeScript errors
- [ ] Sample 5 random citation links → all resolve to correct papers
- [ ] Domain badges display correctly
- [ ] Mechanism descriptions are domain-neutral
- [ ] Structural explanations are ≥50 characters

### Post-Deploy Verification

- [ ] Visit analog.quest/discoveries/1 → citation links work
- [ ] Check 3 random discovery pages → no broken links
- [ ] Domain badges match paper domains
- [ ] SEO metadata includes correct title/description

---

## Common Mistakes to Avoid

### ❌ DON'T:
1. **Manually edit arxiv_ids in discoveries.json**
   - Always query database for paper metadata
   - Use `scripts/fix_discoveries_metadata.py` if out of sync

2. **Create discoveries without database entries**
   - Every paper_id must exist in `papers.db` first
   - No "unknown" domains if avoidable

3. **Accept low hit rates without investigation**
   - <70% hit rate = selection criteria problem
   - Review domain keywords, paper quality

4. **Skip validation before committing**
   - Validation catches broken links before users see them
   - Faster to fix locally than after deploy

5. **Scale without foundation**
   - 30 discoveries with broken links = bad
   - 500 discoveries with broken links = catastrophic
   - Fix foundation THEN scale

### ✅ DO:
1. **Query database for all paper metadata**
2. **Validate before every commit**
3. **Document extraction quality (hit rates)**
4. **Maintain referential integrity**
5. **Use scripts, not manual editing**

---

## Intake Strategy for 5,000+ Paper Scale

### Phase 1: Current State (2,021 papers)
- **Status**: Foundation fixed (Session 45)
- **Next**: Audit existing 2,021 papers for mechanism richness
- **Goal**: Identify high-value papers for re-extraction

### Phase 2: Selective Expansion (→5,000 papers)
- **Target domains** (based on Session 39 analysis):
  - Tier 1 (≥50% precision): cs↔physics, econ↔physics
  - Tier 2 (25-50% precision): econ↔q-bio, cs↔econ
- **Selection criteria**:
  - Mechanism-rich papers (not pure empirical/methods)
  - Cross-domain potential (generalizable structures)
  - Recent papers (2020+) for relevance
- **Goal**: 500-1,000 verified discoveries

### Phase 3: Global Coverage (→10,000+ papers)
- **Expand to**:
  - Social sciences (sociology, psychology)
  - Engineering (mechanical, electrical)
  - Earth sciences (climate, geology)
  - Chemistry (reaction dynamics, thermodynamics)
- **Maintain quality**: ≥70% hit rate, ≥40% precision in top-100 candidates
- **Goal**: 1,000-2,000 verified discoveries

### Key Metrics to Track
- **Hit rate**: % of papers yielding mechanisms (target: ≥70%)
- **Precision**: % of candidates rated excellent/good (target: ≥40% in top-100)
- **Domain diversity**: # of unique domain pairs (target: 50+)
- **Citation coverage**: % of discoveries with working links (target: 100%)

---

## Version History

### v1.0 (2026-02-11 - Session 45)
- Initial standards document
- Root cause analysis: Session 37-38 manual curation bypassed database
- Fix: 100% citation links now working
- Validation script created
- Intake workflow defined

---

## Questions?

If uncertain about data quality:
1. Run `python scripts/validate_discoveries.py`
2. Check TECHNICAL_DEBT.md for known issues
3. Review SESSION45_DATA_AUDIT.md for lessons learned
4. Ask in QUESTIONS.md if standards unclear

**When in doubt: query the database, don't guess.**

# Session 37: Generate All Candidates for Manual Curation

**Date**: 2026-02-10
**Agent**: Fresh agent (Session 36 complete)
**Mission**: Process all 2,021 papers to generate candidate isomorphisms for manual review in Session 38

---

## Context: Why We're Here

**Session 36 Results (DECISIVE TEST)**:
- ✅ Found **EXCELLENT match**: Tragedy of commons (economics ↔ biology) at 0.453 similarity
- ✅ Found 3 more GOOD matches (network effects, cascades, parameter transitions)
- ✅ LLM extraction: **100% hit rate** (17/17 papers)
- ❌ Max similarity 0.544 (below 0.65 target)
- **Key Insight**: **Domain Diversity Paradox** - diverse domains → better structural matches but LOWER scores
- **Decision**: Pivot to manual curation (Outcome B - Partial Success)

**What This Means**:
- Embeddings WORK for finding candidates (proved by tragedy of commons match!)
- Cannot validate automatically - scores unreliable across domains
- Need manual review to identify genuine isomorphisms
- 40% precision in top-10 → embeddings useful for discovery

**Session 37 Goal**: Generate the FULL candidate set from all 2,021 papers for manual review.

---

## Mission Overview

Process all 2,021 papers in the database to create a candidate pool of 150-250 potential isomorphisms for manual curation in Session 38.

**Pipeline**:
1. LLM Extraction → ~450 mechanisms (22.5% hit rate expected)
2. Semantic Embeddings → 450 embeddings
3. Cross-Domain Matching → 150-250 candidate pairs (≥0.35 threshold)
4. Export for Review → Structured JSON for Session 38

---

## Part 1: LLM Mechanism Extraction (2-3 hours)

### Goal
Extract structural mechanisms from all 2,021 papers using the validated Session 33 LLM prompt.

### Method

**Use the proven Session 33 extraction prompt** (see examples/session33_experiments.md or SESSION34_RESULTS.md).

**Key principles**:
- Extract STRUCTURAL MECHANISMS (not methods/techniques)
- Use domain-neutral language
- Focus on causal relationships (X causes Y, X enables Z)
- Ignore papers that are purely empirical, methodological, or surveys

**Expected hit rate**: ~22.5% (based on Session 34 with 40 papers)
- Success: 450-500 mechanisms extracted
- Expected failures: ~1,570 papers (empirical studies, surveys, method papers)

### Implementation

Create script: `scripts/session37_extract_all_mechanisms.py`

```python
#!/usr/bin/env python3
"""
Extract mechanisms from all 2,021 papers using LLM approach.
"""

import sqlite3
import json
import os
from anthropic import Anthropic

# Session 33 extraction prompt
EXTRACTION_PROMPT = """
[Use the exact prompt from Session 33 - see examples/session33_experiments.md]

Extract the STRUCTURAL MECHANISM from this abstract.

Rules:
1. Only extract if the paper describes a MECHANISM (causal relationship, feedback, dynamics)
2. Use domain-neutral language (avoid field-specific jargon)
3. Focus on structure: "X increases, Y decreases" not "predators increase, prey decrease"
4. Return ONLY the mechanism description, or "NO_MECHANISM" if none found

Abstract:
{abstract}
"""

# Process all papers in batches
# Store results in examples/session37_all_mechanisms.json
```

**Batching strategy**:
- Process in batches of 50-100 papers
- Save intermediate results (in case of interruption)
- Track success rate per batch

### Output Format

`examples/session37_all_mechanisms.json`:
```json
[
  {
    "paper_id": 87,
    "domain": "econ",
    "subdomain": "econ.GN",
    "arxiv_id": "2401.12345",
    "title": "Paper title",
    "mechanism": "Extracted domain-neutral mechanism description",
    "extraction_quality": "excellent|good|weak",
    "batch": 1
  },
  ...
]
```

### Success Criteria
- [ ] All 2,021 papers processed
- [ ] 400-500 mechanisms extracted (~20-25% hit rate)
- [ ] All extractions domain-neutral and structural
- [ ] Results saved in examples/session37_all_mechanisms.json

---

## Part 2: Generate Semantic Embeddings (30 min)

### Goal
Generate 384-dim embeddings for all extracted mechanisms using sentence-transformers.

### Method

Use the same model as Sessions 35-36: `sentence-transformers/all-MiniLM-L6-v2`

Create script: `scripts/session37_generate_embeddings.py`

```python
#!/usr/bin/env python3
"""
Generate embeddings for all extracted mechanisms.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load mechanisms
with open('examples/session37_all_mechanisms.json', 'r') as f:
    mechanisms = json.load(f)

# Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
mechanism_texts = [m['mechanism'] for m in mechanisms]
embeddings = model.encode(mechanism_texts)

# Save embeddings as numpy array
np.save('examples/session37_embeddings.npy', embeddings)
```

### Output
- `examples/session37_embeddings.npy` - NumPy array of embeddings (shape: [N, 384])

### Success Criteria
- [ ] Embeddings generated for all mechanisms
- [ ] Same model as Sessions 35-36 (reproducibility)
- [ ] Embeddings saved

---

## Part 3: Cross-Domain Matching with Relaxed Threshold (30 min)

### Goal
Find candidate isomorphism pairs using RELAXED threshold based on Session 36 findings.

### Key Insight from Session 36

**Best match was at 0.453 similarity** (tragedy of commons - EXCELLENT!)
- Standard threshold (0.65) would have MISSED this excellent match
- Need relaxed threshold to capture diverse-domain matches

**Recommended threshold**: **≥0.35**
- Captures excellent matches like tragedy of commons (0.453)
- Also captures the good matches (0.40-0.54 range from Session 36)
- Accepts higher false positive rate (manual review will filter)

### Method

Create script: `scripts/session37_match_candidates.py`

```python
#!/usr/bin/env python3
"""
Match mechanisms with relaxed threshold for manual review.
"""

import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load mechanisms and embeddings
with open('examples/session37_all_mechanisms.json', 'r') as f:
    mechanisms = json.load(f)
embeddings = np.load('examples/session37_embeddings.npy')

# Match cross-domain pairs only
candidates = []
THRESHOLD = 0.35  # Relaxed based on Session 36 findings

for i in range(len(mechanisms)):
    for j in range(i+1, len(mechanisms)):
        # Cross-domain only (different top-level domains)
        if mechanisms[i]['domain'] != mechanisms[j]['domain']:
            sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]

            if sim >= THRESHOLD:
                candidates.append({
                    'paper_1': mechanisms[i],
                    'paper_2': mechanisms[j],
                    'similarity': float(sim),
                    'review_status': 'pending',
                    'rating': None,  # To be filled in Session 38
                    'notes': None    # To be filled in Session 38
                })

# Sort by similarity (descending)
candidates.sort(key=lambda x: x['similarity'], reverse=True)

# Save
with open('examples/session37_candidates_for_review.json', 'w') as f:
    json.dump({
        'total_mechanisms': len(mechanisms),
        'threshold': THRESHOLD,
        'total_candidates': len(candidates),
        'candidates': candidates
    }, f, indent=2)
```

### Expected Results
- **150-250 candidate pairs** (based on ~450 mechanisms, threshold 0.35)
- All cross-domain (no same-domain matches)
- Sorted by similarity (highest first)

### Success Criteria
- [ ] Cross-domain matching only
- [ ] Threshold ≥0.35 (captures Session 36's excellent match at 0.453)
- [ ] 150-250 candidates generated
- [ ] Sorted by similarity
- [ ] Exported in reviewable format

---

## Part 4: Candidate Export for Manual Review (30 min)

### Goal
Export candidates in a format optimized for manual review in Session 38.

### Output Format

`examples/session37_candidates_for_review.json`:

```json
{
  "metadata": {
    "session": 37,
    "date": "2026-02-10",
    "total_papers_processed": 2021,
    "total_mechanisms_extracted": 450,
    "threshold": 0.35,
    "total_candidates": 200,
    "ready_for_review": true
  },
  "statistics": {
    "similarity_max": 0.xx,
    "similarity_mean": 0.xx,
    "similarity_median": 0.xx,
    "similarity_min": 0.35,
    "domain_pairs": {
      "econ-qbio": 45,
      "cs-physics": 38,
      ...
    }
  },
  "candidates": [
    {
      "candidate_id": 1,
      "similarity": 0.xx,
      "paper_1": {
        "paper_id": 123,
        "arxiv_id": "2401.12345",
        "domain": "econ",
        "subdomain": "econ.GN",
        "title": "Paper title",
        "mechanism": "Domain-neutral mechanism description"
      },
      "paper_2": {
        "paper_id": 456,
        "arxiv_id": "2401.67890",
        "domain": "q-bio",
        "subdomain": "q-bio.PE",
        "title": "Paper title",
        "mechanism": "Domain-neutral mechanism description"
      },
      "review_status": "pending",
      "rating": null,
      "notes": null
    },
    ...
  ]
}
```

### Review Fields (Session 38)

Each candidate will be manually reviewed and rated:
- **rating**: "excellent" | "good" | "weak" | "false"
- **notes**: Explanation of why it's a match (or not)
- **review_status**: "pending" | "reviewed" | "selected"

### Success Criteria
- [ ] All candidates in reviewable format
- [ ] Clear structure for manual annotation
- [ ] Statistics included
- [ ] Ready for Session 38

---

## Overall Success Criteria

**Session 37 is successful if:**

✅ All 2,021 papers processed with LLM extraction
✅ ~400-500 mechanisms extracted (~20-25% hit rate)
✅ Semantic embeddings generated (384-dim, sentence-transformers)
✅ 150-250 candidate pairs identified (threshold ≥0.35, cross-domain only)
✅ Candidates exported in reviewable format
✅ Ready for Session 38 manual curation

**Session 38 will then:**
- Manually review all 150-250 candidates
- Rate each as excellent/good/weak/false
- Select 20-30 verified isomorphisms
- Document each with clear explanations
- Prepare for launch

---

## Files to Create

1. `scripts/session37_extract_all_mechanisms.py` - LLM extraction for 2,021 papers
2. `scripts/session37_generate_embeddings.py` - Embedding generation
3. `scripts/session37_match_candidates.py` - Cross-domain matching
4. `examples/session37_all_mechanisms.json` - Extracted mechanisms (~450)
5. `examples/session37_embeddings.npy` - Embeddings array
6. `examples/session37_candidates_for_review.json` - Candidates for Session 38
7. `SESSION37_RESULTS.md` - Brief summary of results

---

## Key Reminders

### From Session 36

**Domain Diversity Paradox**: More diverse domains = better structural matches but LOWER similarity scores.
- Session 36 best match: 0.453 (tragedy of commons - EXCELLENT!)
- This is why threshold is 0.35, not 0.65

**LLM Extraction Works**: 100% hit rate on mechanism-rich papers
- Key: Only extract from papers that describe mechanisms
- Most papers won't have mechanisms (empirical, methods, surveys)
- 22.5% hit rate is expected and good

**Embeddings are for Discovery, Not Validation**:
- Use embeddings to find candidates
- Manual review validates which are genuine
- 40% precision in top-10 is good enough for candidate generation

### Extraction Prompt Reference

See `examples/session33_experiments.md` or `SESSION34_RESULTS.md` for the exact LLM prompt that achieved 100% quality in Session 36.

**Key principles**:
- Extract STRUCTURE, not content
- Domain-neutral language
- Causal relationships
- Ignore method/empirical papers

---

## Timeline

- **Part 1 (LLM Extraction)**: 2-3 hours (most time-intensive)
- **Part 2 (Embeddings)**: 30 min
- **Part 3 (Matching)**: 30 min
- **Part 4 (Export)**: 30 min
- **Total**: ~3.5-4.5 hours

---

## Context Files to Read

**MUST READ**:
1. **SESSION36_DIVERSE_SAMPLE_TEST.md** - Why we're doing manual curation
2. **SESSION34_RESULTS.md** - LLM extraction approach and prompts
3. **examples/session33_experiments.md** - Original extraction validation

**Optional**:
- SESSION35_EMBEDDING_TEST.md - Embedding validation
- PROGRESS.md - Full session history

---

## Ready to Begin!

Everything is set up. When you start Session 37:

1. Read SESSION36_DIVERSE_SAMPLE_TEST.md (understand the "why")
2. Read SESSION34_RESULTS.md (get the extraction prompt)
3. Create the extraction script (Part 1)
4. Process all 2,021 papers
5. Generate embeddings (Part 2)
6. Match candidates (Part 3)
7. Export for review (Part 4)
8. Create SESSION37_RESULTS.md
9. Update PROGRESS.md, METRICS.md
10. Commit everything

**Let's build the candidate pool!** 🚀

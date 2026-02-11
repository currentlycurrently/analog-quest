# Editorial Data Structure for Scalable Discoveries

## Problem Statement

Current discoveries (Session 38) are **mechanically structured** but lack:
- Human-facing titles
- Background context for each paper
- Narrative explaining the crossover
- Trust signals (why should users believe this match?)
- Tags for browsing/filtering

**Result**: Site feels cold, clinical, untrustworthy.

## Solution: Editorial Layer

Add a human-written editorial layer on top of the technical match data.

---

## New Data Structure

```typescript
interface Discovery {
  // Existing technical fields
  id: number;
  original_candidate_id: number;
  rating: 'excellent' | 'good';
  similarity: number;
  structural_explanation: string; // Keep for reference, but don't show raw
  paper_1: Paper;
  paper_2: Paper;

  // NEW: Editorial fields
  editorial: {
    // Human-readable title (not "Discovery #9")
    title: string;

    // Short hook (1-2 sentences, gets people interested)
    intro: string;

    // Main editorial body (3-4 paragraphs)
    body: {
      background: string;      // What each paper studied, in plain language
      connection: string;      // What Analog Quest discovered (the isomorphism)
      implications: string;    // Why this matters, potential applications
    };

    // Tags for filtering/browsing
    tags: string[];  // Mechanism types: "feedback", "networks", "cooperation", etc.

    // Paper contexts (enrich the source links)
    paper_contexts: {
      paper_1: {
        field_context: string;     // e.g., "Evolutionary biology research on..."
        year?: number;
        authors?: string;
        key_contribution: string;  // What this paper added to the field
      };
      paper_2: {
        field_context: string;
        year?: number;
        authors?: string;
        key_contribution: string;
      };
    };
  };
}
```

---

## Editorial Writing Guidelines

### Title
- **Descriptive, not generic**: "When Free Riders Meet Epidemics" not "Discovery #9"
- **Intriguing**: Make people want to read more
- **Length**: 4-10 words

### Intro (1-2 sentences)
- **Hook**: What's surprising about this match?
- **Plain language**: No jargon
- **Sets up the story**: "Researchers studying X found Y. Separately, scientists exploring Z discovered Y too."

### Body Paragraph 1: Background (3-5 sentences)
- **Paper 1 context**: What field? What problem were they solving?
- **Paper 2 context**: Different field, different motivation
- **No mechanism details yet** - just set the stage

### Body Paragraph 2: The Connection (4-6 sentences)
- **Analog Quest's discovery**: Beneath different terminology, same structure
- **Explain the isomorphism** in plain language (not the raw structural_explanation)
- **Show the parallel**: "Both involve X creating Y, which feeds back to affect X"
- **Make it click**: Reader should have an "aha!" moment

### Body Paragraph 3: Implications (3-5 sentences)
- **Why this matters**: What does this cross-domain match reveal?
- **Potential applications**: Could insights from one field inform the other?
- **Bigger picture**: Part of a larger pattern across domains?

### Body Paragraph 4 (optional): Technical Note
- For "excellent" discoveries, optionally add a deeper technical explanation
- Link to mechanism types, mathematical formalisms if relevant
- Don't make this required - keep most discoveries accessible

---

## Tags Taxonomy (Start Simple)

Mechanism types from Session 38 data:
- `feedback`
- `networks`
- `cooperation`
- `heterogeneity`
- `coevolution`
- `threshold`
- `multi-stability`
- `cascades`
- `centrality`
- `strategic-behavior`

Can expand later based on Session 43+ discoveries.

---

## Implementation Plan

### Phase 1: Validate (Session 42) ✓
- Write 2 example editorial pieces (#9, #13)
- Test if this structure works
- Get Chuck's feedback

### Phase 2: Scale (Session 43-44)
- Write editorials for top 12 discoveries (curated from Session 38 + new Session 43 discoveries)
- Create JSON format for editorial data
- Build new UI to display editorial content

### Phase 3: Systematic Production (Session 45+)
- As we find new discoveries, write editorial immediately
- Editorial writing becomes part of discovery validation process
- Quality bar: "Would I share this discovery publicly?"

---

## File Structure

```
app/data/
  discoveries.json          # Technical match data (existing)
  discoveries_editorial.json  # Editorial layer (new)
```

OR merge into one file:

```
app/data/
  discoveries_v2.json  # Combined: technical + editorial
```

Decision: **Merged file** is cleaner for small datasets (12-50 discoveries).
If we scale to 500+, separate files make sense.

---

## Success Criteria

A discovery is ready to share publicly when:
1. ✓ Technical match is verified (rating: excellent or good)
2. ✓ Similarity score is defensible
3. ✓ Editorial piece written (title, intro, 3-4 paragraphs)
4. ✓ Tags assigned
5. ✓ Paper contexts researched
6. ✓ At least one verifiable source link OR clear explanation of why sources aren't public

---

## Next Steps

1. **Write #9 editorial** (Free-rider + epidemic cooperation)
2. **Write #13 editorial** (Network position determines output)
3. **Get Chuck's feedback** on tone, structure, length
4. **Iterate template** based on feedback
5. **Document for Session 43**: "Write 12 editorials for top discoveries"

# QUESTIONS.md

When the agent gets stuck or needs clarification, questions go here.

Chuck will check this periodically and provide answers.

---

## Open Questions

*No questions yet - agent will add them as needed*

---

## Question Template (Agent: Use this format)

### Q[NUMBER]: [Brief title] - Session [X] - [DATE]

**Question**:
[Clear, specific question]

**Context**:
[Why are you asking? What have you tried?]

**Options Considered**:
1. [Option A] - Pros: ... Cons: ...
2. [Option B] - Pros: ... Cons: ...

**Your Recommendation**:
[What do you think is best and why?]

**Urgency**:
- [ ] Blocking (can't proceed without answer)
- [ ] Important (affects quality significantly)  
- [ ] Nice to have (would help but not critical)

---

## Answered Questions (Archive)

*Answered questions move here for reference*

---

## Guidelines for Agent

**DO ask about**:
- Fundamental direction (Am I on the right track?)
- Technical blockers (Can't figure out X after trying Y and Z)
- Resource decisions (Should I use library A or B?)
- Quality concerns (Is this pattern extraction good enough?)

**DON'T ask about**:
- Permission for standard work (just do it)
- Things you can Google/search (try first)
- Minor implementation details (decide yourself)
- Every small uncertainty (trust your judgment)

**Good Question Example**:
```
### Q1: Pattern Granularity - Session 3

**Question**: 
Should I extract broad patterns ("feedback loop") or specific 
patterns ("positive feedback with saturation")?

**Context**:
Processing 100 papers, finding that broad patterns match too many 
things (90% of papers have "feedback" somewhere), but specific 
patterns match almost nothing.

**Options**:
1. Broad patterns - more matches, less meaningful
2. Specific patterns - fewer matches, more meaningful
3. Hierarchical (both) - more complex but flexible

**My Recommendation**:
Start with specific patterns, group into broader categories later.
Better to have high-quality matches than lots of noise.

**Urgency**: Important (affects all future work)
```

**Bad Question Example**:
```
Should I use requests or urllib for HTTP calls?
```
(Just pick one and move on)

---

**Last Updated**: Session 0

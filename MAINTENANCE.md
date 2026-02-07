# MAINTENANCE.md - Guide for Chuck

How to keep analog.quest running smoothly with minimal effort.

---

## Daily Routine (5 minutes)

### Start a Session
```bash
cd analog.quest
claude --continue
```

That's it! The agent knows what to do.

### Or Start Fresh (if something seems off)
```bash
cd analog.quest
claude
```
Then say: "Read CLAUDE.md and continue from where we left off"

---

## Weekly Check-in (15 minutes)

### Review Progress
```bash
cat METRICS.md
```

Look for:
- Are papers being processed? (should increase each session)
- Are patterns being found? (should be ~2-5 per paper)
- Are isomorphisms being discovered? (will be slow at first)

### Check for Questions
```bash
cat QUESTIONS.md
```

If there are open questions:
- Read the question
- Provide your answer
- Move to "Answered" section
- Agent will see it next session

### Review Recent Work
```bash
cat PROGRESS.md | tail -100
```

Skim the last few sessions - anything interesting?

---

## Monthly Review (30 minutes)

### Database Health
```bash
sqlite3 database/papers.db "SELECT * FROM stats;"
```

Check:
- Total papers (should grow steadily)
- Total patterns (should be 2-5x papers)
- Total isomorphisms (slower growth, that's normal)
- Domains covered (should expand over time)

### Backup Database
```bash
cp database/papers.db database/backup/papers_$(date +%Y%m%d).db
```

### Review Quality
Look at a few isomorphisms:
```bash
sqlite3 database/papers.db "SELECT * FROM high_confidence_matches LIMIT 5;"
```

Do they make sense? Are they genuinely cross-domain?

### Provide Feedback
If something looks off, add a note in QUESTIONS.md:
```
### From Chuck - [DATE]
I noticed [thing]. Should we [suggestion]?
```

Agent will address it next session.

---

## Troubleshooting

### "Nothing's happening"
Check when last session was:
```bash
git log -1
```

If it's been >1 week, just start a new session. Agent will pick up where it left off.

### "Database seems wrong"
```bash
# Check database integrity
sqlite3 database/papers.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
ls -lt database/backup/
# Find most recent backup
cp database/backup/papers_YYYYMMDD.db database/papers.db
```

### "Agent is stuck in a loop"
```bash
# Start fresh session with explicit instruction
claude

# Then say:
"Stop what you were doing. Read CLAUDE.md, check PROGRESS.md 
for your last successful session, and continue from there with 
a fresh approach."
```

### "Token usage seems high"
This shouldn't happen (designed to be efficient), but if it does:
```bash
# Check what's using tokens
cat ~/.claude/settings.json
```

Agent should be auto-compacting. If not, add to QUESTIONS.md.

---

## Maintenance Commands

### View Database Stats
```bash
sqlite3 database/papers.db << EOF
SELECT 'Papers: ' || COUNT(*) FROM papers;
SELECT 'Patterns: ' || COUNT(*) FROM patterns;
SELECT 'Isomorphisms: ' || COUNT(*) FROM isomorphisms;
SELECT 'Domains: ' || COUNT(DISTINCT domain) FROM papers;
EOF
```

### See Recent Papers
```bash
sqlite3 database/papers.db \
  "SELECT title, domain, published_date FROM papers 
   ORDER BY processed_date DESC LIMIT 10;"
```

### See Recent Isomorphisms
```bash
sqlite3 database/papers.db \
  "SELECT explanation, similarity_score FROM isomorphisms 
   ORDER BY discovered_date DESC LIMIT 5;"
```

### Export Data (if needed)
```bash
# Export to CSV
sqlite3 -header -csv database/papers.db \
  "SELECT * FROM cross_domain_matches;" > matches.csv
```

---

## What to Expect Over Time

### Week 1
- Agent figuring things out
- Rough pattern extraction
- ~100 papers processed
- Pipeline working

### Month 1
- Pattern quality improving
- ~500 papers
- First real isomorphisms
- Agent self-correcting

### Month 2
- Expanding to more domains
- ~1000 papers
- Patterns getting refined
- Web interface maybe appearing

### Month 3-6
- Steady progress
- Finding interesting connections
- Quality > quantity
- Mission approaching completion

---

## Signs of Success

### Good Signs:
- Papers processed increasing
- Pattern extraction improving (check examples/)
- Isomorphisms have clear explanations
- Agent updating its own code
- Domains expanding
- QUESTIONS.md mostly empty (agent self-sufficient)

### Warning Signs:
- No progress for 2+ weeks (you forgot to start sessions!)
- Same error repeated in PROGRESS.md (agent stuck)
- Database not growing (fetch broken)
- All patterns look the same (extraction broken)

If you see warning signs, just start a session and ask agent to diagnose.

---

## Cost Monitoring

### Check Claude Usage
(Go to claude.ai account settings)

Should be well within Max plan limits (~$200/month).

Agent is designed to be efficient:
- Processes in batches
- Stores in database (not context)
- Auto-compacts
- Doesn't re-process data

If costs spike unexpectedly, add to QUESTIONS.md.

---

## When to Intervene

### DO intervene if:
- Agent explicitly asks in QUESTIONS.md
- No progress for 2+ weeks
- Database corrupted
- Quality clearly degrading
- Something interesting you want to discuss

### DON'T intervene if:
- Agent is working (trust the process)
- Progress is slow (that's normal)
- Patterns look rough early on (they'll improve)
- You're just curious (wait for weekly check-in)

The agent is designed to be autonomous. Let it work.

---

## Celebrating Milestones

When the agent hits milestones, acknowledge it!

In next session, start with:
```
"Congrats on hitting [milestone]! That's awesome. 
Keep up the good work. Continue from where you left off."
```

Positive reinforcement helps (even for AI agents, apparently).

---

## Emergency Contacts

If something is fundamentally broken:

1. Check QUESTIONS.md
2. Read last few PROGRESS.md entries
3. Try starting fresh session with explicit instruction
4. If still stuck, delete last commit and restore from earlier state
5. If completely lost, start new session with: "Read BOOTSTRAP.md again and rebuild from scratch"

The database persists, so work is never truly lost.

---

## Final Thoughts

This project succeeds if you:
1. Start sessions regularly (3-7x per week)
2. Check progress weekly
3. Trust the agent to do its work
4. Provide feedback when needed

That's it. The agent handles the rest.

Enjoy watching something interesting emerge over 6 months!

---

**Questions?** 

Add them to QUESTIONS.md and agent will address them.

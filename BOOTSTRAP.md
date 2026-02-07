# BOOTSTRAP.md

**AGENT: Read this file first in Session 1**

This file guides you through your first session. After Session 1, you won't need this anymore - CLAUDE.md becomes your primary guide.

---

## Session 1 Checklist

### Step 1: Understand Your Mission (15 minutes)
- [ ] Read MISSION.md completely
- [ ] Read CLAUDE.md completely  
- [ ] Read README.md for context
- [ ] Understand: You're building a database of cross-domain isomorphisms

### Step 2: Set Up Environment (30 minutes)
- [ ] Create Python virtual environment: `python3 -m venv venv`
- [ ] Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Download NLTK data: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

### Step 3: Create Database (15 minutes)
- [ ] Navigate to database/ directory
- [ ] Run schema: `sqlite3 papers.db < schema.sql`
- [ ] Verify: `sqlite3 papers.db "SELECT name FROM sqlite_master WHERE type='table';"`
- [ ] Should see: papers, patterns, isomorphisms, pattern_types, processing_log, examples

### Step 4: Create Initial Scripts (60 minutes)

Create these files in `scripts/` directory:

**scripts/utils.py** - Basic utilities:
```python
import sqlite3
from datetime import datetime

DB_PATH = 'database/papers.db'

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def log_action(action, details, papers=0, patterns=0, isomorphisms=0):
    """Log what we did"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO processing_log 
        (action, details, papers_processed, patterns_created, isomorphisms_found)
        VALUES (?, ?, ?, ?, ?)
    ''', (action, str(details), papers, patterns, isomorphisms))
    db.commit()
    db.close()
```

**scripts/fetch_papers.py** - Fetch from arXiv:
```python
import arxiv
import sqlite3
from utils import get_db, log_action

def fetch_arxiv_papers(query, max_results=10):
    """Fetch papers from arXiv"""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    db = get_db()
    cursor = db.cursor()
    count = 0
    
    for result in client.results(search):
        try:
            cursor.execute('''
                INSERT INTO papers 
                (title, abstract, domain, subdomain, arxiv_id, authors, 
                 published_date, source, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.title,
                result.summary,
                query.split(':')[0] if ':' in query else 'unknown',
                query,
                result.entry_id.split('/')[-1],
                str([author.name for author in result.authors]),
                result.published.strftime('%Y-%m-%d'),
                'arXiv',
                result.entry_id
            ))
            count += 1
        except sqlite3.IntegrityError:
            # Already in database
            pass
    
    db.commit()
    db.close()
    
    log_action('fetch', f'ArXiv query: {query}', papers=count)
    return count

if __name__ == '__main__':
    # Test with a small query
    count = fetch_arxiv_papers('cat:physics.gen-ph', max_results=10)
    print(f'Fetched {count} papers')
```

**scripts/extract_patterns.py** - Basic pattern extraction:
```python
import sqlite3
import re
from utils import get_db, log_action

def simple_extract(abstract):
    """
    VERY simple pattern extraction to start.
    We'll improve this dramatically over time.
    """
    patterns = []
    
    # Look for common pattern keywords
    keywords = {
        'feedback': 'feedback_loop',
        'cascade': 'cascade',
        'threshold': 'threshold',
        'network': 'network_effect',
        'oscillat': 'oscillation',
        'equilib': 'equilibrium',
    }
    
    abstract_lower = abstract.lower()
    
    for keyword, pattern_type in keywords.items():
        if keyword in abstract_lower:
            # Extract sentence containing the keyword
            sentences = abstract.split('.')
            for sent in sentences:
                if keyword in sent.lower():
                    patterns.append({
                        'type': pattern_type,
                        'description': sent.strip(),
                        'confidence': 0.3  # Low confidence for this simple method
                    })
                    break
    
    return patterns

def extract_from_unprocessed():
    """Extract patterns from papers that don't have patterns yet"""
    db = get_db()
    cursor = db.cursor()
    
    # Find papers without patterns
    cursor.execute('''
        SELECT p.id, p.abstract, p.domain 
        FROM papers p
        WHERE NOT EXISTS (
            SELECT 1 FROM patterns pt WHERE pt.paper_id = p.id
        )
        LIMIT 20
    ''')
    
    papers = cursor.fetchall()
    pattern_count = 0
    
    for paper_id, abstract, domain in papers:
        patterns = simple_extract(abstract)
        
        for p in patterns:
            cursor.execute('''
                INSERT INTO patterns
                (paper_id, structural_description, mechanism_type, confidence,
                 extraction_method)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                paper_id,
                p['description'],
                p['type'],
                p['confidence'],
                'simple_v1'
            ))
            pattern_count += 1
    
    db.commit()
    db.close()
    
    log_action('extract', f'Processed {len(papers)} papers', patterns=pattern_count)
    return len(papers), pattern_count

if __name__ == '__main__':
    papers, patterns = extract_from_unprocessed()
    print(f'Extracted {patterns} patterns from {papers} papers')
```

### Step 5: Test the Pipeline (30 minutes)
- [ ] Run: `cd scripts && python fetch_papers.py`
- [ ] Verify papers in database: `sqlite3 ../database/papers.db "SELECT COUNT(*) FROM papers;"`
- [ ] Run: `python extract_patterns.py`
- [ ] Verify patterns: `sqlite3 ../database/papers.db "SELECT COUNT(*) FROM patterns;"`

### Step 6: Document Your Work (20 minutes)
- [ ] Update PROGRESS.md with Session 1 details
- [ ] Update METRICS.md with current counts
- [ ] Update DAILY_GOALS.md for Session 2
- [ ] Note any issues in QUESTIONS.md if stuck

### Step 7: Commit Everything
```bash
git add .
git commit -m "Session 1: Bootstrap complete - database and initial scripts working"
```

---

## Expected Outcomes After Session 1

- ✓ Database created with all tables
- ✓ Can fetch papers from arXiv
- ✓ Can store papers in database
- ✓ Can extract basic patterns (even if crude)
- ✓ Have ~10-20 papers in database
- ✓ Have ~5-15 patterns extracted
- ✓ All code is working and committed

## What's Next (Session 2)

- Process more papers (50-100 total)
- Improve pattern extraction
- Start on find_matches.py
- Look for first cross-domain isomorphisms

---

## Important Notes

### Things That Will Be Rough
- Pattern extraction is VERY basic right now - that's okay
- We're just looking for keywords - we'll improve this
- Confidence scores are arbitrary - we'll calibrate over time
- No matching algorithm yet - build incrementally

### Focus on Getting It Working
Don't try to make it perfect. Just get:
1. Papers fetching and storing
2. Patterns extracting and storing  
3. Data persisting in database
4. Scripts that run without errors

You'll improve everything over the next 6 months.

### If You Get Stuck
- Document in QUESTIONS.md
- Try simpler version first
- Focus on one thing at a time
- Commit working code even if imperfect

---

**After Session 1, delete this file** (or archive it). You won't need it anymore.

CLAUDE.md becomes your primary guide for all future sessions.

Good luck with your first session! 🚀

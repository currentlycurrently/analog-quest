# 🚨 FIX THE INFRASTRUCTURE - STEP BY STEP 🚨

## Do This RIGHT NOW (30 minutes)

### Step 1: Install Vercel CLI (2 min)
```bash
npm i -g vercel
```

### Step 2: Link to Your Project (2 min)
```bash
vercel link
# Choose your project analog-quest
```

### Step 3: Go to Vercel Dashboard
1. Go to: https://vercel.com/dashboard
2. Click on your analog-quest project
3. Go to "Storage" tab
4. Click "Create Database"
5. Choose "Postgres"
6. Name it: `analog-quest-db`
7. Choose region closest to you
8. Click "Create"

### Step 4: Get Your Environment Variables (2 min)
1. After creating, click "Show secret"
2. Copy all the environment variables
3. Create `.env.local` in your project:

```bash
# Create the file
touch .env.local
```

Then paste:
```
POSTGRES_URL="postgres://..."
POSTGRES_PRISMA_URL="postgres://..."
POSTGRES_URL_NON_POOLING="postgres://..."
POSTGRES_USER="default"
POSTGRES_HOST="..."
POSTGRES_PASSWORD="..."
POSTGRES_DATABASE="verceldb"
```

### Step 5: Install Vercel Postgres SDK (1 min)
```bash
npm install @vercel/postgres
```

### Step 6: Create Your Database Tables (5 min)
Go to Vercel Dashboard → Storage → Your Database → Query

Run this SQL:
```sql
-- Core discoveries table
CREATE TABLE discoveries (
  id SERIAL PRIMARY KEY,
  mechanism_1_id INTEGER NOT NULL,
  mechanism_2_id INTEGER NOT NULL,
  mechanism_1_desc TEXT,
  mechanism_2_desc TEXT,
  domain_1 VARCHAR(100),
  domain_2 VARCHAR(100),
  paper_1_title VARCHAR(500),
  paper_2_title VARCHAR(500),
  similarity DECIMAL(5,4) NOT NULL,
  rating VARCHAR(20) NOT NULL,
  structural_similarity TEXT,
  session_number INTEGER,
  discovered_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(mechanism_1_id, mechanism_2_id)
);

-- Index for faster queries
CREATE INDEX idx_similarity ON discoveries(similarity DESC);
CREATE INDEX idx_rating ON discoveries(rating);
CREATE INDEX idx_session ON discoveries(session_number);
```

### Step 7: Create Your First API Route (5 min)
```bash
mkdir -p app/api/discoveries
```

Create `app/api/discoveries/route.ts`:
```typescript
import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const { rows } = await sql`
      SELECT * FROM discoveries
      ORDER BY similarity DESC
    `;
    return NextResponse.json({ discoveries: rows });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch discoveries' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const { rows } = await sql`
      INSERT INTO discoveries (
        mechanism_1_id, mechanism_2_id,
        mechanism_1_desc, mechanism_2_desc,
        domain_1, domain_2,
        paper_1_title, paper_2_title,
        similarity, rating,
        structural_similarity, session_number
      ) VALUES (
        ${body.mechanism_1_id}, ${body.mechanism_2_id},
        ${body.mechanism_1_desc}, ${body.mechanism_2_desc},
        ${body.domain_1}, ${body.domain_2},
        ${body.paper_1_title}, ${body.paper_2_title},
        ${body.similarity}, ${body.rating},
        ${body.structural_similarity}, ${body.session_number}
      )
      RETURNING *
    `;

    return NextResponse.json({ discovery: rows[0] });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to create discovery' }, { status: 500 });
  }
}
```

### Step 8: Test Locally (5 min)
```bash
npm run dev
```

Go to: http://localhost:3000/api/discoveries
You should see: `{"discoveries":[]}`

### Step 9: Migrate Your Existing Data (10 min)
Create `scripts/migrate_to_vercel.py`:
```python
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

# Load your discoveries
with open('app/data/discovered_pairs.json', 'r') as f:
    pairs = json.load(f)

# Your local API endpoint (while npm run dev is running)
API_URL = "http://localhost:3000/api/discoveries"

for pair in pairs['discovered_pairs']:
    # Get the details from session files
    # This is a simplified version - adapt based on your data structure

    data = {
        "mechanism_1_id": pair.get('paper_1_id') or pair.get('mechanism_1_id'),
        "mechanism_2_id": pair.get('paper_2_id') or pair.get('mechanism_2_id'),
        "similarity": pair['similarity'],
        "rating": pair['rating'],
        "session_number": pair['discovered_in_session'],
        "mechanism_1_desc": "To be filled",  # You'll need to get these from session files
        "mechanism_2_desc": "To be filled",
        "domain_1": "unknown",
        "domain_2": "unknown",
        "paper_1_title": "To be filled",
        "paper_2_title": "To be filled",
        "structural_similarity": "To be filled"
    }

    response = requests.post(API_URL, json=data)
    if response.status_code == 200:
        print(f"✓ Migrated discovery {pair['mechanism_1_id']} ↔ {pair['mechanism_2_id']}")
    else:
        print(f"✗ Failed to migrate: {response.text}")
```

### Step 10: Deploy It! (2 min)
```bash
vercel --prod
```

## What You'll Have After This:

✅ Real database in production
✅ API endpoints that work
✅ Can add discoveries programmatically
✅ No more JSON file editing
✅ Proper infrastructure for scaling

## Next Steps (After This Works):
1. Update frontend to fetch from API
2. Create admin interface
3. Set up automated discovery pipeline
4. Remove dependency on static JSON

---

**DO THIS NOW! Don't mine another discovery until this is working!**
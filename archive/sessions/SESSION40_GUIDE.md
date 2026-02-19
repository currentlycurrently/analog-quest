# Session 40: Frontend Core Build

**Mission**: Build the functional MVP of analog.quest following FRONTEND_SPEC.md exactly.

**Goal**: By end of this session, all 30 discoveries should be browsable on localhost.

**Time Budget**: 4-5 hours

---

## Part 1: Project Setup (30 min)

### Create Next.js project

```bash
npx create-next-app@latest analog-quest-frontend --typescript --tailwind --app
cd analog-quest-frontend
```

### Install dependencies

```bash
npm install
```

### Configure

**next.config.js** - Enable static export:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
}

module.exports = nextConfig
```

**tailwind.config.js** - Add custom colors for domains:
```javascript
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'domain-econ': '#3b82f6',     // blue
        'domain-qbio': '#10b981',     // green
        'domain-physics': '#8b5cf6',  // purple
        'domain-cs': '#f97316',       // orange
        'domain-nlin': '#ef4444',     // red
        'domain-unknown': '#6b7280',  // gray
      },
    },
  },
  plugins: [],
}
```

**Create data folder:**
```bash
mkdir -p public/data
```

---

## Part 2: Data Transformation (45 min)

### Create transformation script

**scripts/transform_for_frontend.js**

Convert `examples/SESSION38_VERIFIED_ISOMORPHISMS.json` → `public/data/discoveries.json`

**Transform to frontend-friendly format:**
```json
{
  "meta": {
    "total": 30,
    "excellent": 10,
    "good": 20,
    "lastUpdated": "2026-02-10"
  },
  "discoveries": [
    {
      "id": "cell-size-control",
      "name": "Cell Size Feedback Control",
      "rating": "excellent",
      "similarity": 0.736,
      "domainPair": ["unknown", "q-bio"],
      "explanation": "Both describe cell size feedback control through phase-specific mechanisms...",
      "paper1": {
        "domain": "unknown",
        "title": "Effects of multi-phase control mechanism on fibroblast dynamics",
        "mechanism": "Cell size determined by control mechanisms...",
        "arxivId": "N/A"
      },
      "paper2": { /* same structure */ }
    }
  ]
}
```

**Key transformations:**
1. Generate slugified IDs from paper titles or sequential numbers
2. Simplify domain names (q-bio, econ, physics, etc.)
3. Format domainPair as array for easy display
4. Keep all essential fields from Session 38

**Run transformation:**
```bash
node scripts/transform_for_frontend.js
```

**Validate output:**
- Check all 30 discoveries present
- Verify JSON is valid
- Confirm all fields populated

---

## Part 3: Component Library (1.5 hours)

Build the 3 core components from FRONTEND_SPEC.md:

### 1. DiscoveryCard Component

**components/DiscoveryCard.tsx**

```typescript
interface DiscoveryCardProps {
  id: string
  name: string
  rating: 'excellent' | 'good'
  similarity: number
  domainPair: [string, string]
  explanation: string
}

export default function DiscoveryCard(props: DiscoveryCardProps) {
  // Shows:
  // - Quality badge (excellent = gold, good = blue)
  // - Name (bold, 18px)
  // - Domain badges
  // - Truncated explanation (200 chars)
  // - Similarity score
  // - Link to /discoveries/[id]

  // Styling: Card with shadow, hover effect
}
```

### 2. DomainBadge Component

**components/DomainBadge.tsx**

```typescript
interface DomainBadgeProps {
  domain: string
  size?: 'sm' | 'md' | 'lg'
}

export default function DomainBadge({ domain, size = 'md' }: DomainBadgeProps) {
  // Shows: domain name with color
  // Colors:
  // - econ: blue
  // - q-bio: green
  // - physics: purple
  // - cs: orange
  // - nlin: red
  // - unknown: gray

  // Style: rounded pill badge
}
```

### 3. SimilarityScore Component

**components/SimilarityScore.tsx**

```typescript
interface SimilarityScoreProps {
  score: number  // 0-1
  showBar?: boolean
}

export default function SimilarityScore({ score, showBar = true }: SimilarityScoreProps) {
  // Shows: score number + progress bar
  // Visual: gradient color based on score
  // - ≥0.70: green
  // - ≥0.60: yellow
  // - ≥0.50: orange
  // - <0.50: red
}
```

**Test each component:**
Create test page at `app/components-test/page.tsx` to verify styling and functionality.

---

## Part 4: Page Implementation (2 hours)

### 1. Home Page

**app/page.tsx**

**Structure:**
```
┌─────────────────────────────────────────────┐
│ HERO SECTION                                │
│ H1: "30 Verified Cross-Domain Structural   │
│      Isomorphisms"                          │
│ Subtitle: Mapping hidden connections...    │
├─────────────────────────────────────────────┤
│ STATS ROW                                   │
│ [2,021 papers] [54 mechanisms]             │
│ [30 discoveries] [67% precision]           │
├─────────────────────────────────────────────┤
│ TOP 3 DISCOVERIES                           │
│ [Card 1] [Card 2] [Card 3]                 │
│ (Highest similarity Excellent matches)     │
├─────────────────────────────────────────────┤
│ CALL TO ACTION                              │
│ [Explore All Discoveries →]                │
│ [How It Works] [GitHub]                    │
└─────────────────────────────────────────────┘
```

**Implementation:**
- Load discoveries.json
- Sort by similarity descending
- Filter rating === 'excellent'
- Take top 3
- Use DiscoveryCard component

### 2. Discoveries Page

**app/discoveries/page.tsx**

**Structure:**
```
┌─────────────────────────────────────────────┐
│ DISCOVERIES (30 total)                     │
├─────────────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐                   │
│ │ Card│ │ Card│ │ Card│  (3 cols desktop) │
│ └─────┘ └─────┘ └─────┘                   │
│ ┌─────┐ ┌─────┐ ┌─────┐                   │
│ │ Card│ │ Card│ │ Card│                   │
│ └─────┘ └─────┘ └─────┘                   │
│ ... (grid continues)                       │
└─────────────────────────────────────────────┘
```

**Implementation:**
- Load all 30 discoveries
- Display in grid:
  - Desktop (≥1024px): 3 columns
  - Tablet (768-1023px): 2 columns
  - Mobile (<768px): 1 column
- Use DiscoveryCard component
- Simple layout (no filters yet - Session 41)

### 3. Discovery Detail Page

**app/discoveries/[id]/page.tsx**

**Structure:**
```
┌─────────────────────────────────────────────┐
│ [← Back to Discoveries]                    │
│                                             │
│ Cell Size Feedback Control                 │
│ 🏆 EXCELLENT  Similarity: 0.74 [████░░]    │
│ [unknown] ↔ [q-bio]                        │
├─────────────────────────────────────────────┤
│ STRUCTURAL EXPLANATION                      │
│ Both describe cell size feedback control   │
│ through phase-specific mechanisms...       │
├─────────────────────────────────────────────┤
│ PAPER 1                    PAPER 2          │
│ ┌──────────────┐          ┌──────────────┐ │
│ │ [unknown]    │          │ [q-bio]      │ │
│ │ Title...     │          │ Title...     │ │
│ │              │          │              │ │
│ │ Mechanism... │          │ Mechanism... │ │
│ └──────────────┘          └──────────────┘ │
├─────────────────────────────────────────────┤
│ [← Previous]              [Next →]         │
└─────────────────────────────────────────────┘
```

**Implementation:**
- Dynamic route based on discovery.id
- Load discovery from discoveries.json
- Display full details:
  - Header: name, rating, similarity, domains
  - Structural explanation (prominent, large text)
  - Papers side-by-side (2 columns on desktop, stacked on mobile)
  - Each paper: domain badge, title, mechanism
- Navigation: previous/next discovery links
- Back button to /discoveries

**generateStaticParams:**
```typescript
export async function generateStaticParams() {
  const discoveries = await loadDiscoveries()
  return discoveries.map((d) => ({ id: d.id }))
}
```

---

## Part 5: Basic Styling (30 min)

### Apply Tailwind consistently

**Typography:**
- H1: `text-4xl font-bold`
- H2: `text-3xl font-bold`
- H3: `text-2xl font-semibold`
- Body: `text-base`
- Small: `text-sm`

**Spacing:**
- Page padding: `px-4 py-8 md:px-8 lg:px-16`
- Section gaps: `space-y-8`
- Card padding: `p-6`

**Colors:**
- Background: `bg-gray-50`
- Cards: `bg-white`
- Text: `text-gray-900`
- Muted: `text-gray-600`

**Cards:**
- Border: `border border-gray-200`
- Rounded: `rounded-lg`
- Shadow: `shadow-sm hover:shadow-md`
- Transition: `transition-shadow duration-200`

### Test responsiveness

**Test on:**
- Desktop: 1920px
- Tablet: 768px
- Mobile: 375px

**Check:**
- Grid collapses correctly
- Text is readable
- Cards stack on mobile
- Navigation works
- No horizontal scroll

---

## Success Criteria

By end of Session 40:

✅ **Next.js project running locally**
- `npm run dev` works
- No TypeScript errors
- No console errors

✅ **discoveries.json created and validated**
- All 30 discoveries present
- Valid JSON structure
- All fields populated

✅ **3 components built and working**
- DiscoveryCard renders correctly
- DomainBadge shows colors
- SimilarityScore displays bar

✅ **3 pages functional**
- Home page (/, with hero + stats + top 3)
- Discoveries list (/discoveries, all 30 in grid)
- Detail page (/discoveries/[id], full info)

✅ **All 30 discoveries browsable**
- Can navigate from home → list → detail
- All links work
- Content displays correctly

✅ **Mobile responsive**
- Grid collapses on mobile
- Text readable on small screens
- No layout breaks

✅ **Ready for Session 41 polish**
- Clean codebase
- No TODO comments
- Git committed

---

## What NOT to do yet

Session 40 is about **core functionality only**. Do NOT implement:

❌ **Filtering/sorting** (Session 41)
❌ **Methodology page** (Session 41)
❌ **About page** (Session 41)
❌ **SEO optimization** (Session 41)
❌ **Deployment** (Session 41)
❌ **Search functionality** (Session 41)
❌ **Advanced animations** (Session 41)

Focus on core functionality first!

---

## Quick Reference

**Key files to create:**
- `scripts/transform_for_frontend.js` - Data transformation
- `public/data/discoveries.json` - Frontend data
- `components/DiscoveryCard.tsx` - Card component
- `components/DomainBadge.tsx` - Domain badge
- `components/SimilarityScore.tsx` - Score display
- `app/page.tsx` - Home page
- `app/discoveries/page.tsx` - List page
- `app/discoveries/[id]/page.tsx` - Detail page
- `lib/data.ts` - Data loading utilities

**Data source:**
- `examples/SESSION38_VERIFIED_ISOMORPHISMS.json` (30 verified discoveries)

**Reference:**
- `FRONTEND_SPEC.md` - Complete specification
- `GROWTH_STRATEGY.md` - Context on the project

---

**Time Budget**: 4-5 hours

Let's build! 🚀

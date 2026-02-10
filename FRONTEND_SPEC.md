# FRONTEND SPEC.md

**Version**: 1.0
**Date**: 2026-02-10
**Target**: analog.quest v1.0 MVP
**Build Timeline**: Sessions 40-41 (7-9 hours total)

---

## Executive Summary

Build a clean, fast, static Next.js site showcasing **30 verified cross-domain isomorphisms**. Focus on:
1. **Discoverability**: Easy to browse and filter discoveries
2. **Clarity**: Clear explanations of what makes each match an isomorphism
3. **Credibility**: Transparent methodology and quality standards
4. **Delight**: Beautiful, polished UI that invites exploration

**Technology**: Next.js 14+ (App Router), Tailwind CSS, Static Export, Vercel deployment

---

## Site Architecture

### Pages

1. **`/` (Home/Landing)**
   - Hero section with value proposition
   - Featured discoveries (top 3 excellent matches)
   - Quick stats (30 discoveries, 6 domains, etc.)
   - Call-to-action to explore all discoveries

2. **`/discoveries` (Browse)**
   - Grid of discovery cards (all 30)
   - Filter by domain pair, rating, similarity
   - Sort by similarity, rating, or domain
   - Search by keyword (title, mechanism)

3. **`/discoveries/[id]` (Individual Discovery)**
   - Full details of a single isomorphism
   - Side-by-side comparison of both papers
   - Structural explanation front and center
   - Similarity score with visual indicator
   - Links to original papers (if arXiv IDs available)

4. **`/methodology` (How It Works)**
   - Explanation of the process
   - LLM extraction → embeddings → manual curation
   - Quality standards and rating system
   - Limitations and future work

5. **`/about` (About the Project)**
   - Story: Why this project exists
   - Built with Claude Code (link to repo)
   - Contact/feedback form or email
   - Future roadmap

### Navigation Structure

```
analog.quest/
├── Home (/)
├── Discoveries (/discoveries)
│   └── Individual Discovery (/discoveries/[id])
├── Methodology (/methodology)
└── About (/about)
```

---

## Data Structure

### Source Data
**File**: `examples/SESSION38_VERIFIED_ISOMORPHISMS.json` (46KB)

**Structure**:
```json
{
  "metadata": {
    "session": 38,
    "total_verified": 30,
    "excellent": 10,
    "good": 20,
    "similarity_range": { "min": 0.44, "max": 0.74, "mean": 0.54 }
  },
  "domain_pairs": {
    "econ-q-bio": 7,
    "physics-q-bio": 5,
    ...
  },
  "verified_isomorphisms": [
    {
      "id": 1,
      "rating": "excellent",
      "similarity": 0.736,
      "structural_explanation": "Both describe cell size feedback control...",
      "paper_1": {
        "paper_id": 525,
        "domain": "unknown",
        "title": "Effects of multi-phase control...",
        "mechanism": "Cell size determined by control..."
      },
      "paper_2": { ... }
    },
    ...
  ]
}
```

### Frontend Data Transformation

**File**: `app/data/discoveries.json`

Transform source data to frontend-optimized structure:
```json
{
  "meta": {
    "total": 30,
    "excellent": 10,
    "good": 20,
    "lastUpdated": "2026-02-10",
    "domains": ["econ", "q-bio", "physics", "cs", "nlin", "unknown"]
  },
  "discoveries": [
    {
      "id": "1",
      "title": "Cell Size Feedback Control",  // Generated from papers
      "rating": "excellent",
      "similarity": 0.736,
      "domainPair": ["unknown", "q-bio"],
      "explanation": "Both describe cell size feedback control...",
      "paper1": {
        "domain": "unknown",
        "title": "Effects of multi-phase control...",
        "mechanism": "Cell size determined by control...",
        "arxivId": "N/A"
      },
      "paper2": { ... },
      "tags": ["feedback", "cell-size", "homeostasis"]  // Auto-generated
    },
    ...
  ]
}
```

**Transformation script**: `scripts/transform_for_frontend.js`

---

## Component Specifications

### 1. DiscoveryCard Component

**Location**: `components/DiscoveryCard.tsx`

**Props**:
```typescript
interface DiscoveryCardProps {
  id: string
  title: string
  rating: 'excellent' | 'good'
  similarity: number
  domainPair: [string, string]
  explanation: string  // truncated to 200 chars
  paper1Domain: string
  paper2Domain: string
}
```

**Design**:
```
┌─────────────────────────────────────────┐
│ 🏆 EXCELLENT          Similarity: 0.74 │  <- Badge + Score
├─────────────────────────────────────────┤
│ Cell Size Feedback Control             │  <- Title (bold, 18px)
├─────────────────────────────────────────┤
│ [unknown] ↔ [q-bio]                    │  <- Domain badges
├─────────────────────────────────────────┤
│ Both describe cell size feedback        │  <- Truncated explanation
│ control through phase-specific...       │
│                                         │
│ [Read More →]                           │  <- Link to /discoveries/[id]
└─────────────────────────────────────────┘
```

**Styling**:
- Card: `border rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white`
- Rating badge: `excellent` = gold/yellow, `good` = blue/teal
- Similarity score: Color-coded (>0.7 = green, >0.6 = yellow, >0.5 = orange)
- Domain badges: Each domain has a distinct color

### 2. DomainBadge Component

**Location**: `components/DomainBadge.tsx`

**Props**:
```typescript
interface DomainBadgeProps {
  domain: string
  size?: 'sm' | 'md' | 'lg'
}
```

**Domain Colors**:
```typescript
const DOMAIN_COLORS = {
  'econ': 'bg-blue-100 text-blue-800',
  'q-bio': 'bg-green-100 text-green-800',
  'physics': 'bg-purple-100 text-purple-800',
  'cs': 'bg-orange-100 text-orange-800',
  'nlin': 'bg-red-100 text-red-800',
  'unknown': 'bg-gray-100 text-gray-800',
}
```

**Design**: Small rounded pill with colored background

### 3. SimilarityScore Component

**Location**: `components/SimilarityScore.tsx`

**Props**:
```typescript
interface SimilarityScoreProps {
  score: number  // 0-1
  showBar?: boolean  // Show visual bar
}
```

**Design**:
```
Similarity: 0.74  [████████████░░░░░░░░]  (74%)
```

**Colors**:
- ≥0.70: `text-green-600`
- ≥0.60: `text-yellow-600`
- ≥0.50: `text-orange-600`
- <0.50: `text-red-600`

### 4. FilterBar Component

**Location**: `components/FilterBar.tsx`

**Props**:
```typescript
interface FilterBarProps {
  onFilterChange: (filters: Filters) => void
  domains: string[]
}

interface Filters {
  domainPair?: string  // "econ↔q-bio" or "all"
  rating?: 'excellent' | 'good' | 'all'
  minSimilarity?: number
  sortBy?: 'similarity' | 'rating' | 'domain'
}
```

**Design**:
```
┌────────────────────────────────────────────────────────────────┐
│ Filters:  [Domain Pair ▼] [Rating ▼] [Min Similarity: 0.5]   │
│ Sort by:  [Similarity ▼]                                      │
│                                                  30 results    │
└────────────────────────────────────────────────────────────────┘
```

### 5. ComparisonView Component

**Location**: `components/ComparisonView.tsx`

**Props**:
```typescript
interface ComparisonViewProps {
  paper1: Paper
  paper2: Paper
  structuralExplanation: string
}
```

**Design**: Two-column layout with structural explanation at top

```
┌─────────────────────────────────────────────────────────────┐
│ STRUCTURAL ISOMORPHISM                                      │
│ Both describe cell size feedback control through...        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────┬─────────────────────────┐
│ Paper 1: [unknown]      │ Paper 2: [q-bio]       │
├─────────────────────────┼─────────────────────────┤
│ Effects of multi-phase  │ Coarse-graining and    │
│ control mechanism...    │ stochastic...          │
├─────────────────────────┼─────────────────────────┤
│ MECHANISM:              │ MECHANISM:             │
│ Cell size determined by │ Cell size feedback     │
│ control mechanisms...   │ operates through...    │
│                         │                        │
│ [View on arXiv →]       │ [View on arXiv →]      │
└─────────────────────────┴─────────────────────────┘
```

---

## Page Layouts

### Home Page (`/`)

**Hero Section**:
```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│              🔬 analog.quest                              │
│                                                           │
│      Mapping Structural Isomorphisms Across Science       │
│                                                           │
│   The same idea appears in different fields, wearing     │
│   different terminology. We find the hidden connections. │
│                                                           │
│              [Explore 30 Discoveries →]                   │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**Quick Stats**:
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 30          │ 6           │ 10          │ 0.54        │
│ Discoveries │ Domains     │ Excellent   │ Avg Score   │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Featured Discoveries** (3 cards):
- Show top 3 excellent matches by similarity
- Use DiscoveryCard component

**How It Works** (3-step visual):
```
1. Extract           2. Match             3. Curate
   Mechanisms    →     Semantically    →     Manually
   [icon]             [icon]               [icon]
```

**Footer**:
- Links to methodology, about, GitHub
- "Built with Claude Code"
- Last updated date

### Discoveries Page (`/discoveries`)

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ DISCOVERIES (30 total)                                    │
│                                                            │
│ [FilterBar component]                                     │
│                                                            │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                     │
│ │ Card 1  │ │ Card 2  │ │ Card 3  │                     │
│ └─────────┘ └─────────┘ └─────────┘                     │
│                                                            │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                     │
│ │ Card 4  │ │ Card 5  │ │ Card 6  │                     │
│ └─────────┘ └─────────┘ └─────────┘                     │
│                                                            │
│ ... (grid continues)                                      │
└────────────────────────────────────────────────────────────┘
```

**Grid**: 3 columns on desktop, 2 on tablet, 1 on mobile

**State Management**: Use React `useState` for filters, no external state management needed

### Individual Discovery Page (`/discoveries/[id]`)

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ [← Back to Discoveries]                                   │
│                                                            │
│ Cell Size Feedback Control                                │
│ 🏆 EXCELLENT    Similarity: 0.74 [████████████░░░░]      │
│ [unknown] ↔ [q-bio]                                       │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ [ComparisonView component]                                │
│                                                            │
│ STRUCTURAL EXPLANATION                                     │
│ Both describe cell size feedback control through          │
│ phase-specific mechanisms (sizer/timer/adder)...          │
│                                                            │
│ ┌──────────────────────┬──────────────────────┐          │
│ │ Paper 1: [unknown]   │ Paper 2: [q-bio]    │          │
│ │ ...                  │ ...                 │          │
│ └──────────────────────┴──────────────────────┘          │
│                                                            │
│ [← Previous Discovery]    [Next Discovery →]              │
└────────────────────────────────────────────────────────────┘
```

### Methodology Page (`/methodology`)

**Sections**:
1. **Overview**: What is a structural isomorphism?
2. **Process**: 3-step pipeline (extract → match → curate)
3. **Quality Standards**: Rating system (excellent/good/weak/false)
4. **Limitations**: What we can and can't capture
5. **Future Work**: Planned improvements

**Design**: Long-form text with diagrams/visuals

### About Page (`/about`)

**Sections**:
1. **Story**: Why this project exists (short, personal)
2. **Technology**: Built with Claude Code, Next.js, embeddings
3. **Team**: Solo project by [name]
4. **Contact**: Email or feedback form
5. **Roadmap**: Future plans (200+ discoveries, more domains)

---

## Technology Stack

### Core Framework
- **Next.js 14+** (App Router, not Pages Router)
- **React 18+**
- **TypeScript** (strict mode)

### Styling
- **Tailwind CSS 3+**
- **Headless UI** (for dropdowns, modals if needed)
- No CSS-in-JS, no styled-components

### Deployment
- **Static Export** (`next export`)
- **Vercel** (free tier, automatic deployments)
- Custom domain: `analog.quest`

### Data
- **Static JSON** (no database for 30 items)
- **No API calls** (all data at build time)
- **ISR not needed** (updates are manual, infrequent)

### Optional Libraries
- **Fuse.js** - Client-side fuzzy search (lightweight)
- **react-hot-toast** - Toast notifications (if needed)
- **framer-motion** - Animations (if time permits)

---

## File Structure

```
analog-quest-frontend/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Home page
│   ├── discoveries/
│   │   ├── page.tsx              # Browse page
│   │   └── [id]/
│   │       └── page.tsx          # Individual discovery
│   ├── methodology/
│   │   └── page.tsx
│   ├── about/
│   │   └── page.tsx
│   └── globals.css               # Global styles + Tailwind
├── components/
│   ├── DiscoveryCard.tsx
│   ├── DomainBadge.tsx
│   ├── SimilarityScore.tsx
│   ├── FilterBar.tsx
│   ├── ComparisonView.tsx
│   ├── Navigation.tsx
│   └── Footer.tsx
├── lib/
│   ├── data.ts                   # Load and parse discoveries.json
│   ├── filters.ts                # Filter/sort logic
│   └── utils.ts                  # Utility functions
├── public/
│   ├── data/
│   │   └── discoveries.json      # Frontend-optimized data
│   └── images/
│       └── og-image.png          # Open Graph image
├── scripts/
│   └── transform-data.ts         # Transform SESSION38 JSON → frontend JSON
├── tailwind.config.js
├── next.config.js                # Static export config
├── tsconfig.json
└── package.json
```

---

## Build Timeline

### Session 40: Core Build (4-5 hours)

**Hour 1: Setup & Data**
- [ ] Create Next.js 14 app with TypeScript + Tailwind
- [ ] Create transformation script
- [ ] Transform SESSION38_VERIFIED_ISOMORPHISMS.json → discoveries.json
- [ ] Create data loading utilities

**Hour 2: Core Components**
- [ ] Build DiscoveryCard component
- [ ] Build DomainBadge component
- [ ] Build SimilarityScore component
- [ ] Build Navigation and Footer

**Hour 3: Home + Discoveries Pages**
- [ ] Build home page (hero, stats, featured)
- [ ] Build discoveries browse page (grid + basic filtering)

**Hour 4: Individual Discovery Page**
- [ ] Build discovery detail page
- [ ] Build ComparisonView component
- [ ] Add navigation (previous/next)

**Hour 5: Polish Core**
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Accessibility (ARIA labels, keyboard nav)
- [ ] Performance (image optimization, lazy loading)

### Session 41: Polish & Deploy (3-4 hours)

**Hour 1: Advanced Features**
- [ ] Build FilterBar component (domain, rating, similarity)
- [ ] Add client-side search (Fuse.js)
- [ ] Add sorting (similarity, rating, domain)

**Hour 2: Content Pages**
- [ ] Build methodology page (with visuals)
- [ ] Build about page (story, contact)

**Hour 3: Final Polish**
- [ ] SEO (meta tags, Open Graph, sitemap)
- [ ] Loading states and error handling
- [ ] Cross-browser testing
- [ ] Final design tweaks

**Hour 4: Deploy**
- [ ] Configure static export
- [ ] Deploy to Vercel
- [ ] Configure custom domain (analog.quest)
- [ ] Test production build
- [ ] Share publicly!

---

## Design System

### Colors

**Primary Palette**:
```css
--primary: #2563eb      /* Blue */
--secondary: #7c3aed    /* Purple */
--accent: #f59e0b       /* Amber */
--success: #10b981      /* Green */
--warning: #f59e0b      /* Orange */
--danger: #ef4444       /* Red */
```

**Domain Colors** (see DomainBadge component)

**Neutrals**:
```css
--gray-50: #f9fafb
--gray-100: #f3f4f6
--gray-200: #e5e7eb
--gray-300: #d1d5db
--gray-500: #6b7280
--gray-700: #374151
--gray-900: #111827
```

### Typography

**Font Stack**:
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

**Sizes**:
- Heading 1: `text-4xl font-bold` (36px)
- Heading 2: `text-3xl font-bold` (30px)
- Heading 3: `text-2xl font-semibold` (24px)
- Body: `text-base` (16px)
- Small: `text-sm` (14px)
- Tiny: `text-xs` (12px)

### Spacing

**Scale**: `0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32`
- Use Tailwind defaults: `p-4`, `mt-8`, etc.

### Breakpoints

```css
sm: 640px   /* Mobile landscape, small tablet */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

---

## SEO Strategy

### Meta Tags (All Pages)

```tsx
export const metadata: Metadata = {
  title: 'analog.quest - Structural Isomorphisms Across Science',
  description: '30 verified cross-domain isomorphisms: the same mechanism in different fields. Explore hidden connections across economics, biology, physics, and more.',
  keywords: 'isomorphism, cross-domain, analogies, science, patterns, mechanisms',
  openGraph: {
    title: 'analog.quest - Structural Isomorphisms Across Science',
    description: '30 verified cross-domain isomorphisms discovered through semantic matching',
    images: ['/images/og-image.png'],
    url: 'https://analog.quest',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'analog.quest - Structural Isomorphisms Across Science',
    description: '30 verified cross-domain isomorphisms',
    images: ['/images/og-image.png'],
  },
}
```

### Sitemap

Generate static sitemap.xml:
- `/`
- `/discoveries`
- `/discoveries/[1-30]`
- `/methodology`
- `/about`

### Performance Targets

- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3.5s
- **Lighthouse Score**: ≥90 (all categories)

---

## Launch Checklist

### Pre-Launch
- [ ] All 30 discoveries render correctly
- [ ] Filters work (domain, rating, similarity)
- [ ] Mobile responsive (test on real device)
- [ ] No console errors
- [ ] Links to arXiv work (if arXiv IDs present)
- [ ] Methodology page explains process clearly
- [ ] About page has contact info

### Launch
- [ ] Deploy to Vercel
- [ ] Configure custom domain
- [ ] Test production build
- [ ] Submit to Google Search Console
- [ ] Share on Twitter, HN, Reddit

### Post-Launch
- [ ] Monitor analytics (Vercel Analytics)
- [ ] Gather user feedback
- [ ] Track which discoveries are most viewed
- [ ] Plan Session 42 (first expansion cycle)

---

## Future Enhancements (Post-MVP)

**Phase 2 (Sessions 45+)**:
- [ ] User accounts (save favorites)
- [ ] Comments/discussion per discovery
- [ ] User-submitted isomorphisms
- [ ] Visualization of domain network
- [ ] API for programmatic access

**Phase 3 (Months 3-6)**:
- [ ] Search by paper title/author
- [ ] Filter by mechanism type
- [ ] "Related discoveries" suggestions
- [ ] Email newsletter for new discoveries
- [ ] Embeddable widgets for researchers

---

## Success Criteria

**Launch (Session 41)**:
- [ ] Site is live at analog.quest
- [ ] All 30 discoveries are accessible
- [ ] Mobile-friendly and fast (<3s load)
- [ ] 0 critical accessibility issues

**Week 1**:
- [ ] 100+ unique visitors
- [ ] 0 critical bugs reported
- [ ] At least 1 piece of positive feedback

**Month 1**:
- [ ] 1,000+ unique visitors
- [ ] 50+ discoveries added (Session 42-44)
- [ ] Featured on HN or similar

---

## Open Questions

1. **Domain naming**: Use "unknown" or rename to original domain from Session 34?
2. **arXiv links**: Many papers have "N/A" - should we hide link button?
3. **Explanation length**: Truncate at 200 chars or show full text in card?
4. **Rating display**: Show "excellent" badge prominently or subtle indicator?
5. **Analytics**: Use Vercel Analytics (free) or Google Analytics?

**Recommendation**: Start simple, iterate based on user feedback

---

## Document Maintenance

**Review frequency**: After major feature additions
**Update triggers**:
- New page added
- Component API changes
- Design system updates

**Last updated**: 2026-02-10 (Session 39)
**Next review**: After Session 41 (v1 launch)


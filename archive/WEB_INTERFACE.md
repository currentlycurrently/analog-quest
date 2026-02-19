# Analog Quest Web Interface

A Next.js web application for exploring cross-domain isomorphisms in academic papers.

## Features

- **Dashboard**: Overview of stats, domains, and pattern types
- **Papers Browser**: Browse all 150 papers with domain filtering
- **Patterns Explorer**: Filter 261 patterns by domain and mechanism type
- **Isomorphisms Viewer**: Explore cross-domain matches with similarity scoring
- **Paper Details**: View full paper info with extracted patterns

## Running Locally

```bash
# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: SQLite via better-sqlite3
- **Features**: Server-side rendering, API routes, pagination, filtering

## Project Structure

```
app/
├── api/              # API routes for database queries
│   ├── stats/        # Overall statistics
│   ├── papers/       # Papers listing and details
│   ├── patterns/     # Patterns listing
│   └── isomorphisms/ # Cross-domain matches
├── papers/           # Papers browser pages
├── patterns/         # Patterns explorer page
├── isomorphisms/     # Isomorphisms viewer page
├── layout.tsx        # Root layout with navigation
├── page.tsx          # Dashboard homepage
└── globals.css       # Global styles

lib/
└── db.ts            # Database connection and types
```

## API Endpoints

### GET /api/stats
Returns overall statistics:
- Total papers, patterns, isomorphisms
- Hit rate, domains, pattern types

### GET /api/papers
Query parameters:
- `domain`: Filter by domain (optional)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

### GET /api/papers/[id]
Returns paper details with extracted patterns

### GET /api/patterns
Query parameters:
- `domain`: Filter by domain (optional)
- `mechanism_type`: Filter by pattern type (optional)
- `paper_id`: Get patterns for specific paper (optional)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)

### GET /api/isomorphisms
Query parameters:
- `min_score`: Minimum similarity score (default: 0.5)
- `max_score`: Maximum similarity score (default: 1.0)
- `domain1`: Filter first domain (optional)
- `domain2`: Filter second domain (optional)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)

## Database

The web interface connects to `database/papers.db` in read-only mode. All queries are safe and performant.

## Building for Production

```bash
npm run build
npm run start
```

## Deployment

The app can be deployed to Vercel, Netlify, or any platform that supports Next.js:

```bash
# Vercel deployment (recommended)
vercel deploy
```

Make sure to include the `database/papers.db` file in your deployment.

## Future Enhancements

- [ ] Search functionality (full-text search)
- [ ] Graph visualization of domain connections
- [ ] Export data (CSV/JSON)
- [ ] Real-time updates when new papers are processed
- [ ] User authentication for data curation
- [ ] Advanced filtering and sorting options
- [ ] Save favorite isomorphisms

## Session 6 Notes

Built in Session 6 (2026-02-07):
- Complete Next.js setup with TypeScript
- 4 main pages with filtering and pagination
- Clean, responsive UI with dark mode
- All 150 papers, 261 patterns browsable
- Currently showing 100 of 1030 isomorphisms (to be expanded)

---

**Last Updated**: Session 6 - 2026-02-07

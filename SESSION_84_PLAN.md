# Session 84 Plan: Frontend → API Migration

## Goal
Migrate frontend from static JSON to API calls so the system works properly on any platform (Railway, Vercel, etc.)

## Current Problem
- Frontend reads from `app/data/discoveries.json` (static, has duplicates)
- API reads from PostgreSQL (dynamic, clean data)
- They're completely disconnected!

## Migration Strategy

### Phase 1: Create API Client Functions
Replace static imports with API calls:

```typescript
// lib/api-client.ts (NEW)
export async function fetchDiscoveries() {
  const res = await fetch('/api/discoveries?limit=200');
  const data = await res.json();
  return data.data;
}

export async function fetchDiscoveryById(id: number) {
  const res = await fetch(`/api/discoveries/${id}`);
  const data = await res.json();
  return data.data;
}
```

### Phase 2: Update Data Fetching

#### For Static Pages (SSG)
Convert to use `fetch()` in server components:

```typescript
// app/discoveries/page.tsx
async function DiscoveriesPage() {
  const discoveries = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/discoveries?limit=200`)
    .then(res => res.json())
    .then(data => data.data);

  // Rest of component
}
```

#### For Dynamic Pages
Use Next.js data fetching:

```typescript
// app/discoveries/[id]/page.tsx
export async function generateStaticParams() {
  const discoveries = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/discoveries`)
    .then(res => res.json());

  return discoveries.data.map((d) => ({
    id: d.id.toString(),
  }));
}
```

### Phase 3: Handle Client Components
For components that need client-side state, use SWR or React Query:

```typescript
// components/DiscoveryList.tsx
'use client';
import useSWR from 'swr';

export default function DiscoveryList() {
  const { data, error } = useSWR('/api/discoveries', fetcher);

  if (error) return <div>Failed to load</div>;
  if (!data) return <div>Loading...</div>;

  return <div>{/* render discoveries */}</div>;
}
```

### Phase 4: Environment Configuration

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:3000  # Development

# .env.production
NEXT_PUBLIC_API_URL=https://analog.quest   # Production
```

For Railway deployment:
```bash
# Railway will need:
DATABASE_URL=postgresql://...  # From Railway PostgreSQL
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

### Phase 5: Remove Static JSON Dependencies
1. Delete imports of `discoveries.json`
2. Update `lib/data.ts` to use API
3. Keep JSON files as backup only

## Files to Modify

### Priority 1 (Core Changes)
- [ ] `lib/data.ts` - Convert to API calls
- [ ] `app/discoveries/page.tsx` - Use API data
- [ ] `app/discoveries/[id]/page.tsx` - Fetch from API
- [ ] `app/page.tsx` - Update homepage

### Priority 2 (Supporting)
- [ ] Create `lib/api-client.ts` - Centralized API functions
- [ ] Update `.env.local` and `.env.production`
- [ ] Add error handling for API failures
- [ ] Add loading states

### Priority 3 (Cleanup)
- [ ] Remove static JSON imports
- [ ] Update any remaining components
- [ ] Test all pages thoroughly

## Benefits of This Approach

1. **Platform Agnostic**: Works on Railway, Vercel, anywhere
2. **Single Source of Truth**: Database is authoritative
3. **Real-time Updates**: Changes reflect immediately
4. **Scalable**: No need to rebuild for data changes
5. **Proper Architecture**: Frontend and backend properly separated

## Testing Plan

1. **Local Testing**:
   ```bash
   npm run dev
   # Test all pages load
   # Test discovery details work
   # Test sorting/filtering
   ```

2. **Production Testing**:
   ```bash
   npm run build
   npm start
   # Verify production build works
   ```

3. **API Testing**:
   ```bash
   # Test API endpoints directly
   curl http://localhost:3000/api/discoveries
   curl http://localhost:3000/api/discoveries/1
   ```

## Rollback Plan
If issues arise:
1. Git revert the changes
2. Static JSON files remain as backup
3. Can quickly restore old version

## Success Criteria
- [ ] All pages load data from API
- [ ] No more static JSON imports
- [ ] Works locally and in production
- [ ] No duplicate discoveries shown
- [ ] Can deploy to Railway successfully

## Notes for Implementation
- Use server components where possible (better SEO)
- Add proper error boundaries
- Consider caching strategy (ISR vs on-demand)
- Keep API response format consistent
- Test with slow network to ensure good UX

---

This migration will make the system production-ready for any platform!
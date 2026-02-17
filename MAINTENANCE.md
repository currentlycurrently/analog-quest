# Maintenance Guide - Analog Quest

## Quick Start (Daily)

### Start a Session
```bash
cd /Users/user/Dev/nextjs/analog-quest
claude --continue
```

### Check Production Health
```bash
# API Health
curl https://analog.quest/api/health | jq

# View recent discoveries
curl https://analog.quest/api/discoveries?limit=5 | jq '.data[].id'
```

## Infrastructure Overview

### Production Stack
- **Frontend**: Next.js 15 on Vercel (analog.quest)
- **Database**: PostgreSQL on Neon (2,397 papers, 305 mechanisms, 133 discoveries)
- **API**: Next.js API routes with database connection pooling
- **Repository**: github.com/currentlycurrently/analog-quest

### Key Files
- `app/data/discoveries.json` - Static discovery data with URLs
- `app/data/discovered_pairs.json` - Tracking for unique discoveries
- `lib/db.ts` - Database connection and queries
- `ROADMAP.md` - Development priorities and timeline

## Daily Operations

### Pre-Session Checklist
- [ ] Check API health: `curl https://analog.quest/api/health | jq`
- [ ] Review recent commits: `git log --oneline -5`
- [ ] Pull latest changes: `git pull`
- [ ] Check Vercel dashboard for deployment status

### During Session
- [ ] Mine candidates from `examples/session74_candidates.json`
- [ ] Update `discovered_pairs.json` with new discoveries
- [ ] Test locally before pushing: `npm run build`
- [ ] Document in PROGRESS.md
- [ ] Update METRICS.md

### End of Session
- [ ] Commit with clear message
- [ ] Push to GitHub
- [ ] Monitor Vercel deployment
- [ ] Check production site

## Weekly Tasks

### Data Quality Audit
```bash
# Check for duplicates in discovered_pairs
cat app/data/discovered_pairs.json | jq '.discovered_pairs | group_by(.paper_1_id, .paper_2_id) | map(select(length > 1))'

# Verify discovery count matches
curl https://analog.quest/api/health | jq '.checks.database.tables'
```

### Database Backup
```bash
# Run backup script
./scripts/backup_critical_data.sh

# Verify backup
ls -lah backups/
```

### Clean Technical Debt
```bash
# Remove old backup files
rm -f app/data/*.bak

# Archive old session scripts
mv scripts/session[0-7]*.py archive/scripts/
```

## Common Tasks

### Add New Discoveries
1. Review candidates from `examples/session74_candidates.json`
2. Apply quality criteria from `DATA_QUALITY_STANDARDS.md`
3. Add to `discovered_pairs.json`
4. Update static data: `npm run update-static-data`
5. Commit and push

### Fix Duplicate Discoveries
```sql
-- Connect to database
psql $DATABASE_URL

-- Find duplicates
SELECT paper_1_id, paper_2_id, COUNT(*)
FROM discovered_pairs
GROUP BY paper_1_id, paper_2_id
HAVING COUNT(*) > 1;

-- Remove duplicates (keep first)
DELETE FROM discovered_pairs a
USING discovered_pairs b
WHERE a.ctid > b.ctid
  AND a.paper_1_id = b.paper_1_id
  AND a.paper_2_id = b.paper_2_id;
```

### Update Paper URLs
```javascript
// Update static JSON with URLs from database
node scripts/update_discoveries_with_urls.js

// Commit and push
git add app/data/discoveries.json
git commit -m "Update paper URLs in static data"
git push
```

## Troubleshooting

### "Build Failing on Vercel"
```bash
# Test locally
npm run build

# Check TypeScript errors
npx tsc --noEmit

# Check environment variables
vercel env pull
```

### "Database Connection Issues"
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check Neon status
curl https://status.neon.tech

# Verify connection string
echo $DATABASE_URL | grep -o "sslmode=require"
```

### "Paper URLs Not Showing"
1. Check database has URLs: `psql $DATABASE_URL -c "SELECT COUNT(*) FROM papers WHERE url IS NOT NULL"`
2. Update static JSON: `node scripts/update_discoveries_with_urls.js`
3. Push and redeploy

### "Duplicate Discoveries"
1. Query database for duplicates
2. Update `discovered_pairs.json`
3. Clean discoveries table
4. Rebuild and deploy

## Quality Standards

### Discovery Ratings
- **Excellent**: Clear isomorphism, non-obvious, valuable
- **Good**: Valid similarity, useful connection
- **Weak**: Surface-level or obvious - REJECT

### Required for Each Discovery
- [ ] Both paper URLs present
- [ ] Clear structural explanation
- [ ] Proper domain classification
- [ ] Quality rating assigned
- [ ] No duplicate pairs

## Monitoring

### Health Endpoints
```bash
# Overall health
curl https://analog.quest/api/health | jq

# Discovery stats
curl https://analog.quest/api/discoveries?limit=1 | jq '.metadata.stats'

# Pairs count
curl https://analog.quest/api/pairs?limit=1 | jq '.metadata.total'
```

### Database Stats
```bash
psql $DATABASE_URL << EOF
  SELECT 'Papers' as type, COUNT(*) FROM papers
  UNION ALL
  SELECT 'Mechanisms', COUNT(*) FROM mechanisms
  UNION ALL
  SELECT 'Discoveries', COUNT(*) FROM discoveries
  UNION ALL
  SELECT 'Pairs', COUNT(*) FROM discovered_pairs;
EOF
```

## Development Workflow

### Local Development
```bash
# Start dev server
npm run dev

# Test API locally
curl http://localhost:3000/api/health

# Test with production database
DATABASE_URL="postgresql://..." npm run dev
```

### Deployment Process
```bash
# 1. Test locally
npm run build

# 2. Commit changes
git add .
git commit -m "Description of changes"

# 3. Push to trigger deployment
git push

# 4. Monitor deployment
# Check Vercel dashboard or wait ~2 minutes

# 5. Verify production
curl https://analog.quest/api/health
```

## Emergency Procedures

### Rollback Deployment
```bash
# Revert last commit
git revert HEAD
git push

# Or reset to specific commit
git reset --hard <commit-hash>
git push --force
```

### Database Recovery
```bash
# From local backup
psql $DATABASE_URL < backups/analog_quest_backup_YYYYMMDD.sql

# From Neon dashboard
# Go to Neon console > Backups > Restore
```

### Clear Cache
```bash
# Force rebuild on Vercel
vercel --force

# Clear ISR cache (visit pages)
for i in {1..10}; do
  curl https://analog.quest/discoveries/$i > /dev/null
done
```

## Cost Management

### Monitor Usage
- Check Vercel dashboard for bandwidth/invocations
- Review Neon dashboard for database usage
- Track Claude usage in sessions

### Optimization Tips
- Use ISR instead of SSR for discovery pages
- Batch database operations
- Archive old session data
- Clean up unused files

## Maintenance Schedule

### Daily
- [ ] Start Claude session
- [ ] Check production health
- [ ] Review and commit changes

### Weekly
- [ ] Database backup
- [ ] Quality audit
- [ ] Clean technical debt
- [ ] Update documentation

### Monthly
- [ ] Review roadmap progress
- [ ] Optimize database queries
- [ ] Security updates
- [ ] Archive old data

## Contact & Support

### Services
- **Vercel Status**: status.vercel.com
- **Neon Status**: status.neon.tech
- **GitHub Status**: githubstatus.com

### Documentation
- **Next.js**: nextjs.org/docs
- **Neon**: neon.tech/docs
- **Vercel**: vercel.com/docs

---

**Last Updated**: February 17, 2026
**Next Review**: February 24, 2026
**Maintained By**: Chuck & Claude Agent
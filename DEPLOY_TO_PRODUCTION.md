# 🚀 Deploy to Production - Quick Guide

## You're 30 minutes from production!

### Step 1: Choose Your Database (5 min)

#### Option A: Neon (RECOMMENDED - Easiest)
1. Go to https://neon.tech
2. Sign up (free tier is fine)
3. Create database "analog-quest"
4. Copy the connection string

#### Option B: Supabase
1. Go to https://supabase.com
2. Create new project
3. Go to Settings → Database
4. Copy the connection string

### Step 2: Export Your Data (5 min)

```bash
# Export your local PostgreSQL data
pg_dump -U user analog_quest > backup.sql

# Or use the full path if pg_dump not in PATH:
/opt/homebrew/opt/postgresql@17/bin/pg_dump -U user analog_quest > backup.sql
```

### Step 3: Import to Production Database (10 min)

```bash
# For Neon or Supabase
psql "[YOUR_CONNECTION_STRING]" < backup.sql

# If psql not in PATH:
/opt/homebrew/opt/postgresql@17/bin/psql "[YOUR_CONNECTION_STRING]" < backup.sql
```

### Step 4: Update Vercel Environment (5 min)

1. Go to https://vercel.com/dashboard
2. Select your `analog-quest` project
3. Go to Settings → Environment Variables
4. Add these variables:

```
DATABASE_URL = [your_production_connection_string]
USE_DATABASE = true
ENABLE_WRITE_OPS = false
API_VERSION = 2.0.0
```

### Step 5: Deploy (5 min)

```bash
# Commit your changes
git add -A
git commit -m "Production database configuration"
git push origin main
```

Vercel will auto-deploy from your git push!

### Step 6: Verify

```bash
# Test production API
curl https://analog.quest/api/health

# Should see:
# status: "healthy"
# database.status: "connected"
```

---

## ✅ That's it! You're live!

Your discoveries are now served from a real database, not JSON files.

## 🔧 Troubleshooting

### "Connection refused" error
- Make sure to use the connection string from your cloud provider, not localhost
- Check that SSL is enabled (most cloud providers require it)

### "Relation does not exist" error
- The import might have failed. Try importing again
- Make sure you created the database first

### API returns empty data
- Check environment variables in Vercel dashboard
- Verify DATABASE_URL is set correctly
- Check Vercel function logs for errors

### Slow API responses
- Normal on first request (cold start)
- Consider upgrading to paid database tier if consistent

---

## 📊 What You Now Have

- ✅ Real database in the cloud
- ✅ API serving from database
- ✅ 125 discoveries available via API
- ✅ Vector similarity search working
- ✅ Proper architecture for scaling

## 🎯 Next Steps (Optional)

1. **Enable pgvector in production** (for similarity search):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Set up automated backups** (check your provider's docs)

3. **Monitor usage** (both Vercel and database provider have dashboards)

4. **When ready for Session 82**:
   - Continue mining discoveries
   - They'll automatically appear on the site
   - No more JSON file editing!

---

**Questions?** The system is working locally, so any production issues are just configuration. Check:
1. Connection string is correct
2. Environment variables are set in Vercel
3. Database has the data (connect with psql to verify)

---

**Total time**: 30 minutes
**Cost**: Free tier should be sufficient
**Result**: Production-ready discovery platform!
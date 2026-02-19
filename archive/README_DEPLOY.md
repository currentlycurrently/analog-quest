# Analog Quest - Deployment Guide

## Production Deployment

### Prerequisites

- Node.js 18+
- PostgreSQL database (local or cloud)
- Environment variables configured

### Environment Setup

Create `.env.local` (development) or set in deployment platform:

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Optional
NEXT_PUBLIC_API_URL=https://your-domain.com  # Defaults to relative URLs
ENABLE_WRITE_OPS=true                        # Enable POST/PUT operations
```

### Database Setup

1. Create PostgreSQL database
2. Run migration scripts:
```bash
psql $DATABASE_URL < scripts/schema.sql
psql $DATABASE_URL < scripts/seed_data.sql
```

## Deployment Options

### Railway (Recommended)

1. Connect GitHub repo
2. Add PostgreSQL service
3. Deploy:
```bash
railway up
```

Railway automatically:
- Builds the Next.js app
- Sets up PostgreSQL
- Configures environment variables
- Handles SSL/domains

### Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Add environment variables in Vercel dashboard
4. Use external PostgreSQL (Neon, Supabase, etc.)

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
docker build -t analog-quest .
docker run -p 3000:3000 --env-file .env analog-quest
```

### Manual Deployment

```bash
# Build
npm run build

# Start with PM2
pm2 start npm --name "analog-quest" -- start

# Or with systemd service
[Service]
ExecStart=/usr/bin/node /path/to/app/.next/standalone/server.js
Environment="DATABASE_URL=..."
```

## Production Checklist

- [ ] Database connection configured
- [ ] Environment variables set
- [ ] Build successful (`npm run build`)
- [ ] API endpoints responding
- [ ] Database has data (125 discoveries)
- [ ] Frontend loads without errors
- [ ] SSL certificate configured
- [ ] Domain DNS configured

## Monitoring

### Health Check
```bash
curl https://your-domain.com/api/health
```

### Database Status
```bash
curl https://your-domain.com/api/discoveries?limit=1
```

Should return metadata showing 125 discoveries.

## Troubleshooting

### Build Errors
- Ensure Node.js 18+
- Clear `.next` directory
- Check environment variables

### Database Connection
- Verify DATABASE_URL format
- Check SSL requirements
- Test connection with `psql`

### API Errors
- Check server logs
- Verify database permissions
- Ensure tables exist

## Performance

- Uses dynamic rendering (no static generation)
- API responses cached by CDN
- Database queries optimized with indexes
- Consider adding Redis for caching

## Security

- Database credentials in environment variables
- API routes validate input
- SQL injection prevented via parameterized queries
- CORS configured for production domain

---

For development setup, see main README.md
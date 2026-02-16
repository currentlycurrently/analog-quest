import { NextResponse } from 'next/server';
import discoveriesData from '@/app/data/discoveries.json';
import discoveredPairsData from '@/app/data/discovered_pairs.json';
import fs from 'fs';
import path from 'path';

// GET /api/health - Check API and data health
export async function GET() {
  try {
    const checks = {
      api: 'healthy',
      data_sources: {},
      database: {},
      issues: [],
      recommendations: []
    };

    // Check static JSON data
    checks.data_sources = {
      discoveries_json: {
        status: 'available',
        count: discoveriesData.length,
        last_id: Math.max(...discoveriesData.map(d => d.id))
      },
      discovered_pairs_json: {
        status: 'available',
        count: discoveredPairsData.discovered_pairs.length,
        metadata: discoveredPairsData.metadata
      }
    };

    // Check for data inconsistencies
    const discrepancy = discoveriesData.length - discoveredPairsData.discovered_pairs.length;
    if (discrepancy > 0) {
      checks.issues.push({
        type: 'data_inconsistency',
        message: `Frontend shows ${discoveriesData.length} discoveries but only ${discoveredPairsData.discovered_pairs.length} unique pairs tracked`,
        discrepancy,
        severity: 'warning'
      });
      checks.recommendations.push('Run deduplication script to sync discoveries with discovered_pairs');
    }

    // Check if database file exists (but don't try to connect)
    const dbPath = path.join(process.cwd(), 'database', 'papers.db');
    try {
      const stats = fs.statSync(dbPath);
      checks.database = {
        sqlite_file: 'exists',
        size_mb: (stats.size / (1024 * 1024)).toFixed(2),
        connection: 'not_configured',
        note: 'Database exists locally but not connected to API'
      };
      checks.issues.push({
        type: 'database_disconnected',
        message: 'SQLite database exists but API uses static JSON',
        severity: 'info'
      });
      checks.recommendations.push('Configure database connection for dynamic data');
    } catch (e) {
      checks.database = {
        sqlite_file: 'not_found',
        connection: 'not_configured'
      };
    }

    // Check environment variables (without exposing values)
    const envVars = {
      has_postgres_url: !!process.env.POSTGRES_URL,
      has_database_url: !!process.env.DATABASE_URL,
      node_env: process.env.NODE_ENV || 'development',
      vercel_env: process.env.VERCEL_ENV || 'local'
    };

    // Overall status
    const overallStatus = checks.issues.filter(i => i.severity === 'error').length > 0 ? 'degraded' : 'healthy';

    return NextResponse.json({
      status: overallStatus,
      timestamp: new Date().toISOString(),
      environment: envVars,
      checks,
      api_endpoints: {
        discoveries: {
          list: '/api/discoveries',
          detail: '/api/discoveries/[id]',
          capabilities: ['read', 'filter', 'sort', 'paginate']
        },
        pairs: {
          list: '/api/pairs',
          capabilities: ['read', 'filter', 'paginate']
        },
        health: {
          status: '/api/health',
          capabilities: ['monitor']
        }
      },
      next_steps: [
        '1. Set up database connection (Neon, Supabase, or Vercel Postgres)',
        '2. Create database schema and migrate data',
        '3. Update API routes to use database',
        '4. Implement write operations',
        '5. Add authentication for write endpoints'
      ]
    });

  } catch (error) {
    console.error('Error in health check:', error);
    return NextResponse.json(
      {
        status: 'error',
        error: 'Health check failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
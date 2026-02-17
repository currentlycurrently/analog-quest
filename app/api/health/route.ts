import { NextResponse } from 'next/server';
import { checkConnection, getStats } from '@/lib/db';
import fs from 'fs';
import path from 'path';

// GET /api/health - Check API and data health
export async function GET() {
  try {
    const checks: {
      api: string;
      database: any;
      data_sources: any;
      issues: any[];
      recommendations: string[];
    } = {
      api: 'healthy',
      database: {},
      data_sources: {},
      issues: [],
      recommendations: []
    };

    // Check PostgreSQL database connection
    let dbHealthy = false;
    let dbStats: Record<string, number> | null = null;

    try {
      dbHealthy = await checkConnection();
      if (dbHealthy) {
        dbStats = await getStats();
        checks.database = {
          status: 'connected',
          type: 'postgresql',
          database: 'analog_quest',
          tables: dbStats
        };
      } else {
        checks.database = {
          status: 'disconnected',
          type: 'postgresql',
          error: 'Connection check failed'
        };
        checks.issues.push({
          type: 'database_connection',
          message: 'PostgreSQL connection failed',
          severity: 'error'
        });
      }
    } catch (error) {
      checks.database = {
        status: 'error',
        type: 'postgresql',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      checks.issues.push({
        type: 'database_error',
        message: `Database error: ${error instanceof Error ? error.message : 'Unknown'}`,
        severity: 'error'
      });
      checks.recommendations.push('Check PostgreSQL connection settings in .env.local');
    }

    // Check if legacy SQLite database exists (for reference)
    const sqlitePath = path.join(process.cwd(), 'database', 'papers.db');
    try {
      const stats = fs.statSync(sqlitePath);
      checks.data_sources.sqlite_legacy = {
        status: 'available',
        size_mb: (stats.size / (1024 * 1024)).toFixed(2),
        note: 'Legacy database - not actively used'
      };
    } catch (e) {
      // SQLite doesn't exist, that's fine
    }

    // Check static JSON files (for editorial content)
    const jsonFiles = ['discoveries.json', 'discovered_pairs.json', 'discoveries_editorial.json'];
    for (const filename of jsonFiles) {
      const filePath = path.join(process.cwd(), 'app', 'data', filename);
      try {
        const exists = fs.existsSync(filePath);
        checks.data_sources[filename] = {
          status: exists ? 'available' : 'missing',
          note: exists ? 'Available for reference/editorial' : 'Not found'
        };
      } catch (e) {
        checks.data_sources[filename] = {
          status: 'error',
          error: e instanceof Error ? e.message : 'Unknown'
        };
      }
    }

    // Check environment variables (without exposing values)
    const envVars = {
      has_postgres_url: !!process.env.POSTGRES_URL,
      has_database_url: !!process.env.DATABASE_URL,
      use_database: process.env.USE_DATABASE === 'true',
      enable_write_ops: process.env.ENABLE_WRITE_OPS === 'true',
      node_env: process.env.NODE_ENV || 'development',
      vercel_env: process.env.VERCEL_ENV || 'local'
    };

    // Data integrity checks
    if (dbHealthy && dbStats) {
      const discoveryCount = dbStats.discoveries || 0;
      const pairCount = dbStats.discovered_pairs || 0;

      if (discoveryCount !== pairCount) {
        checks.issues.push({
          type: 'data_sync',
          message: `Discovery count (${discoveryCount}) differs from pair count (${pairCount})`,
          severity: 'info'
        });
      }
    }

    // Overall status
    const hasErrors = checks.issues.filter(i => i.severity === 'error').length > 0;
    const overallStatus = hasErrors ? 'degraded' : 'healthy';

    // Recommendations based on status
    if (!dbHealthy) {
      checks.recommendations.push('Fix PostgreSQL connection');
    }
    if (!envVars.enable_write_ops) {
      checks.recommendations.push('Enable write operations when ready (ENABLE_WRITE_OPS=true)');
    }

    return NextResponse.json({
      status: overallStatus,
      timestamp: new Date().toISOString(),
      version: '2.0.0',
      environment: envVars,
      checks,
      api_endpoints: {
        discoveries: {
          list: 'GET /api/discoveries',
          detail: 'GET /api/discoveries/[id]',
          statistics: 'OPTIONS /api/discoveries',
          capabilities: ['read', 'filter', 'sort', 'paginate']
        },
        pairs: {
          list: 'GET /api/pairs',
          capabilities: ['read', 'filter', 'paginate']
        },
        health: {
          status: 'GET /api/health',
          capabilities: ['monitor']
        }
      }
    });

  } catch (error) {
    console.error('Error in health check:', error);
    return NextResponse.json(
      {
        status: 'error',
        error: 'Health check failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
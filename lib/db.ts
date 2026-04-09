/**
 * Database connection module for Analog Quest
 *
 * Provides connection pooling and query utilities for PostgreSQL.
 * Uses the 'pg' package directly for local development and production.
 * Compatible with Vercel deployment via environment variables.
 */

import { Pool } from 'pg';

// Singleton pool instance for connection reuse
let pool: Pool | null = null;

/**
 * Get or create the connection pool
 */
function getPool(): Pool {
  if (!pool) {
    // Use POSTGRES_URL if available, otherwise fall back to individual params
    const connectionString =
      process.env.POSTGRES_URL ||
      process.env.POSTGRES_URL_NON_POOLING ||
      process.env.DATABASE_URL ||
      `postgresql://${process.env.POSTGRES_USER || 'user'}@${process.env.POSTGRES_HOST || 'localhost'}:${process.env.POSTGRES_PORT || 5432}/${process.env.POSTGRES_DATABASE || 'analog_quest'}`;

    pool = new Pool({
      connectionString,
      // SSL settings for production; disabled for local
      ssl: connectionString.includes('localhost') || connectionString.includes('127.0.0.1')
        ? false
        : { rejectUnauthorized: false },
      // Connection pool settings
      max: 10,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000,
    });

    // Handle pool errors
    pool.on('error', (err) => {
      console.error('Unexpected error on idle PostgreSQL client', err);
    });
  }

  return pool;
}

/**
 * Execute a SQL query with connection pooling
 *
 * Example:
 * ```ts
 * const result = await query('SELECT * FROM papers WHERE id = $1', [1]);
 * ```
 */
export async function query<T = any>(
  text: string,
  params?: any[]
): Promise<{ rows: T[]; rowCount: number }> {
  const pool = getPool();
  try {
    const result = await pool.query(text, params);
    return {
      rows: result.rows as T[],
      rowCount: result.rowCount || 0,
    };
  } catch (error) {
    console.error('Database query error:', error);
    throw error;
  }
}

/**
 * Get a single row from a query
 *
 * Example:
 * ```ts
 * const paper = await queryOne('SELECT * FROM papers WHERE id = $1', [1]);
 * ```
 */
export async function queryOne<T = any>(
  text: string,
  params?: any[]
): Promise<T | null> {
  const result = await query<T>(text, params);
  return result.rows[0] || null;
}

/**
 * Check database connection health
 */
export async function checkConnection(): Promise<boolean> {
  try {
    const result = await query('SELECT 1 as ok');
    return result.rows[0]?.ok === 1;
  } catch (error) {
    console.error('Database connection check failed:', error);
    return false;
  }
}

/**
 * Get database statistics
 */
export async function getStats() {
  try {
    const tables = ['papers', 'queue', 'extractions', 'isomorphisms', 'contributors'];
    const counts: Record<string, number> = {};

    for (const table of tables) {
      const result = await query(`SELECT COUNT(*) as count FROM ${table}`);
      counts[table] = parseInt(result.rows[0]?.count || '0');
    }

    return counts;
  } catch (error) {
    console.error('Error getting database stats:', error);
    return null;
  }
}

export interface Paper {
  id: number;
  arxiv_id?: string;
  openalex_id?: string;
  title: string;
  abstract?: string;
  domain?: string;
  published?: string;
  url?: string;
}

export interface Isomorphism {
  id: number;
  paper_1_id: number;
  paper_2_id: number;
  equation_class: string;
  latex_paper_1?: string[];
  latex_paper_2?: string[];
  explanation?: string;
  confidence: number;
  validation_count: number;
  status: 'candidate' | 'verified' | 'rejected';
  discovered_at: string;
}

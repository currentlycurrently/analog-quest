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
    const tables = ['papers', 'mechanisms', 'discovered_pairs', 'discoveries'];
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

/**
 * Type definitions for database rows
 */
export interface Paper {
  id: number;
  title: string;
  abstract: string;
  domain: string;
  arxiv_id?: string;
  published_date?: string;
  authors?: string;
  url?: string;
}

export interface Mechanism {
  id: number;
  paper_id: number;
  description: string;
  structural_description?: string;
  domain?: string;
  mechanism_type?: string;
  extracted_at?: string;
}

export interface Discovery {
  id: number;
  mechanism_1_id: number;
  mechanism_2_id: number;
  similarity: number;
  rating: 'excellent' | 'good' | 'weak';
  explanation?: string;
  session?: number;
}

export interface DiscoveredPair {
  paper_1_id: number;
  paper_2_id: number;
  discovered_in_session: number;
  // These fields come from JOIN with discoveries if available
  similarity?: number;
  rating?: 'excellent' | 'good' | 'weak';
}

/**
 * Extended discovery with paper and mechanism details
 */
export interface DiscoveryWithDetails extends Discovery {
  paper_1_id?: number;
  paper_1_title?: string;
  paper_1_domain?: string;
  paper_1_arxiv_id?: string;
  mechanism_1_description?: string;

  paper_2_id?: number;
  paper_2_title?: string;
  paper_2_domain?: string;
  paper_2_arxiv_id?: string;
  mechanism_2_description?: string;

  domains?: string[];
}

/**
 * Common queries
 */
export const queries = {
  /**
   * Get all discoveries with full details (papers + mechanisms)
   */
  getAllDiscoveriesWithDetails: async (filters?: {
    rating?: string;
    domain?: string;
    minSimilarity?: number;
    limit?: number;
    offset?: number;
    sortBy?: string;
    order?: 'asc' | 'desc';
  }): Promise<DiscoveryWithDetails[]> => {
    let queryText = `
      SELECT
        d.id,
        d.mechanism_1_id,
        d.mechanism_2_id,
        d.similarity,
        d.rating,
        d.explanation,
        d.session,

        -- Paper 1 details
        p1.id as paper_1_id,
        p1.title as paper_1_title,
        p1.domain as paper_1_domain,
        p1.arxiv_id as paper_1_arxiv_id,

        -- Mechanism 1 details
        m1.description as mechanism_1_description,

        -- Paper 2 details
        p2.id as paper_2_id,
        p2.title as paper_2_title,
        p2.domain as paper_2_domain,
        p2.arxiv_id as paper_2_arxiv_id,

        -- Mechanism 2 details
        m2.description as mechanism_2_description

      FROM discoveries d
      JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
      JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
      JOIN papers p1 ON m1.paper_id = p1.id
      JOIN papers p2 ON m2.paper_id = p2.id
      WHERE 1=1
    `;

    const params: any[] = [];
    let paramIndex = 1;

    // Apply filters
    if (filters?.rating) {
      queryText += ` AND d.rating = $${paramIndex}`;
      params.push(filters.rating);
      paramIndex++;
    }

    if (filters?.domain) {
      queryText += ` AND (p1.domain = $${paramIndex} OR p2.domain = $${paramIndex})`;
      params.push(filters.domain);
      paramIndex++;
    }

    if (filters?.minSimilarity) {
      queryText += ` AND d.similarity >= $${paramIndex}`;
      params.push(filters.minSimilarity);
      paramIndex++;
    }

    // Apply sorting
    const sortBy = filters?.sortBy || 'similarity';
    const order = filters?.order || 'desc';

    if (sortBy === 'similarity') {
      queryText += ` ORDER BY d.similarity ${order.toUpperCase()}`;
    } else if (sortBy === 'rating') {
      queryText += ` ORDER BY d.rating ${order.toUpperCase()}, d.similarity DESC`;
    } else if (sortBy === 'session') {
      queryText += ` ORDER BY d.session ${order.toUpperCase()}`;
    } else {
      queryText += ` ORDER BY d.id ${order.toUpperCase()}`;
    }

    // Apply pagination
    if (filters?.limit) {
      queryText += ` LIMIT $${paramIndex}`;
      params.push(filters.limit);
      paramIndex++;
    }

    if (filters?.offset) {
      queryText += ` OFFSET $${paramIndex}`;
      params.push(filters.offset);
      paramIndex++;
    }

    const result = await query<DiscoveryWithDetails>(queryText, params);

    // Add domains array to each discovery
    return result.rows.map(row => ({
      ...row,
      domains: [row.paper_1_domain, row.paper_2_domain].filter(Boolean) as string[]
    }));
  },

  /**
   * Get a single discovery by ID with full details
   */
  getDiscoveryById: async (id: number): Promise<DiscoveryWithDetails | null> => {
    const queryText = `
      SELECT
        d.id,
        d.mechanism_1_id,
        d.mechanism_2_id,
        d.similarity,
        d.rating,
        d.explanation,
        d.session,

        -- Paper 1 details
        p1.id as paper_1_id,
        p1.title as paper_1_title,
        p1.abstract as paper_1_abstract,
        p1.domain as paper_1_domain,
        p1.arxiv_id as paper_1_arxiv_id,

        -- Mechanism 1 details
        m1.description as mechanism_1_description,

        -- Paper 2 details
        p2.id as paper_2_id,
        p2.title as paper_2_title,
        p2.abstract as paper_2_abstract,
        p2.domain as paper_2_domain,
        p2.arxiv_id as paper_2_arxiv_id,

        -- Mechanism 2 details
        m2.description as mechanism_2_description

      FROM discoveries d
      JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
      JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
      JOIN papers p1 ON m1.paper_id = p1.id
      JOIN papers p2 ON m2.paper_id = p2.id
      WHERE d.id = $1
    `;

    const result = await queryOne<DiscoveryWithDetails>(queryText, [id]);

    if (result) {
      result.domains = [result.paper_1_domain, result.paper_2_domain].filter(Boolean) as string[];
    }

    return result;
  },

  /**
   * Get all discovered pairs with optional join to discoveries for extra metadata
   *
   * Note: The discovered_pairs table only has paper_1_id, paper_2_id,
   * discovered_in_session. We LEFT JOIN discoveries through mechanisms to
   * enrich with similarity and rating where a matching discovery record exists.
   */
  getAllDiscoveredPairs: async (filters?: {
    session?: number;
    rating?: string;
    minSimilarity?: number;
    limit?: number;
    offset?: number;
  }): Promise<DiscoveredPair[]> => {
    // Build a query that gets discovered_pairs and tries to join with discoveries
    // through the mechanisms table (which links to papers)
    let queryText = `
      SELECT DISTINCT
        dp.paper_1_id,
        dp.paper_2_id,
        dp.discovered_in_session,
        d.similarity,
        d.rating,
        p1.title as paper_1_title,
        p1.domain as paper_1_domain,
        p2.title as paper_2_title,
        p2.domain as paper_2_domain
      FROM discovered_pairs dp
      LEFT JOIN papers p1 ON dp.paper_1_id = p1.id
      LEFT JOIN papers p2 ON dp.paper_2_id = p2.id
      LEFT JOIN (
        SELECT
          d_inner.*,
          m1_inner.paper_id as p1_id,
          m2_inner.paper_id as p2_id
        FROM discoveries d_inner
        JOIN mechanisms m1_inner ON d_inner.mechanism_1_id = m1_inner.id
        JOIN mechanisms m2_inner ON d_inner.mechanism_2_id = m2_inner.id
      ) d ON (
        (d.p1_id = dp.paper_1_id AND d.p2_id = dp.paper_2_id)
        OR (d.p1_id = dp.paper_2_id AND d.p2_id = dp.paper_1_id)
      )
      WHERE 1=1
    `;

    const params: any[] = [];
    let paramIndex = 1;

    if (filters?.session) {
      queryText += ` AND dp.discovered_in_session = $${paramIndex}`;
      params.push(filters.session);
      paramIndex++;
    }

    if (filters?.rating) {
      queryText += ` AND d.rating = $${paramIndex}`;
      params.push(filters.rating);
      paramIndex++;
    }

    if (filters?.minSimilarity) {
      queryText += ` AND d.similarity >= $${paramIndex}`;
      params.push(filters.minSimilarity);
      paramIndex++;
    }

    queryText += ` ORDER BY d.similarity DESC NULLS LAST, dp.discovered_in_session DESC`;

    if (filters?.limit) {
      queryText += ` LIMIT $${paramIndex}`;
      params.push(filters.limit);
      paramIndex++;
    }

    if (filters?.offset) {
      queryText += ` OFFSET $${paramIndex}`;
      params.push(filters.offset);
    }

    const result = await query<DiscoveredPair>(queryText, params);
    return result.rows;
  },

  /**
   * Count discoveries matching the given filters (for pagination)
   */
  countDiscoveries: async (filters?: {
    rating?: string;
    domain?: string;
    minSimilarity?: number;
  }): Promise<number> => {
    let queryText = `
      SELECT COUNT(*) as count
      FROM discoveries d
      JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
      JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
      JOIN papers p1 ON m1.paper_id = p1.id
      JOIN papers p2 ON m2.paper_id = p2.id
      WHERE 1=1
    `;

    const params: any[] = [];
    let paramIndex = 1;

    if (filters?.rating) {
      queryText += ` AND d.rating = $${paramIndex}`;
      params.push(filters.rating);
      paramIndex++;
    }

    if (filters?.domain) {
      queryText += ` AND (p1.domain = $${paramIndex} OR p2.domain = $${paramIndex})`;
      params.push(filters.domain);
      paramIndex++;
    }

    if (filters?.minSimilarity) {
      queryText += ` AND d.similarity >= $${paramIndex}`;
      params.push(filters.minSimilarity);
      paramIndex++;
    }

    const result = await query(queryText, params);
    return parseInt(result.rows[0]?.count || '0');
  },

  /**
   * Get discovery statistics
   */
  getDiscoveryStats: async () => {
    const countByRating = await query(`
      SELECT rating, COUNT(*) as count
      FROM discoveries
      GROUP BY rating
    `);

    const domainPairs = await query(`
      SELECT p1.domain as domain1, p2.domain as domain2, COUNT(*) as count
      FROM discoveries d
      JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
      JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
      JOIN papers p1 ON m1.paper_id = p1.id
      JOIN papers p2 ON m2.paper_id = p2.id
      GROUP BY p1.domain, p2.domain
      ORDER BY count DESC
    `);

    const similarityStats = await query(`
      SELECT
        MIN(similarity) as min,
        MAX(similarity) as max,
        AVG(similarity) as avg
      FROM discoveries
    `);

    const uniqueDomains = await query(`
      SELECT DISTINCT domain
      FROM (
        SELECT p.domain
        FROM discoveries d
        JOIN mechanisms m ON d.mechanism_1_id = m.id OR d.mechanism_2_id = m.id
        JOIN papers p ON m.paper_id = p.id
      ) as all_domains
      ORDER BY domain
    `);

    return {
      byRating: countByRating.rows,
      domainPairs: domainPairs.rows,
      similarity: similarityStats.rows[0],
      uniqueDomains: uniqueDomains.rows.map((r: any) => r.domain)
    };
  }
};

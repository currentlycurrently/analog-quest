import { NextRequest, NextResponse } from 'next/server';
import { queries, query } from '@/lib/db';

// GET /api/pairs - Get discovered pairs (source of truth for unique discoveries)
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Get query parameters
    const session = searchParams.get('session') ? parseInt(searchParams.get('session')!) : undefined;
    const rating = searchParams.get('rating') || undefined;
    const minSimilarity = searchParams.get('minSimilarity')
      ? parseFloat(searchParams.get('minSimilarity')!)
      : undefined;
    const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : undefined;
    const offset = searchParams.get('offset') ? parseInt(searchParams.get('offset')!) : 0;

    // Fetch discovered pairs from database
    const pairs = await queries.getAllDiscoveredPairs({
      session,
      rating,
      minSimilarity,
      limit,
      offset
    });

    // Calculate stats
    const total = pairs.length;
    const stats = {
      total,
      excellent: pairs.filter(p => p.rating === 'excellent').length,
      good: pairs.filter(p => p.rating === 'good').length,
      sessions: [...new Set(pairs.map(p => p.discovered_in_session))].sort((a, b) => a - b),
      similarity_range: pairs.length > 0 ? {
        min: Math.min(...pairs.map(p => p.similarity)),
        max: Math.max(...pairs.map(p => p.similarity)),
        avg: pairs.reduce((sum, p) => sum + p.similarity, 0) / pairs.length
      } : null
    };

    // Get metadata about the discovered_pairs table
    const countResult = await query('SELECT COUNT(*) as total FROM discovered_pairs');
    const totalInDb = parseInt(countResult.rows[0]?.total || '0');

    return NextResponse.json({
      data: pairs,
      metadata: {
        total: totalInDb,
        returned: pairs.length,
        offset,
        limit,
        filters: {
          session,
          rating,
          minSimilarity
        },
        stats,
        source: 'postgresql',
        database: 'analog_quest'
      }
    });

  } catch (error) {
    console.error('Error in GET /api/pairs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch pairs', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// POST /api/pairs - Add a new discovered pair (future feature)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const enableWriteOps = process.env.ENABLE_WRITE_OPS === 'true';

    if (!enableWriteOps) {
      return NextResponse.json(
        {
          error: 'Write operations not enabled',
          message: 'Set ENABLE_WRITE_OPS=true in environment to enable',
          received: body
        },
        { status: 501 }
      );
    }

    // Validate required fields
    const required = ['paper_1_id', 'paper_2_id', 'similarity', 'rating', 'discovered_in_session'];
    const missing = required.filter(field => !(field in body));

    if (missing.length > 0) {
      return NextResponse.json(
        {
          error: 'Missing required fields',
          missing,
          required
        },
        { status: 400 }
      );
    }

    // TODO: Implement when write operations are enabled
    return NextResponse.json(
      {
        error: 'Not implemented',
        message: 'Write operations coming soon',
        received: body
      },
      { status: 501 }
    );

  } catch (error) {
    console.error('Error in POST /api/pairs:', error);
    return NextResponse.json(
      { error: 'Invalid request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 400 }
    );
  }
}
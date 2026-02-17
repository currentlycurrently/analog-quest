import { NextRequest, NextResponse } from 'next/server';
import { queries } from '@/lib/db';

// GET /api/discoveries - Get all discoveries or filtered results
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Get query parameters
    const rating = searchParams.get('rating') || undefined;
    const domain = searchParams.get('domain') || undefined;
    const minSimilarity = searchParams.get('minSimilarity')
      ? parseFloat(searchParams.get('minSimilarity')!)
      : undefined;
    const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : undefined;
    const offset = searchParams.get('offset') ? parseInt(searchParams.get('offset')!) : 0;
    const sortBy = searchParams.get('sortBy') || 'similarity';
    const order = (searchParams.get('order') || 'desc') as 'asc' | 'desc';

    // Fetch discoveries from database with filters
    // Run queries in parallel for performance
    const [discoveries, total, stats] = await Promise.all([
      queries.getAllDiscoveriesWithDetails({
        rating,
        domain,
        minSimilarity,
        limit,
        offset,
        sortBy,
        order
      }),
      // Count total matching records (without pagination) for metadata
      queries.countDiscoveries({ rating, domain, minSimilarity }),
      // Get overall database statistics
      queries.getDiscoveryStats()
    ]);

    // Calculate stats for current page
    const excellent = discoveries.filter(d => d.rating === 'excellent').length;
    const good = discoveries.filter(d => d.rating === 'good').length;
    const uniqueDomains = [...new Set(discoveries.flatMap(d => d.domains || []))];

    // Return response with metadata
    return NextResponse.json({
      data: discoveries,
      metadata: {
        total,
        returned: discoveries.length,
        offset,
        limit,
        filters: {
          rating,
          domain,
          minSimilarity
        },
        stats: {
          excellent,
          good,
          uniqueDomains: uniqueDomains.length,
          domains: uniqueDomains.sort(),
          database_stats: stats
        },
        source: 'postgresql',
        database: 'analog_quest'
      }
    });

  } catch (error) {
    console.error('Error in GET /api/discoveries:', error);
    return NextResponse.json(
      { error: 'Failed to fetch discoveries', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// POST /api/discoveries - Add a new discovery (future feature)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Check if write operations are enabled
    const enableWriteOps = process.env.ENABLE_WRITE_OPS === 'true';

    if (!enableWriteOps) {
      return NextResponse.json(
        {
          error: 'Write operations not enabled',
          message: 'Set ENABLE_WRITE_OPS=true in environment to enable',
          received: body
        },
        { status: 501 } // Not Implemented
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
    console.error('Error in POST /api/discoveries:', error);
    return NextResponse.json(
      { error: 'Invalid request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 400 }
    );
  }
}

// OPTIONS /api/discoveries - Get statistics and capabilities
export async function OPTIONS(request: NextRequest) {
  try {
    const stats = await queries.getDiscoveryStats();

    return NextResponse.json({
      api_version: '2.0.0',
      database: 'postgresql',
      capabilities: {
        filtering: true,
        sorting: true,
        pagination: true,
        writing: process.env.ENABLE_WRITE_OPS === 'true',
        database: true
      },
      stats: stats,
      endpoints: {
        list: 'GET /api/discoveries',
        detail: 'GET /api/discoveries/[id]',
        create: 'POST /api/discoveries (not enabled)',
        statistics: 'OPTIONS /api/discoveries'
      }
    });
  } catch (error) {
    console.error('Error in OPTIONS /api/discoveries:', error);
    return NextResponse.json(
      { error: 'Failed to get statistics', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
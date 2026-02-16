import { NextRequest, NextResponse } from 'next/server';
import discoveriesData from '@/app/data/discoveries.json';
import discoveredPairsData from '@/app/data/discovered_pairs.json';

// GET /api/discoveries - Get all discoveries or filtered results
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Get query parameters
    const rating = searchParams.get('rating');
    const domain = searchParams.get('domain');
    const minSimilarity = searchParams.get('minSimilarity');
    const limit = searchParams.get('limit');
    const offset = searchParams.get('offset');
    const sortBy = searchParams.get('sortBy') || 'similarity';
    const order = searchParams.get('order') || 'desc';

    // Start with all discoveries
    let discoveries = [...discoveriesData];

    // Apply filters
    if (rating) {
      discoveries = discoveries.filter(d => d.rating === rating);
    }

    if (domain) {
      discoveries = discoveries.filter(d =>
        d.domains && d.domains.includes(domain)
      );
    }

    if (minSimilarity) {
      const threshold = parseFloat(minSimilarity);
      discoveries = discoveries.filter(d => d.similarity >= threshold);
    }

    // Apply sorting
    discoveries.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'similarity':
          comparison = b.similarity - a.similarity;
          break;
        case 'rating':
          // Excellent first, then by similarity
          if (a.rating === 'excellent' && b.rating === 'good') comparison = -1;
          else if (a.rating === 'good' && b.rating === 'excellent') comparison = 1;
          else comparison = b.similarity - a.similarity;
          break;
        case 'id':
          comparison = a.id - b.id;
          break;
        case 'session':
          comparison = (a.session || 0) - (b.session || 0);
          break;
        default:
          comparison = b.similarity - a.similarity;
      }

      return order === 'desc' ? comparison : -comparison;
    });

    // Calculate metadata before pagination
    const total = discoveries.length;
    const excellent = discoveries.filter(d => d.rating === 'excellent').length;
    const good = discoveries.filter(d => d.rating === 'good').length;
    const uniqueDomains = [...new Set(discoveries.flatMap(d => d.domains || []))];

    // Apply pagination
    const limitNum = limit ? parseInt(limit) : undefined;
    const offsetNum = offset ? parseInt(offset) : 0;

    if (limitNum) {
      discoveries = discoveries.slice(offsetNum, offsetNum + limitNum);
    } else if (offsetNum > 0) {
      discoveries = discoveries.slice(offsetNum);
    }

    // Return response with metadata
    return NextResponse.json({
      data: discoveries,
      metadata: {
        total,
        returned: discoveries.length,
        offset: offsetNum,
        limit: limitNum,
        filters: {
          rating,
          domain,
          minSimilarity: minSimilarity ? parseFloat(minSimilarity) : null
        },
        stats: {
          excellent,
          good,
          uniqueDomains: uniqueDomains.length,
          domains: uniqueDomains.sort()
        },
        source: 'static_json',
        note: 'Currently serving from static JSON. Database integration coming soon.'
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

// GET /api/discoveries/[id] - We'll need a dynamic route for this
// For now, you can get by ID using a filter

// POST /api/discoveries - Add a new discovery (placeholder for future)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // For now, return an error since we can't write to static JSON
    // This will be implemented when we add database support
    return NextResponse.json(
      {
        error: 'Write operations not yet supported',
        message: 'Database integration required for adding new discoveries',
        received: body
      },
      { status: 501 } // Not Implemented
    );

  } catch (error) {
    console.error('Error in POST /api/discoveries:', error);
    return NextResponse.json(
      { error: 'Invalid request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 400 }
    );
  }
}

// Helper endpoint to get statistics
export async function OPTIONS(request: NextRequest) {
  const stats = {
    total_discoveries: discoveriesData.length,
    unique_pairs: discoveredPairsData.discovered_pairs.length,
    ratings: {
      excellent: discoveriesData.filter(d => d.rating === 'excellent').length,
      good: discoveriesData.filter(d => d.rating === 'good').length
    },
    similarity_range: {
      min: Math.min(...discoveriesData.map(d => d.similarity)),
      max: Math.max(...discoveriesData.map(d => d.similarity)),
      avg: discoveriesData.reduce((sum, d) => sum + d.similarity, 0) / discoveriesData.length
    },
    domains: [...new Set(discoveriesData.flatMap(d => d.domains || []))].sort(),
    sessions: [...new Set(discoveriesData.map(d => d.session || 0))].sort((a, b) => a - b),
    api_version: '1.0.0',
    capabilities: {
      filtering: true,
      sorting: true,
      pagination: true,
      writing: false,
      database: false
    }
  };

  return NextResponse.json(stats);
}
import { NextRequest, NextResponse } from 'next/server';
import discoveredPairsData from '@/app/data/discovered_pairs.json';

// GET /api/pairs - Get discovered pairs (source of truth for unique discoveries)
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Get query parameters
    const session = searchParams.get('session');
    const rating = searchParams.get('rating');
    const minSimilarity = searchParams.get('minSimilarity');
    const limit = searchParams.get('limit');
    const offset = searchParams.get('offset');

    // Start with all pairs
    let pairs = [...discoveredPairsData.discovered_pairs];

    // Apply filters
    if (session) {
      const sessionNum = parseInt(session);
      pairs = pairs.filter(p => p.discovered_in_session === sessionNum);
    }

    if (rating) {
      pairs = pairs.filter(p => p.rating === rating);
    }

    if (minSimilarity) {
      const threshold = parseFloat(minSimilarity);
      pairs = pairs.filter(p => p.similarity >= threshold);
    }

    // Sort by similarity (highest first)
    pairs.sort((a, b) => b.similarity - a.similarity);

    // Calculate stats before pagination
    const total = pairs.length;
    const stats = {
      total,
      excellent: pairs.filter(p => p.rating === 'excellent').length,
      good: pairs.filter(p => p.rating === 'good').length,
      sessions: [...new Set(pairs.map(p => p.discovered_in_session))].sort((a, b) => a - b),
      similarity_range: {
        min: Math.min(...pairs.map(p => p.similarity)),
        max: Math.max(...pairs.map(p => p.similarity)),
        avg: pairs.reduce((sum, p) => sum + p.similarity, 0) / pairs.length
      }
    };

    // Apply pagination
    const limitNum = limit ? parseInt(limit) : undefined;
    const offsetNum = offset ? parseInt(offset) : 0;

    if (limitNum) {
      pairs = pairs.slice(offsetNum, offsetNum + limitNum);
    } else if (offsetNum > 0) {
      pairs = pairs.slice(offsetNum);
    }

    return NextResponse.json({
      data: pairs,
      metadata: {
        ...discoveredPairsData.metadata,
        returned: pairs.length,
        offset: offsetNum,
        limit: limitNum,
        stats
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

// POST /api/pairs - Add a new discovered pair (placeholder)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

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

    // For now, we can't actually save to the JSON file
    return NextResponse.json(
      {
        error: 'Write operations not yet supported',
        message: 'Database integration required for adding new pairs',
        received: body,
        note: 'Use scripts/add_discovered_pair.py locally for now'
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
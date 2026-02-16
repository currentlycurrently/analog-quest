import { NextRequest, NextResponse } from 'next/server';
import discoveriesData from '@/app/data/discoveries.json';
import editorialData from '@/app/data/discoveries_editorial.json';

interface RouteParams {
  params: {
    id: string;
  };
}

// GET /api/discoveries/[id] - Get a single discovery by ID
export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json(
        { error: 'Invalid ID format', details: 'ID must be a number' },
        { status: 400 }
      );
    }

    // Find the discovery
    const discovery = discoveriesData.find(d => d.id === id);

    if (!discovery) {
      return NextResponse.json(
        { error: 'Discovery not found', id },
        { status: 404 }
      );
    }

    // Try to get editorial content if it exists
    let editorial = null;
    try {
      const editorials = (editorialData as any).editorials;
      editorial = editorials[id.toString()] || null;
    } catch (e) {
      // Editorial data might not exist or be in different format
      console.log('No editorial data found for discovery', id);
    }

    // Return the discovery with optional editorial
    return NextResponse.json({
      data: {
        ...discovery,
        editorial
      },
      metadata: {
        has_editorial: editorial !== null,
        source: 'static_json'
      }
    });

  } catch (error) {
    console.error('Error in GET /api/discoveries/[id]:', error);
    return NextResponse.json(
      { error: 'Failed to fetch discovery', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// PUT /api/discoveries/[id] - Update a discovery (placeholder)
export async function PUT(request: NextRequest, { params }: RouteParams) {
  try {
    const id = parseInt(params.id);
    const body = await request.json();

    return NextResponse.json(
      {
        error: 'Update operations not yet supported',
        message: 'Database integration required for updating discoveries',
        id,
        received: body
      },
      { status: 501 }
    );

  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 400 }
    );
  }
}

// DELETE /api/discoveries/[id] - Delete a discovery (placeholder)
export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    const id = parseInt(params.id);

    return NextResponse.json(
      {
        error: 'Delete operations not yet supported',
        message: 'Database integration required for deleting discoveries',
        id
      },
      { status: 501 }
    );

  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 400 }
    );
  }
}
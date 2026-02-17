import { NextRequest, NextResponse } from 'next/server';
import { queries } from '@/lib/db';
import fs from 'fs';
import path from 'path';

type RouteParams = {
  params: Promise<{
    id: string;
  }>;
}

// GET /api/discoveries/[id] - Get a single discovery by ID
export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const resolvedParams = await params;
    const id = parseInt(resolvedParams.id);

    if (isNaN(id)) {
      return NextResponse.json(
        { error: 'Invalid ID format', details: 'ID must be a number' },
        { status: 400 }
      );
    }

    // Fetch discovery from database
    const discovery = await queries.getDiscoveryById(id);

    if (!discovery) {
      return NextResponse.json(
        { error: 'Discovery not found', id },
        { status: 404 }
      );
    }

    // Try to get editorial content if it exists
    let editorial = null;
    try {
      const editorialPath = path.join(process.cwd(), 'app', 'data', 'discoveries_editorial.json');
      if (fs.existsSync(editorialPath)) {
        const editorialData = JSON.parse(fs.readFileSync(editorialPath, 'utf-8'));
        editorial = editorialData.editorials?.[id.toString()] || null;
      }
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
        source: 'postgresql',
        database: 'analog_quest'
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

// PUT /api/discoveries/[id] - Update a discovery (future feature)
export async function PUT(request: NextRequest, { params }: RouteParams) {
  try {
    const resolvedParams = await params;
    const id = parseInt(resolvedParams.id);
    const body = await request.json();

    const enableWriteOps = process.env.ENABLE_WRITE_OPS === 'true';

    if (!enableWriteOps) {
      return NextResponse.json(
        {
          error: 'Write operations not enabled',
          message: 'Set ENABLE_WRITE_OPS=true in environment to enable',
          id,
          received: body
        },
        { status: 501 }
      );
    }

    // TODO: Implement when write operations are enabled
    return NextResponse.json(
      {
        error: 'Not implemented',
        message: 'Update operations coming soon',
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

// DELETE /api/discoveries/[id] - Delete a discovery (future feature)
export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    const resolvedParams = await params;
    const id = parseInt(resolvedParams.id);

    const enableWriteOps = process.env.ENABLE_WRITE_OPS === 'true';

    if (!enableWriteOps) {
      return NextResponse.json(
        {
          error: 'Write operations not enabled',
          message: 'Set ENABLE_WRITE_OPS=true in environment to enable',
          id
        },
        { status: 501 }
      );
    }

    // TODO: Implement when write operations are enabled
    return NextResponse.json(
      {
        error: 'Not implemented',
        message: 'Delete operations coming soon',
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
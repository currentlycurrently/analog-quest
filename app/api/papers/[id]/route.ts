import { NextResponse } from 'next/server';
import { getDb, Paper, Pattern } from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const db = getDb();

    // Get paper
    const paper = db.prepare('SELECT * FROM papers WHERE id = ?').get(id) as Paper | undefined;

    if (!paper) {
      db.close();
      return NextResponse.json(
        { error: 'Paper not found' },
        { status: 404 }
      );
    }

    // Get patterns for this paper
    const patterns = db.prepare(`
      SELECT * FROM patterns WHERE paper_id = ?
    `).all(id) as Pattern[];

    db.close();

    return NextResponse.json({
      paper,
      patterns,
    });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch paper' },
      { status: 500 }
    );
  }
}

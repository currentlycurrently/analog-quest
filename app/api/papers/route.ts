import { NextResponse } from 'next/server';
import { getDb, Paper } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const domain = searchParams.get('domain');
    const search = searchParams.get('search');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const offset = (page - 1) * limit;

    const db = getDb();

    let query = 'SELECT * FROM papers';
    let countQuery = 'SELECT COUNT(*) as count FROM papers';
    const params: any[] = [];
    const conditions: string[] = [];

    if (domain && domain !== 'all') {
      conditions.push('domain = ?');
      params.push(domain);
    }

    if (search && search.trim()) {
      conditions.push('(title LIKE ? OR abstract LIKE ?)');
      const searchTerm = `%${search.trim()}%`;
      params.push(searchTerm, searchTerm);
    }

    if (conditions.length > 0) {
      const whereClause = ' WHERE ' + conditions.join(' AND ');
      query += whereClause;
      countQuery += whereClause;
    }

    query += ' ORDER BY published_date DESC LIMIT ? OFFSET ?';

    const papers = db.prepare(query).all(...params, limit, offset) as Paper[];
    const total = db.prepare(countQuery).get(...params) as { count: number };

    db.close();

    return NextResponse.json({
      papers,
      total: total.count,
      page,
      limit,
      totalPages: Math.ceil(total.count / limit),
    });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch papers' },
      { status: 500 }
    );
  }
}

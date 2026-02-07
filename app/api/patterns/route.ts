import { NextResponse } from 'next/server';
import { getDb, Pattern } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const domain = searchParams.get('domain');
    const mechanismType = searchParams.get('mechanism_type');
    const paperId = searchParams.get('paper_id');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = (page - 1) * limit;

    const db = getDb();

    let query = `
      SELECT
        patterns.*,
        papers.title as paper_title,
        papers.domain as paper_domain,
        papers.arxiv_id
      FROM patterns
      JOIN papers ON patterns.paper_id = papers.id
    `;

    let countQuery = `
      SELECT COUNT(*) as count
      FROM patterns
      JOIN papers ON patterns.paper_id = papers.id
    `;

    const conditions: string[] = [];
    const params: any[] = [];

    if (paperId) {
      conditions.push('patterns.paper_id = ?');
      params.push(paperId);
    }

    if (domain && domain !== 'all') {
      conditions.push('papers.domain = ?');
      params.push(domain);
    }

    if (mechanismType && mechanismType !== 'all') {
      conditions.push('patterns.mechanism_type = ?');
      params.push(mechanismType);
    }

    if (conditions.length > 0) {
      const whereClause = ' WHERE ' + conditions.join(' AND ');
      query += whereClause;
      countQuery += whereClause;
    }

    query += ' ORDER BY patterns.id DESC LIMIT ? OFFSET ?';

    const patterns = db.prepare(query).all(...params, limit, offset) as Pattern[];
    const total = db.prepare(countQuery).get(...params) as { count: number };

    db.close();

    return NextResponse.json({
      patterns,
      total: total.count,
      page,
      limit,
      totalPages: Math.ceil(total.count / limit),
    });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch patterns' },
      { status: 500 }
    );
  }
}

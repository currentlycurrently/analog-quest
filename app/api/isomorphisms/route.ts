import { NextResponse } from 'next/server';
import { getDb, Isomorphism } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const minScore = parseFloat(searchParams.get('min_score') || '0.5');
    const maxScore = parseFloat(searchParams.get('max_score') || '1.0');
    const domain1 = searchParams.get('domain1');
    const domain2 = searchParams.get('domain2');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = (page - 1) * limit;

    const db = getDb();

    let query = `
      SELECT
        isomorphisms.*,
        p1.mechanism_type as pattern_1_type,
        p2.mechanism_type as pattern_2_type,
        p1.structural_description as pattern_1_description,
        p2.structural_description as pattern_2_description,
        paper1.title as paper_1_title,
        paper2.title as paper_2_title,
        paper1.domain as paper_1_domain,
        paper2.domain as paper_2_domain
      FROM isomorphisms
      JOIN patterns p1 ON isomorphisms.pattern_1_id = p1.id
      JOIN patterns p2 ON isomorphisms.pattern_2_id = p2.id
      JOIN papers paper1 ON p1.paper_id = paper1.id
      JOIN papers paper2 ON p2.paper_id = paper2.id
    `;

    let countQuery = `
      SELECT COUNT(*) as count
      FROM isomorphisms
      JOIN patterns p1 ON isomorphisms.pattern_1_id = p1.id
      JOIN patterns p2 ON isomorphisms.pattern_2_id = p2.id
      JOIN papers paper1 ON p1.paper_id = paper1.id
      JOIN papers paper2 ON p2.paper_id = paper2.id
    `;

    const conditions: string[] = [];
    const params: any[] = [];

    conditions.push('isomorphisms.similarity_score >= ?');
    conditions.push('isomorphisms.similarity_score <= ?');
    params.push(minScore, maxScore);

    if (domain1 && domain1 !== 'all') {
      conditions.push('paper1.domain = ?');
      params.push(domain1);
    }

    if (domain2 && domain2 !== 'all') {
      conditions.push('paper2.domain = ?');
      params.push(domain2);
    }

    if (conditions.length > 0) {
      const whereClause = ' WHERE ' + conditions.join(' AND ');
      query += whereClause;
      countQuery += whereClause;
    }

    query += ' ORDER BY isomorphisms.similarity_score DESC LIMIT ? OFFSET ?';

    const isomorphisms = db.prepare(query).all(...params, limit, offset) as Isomorphism[];
    const total = db.prepare(countQuery).get(...params) as { count: number };

    db.close();

    return NextResponse.json({
      isomorphisms,
      total: total.count,
      page,
      limit,
      totalPages: Math.ceil(total.count / limit),
    });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch isomorphisms' },
      { status: 500 }
    );
  }
}

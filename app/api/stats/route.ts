import { NextResponse } from 'next/server';
import { getDb, Stats } from '@/lib/db';

export async function GET() {
  try {
    const db = getDb();

    // Get basic counts
    const total_papers = db.prepare('SELECT COUNT(*) as count FROM papers').get() as { count: number };
    const total_patterns = db.prepare('SELECT COUNT(*) as count FROM patterns').get() as { count: number };
    const total_isomorphisms = db.prepare('SELECT COUNT(*) as count FROM isomorphisms').get() as { count: number };

    // Get papers with patterns
    const papers_with_patterns = db.prepare(
      'SELECT COUNT(DISTINCT paper_id) as count FROM patterns'
    ).get() as { count: number };

    // Calculate hit rate
    const hit_rate = total_papers.count > 0
      ? (papers_with_patterns.count / total_papers.count) * 100
      : 0;

    // Get domain distribution
    const domains = db.prepare(`
      SELECT domain, COUNT(*) as count
      FROM papers
      GROUP BY domain
      ORDER BY count DESC
    `).all() as { domain: string; count: number }[];

    // Get pattern type distribution
    const pattern_types = db.prepare(`
      SELECT mechanism_type, COUNT(*) as count
      FROM patterns
      GROUP BY mechanism_type
      ORDER BY count DESC
      LIMIT 15
    `).all() as { mechanism_type: string; count: number }[];

    const stats: Stats = {
      total_papers: total_papers.count,
      total_patterns: total_patterns.count,
      total_isomorphisms: total_isomorphisms.count,
      papers_with_patterns: papers_with_patterns.count,
      hit_rate: Math.round(hit_rate * 10) / 10,
      domains,
      pattern_types,
    };

    db.close();
    return NextResponse.json(stats);
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    );
  }
}

import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

// GET /api/queue/status
// Public stats — how much work is left, what's been found
export async function GET() {
  const [queueStats, isomorphismStats, contributorStats] = await Promise.all([
    query<{ status: string; count: string }>(`
      SELECT status, COUNT(*) as count FROM queue GROUP BY status
    `),
    query<{ status: string; count: string; equation_class: string }>(`
      SELECT status, equation_class, COUNT(*) as count
      FROM isomorphisms
      GROUP BY status, equation_class
      ORDER BY count DESC
    `),
    query<{ total: string; active_today: string }>(`
      SELECT
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE last_seen > NOW() - INTERVAL '24 hours') as active_today
      FROM contributors
    `),
  ]);

  const queue: Record<string, number> = {};
  for (const row of queueStats.rows) {
    queue[row.status] = parseInt(row.count);
  }

  return NextResponse.json({
    queue: {
      pending: queue.pending ?? 0,
      in_progress: queue.checked_out ?? 0,
      done: queue.done ?? 0,
      total: Object.values(queue).reduce((a, b) => a + b, 0),
    },
    isomorphisms: {
      candidates: isomorphismStats.rows.filter(r => r.status === 'candidate').length,
      verified: isomorphismStats.rows
        .filter(r => r.status === 'verified')
        .reduce((a, r) => a + parseInt(r.count), 0),
      by_class: isomorphismStats.rows.reduce((acc, r) => {
        if (!acc[r.equation_class]) acc[r.equation_class] = 0;
        acc[r.equation_class] += parseInt(r.count);
        return acc;
      }, {} as Record<string, number>),
    },
    contributors: {
      total: parseInt(contributorStats.rows[0]?.total ?? '0'),
      active_today: parseInt(contributorStats.rows[0]?.active_today ?? '0'),
    },
  });
}

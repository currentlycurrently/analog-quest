import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

const VALID_CLASSES = [
  'LOTKA_VOLTERRA',
  'HEAT_EQUATION',
  'HOPF_BIFURCATION',
  'ISING_MODEL',
  'POWER_LAW',
  'KURAMOTO',
  'SIR',
  'SCHRODINGER',
  'NAVIER_STOKES',
  'GAME_THEORY',
  'OTHER',
  'NONE',
] as const;

type EquationClass = typeof VALID_CLASSES[number];

interface SubmitBody {
  queue_id: number;
  token: string;
  equation_class: EquationClass;
  latex_fragments?: string[];
  variables?: { symbol: string; meaning: string }[];
  domain?: string;
  confidence: number;         // 0.0–1.0
  notes?: string;
}

// POST /api/queue/submit
// Agent submits its extraction for a checked-out paper
export async function POST(request: NextRequest) {
  let body: SubmitBody;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const { queue_id, token, equation_class, latex_fragments, variables, domain, confidence, notes } = body;

  // Validate required fields
  if (!queue_id || !token || !equation_class || confidence === undefined) {
    return NextResponse.json(
      { error: 'Required: queue_id, token, equation_class, confidence' },
      { status: 400 }
    );
  }

  if (!VALID_CLASSES.includes(equation_class)) {
    return NextResponse.json(
      { error: `equation_class must be one of: ${VALID_CLASSES.join(', ')}` },
      { status: 400 }
    );
  }

  if (confidence < 0 || confidence > 1) {
    return NextResponse.json({ error: 'confidence must be 0.0–1.0' }, { status: 400 });
  }

  // Verify the queue entry belongs to this token
  const checkout = await query<{ paper_id: number; status: string; checked_out_by: string }>(
    `SELECT paper_id, status, checked_out_by FROM queue WHERE id = $1`,
    [queue_id]
  );

  if (checkout.rowCount === 0) {
    return NextResponse.json({ error: 'queue_id not found' }, { status: 404 });
  }

  const entry = checkout.rows[0];

  if (entry.checked_out_by !== token) {
    return NextResponse.json({ error: 'token does not match checkout' }, { status: 403 });
  }

  if (entry.status !== 'checked_out') {
    return NextResponse.json({ error: `queue entry status is '${entry.status}', expected 'checked_out'` }, { status: 409 });
  }

  // Save the extraction
  await query(`
    INSERT INTO extractions
      (paper_id, contributor_token, equation_class, latex_fragments, variables, domain, confidence, notes)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
  `, [
    entry.paper_id,
    token,
    equation_class,
    latex_fragments ?? [],
    variables ? JSON.stringify(variables) : null,
    domain ?? null,
    confidence,
    notes ?? null,
  ]);

  // Mark queue entry as done
  await query(`UPDATE queue SET status = 'done' WHERE id = $1`, [queue_id]);

  // Update contributor stats
  await query(`
    UPDATE contributors
    SET extractions = extractions + 1, last_seen = NOW()
    WHERE token = $1
  `, [token]);

  // Check if this creates a new isomorphism candidate
  // Find other papers with the same equation_class (skip if NONE)
  let new_candidates = 0;
  if (equation_class !== 'NONE') {
    const matches = await query<{ paper_id: number }>(`
      SELECT DISTINCT paper_id
      FROM extractions
      WHERE equation_class = $1
        AND paper_id != $2
        AND confidence >= 0.6
    `, [equation_class, entry.paper_id]);

    for (const match of matches.rows) {
      const p1 = Math.min(entry.paper_id, match.paper_id);
      const p2 = Math.max(entry.paper_id, match.paper_id);

      // Compute average confidence across both sides
      const avgConf = await query<{ avg: number }>(`
        SELECT AVG(confidence) as avg
        FROM extractions
        WHERE paper_id IN ($1, $2) AND equation_class = $3
      `, [p1, p2, equation_class]);

      const conf = avgConf.rows[0]?.avg ?? confidence;

      await query(`
        INSERT INTO isomorphisms (paper_1_id, paper_2_id, equation_class, latex_paper_1, latex_paper_2, confidence, validation_count)
        VALUES ($1, $2, $3, $4, $5, $6, 1)
        ON CONFLICT (paper_1_id, paper_2_id, equation_class)
        DO UPDATE SET
          validation_count = isomorphisms.validation_count + 1,
          confidence = $6,
          status = CASE WHEN isomorphisms.validation_count + 1 >= 2 THEN 'verified' ELSE 'candidate' END
      `, [p1, p2, equation_class, latex_fragments ?? [], [], conf]);

      new_candidates++;
    }
  }

  return NextResponse.json({
    success: true,
    paper_id: entry.paper_id,
    equation_class,
    new_isomorphism_candidates: new_candidates,
    message: new_candidates > 0
      ? `Found ${new_candidates} potential isomorphism(s)!`
      : 'Extraction saved. Keep going!',
  });
}

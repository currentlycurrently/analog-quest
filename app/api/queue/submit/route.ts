/**
 * POST /api/queue/submit
 *
 * Submit a Mode B (abstract reader) extraction for a checked-out paper.
 *
 * Auth: requires a GitHub-authenticated NextAuth session.
 * Rate limit: 6 requests/minute per user.
 *
 * Body:
 *   queue_id          number     — the queue entry you checked out
 *   equation_class    string     — one of VALID_CLASSES
 *   confidence        number     — 0.0 to 1.0
 *   latex_fragments?  string[]   — raw LaTeX strings
 *   variables?        array      — [{ symbol, meaning }]
 *   domain?           string     — the paper's scientific domain
 *   notes?            string     — free-form, max 500 chars
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

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

type EquationClass = (typeof VALID_CLASSES)[number];

const MAX_NOTES_LENGTH = 500;
const MAX_LATEX_FRAGMENTS = 20;
const MAX_LATEX_FRAGMENT_LENGTH = 1000;
const MAX_VARIABLES = 30;

interface SubmitBody {
  queue_id: number;
  equation_class: EquationClass;
  latex_fragments?: string[];
  variables?: { symbol: string; meaning: string }[];
  domain?: string;
  confidence: number;
  notes?: string;
}

export async function POST(request: NextRequest) {
  const authResult = await requireUser(request);
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('queueSubmit', `user:${user.id}`);
  if (limited) return limited;

  let body: SubmitBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON' }, { status: 400 });
  }

  const { queue_id, equation_class, confidence, latex_fragments, variables, domain, notes } = body;

  // Required fields
  if (typeof queue_id !== 'number' || !equation_class || confidence === undefined) {
    return NextResponse.json(
      { error: 'required: queue_id (number), equation_class, confidence' },
      { status: 400 }
    );
  }
  if (!VALID_CLASSES.includes(equation_class)) {
    return NextResponse.json(
      { error: `equation_class must be one of: ${VALID_CLASSES.join(', ')}` },
      { status: 400 }
    );
  }
  if (typeof confidence !== 'number' || confidence < 0 || confidence > 1) {
    return NextResponse.json({ error: 'confidence must be a number in [0, 1]' }, { status: 400 });
  }

  // Bounded free-form fields
  if (notes !== undefined && (typeof notes !== 'string' || notes.length > MAX_NOTES_LENGTH)) {
    return NextResponse.json(
      { error: `notes must be a string of at most ${MAX_NOTES_LENGTH} chars` },
      { status: 400 }
    );
  }
  if (domain !== undefined && (typeof domain !== 'string' || domain.length > 100)) {
    return NextResponse.json(
      { error: 'domain must be a string of at most 100 chars' },
      { status: 400 }
    );
  }
  if (latex_fragments !== undefined) {
    if (!Array.isArray(latex_fragments) || latex_fragments.length > MAX_LATEX_FRAGMENTS) {
      return NextResponse.json(
        { error: `latex_fragments must be an array of at most ${MAX_LATEX_FRAGMENTS} strings` },
        { status: 400 }
      );
    }
    for (const f of latex_fragments) {
      if (typeof f !== 'string' || f.length > MAX_LATEX_FRAGMENT_LENGTH) {
        return NextResponse.json(
          { error: `each latex_fragment must be a string of at most ${MAX_LATEX_FRAGMENT_LENGTH} chars` },
          { status: 400 }
        );
      }
    }
  }
  if (variables !== undefined) {
    if (!Array.isArray(variables) || variables.length > MAX_VARIABLES) {
      return NextResponse.json(
        { error: `variables must be an array of at most ${MAX_VARIABLES} items` },
        { status: 400 }
      );
    }
    for (const v of variables) {
      if (
        typeof v !== 'object' ||
        v === null ||
        typeof v.symbol !== 'string' ||
        typeof v.meaning !== 'string' ||
        v.symbol.length > 50 ||
        v.meaning.length > 200
      ) {
        return NextResponse.json(
          { error: 'each variable must be { symbol: string (<=50), meaning: string (<=200) }' },
          { status: 400 }
        );
      }
    }
  }

  // Verify the queue entry belongs to this user and is still checked out.
  const checkout = await query<{ paper_id: number; status: string; checked_out_by: string }>(
    `SELECT paper_id, status, checked_out_by FROM queue WHERE id = $1`,
    [queue_id]
  );
  if (checkout.rowCount === 0) {
    return NextResponse.json({ error: 'queue_id not found' }, { status: 404 });
  }
  const entry = checkout.rows[0];

  if (entry.checked_out_by !== `user:${user.id}`) {
    return NextResponse.json(
      { error: 'this queue entry is not checked out by your account' },
      { status: 403 }
    );
  }
  if (entry.status !== 'checked_out') {
    return NextResponse.json(
      { error: `queue entry status is '${entry.status}', expected 'checked_out'` },
      { status: 409 }
    );
  }

  // Save the extraction linked to the authenticated user.
  await query(
    `
    INSERT INTO extractions
      (paper_id, user_id, contributor_token, equation_class, latex_fragments,
       variables, domain, confidence, notes)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    `,
    [
      entry.paper_id,
      user.id,
      `user:${user.id}`, // legacy column; keep populated for backwards compat
      equation_class,
      latex_fragments ?? [],
      variables ? JSON.stringify(variables) : null,
      domain ?? null,
      confidence,
      notes ?? null,
    ]
  );

  // Mark queue entry as done.
  await query(`UPDATE queue SET status = 'done' WHERE id = $1`, [queue_id]);

  // Update contributor stats.
  await query(
    `UPDATE contributors
       SET submissions_count = submissions_count + 1,
           last_seen_at = NOW()
     WHERE user_id = $1`,
    [user.id]
  );

  // Consensus candidate check: if another user previously extracted the same
  // equation_class from a different-domain paper at reasonable confidence,
  // create or update a candidate isomorphism row in the agent-discovered table.
  let new_candidates = 0;
  if (equation_class !== 'NONE') {
    const matches = await query<{ paper_id: number }>(
      `SELECT DISTINCT paper_id
         FROM extractions
        WHERE equation_class = $1
          AND paper_id != $2
          AND confidence >= 0.6
          AND user_id != $3`,
      [equation_class, entry.paper_id, user.id]
    );

    for (const match of matches.rows) {
      const p1 = Math.min(entry.paper_id, match.paper_id);
      const p2 = Math.max(entry.paper_id, match.paper_id);

      const avgConf = await query<{ avg: number }>(
        `SELECT AVG(confidence) as avg
           FROM extractions
          WHERE paper_id IN ($1, $2) AND equation_class = $3`,
        [p1, p2, equation_class]
      );
      const conf = avgConf.rows[0]?.avg ?? confidence;

      await query(
        `
        INSERT INTO isomorphisms
          (paper_1_id, paper_2_id, equation_class, latex_paper_1, latex_paper_2,
           confidence, validation_count)
        VALUES ($1, $2, $3, $4, $5, $6, 1)
        ON CONFLICT (paper_1_id, paper_2_id, equation_class) DO UPDATE SET
          validation_count = isomorphisms.validation_count + 1,
          confidence = $6,
          status = CASE
            WHEN isomorphisms.validation_count + 1 >= 2 THEN 'verified'
            ELSE 'candidate'
          END
        `,
        [p1, p2, equation_class, latex_fragments ?? [], [], conf]
      );
      new_candidates++;
    }
  }

  return NextResponse.json({
    success: true,
    paper_id: entry.paper_id,
    equation_class,
    new_isomorphism_candidates: new_candidates,
    message:
      new_candidates > 0
        ? `found ${new_candidates} potential isomorphism(s) — keep going!`
        : 'extraction saved',
  });
}

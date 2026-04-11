/**
 * POST /api/pipeline/submit-extractions
 *
 * Mode A submission endpoint. The pipeline contributor's agent has downloaded
 * the arXiv LaTeX source for one or more papers, extracted equations locally,
 * normalized them via SymPy, and posts the results here in a batch.
 *
 * Auth: requires a GitHub-authenticated NextAuth session.
 * Rate limit: 60 requests/minute per user.
 *
 * Body:
 *   {
 *     papers: [
 *       {
 *         paper_id: number,
 *         source_available: boolean,
 *         equations: [
 *           {
 *             latex: string,                      // raw extracted LaTeX
 *             source_env: string,                 // 'equation', 'align', 'inline', etc.
 *             position: number,                   // ordinal in the paper
 *             sympy_parsed: boolean,              // did SymPy succeed
 *             normalized_form?: string | null,    // canonical srepr form, null if not parsed
 *             structure_hash?: string | null,     // sha256(normalized_form)
 *             equation_type?: string | null,      // 'ode', 'pde', 'algebraic', etc.
 *           },
 *           ...
 *         ]
 *       },
 *       ...
 *     ]
 *   }
 *
 * Returns 200 with per-paper counts:
 *   { stored: [{ paper_id, equations_inserted, skipped }, ...] }
 *
 * Idempotency: the pipeline may submit the same paper_id more than once
 * (e.g. two contributors race on the same batch). The second submission's
 * INSERTs will fail on the (paper_id, position) uniqueness check and be
 * silently skipped — no harm, just wasted work on the client side.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

const MAX_PAPERS_PER_REQUEST = 25;
const MAX_EQUATIONS_PER_PAPER = 2000; // some papers have 800+ real equations; cap at 2000
const MAX_LATEX_LENGTH = 4000;
const MAX_NORMALIZED_LENGTH = 8000;

interface EquationIn {
  latex: string;
  source_env?: string;
  position: number;
  sympy_parsed: boolean;
  normalized_form?: string | null;
  structure_hash?: string | null;
  equation_type?: string | null;
}

interface PaperIn {
  paper_id: number;
  source_available: boolean;
  equations?: EquationIn[];
}

interface SubmitBody {
  papers: PaperIn[];
}

function sanitize(s: string | null | undefined): string | null {
  if (s === null || s === undefined) return null;
  return s.replace(/\u0000/g, '');
}

export async function POST(request: NextRequest) {
  const authResult = await requireUser(request);
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('pipelineSubmit', `user:${user.id}`);
  if (limited) return limited;

  let body: SubmitBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON' }, { status: 400 });
  }

  if (!body?.papers || !Array.isArray(body.papers)) {
    return NextResponse.json({ error: 'required: papers (array)' }, { status: 400 });
  }
  if (body.papers.length === 0) {
    return NextResponse.json({ error: 'papers array must not be empty' }, { status: 400 });
  }
  if (body.papers.length > MAX_PAPERS_PER_REQUEST) {
    return NextResponse.json(
      { error: `too many papers in one request (max ${MAX_PAPERS_PER_REQUEST})` },
      { status: 400 }
    );
  }

  // Validate all papers up front before doing any writes.
  const paperIds = new Set<number>();
  for (const p of body.papers) {
    if (typeof p.paper_id !== 'number' || !Number.isFinite(p.paper_id)) {
      return NextResponse.json({ error: 'each paper needs a numeric paper_id' }, { status: 400 });
    }
    if (paperIds.has(p.paper_id)) {
      return NextResponse.json({ error: `duplicate paper_id ${p.paper_id} in request` }, { status: 400 });
    }
    paperIds.add(p.paper_id);

    if (typeof p.source_available !== 'boolean') {
      return NextResponse.json({ error: 'each paper needs source_available (boolean)' }, { status: 400 });
    }

    if (p.equations !== undefined) {
      if (!Array.isArray(p.equations)) {
        return NextResponse.json(
          { error: `paper ${p.paper_id}: equations must be an array` },
          { status: 400 }
        );
      }
      if (p.equations.length > MAX_EQUATIONS_PER_PAPER) {
        return NextResponse.json(
          { error: `paper ${p.paper_id}: too many equations (max ${MAX_EQUATIONS_PER_PAPER})` },
          { status: 400 }
        );
      }
      for (const e of p.equations) {
        if (typeof e.latex !== 'string' || e.latex.length > MAX_LATEX_LENGTH) {
          return NextResponse.json(
            { error: `paper ${p.paper_id}: each equation.latex must be a string (<=${MAX_LATEX_LENGTH} chars)` },
            { status: 400 }
          );
        }
        if (typeof e.position !== 'number' || !Number.isFinite(e.position)) {
          return NextResponse.json(
            { error: `paper ${p.paper_id}: each equation.position must be a number` },
            { status: 400 }
          );
        }
        if (typeof e.sympy_parsed !== 'boolean') {
          return NextResponse.json(
            { error: `paper ${p.paper_id}: each equation.sympy_parsed must be boolean` },
            { status: 400 }
          );
        }
        if (e.normalized_form !== null && e.normalized_form !== undefined) {
          if (typeof e.normalized_form !== 'string' || e.normalized_form.length > MAX_NORMALIZED_LENGTH) {
            return NextResponse.json(
              {
                error: `paper ${p.paper_id}: normalized_form must be a string (<=${MAX_NORMALIZED_LENGTH} chars) or null`,
              },
              { status: 400 }
            );
          }
        }
        if (e.structure_hash !== null && e.structure_hash !== undefined) {
          if (typeof e.structure_hash !== 'string' || e.structure_hash.length > 128) {
            return NextResponse.json(
              { error: `paper ${p.paper_id}: structure_hash must be a string (<=128 chars) or null` },
              { status: 400 }
            );
          }
        }
      }
    }
  }

  // Verify all paper_ids actually exist in our papers table.
  // One query for all of them.
  const existing = await query<{ id: number }>(
    `SELECT id FROM papers WHERE id = ANY($1::int[])`,
    [Array.from(paperIds)]
  );
  const existingSet = new Set(existing.rows.map((r) => r.id));
  const missing = Array.from(paperIds).filter((id) => !existingSet.has(id));
  if (missing.length > 0) {
    return NextResponse.json(
      { error: `unknown paper_ids: ${missing.slice(0, 10).join(', ')}` },
      { status: 400 }
    );
  }

  // Process each paper. We do this serially rather than in one big transaction
  // because failures on one paper shouldn't lose work on the others.
  const stored: { paper_id: number; equations_inserted: number; skipped: number }[] = [];

  for (const p of body.papers) {
    let inserted = 0;
    let skipped = 0;

    if (!p.source_available || !p.equations || p.equations.length === 0) {
      // Sentinel row: mark this paper as "pipeline tried, no equations"
      try {
        const r = await query<{ id: number }>(
          `
          INSERT INTO equations
            (paper_id, latex, source_env, position, sympy_parsed, equation_type,
             submitted_by_user_id)
          VALUES ($1, '', 'none', -1, FALSE, 'none', $2)
          ON CONFLICT DO NOTHING
          RETURNING id
          `,
          [p.paper_id, user.id]
        );
        if (r.rowCount && r.rowCount > 0) inserted++;
        else skipped++;
      } catch (e: any) {
        // Duplicate sentinel — safe to ignore
        skipped++;
      }
      stored.push({ paper_id: p.paper_id, equations_inserted: inserted, skipped });
      continue;
    }

    // Real equations. Insert one at a time so partial failures don't lose everything.
    for (const eq of p.equations) {
      try {
        const r = await query(
          `
          INSERT INTO equations
            (paper_id, latex, source_env, position, sympy_parsed,
             normalized_form, structure_hash, equation_type, submitted_by_user_id)
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
          `,
          [
            p.paper_id,
            sanitize(eq.latex),
            eq.source_env ?? 'unknown',
            eq.position,
            eq.sympy_parsed,
            sanitize(eq.normalized_form ?? null),
            eq.structure_hash ?? null,
            eq.equation_type ?? null,
            user.id,
          ]
        );
        if (r.rowCount && r.rowCount > 0) inserted++;
        else skipped++;
      } catch (err: any) {
        // Likely a unique constraint collision with an existing row for the
        // same paper_id + position. Count as skip, keep going.
        skipped++;
      }
    }

    stored.push({ paper_id: p.paper_id, equations_inserted: inserted, skipped });
  }

  // Update contributor stats: count the paper as a submission regardless of
  // how many equations it produced, so the number is "papers processed" not
  // "equations stored."
  await query(
    `UPDATE contributors
       SET submissions_count = submissions_count + $2,
           last_seen_at = NOW()
     WHERE user_id = $1`,
    [user.id, body.papers.length]
  );

  return NextResponse.json({
    success: true,
    stored,
    total_equations_inserted: stored.reduce((a, r) => a + r.equations_inserted, 0),
    total_skipped: stored.reduce((a, r) => a + r.skipped, 0),
  });
}

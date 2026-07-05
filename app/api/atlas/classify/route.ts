/**
 * POST /api/atlas/classify
 *
 * A Claude Code atlas-classifier session submits its classifications: for each
 * paper, 0-2 template assignments (each with confidence + twist), or an empty
 * list meaning "no canonical structure fits" (recorded as a NULL-template
 * sentinel so the paper is not re-classified).
 *
 * Auth: GitHub session or CLI bearer token.
 * Rate limit: shares the pipeline limiter.
 *
 * Body:
 *   {
 *     model: string,                 // classifier model id, for provenance
 *     classifications: [
 *       {
 *         paper_id: number,
 *         assignments: [
 *           { template_id: string, confidence: number, twist?: string }
 *         ]                           // may be empty -> "no fit"
 *       }, ...
 *     ]
 *   }
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

const MAX_PAPERS = 50;
const MAX_ASSIGNMENTS = 2;
const MAX_TWIST = 500;
// Strip NUL bytes that break Postgres TEXT (same guard as submit-extractions).
const NULL_BYTE = new RegExp(String.fromCharCode(0), 'g');

interface Assignment {
  template_id: string;
  confidence?: number;
  twist?: string | null;
}
interface ClassificationIn {
  paper_id: number;
  assignments: Assignment[];
}
interface Body {
  model?: string;
  classifications: ClassificationIn[];
}

function sanitize(s: string | null | undefined): string | null {
  if (s === null || s === undefined) return null;
  return s.replace(NULL_BYTE, '').slice(0, MAX_TWIST);
}

export async function POST(request: NextRequest) {
  const auth = await requireUser(request);
  if (auth instanceof NextResponse) return auth;
  const { user } = auth;

  const limited = await rateLimit('pipelineSubmit', `user:${user.id}`);
  if (limited) return limited;

  let body: Body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON' }, { status: 400 });
  }

  if (!Array.isArray(body?.classifications) || body.classifications.length === 0) {
    return NextResponse.json({ error: 'required: classifications (non-empty array)' }, { status: 400 });
  }
  if (body.classifications.length > MAX_PAPERS) {
    return NextResponse.json({ error: `too many papers (max ${MAX_PAPERS})` }, { status: 400 });
  }

  const model = sanitize(body.model) || 'unknown';

  const paperIds = new Set<number>();
  for (const c of body.classifications) {
    if (typeof c.paper_id !== 'number' || !Number.isFinite(c.paper_id)) {
      return NextResponse.json({ error: 'each classification needs a numeric paper_id' }, { status: 400 });
    }
    if (paperIds.has(c.paper_id)) {
      return NextResponse.json({ error: `duplicate paper_id ${c.paper_id}` }, { status: 400 });
    }
    paperIds.add(c.paper_id);
    if (!Array.isArray(c.assignments)) {
      return NextResponse.json({ error: `paper ${c.paper_id}: assignments must be an array` }, { status: 400 });
    }
    if (c.assignments.length > MAX_ASSIGNMENTS) {
      return NextResponse.json({ error: `paper ${c.paper_id}: too many assignments (max ${MAX_ASSIGNMENTS})` }, { status: 400 });
    }
    for (const a of c.assignments) {
      if (typeof a.template_id !== 'string' || !a.template_id) {
        return NextResponse.json({ error: `paper ${c.paper_id}: each assignment needs template_id` }, { status: 400 });
      }
    }
  }

  const [papersExist, validTemplates] = await Promise.all([
    query<{ id: number }>(`SELECT id FROM papers WHERE id = ANY($1::int[])`, [Array.from(paperIds)]),
    query<{ template_id: string }>(`SELECT template_id FROM atlas_templates`),
  ]);
  const paperSet = new Set(papersExist.rows.map((r) => r.id));
  const templateSet = new Set(validTemplates.rows.map((r) => r.template_id));
  const missingPapers = Array.from(paperIds).filter((id) => !paperSet.has(id));
  if (missingPapers.length > 0) {
    return NextResponse.json({ error: `unknown paper_ids: ${missingPapers.slice(0, 10).join(', ')}` }, { status: 400 });
  }

  let inserted = 0;
  let skipped = 0;
  let noFit = 0;
  const rejectedTemplates = new Set<string>();

  for (const c of body.classifications) {
    const valid = c.assignments.filter((a) => {
      if (!templateSet.has(a.template_id)) {
        rejectedTemplates.add(a.template_id);
        return false;
      }
      return true;
    });

    if (valid.length === 0) {
      try {
        const r = await query(
          `INSERT INTO atlas_classifications (paper_id, template_id, model, submitted_by_user_id)
           VALUES ($1, NULL, $2, $3) ON CONFLICT DO NOTHING`,
          [c.paper_id, model, user.id]
        );
        if (r.rowCount && r.rowCount > 0) { inserted++; noFit++; } else skipped++;
      } catch { skipped++; }
      continue;
    }

    for (const a of valid) {
      const conf =
        typeof a.confidence === 'number' && Number.isFinite(a.confidence)
          ? Math.max(0, Math.min(1, a.confidence))
          : null;
      try {
        const r = await query(
          `INSERT INTO atlas_classifications
             (paper_id, template_id, confidence, twist, model, submitted_by_user_id)
           VALUES ($1,$2,$3,$4,$5,$6)
           ON CONFLICT (paper_id, template_id) DO NOTHING`,
          [c.paper_id, a.template_id, conf, sanitize(a.twist), model, user.id]
        );
        if (r.rowCount && r.rowCount > 0) inserted++;
        else skipped++;
      } catch { skipped++; }
    }
  }

  await query(
    `UPDATE contributors
        SET submissions_count = submissions_count + $2, last_seen_at = NOW()
      WHERE user_id = $1`,
    [user.id, body.classifications.length]
  );

  return NextResponse.json({
    success: true,
    inserted,
    skipped,
    no_fit: noFit,
    rejected_template_ids: Array.from(rejectedTemplates),
  });
}

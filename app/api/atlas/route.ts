/**
 * GET /api/atlas
 *
 * The atlas: papers grouped by the canonical mathematical structure their core
 * model instantiates. Each group collects papers from potentially different
 * fields — groups spanning >= 2 domains are the cross-domain bridges the
 * project exists to surface.
 *
 * Grouping is by equivalence-class key (atlas_equivalences.group_key), so
 * split-but-equivalent templates (black_scholes_pde / heat_diffusion_equation)
 * collapse into one structure. Trivia-flagged groups are excluded.
 *
 * Returns groups sorted cross-domain-first, then by field breadth, then count.
 */

import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export const dynamic = 'force-dynamic';

interface Row {
  group_key: string;
  template_name: string;
  canonical_form: string | null;
  paper_id: number;
  paper_title: string | null;
  domain: string | null;
  arxiv_id: string | null;
  url: string | null;
  confidence: number | null;
  twist: string | null;
}

export async function GET() {
  // One query: active classifications joined to their equivalence group's
  // representative template, papers, excluding trivia groups.
  const result = await query<Row>(`
    SELECT
      COALESCE(eq.group_key, c.template_id)      AS group_key,
      rep.name                                    AS template_name,
      rep.canonical_form                          AS canonical_form,
      p.id                                        AS paper_id,
      p.title                                     AS paper_title,
      p.domain                                    AS domain,
      p.arxiv_id                                  AS arxiv_id,
      p.url                                       AS url,
      c.confidence                                AS confidence,
      c.twist                                     AS twist
    FROM atlas_classifications c
    JOIN papers p               ON c.paper_id = p.id
    LEFT JOIN atlas_equivalences eq ON c.template_id = eq.template_id
    JOIN atlas_templates rep    ON rep.template_id = COALESCE(eq.group_key, c.template_id)
    WHERE c.status = 'active'
      AND c.template_id IS NOT NULL
      AND NOT EXISTS (
        SELECT 1 FROM atlas_trivia_templates t
        WHERE t.group_key = COALESCE(eq.group_key, c.template_id)
      )
    ORDER BY group_key, c.confidence DESC NULLS LAST
  `);

  // Fold rows into structure groups.
  const groups = new Map<
    string,
    {
      group_key: string;
      name: string;
      canonical_form: string | null;
      papers: {
        paper_id: number;
        title: string | null;
        domain: string | null;
        arxiv_id: string | null;
        url: string | null;
        confidence: number | null;
        twist: string | null;
        archive: string;
      }[];
      archives: Set<string>;
    }
  >();

  for (const r of result.rows) {
    let g = groups.get(r.group_key);
    if (!g) {
      g = {
        group_key: r.group_key,
        name: r.template_name,
        canonical_form: r.canonical_form,
        papers: [],
        archives: new Set(),
      };
      groups.set(r.group_key, g);
    }
    const archive = (r.domain || '').split('.')[0] || 'unknown';
    g.papers.push({
      paper_id: r.paper_id,
      title: r.paper_title,
      domain: r.domain,
      arxiv_id: r.arxiv_id,
      url: r.url,
      confidence: r.confidence,
      twist: r.twist,
      archive,
    });
    g.archives.add(archive);
  }

  const structures = Array.from(groups.values())
    .map((g) => ({
      group_key: g.group_key,
      name: g.name,
      canonical_form: g.canonical_form,
      n_papers: g.papers.length,
      archives: Array.from(g.archives).sort(),
      n_archives: g.archives.size,
      cross_domain: g.archives.size >= 2,
      papers: g.papers,
    }))
    .sort(
      (a, b) =>
        Number(b.cross_domain) - Number(a.cross_domain) ||
        b.n_archives - a.n_archives ||
        b.n_papers - a.n_papers
    );

  return NextResponse.json({
    data: structures,
    summary: {
      structures: structures.length,
      cross_domain: structures.filter((s) => s.cross_domain).length,
      papers_classified: new Set(result.rows.map((r) => r.paper_id)).size,
    },
  });
}

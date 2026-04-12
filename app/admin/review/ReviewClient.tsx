'use client';

import { useCallback, useEffect, useState } from 'react';

type Match = {
  id: number;
  tier: string;
  p1: PaperSide;
  p2: PaperSide;
  normalized_form: string;
  hash_frequency: { equations: number; papers: number; domains: number };
};

type PaperSide = {
  domain: string;
  title: string;
  arxiv_id: string;
  url: string;
  latex: string;
  equation_type: string;
};

const REJECT_REASONS: { value: string; label: string }[] = [
  { value: 'not_cross_domain', label: 'Not cross-domain (same field)' },
  { value: 'parser_error', label: 'Parser error (SymPy mis-parsed)' },
  { value: 'superficial_match', label: 'Superficial (same form, different meaning)' },
  { value: 'trivial_form', label: 'Trivial form (too generic to be a discovery)' },
  {
    value: 'standard_canonical_object',
    label: 'Standard canonical object (textbook — adds hash to trivia list)',
  },
  { value: 'duplicate', label: 'Duplicate of another match' },
  { value: 'other', label: 'Other (see note)' },
];

export default function ReviewClient() {
  const [match, setMatch] = useState<Match | null>(null);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [skip, setSkip] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'idle' | 'promote' | 'reject'>('idle');
  const [promoteTarget, setPromoteTarget] = useState<'tier_2' | 'tier_3' | 'tier_4'>('tier_2');
  const [note, setNote] = useState<string>('');
  const [rejectReason, setRejectReason] = useState<string>('parser_error');
  const [submitting, setSubmitting] = useState<boolean>(false);

  const fetchNext = useCallback(async (offset: number) => {
    setLoading(true);
    setError(null);
    setMode('idle');
    setNote('');
    try {
      const res = await fetch(`/api/admin/matches/next?skip=${offset}`, {
        cache: 'no-store',
      });
      const json = await res.json();
      if (json.done) {
        setMatch(null);
        setPendingCount(0);
      } else {
        setMatch(json.match);
        setPendingCount(json.pending_count);
      }
    } catch (e: any) {
      setError(e?.message ?? 'failed to load');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNext(skip);
  }, [fetchNext, skip]);

  async function submitAction(body: any) {
    if (!match) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch(`/api/admin/matches/${match.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!res.ok) {
        setError(json.error ?? 'action failed');
        setSubmitting(false);
        return;
      }
      // Successfully acted — fetch the next candidate at the same skip index
      // (since this one is no longer 'candidate' status, it drops out of the query).
      setSubmitting(false);
      fetchNext(skip);
    } catch (e: any) {
      setError(e?.message ?? 'request failed');
      setSubmitting(false);
    }
  }

  function handlePromote() {
    if (note.trim().length < 10) {
      setError('note required: at least 10 characters explaining why');
      return;
    }
    submitAction({
      action:
        promoteTarget === 'tier_2'
          ? 'promote_tier_2'
          : promoteTarget === 'tier_3'
          ? 'promote_tier_3'
          : 'promote_tier_4',
      note: note.trim(),
    });
  }

  function handleReject() {
    submitAction({
      action: 'reject',
      reason: rejectReason,
      note: note.trim() || undefined,
    });
  }

  function handleSkip() {
    setSkip(skip + 1);
  }

  if (loading) {
    return <p className="text-black/50 text-sm py-4">loading...</p>;
  }

  if (error && !match) {
    return <p className="text-black/70 text-sm py-4">error: {error}</p>;
  }

  if (!match) {
    return (
      <div className="py-8">
        <p className="text-black/70 mb-2">No pending candidates.</p>
        <p className="text-sm text-black/50">
          Come back when the pipeline surfaces more matches, or run it manually.
        </p>
      </div>
    );
  }

  const { p1, p2, hash_frequency } = match;

  return (
    <div>
      <div className="flex items-baseline justify-between mb-4 text-sm">
        <span className="font-mono">Match #{match.id}</span>
        <span className="text-black/50">
          {pendingCount} pending
        </span>
      </div>

      <div className="border border-black/20 p-5 mb-6">
        <div className="grid md:grid-cols-2 gap-6">
          <PaperColumn {...p1} />
          <PaperColumn {...p2} />
        </div>
        <div className="mt-4 pt-4 border-t border-black/10 text-sm text-black/70 space-y-1">
          <div>
            <span className="font-mono text-xs">hash frequency:</span>{' '}
            {hash_frequency.equations} equations in {hash_frequency.papers} papers
            across {hash_frequency.domains} domains
          </div>
          <div>
            <span className="font-mono text-xs">normalized form:</span>
            <pre className="mt-1 font-mono text-xs whitespace-pre-wrap break-words bg-black/[0.03] p-2">
              {match.normalized_form}
            </pre>
          </div>
        </div>
      </div>

      {mode === 'idle' && (
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setMode('promote')}
            className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors"
          >
            promote
          </button>
          <button
            onClick={() => setMode('reject')}
            className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors"
          >
            reject
          </button>
          <button
            onClick={handleSkip}
            className="border border-black/20 px-4 py-2 text-sm hover:border-black transition-colors"
          >
            skip
          </button>
        </div>
      )}

      {mode === 'promote' && (
        <div className="border border-black/20 p-4">
          <h3 className="mb-3">Promote</h3>
          <div className="space-y-2 mb-4 text-sm">
            {(['tier_2', 'tier_3', 'tier_4'] as const).map((t) => (
              <label key={t} className="flex items-start gap-2">
                <input
                  type="radio"
                  checked={promoteTarget === t}
                  onChange={() => setPromoteTarget(t)}
                />
                <span>
                  <span className="font-mono">{t}</span>
                  {t === 'tier_2' && ' — same structural form, not just syntactic'}
                  {t === 'tier_3' && ' — plausible bidirectional method or theory transfer'}
                  {t === 'tier_4' && ' — expert-validated actionable hypothesis'}
                </span>
              </label>
            ))}
          </div>
          <label className="block text-sm mb-1">
            Note (required, 10-2000 chars — explain why this is more than syntactic)
          </label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={4}
            className="w-full border border-black/20 p-2 font-mono text-xs mb-3"
          />
          <div className="flex gap-3">
            <button
              disabled={submitting}
              onClick={handlePromote}
              className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors disabled:opacity-50"
            >
              {submitting ? 'submitting...' : 'confirm promote'}
            </button>
            <button
              disabled={submitting}
              onClick={() => {
                setMode('idle');
                setNote('');
              }}
              className="border border-black/20 px-4 py-2 text-sm hover:border-black transition-colors"
            >
              cancel
            </button>
          </div>
          {error && <p className="text-sm text-black/70 mt-2">error: {error}</p>}
        </div>
      )}

      {mode === 'reject' && (
        <div className="border border-black/20 p-4">
          <h3 className="mb-3">Reject</h3>
          <label className="block text-sm mb-1">Reason</label>
          <select
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            className="w-full border border-black/20 p-2 text-sm mb-3"
          >
            {REJECT_REASONS.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
          <label className="block text-sm mb-1">Note (optional)</label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={3}
            className="w-full border border-black/20 p-2 font-mono text-xs mb-3"
          />
          <div className="flex gap-3">
            <button
              disabled={submitting}
              onClick={handleReject}
              className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors disabled:opacity-50"
            >
              {submitting ? 'submitting...' : 'confirm reject'}
            </button>
            <button
              disabled={submitting}
              onClick={() => {
                setMode('idle');
                setNote('');
              }}
              className="border border-black/20 px-4 py-2 text-sm hover:border-black transition-colors"
            >
              cancel
            </button>
          </div>
          {error && <p className="text-sm text-black/70 mt-2">error: {error}</p>}
        </div>
      )}
    </div>
  );
}

function PaperColumn({
  domain,
  title,
  arxiv_id,
  url,
  latex,
  equation_type,
}: PaperSide) {
  return (
    <div>
      <div className="font-mono text-xs text-black/50 mb-1">
        {domain} · {equation_type}
      </div>
      <p className="text-sm mb-1">{title}</p>
      {url && (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono text-xs text-black/60"
        >
          {arxiv_id} ↗
        </a>
      )}
      <pre className="mt-2 font-mono text-xs whitespace-pre-wrap break-words text-black/80 bg-black/[0.03] p-2">
        {latex}
      </pre>
    </div>
  );
}

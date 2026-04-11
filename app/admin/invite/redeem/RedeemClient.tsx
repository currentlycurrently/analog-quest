'use client';

import { useState } from 'react';

export default function RedeemClient({ token }: { token: string }) {
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);

  async function redeem() {
    setStatus('submitting');
    setError(null);
    try {
      const res = await fetch('/api/admin/invites/redeem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      const json = await res.json();
      if (!res.ok) {
        setError(json.error ?? 'redeem failed');
        setStatus('error');
      } else {
        setStatus('success');
      }
    } catch (e: any) {
      setError(e?.message ?? 'request failed');
      setStatus('error');
    }
  }

  if (status === 'success') {
    return (
      <div>
        <p className="mb-4">You&apos;re a moderator now.</p>
        <p className="text-sm text-black/70 mb-6">
          You may need to sign out and back in for the role change to take
          effect in your current session.
        </p>
        <a
          href="/admin/review"
          className="border border-black px-4 py-2 text-sm no-underline hover:bg-black hover:text-white transition-colors"
        >
          go to review queue
        </a>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={redeem}
        disabled={status === 'submitting'}
        className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors disabled:opacity-50"
      >
        {status === 'submitting' ? 'redeeming...' : 'accept invite'}
      </button>
      {error && <p className="text-sm text-black/70 mt-3">error: {error}</p>}
    </div>
  );
}

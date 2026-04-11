'use client';

import { useCallback, useEffect, useState } from 'react';

type Invite = {
  id: number;
  token: string;
  created_at: string;
  expires_at: string;
  redeemed_at: string | null;
  redeemed_by_login: string | null;
  note: string | null;
};

export default function ModeratorsClient() {
  const [invites, setInvites] = useState<Invite[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [note, setNote] = useState<string>('');
  const [expiryDays, setExpiryDays] = useState<number>(14);
  const [creating, setCreating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [latestUrl, setLatestUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const fetchInvites = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/invites', { cache: 'no-store' });
      const json = await res.json();
      if (res.ok) setInvites(json.invites ?? []);
      else setError(json.error ?? 'failed to load');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInvites();
  }, [fetchInvites]);

  async function create() {
    setCreating(true);
    setError(null);
    setLatestUrl(null);
    try {
      const res = await fetch('/api/admin/invites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          note: note.trim() || undefined,
          expires_in_days: expiryDays,
        }),
      });
      const json = await res.json();
      if (!res.ok) {
        setError(json.error ?? 'create failed');
      } else {
        setLatestUrl(json.url);
        setNote('');
        fetchInvites();
      }
    } finally {
      setCreating(false);
    }
  }

  function copy(url: string) {
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div>
      {/* Create form */}
      <div className="border border-black/20 p-5 mb-8">
        <h2 className="mb-3">New invite</h2>
        <label className="block text-sm mb-1">Note (optional — who is this for?)</label>
        <input
          type="text"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className="w-full border border-black/20 p-2 text-sm mb-3"
          placeholder="e.g., jane@university — dynamical systems group"
        />
        <label className="block text-sm mb-1">Expires in (days)</label>
        <input
          type="number"
          value={expiryDays}
          onChange={(e) => setExpiryDays(parseInt(e.target.value, 10) || 14)}
          min={1}
          max={90}
          className="w-24 border border-black/20 p-2 text-sm mb-3"
        />
        <div>
          <button
            onClick={create}
            disabled={creating}
            className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors disabled:opacity-50"
          >
            {creating ? 'creating...' : 'create invite'}
          </button>
        </div>
        {error && <p className="text-sm text-black/70 mt-3">error: {error}</p>}
        {latestUrl && (
          <div className="mt-4 p-3 border border-black/20 bg-black/[0.03]">
            <p className="text-sm mb-2">Share this URL with the invitee:</p>
            <code className="block font-mono text-xs break-all mb-2">{latestUrl}</code>
            <button
              onClick={() => copy(latestUrl)}
              className="border border-black/40 px-3 py-1 text-xs hover:bg-black hover:text-white transition-colors"
            >
              {copied ? 'copied' : 'copy'}
            </button>
          </div>
        )}
      </div>

      {/* Existing invites */}
      <h2 className="mb-3">Existing invites</h2>
      {loading ? (
        <p className="text-black/50 text-sm">loading...</p>
      ) : invites.length === 0 ? (
        <p className="text-black/50 text-sm">none yet</p>
      ) : (
        <div className="space-y-3">
          {invites.map((inv) => {
            const redeemed = inv.redeemed_at !== null;
            const expired = new Date(inv.expires_at) < new Date();
            const status = redeemed ? 'redeemed' : expired ? 'expired' : 'active';
            return (
              <div
                key={inv.id}
                className={`border p-3 text-sm ${
                  status === 'active' ? 'border-black/20' : 'border-black/10 text-black/50'
                }`}
              >
                <div className="flex items-baseline justify-between mb-1">
                  <span className="font-mono text-xs">invite #{inv.id}</span>
                  <span className="text-xs">{status}</span>
                </div>
                {inv.note && <div className="text-sm mb-1">{inv.note}</div>}
                <div className="font-mono text-xs">
                  {redeemed
                    ? `redeemed by @${inv.redeemed_by_login} on ${new Date(inv.redeemed_at!).toLocaleString()}`
                    : `expires ${new Date(inv.expires_at).toLocaleString()}`}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

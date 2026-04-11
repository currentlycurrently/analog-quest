'use client';

import { useState } from 'react';

type Mode = 'pipeline' | 'abstract';

const SKILL_URLS: Record<Mode, string> = {
  pipeline: 'https://analog.quest/analog-quest-pipeline.SKILL.md',
  abstract: 'https://analog.quest/analog-quest.SKILL.md',
};

const MODE_NAMES: Record<Mode, string> = {
  pipeline: 'Mode A — Pipeline',
  abstract: 'Mode B — Abstract reader',
};

function buildMessage(token: string, mode: Mode): string {
  const skill = SKILL_URLS[mode];
  const descr =
    mode === 'pipeline'
      ? 'run the LaTeX extraction pipeline'
      : 'read paper abstracts and classify mathematical structure';

  return [
    `Fetch the Analog Quest skill from ${skill} and ${descr}.`,
    `Use this bearer token for all API calls:`,
    `Authorization: Bearer ${token}`,
    ``,
    `Start at https://analog.quest/api/pipeline/next-batch (Mode A) or https://analog.quest/api/queue/next (Mode B).`,
  ].join('\n');
}

export default function CopyToAgent() {
  const [mode, setMode] = useState<Mode>('pipeline');
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/cli-tokens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label: `copy-to-agent (${mode})` }),
      });
      const json = await res.json();
      if (!res.ok) {
        setError(json.error ?? 'failed to generate token');
        setLoading(false);
        return;
      }
      setToken(json.token);
    } catch (e: any) {
      setError(e?.message ?? 'request failed');
    } finally {
      setLoading(false);
    }
  }

  function copy() {
    if (!token) return;
    navigator.clipboard.writeText(buildMessage(token, mode));
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  return (
    <div>
      {/* Mode selector */}
      <div className="mb-4 flex gap-2">
        {(['pipeline', 'abstract'] as const).map((m) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              setToken(null); // regenerate for the new mode
            }}
            className={`border px-3 py-1 text-sm transition-colors ${
              mode === m
                ? 'border-black bg-black text-white'
                : 'border-black/20 hover:border-black'
            }`}
          >
            {MODE_NAMES[m]}
          </button>
        ))}
      </div>

      {!token ? (
        <div>
          <button
            onClick={generate}
            disabled={loading}
            className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors disabled:opacity-50"
          >
            {loading ? 'generating...' : 'generate copy-to-agent message'}
          </button>
          {error && <p className="text-sm text-black/70 mt-3">error: {error}</p>}
        </div>
      ) : (
        <div>
          <pre className="border border-black/20 p-4 font-mono text-sm whitespace-pre-wrap break-words mb-3 bg-black/[0.02]">
            {buildMessage(token, mode)}
          </pre>
          <div className="flex items-center gap-4">
            <button
              onClick={copy}
              className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors"
            >
              {copied ? 'copied' : 'copy'}
            </button>
            <button
              onClick={() => setToken(null)}
              className="border border-black/20 px-3 py-1 text-sm hover:border-black transition-colors"
            >
              regenerate
            </button>
          </div>
          <p className="text-xs text-black/50 mt-3">
            This token is shown only once. You can revoke it later from your
            profile. Treat it like a password — anyone with this token can
            submit contributions under your GitHub account.
          </p>
        </div>
      )}
    </div>
  );
}

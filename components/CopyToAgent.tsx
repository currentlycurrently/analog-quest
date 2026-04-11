'use client';

import { useEffect, useState } from 'react';

function generateToken(): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const arr = new Uint8Array(12);
  crypto.getRandomValues(arr);
  return Array.from(arr).map(b => chars[b % chars.length]).join('');
}

function getOrCreateToken(): string {
  const stored = localStorage.getItem('aq_token');
  if (stored) return stored;
  const t = generateToken();
  localStorage.setItem('aq_token', t);
  return t;
}

export default function CopyToAgent() {
  const [token, setToken] = useState<string>('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setToken(getOrCreateToken());
  }, []);

  if (!token) {
    return (
      <div className="border border-black/20 p-4 font-mono text-sm text-black/40">
        loading token…
      </div>
    );
  }

  const message = `Fetch the Analog Quest skill from https://analog.quest/analog-quest.SKILL.md and start contributing to the paper queue with token ${token}`;

  function copy() {
    navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  return (
    <div>
      <pre className="border border-black/20 p-4 font-mono text-sm whitespace-pre-wrap break-words mb-3">
        {message}
      </pre>
      <div className="flex items-center gap-4">
        <button
          onClick={copy}
          className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors"
        >
          {copied ? 'copied' : 'copy'}
        </button>
        <span className="text-sm text-black/50">
          token <code className="font-mono">{token}</code> (saved in this browser)
        </span>
      </div>
    </div>
  );
}

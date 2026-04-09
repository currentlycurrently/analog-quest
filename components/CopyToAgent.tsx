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

  if (!token) return null;

  const message = `Fetch the Analog Quest skill from https://analog.quest/analog-quest.SKILL.md and start contributing to the paper queue with token ${token}`;

  function copy() {
    navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  return (
    <div className="bg-teal p-6">
      <p className="font-mono text-xs text-brown/60 mb-4">PASTE THIS INTO ANY CLAUDE CODE SESSION</p>
      <div className="bg-cream/60 p-4 font-mono text-sm text-brown mb-4 leading-relaxed break-all">
        {message}
      </div>
      <button
        onClick={copy}
        className="font-mono text-xs bg-brown-dark text-cream px-6 py-2 hover:bg-brown transition-colors"
      >
        {copied ? 'copied!' : 'copy to clipboard'}
      </button>
      <p className="text-brown/50 text-xs mt-3">
        Your token <code className="font-mono bg-cream/50 px-1">{token}</code> is saved in this browser.
      </p>
    </div>
  );
}

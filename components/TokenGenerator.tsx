'use client';

import { useEffect, useState } from 'react';

function generateToken(): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const arr = new Uint8Array(12);
  crypto.getRandomValues(arr);
  return Array.from(arr).map(b => chars[b % chars.length]).join('');
}

export default function TokenGenerator() {
  const [token, setToken] = useState<string>('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('aq_token');
    if (stored) {
      setToken(stored);
    } else {
      const t = generateToken();
      localStorage.setItem('aq_token', t);
      setToken(t);
    }
  }, []);

  function copy() {
    navigator.clipboard.writeText(token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function regenerate() {
    const t = generateToken();
    localStorage.setItem('aq_token', t);
    setToken(t);
    setCopied(false);
  }

  if (!token) return null;

  return (
    <div className="bg-teal p-6">
      <p className="font-mono text-xs text-brown/60 mb-3">YOUR CONTRIBUTOR TOKEN</p>
      <div className="flex items-center gap-3">
        <code className="font-mono text-lg text-brown-dark tracking-widest flex-1">{token}</code>
        <button
          onClick={copy}
          className="font-mono text-xs bg-brown-dark text-cream px-4 py-2 hover:bg-brown transition-colors flex-shrink-0"
        >
          {copied ? 'copied!' : 'copy'}
        </button>
      </div>
      <p className="text-brown/60 text-sm mt-3">
        Saved in your browser. Same token every time you visit — paste it into{' '}
        <code className="font-mono text-xs bg-cream/50 px-1">ANALOG_QUEST.md</code> where it says{' '}
        <code className="font-mono text-xs bg-cream/50 px-1">YOUR_TOKEN_HERE</code>.{' '}
        <button onClick={regenerate} className="underline hover:no-underline">
          generate a new one
        </button>
      </p>
    </div>
  );
}

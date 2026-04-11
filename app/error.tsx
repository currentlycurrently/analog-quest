'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="max-w-3xl mx-auto px-6 py-24">
      <h1 className="mb-4">Something went wrong</h1>
      <p className="mb-8 text-black/70">
        {error.message || 'An unexpected error occurred.'}
      </p>
      <div className="flex gap-3">
        <button
          onClick={reset}
          className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors"
        >
          try again
        </button>
        <Link
          href="/"
          className="border border-black/20 px-4 py-2 text-sm no-underline hover:border-black transition-colors"
        >
          go home
        </Link>
      </div>
    </div>
  );
}

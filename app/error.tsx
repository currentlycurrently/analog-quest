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
    <div className="bg-cream min-h-screen flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <h2 className="text-3xl font-serif text-brown-dark mb-4">
          Something went wrong
        </h2>
        <p className="text-brown/70 mb-8">
          {error.message || 'An unexpected error occurred while loading the page.'}
        </p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={reset}
            className="bg-brown text-cream px-6 py-2 font-mono text-sm hover:bg-brown-dark transition-colors"
          >
            Try again
          </button>
          <Link
            href="/"
            className="border border-brown/20 text-brown px-6 py-2 font-mono text-sm hover:border-brown/40 transition-colors"
          >
            Go home
          </Link>
        </div>
      </div>
    </div>
  );
}
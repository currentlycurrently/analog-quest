import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-24">
      <h1 className="mb-4">404</h1>
      <p className="mb-8 text-black/70">This page doesn&apos;t exist.</p>
      <div className="flex gap-3">
        <Link
          href="/"
          className="border border-black px-4 py-2 text-sm no-underline hover:bg-black hover:text-white transition-colors"
        >
          go home
        </Link>
        <Link
          href="/discoveries"
          className="border border-black/20 px-4 py-2 text-sm no-underline hover:border-black transition-colors"
        >
          discoveries
        </Link>
      </div>
    </div>
  );
}

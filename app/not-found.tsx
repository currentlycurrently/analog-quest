import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="bg-cream min-h-screen flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-serif text-brown-dark mb-4">404</h1>
        <h2 className="text-2xl font-serif text-brown mb-6">
          Page Not Found
        </h2>
        <p className="text-brown/70 mb-8">
          The page you're looking for doesn't exist or may have been moved.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/"
            className="bg-brown text-cream px-6 py-2 font-mono text-sm hover:bg-brown-dark transition-colors"
          >
            Go home
          </Link>
          <Link
            href="/discoveries"
            className="border border-brown/20 text-brown px-6 py-2 font-mono text-sm hover:border-brown/40 transition-colors"
          >
            View discoveries
          </Link>
        </div>
      </div>
    </div>
  );
}
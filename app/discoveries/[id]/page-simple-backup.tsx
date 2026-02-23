import { notFound } from 'next/navigation';
import Link from 'next/link';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function SimpleDiscoveryPage({ params }: PageProps) {
  const resolvedParams = await params;
  const discoveryId = parseInt(resolvedParams.id);

  // For testing - just show a simple page with the ID
  if (discoveryId < 1 || discoveryId > 6) {
    notFound();
  }

  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/discoveries" className="text-brown hover:text-brown-dark">
          ← Back to discoveries
        </Link>

        <h1 className="text-4xl font-serif text-brown-dark mt-8 mb-4">
          Discovery #{discoveryId}
        </h1>

        <div className="bg-brown-dark text-cream p-4 rounded mb-4">
          <span>excellent discovery</span>
        </div>

        <p className="text-brown mb-8">
          This is a test page for discovery {discoveryId}. If you can see this, the page routing is working!
        </p>

        <div className="border border-brown/20 p-6 rounded">
          <h2 className="text-2xl font-serif text-brown mb-4">Debug Info</h2>
          <ul className="space-y-2 text-brown/80">
            <li>Discovery ID: {discoveryId}</li>
            <li>Page Type: Simple Test Page</li>
            <li>Async Params: Working</li>
            <li>Rendering: Server-side</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
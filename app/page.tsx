import Link from 'next/link';
import { fetchDiscoveries } from '@/lib/api-client';
import RebuildNotice from '@/components/RebuildNotice';
import IsomorphismCard from '@/components/IsomorphismCard';
import fs from 'fs/promises';
import path from 'path';

// Use dynamic rendering for the homepage to fetch latest data
export const dynamic = 'force-dynamic';

export default async function Home() {
  // Load the real isomorphisms
  const isomorphismsPath = path.join(process.cwd(), 'app/data/real_isomorphisms.json');
  const isomorphismsData = await fs.readFile(isomorphismsPath, 'utf-8');
  const realIsomorphisms = JSON.parse(isomorphismsData);

  // Load rebuild status
  const statusPath = path.join(process.cwd(), 'app/data/rebuild_status.json');
  const statusData = await fs.readFile(statusPath, 'utf-8');
  const rebuildStatus = JSON.parse(statusData);

  return (
    <div className="bg-cream">
      {/* Rebuild Notice */}
      <RebuildNotice status={rebuildStatus} />

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 lg:px-8 py-24">
        <div className="max-w-3xl">
          <h1 className="text-4xl md:text-5xl font-serif font-normal text-brown mb-8 leading-tight">
            Finding the deep mathematical structures that unite all of science
          </h1>
          <p className="text-lg text-brown/80 mb-12 leading-relaxed max-w-2xl">
            Analog Quest reveals when different fields are solving the <strong>exact same equation</strong>.
            Not semantic similarity. Not "both have feedback loops."
            Real mathematical isomorphisms like discovering the Black-Scholes equation IS the heat equation.
          </p>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 mb-12">
            <h3 className="font-mono text-sm font-semibold text-brown mb-2">
              FUNDAMENTAL REBUILD IN PROGRESS
            </h3>
            <p className="text-brown/80">
              After analyzing 125 "discoveries", we found <strong>0% were real mathematical isomorphisms</strong>.
              We're rebuilding from scratch to find actual structural equivalences.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/methodology"
              className="inline-block bg-brown-dark text-cream px-8 py-3 font-mono text-sm hover:bg-brown transition-colors"
            >
              new methodology
            </Link>
            <Link
              href="#real-examples"
              className="inline-block border border-brown/20 text-brown px-8 py-3 font-mono text-sm hover:border-brown/40 transition-colors"
            >
              see real isomorphisms
            </Link>
          </div>
        </div>
      </section>

      {/* What Changed Section */}
      <section className="bg-brown-dark text-cream py-16">
        <div className="max-w-5xl mx-auto px-6 lg:px-8">
          <h2 className="text-3xl font-serif font-normal mb-8">What Changed?</h2>

          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h3 className="font-mono text-sm mb-4 text-yellow-300">OLD APPROACH (Shallow)</h3>
              <div className="bg-brown/30 p-6 rounded">
                <p className="font-mono text-sm mb-2">"This paper mentions feedback loops"</p>
                <p className="font-mono text-sm mb-2">"This other paper also mentions feedback"</p>
                <p className="font-mono text-sm text-red-300">→ "Discovery!" (worthless)</p>
              </div>
              <p className="mt-4 text-cream/80">
                Result: 125 trivial observations that anyone could make.
              </p>
            </div>

            <div>
              <h3 className="font-mono text-sm mb-4 text-green-300">NEW APPROACH (Deep)</h3>
              <div className="bg-brown/30 p-6 rounded">
                <p className="font-mono text-sm mb-2">dx/dt = ax - bxy</p>
                <p className="font-mono text-sm mb-2">d[A]/dt = k₁[A] - k₂[A][B]</p>
                <p className="font-mono text-sm text-green-300">→ Lotka-Volterra isomorphism!</p>
              </div>
              <p className="mt-4 text-cream/80">
                Result: Real mathematical equivalences that enable cross-domain method transfer.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Real Isomorphisms Section */}
      <section id="real-examples" className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
        <div className="mb-16">
          <h2 className="text-3xl font-serif font-normal text-brown mb-4">
            Verified Mathematical Isomorphisms
          </h2>
          <p className="text-brown/70 max-w-2xl">
            These are the only {realIsomorphisms.length} verified isomorphisms from our database of 5,000+ papers.
            Each represents an exact mathematical equivalence between different fields.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {realIsomorphisms.map((iso: any) => (
            <IsomorphismCard key={iso.id} isomorphism={iso} />
          ))}
        </div>

        <div className="mt-12 p-6 bg-gray-50 rounded">
          <p className="text-sm text-gray-600">
            <strong>Why only {realIsomorphisms.length}?</strong> Real isomorphisms are rare and valuable.
            Finding that two fields use the exact same mathematical structure is a potential breakthrough.
            We'd rather have {realIsomorphisms.length} real discoveries than 125 trivial observations.
          </p>
        </div>
      </section>

      {/* Timeline Section */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-5xl mx-auto px-6 lg:px-8">
          <h2 className="text-3xl font-serif font-normal text-brown mb-8">
            Rebuild Timeline
          </h2>

          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-green-500 text-white rounded-full flex items-center justify-center font-mono text-sm">✓</div>
              <div>
                <h3 className="font-semibold">Week 0: Proof of Concept</h3>
                <p className="text-gray-600">Built pattern matching for Lotka-Volterra, Heat equation detection</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-yellow-500 text-white rounded-full flex items-center justify-center font-mono text-sm">...</div>
              <div>
                <h3 className="font-semibold">Weeks 1-4: Equation Extraction</h3>
                <p className="text-gray-600">LaTeX parsing, SymPy integration, canonical forms</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-gray-300 text-white rounded-full flex items-center justify-center font-mono text-sm">5-7</div>
              <div>
                <h3 className="font-semibold">Weeks 5-7: Graph Structures</h3>
                <p className="text-gray-600">NetworkX integration, graph isomorphism detection</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-gray-300 text-white rounded-full flex items-center justify-center font-mono text-sm">8+</div>
              <div>
                <h3 className="font-semibold">Weeks 8-16: Scale & Validate</h3>
                <p className="text-gray-600">Process 1,000+ papers, find 10+ publication-worthy discoveries</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="bg-brown-dark text-cream py-16">
        <div className="max-w-3xl mx-auto px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-serif font-normal mb-6">
            This is Science, Not Pattern Matching
          </h2>
          <p className="text-lg mb-8 text-cream/80">
            We're building something that could actually advance scientific understanding.
            Follow the rebuild as we search for the deep mathematical structures that unite all fields.
          </p>
          <Link
            href="/methodology"
            className="inline-block bg-yellow-400 text-brown px-8 py-3 font-mono text-sm hover:bg-yellow-300 transition-colors"
          >
            Read the Technical Specification
          </Link>
        </div>
      </section>
    </div>
  );
}
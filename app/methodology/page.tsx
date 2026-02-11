import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Methodology',
  description:
    'Learn how Analog Quest discovers cross-domain structural isomorphisms through LLM extraction, semantic embeddings, and manual curation across 2,021 academic papers.',
};

export default function MethodologyPage() {
  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-3xl mx-auto px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="mb-16">
          <h1 className="text-4xl font-serif font-normal text-brown mb-6">
            Methodology
          </h1>
          <p className="text-lg text-brown/80 leading-relaxed">
            How Analog Quest discovers cross-domain structural isomorphisms
          </p>
        </div>

        {/* What is Analog Quest */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">
            What is Analog Quest?
          </h2>
          <p className="text-brown/90 mb-6 leading-relaxed">
            Analog Quest is an AI-assisted research project that maps{' '}
            <strong>structural isomorphisms</strong> across academic domains.
          </p>
          <p className="text-brown/90 mb-6 leading-relaxed">
            A structural isomorphism occurs when two ideas from different fields
            describe the <em>same underlying mechanism</em>, even though they use
            completely different terminology.
          </p>
          <div className="bg-teal-light/50 border-l-4 border-brown-dark p-6 my-8">
            <p className="text-sm text-brown/90 leading-relaxed">
              <strong>Example:</strong> The &quot;tragedy of the commons&quot; in
              economics and &quot;resource competition in ecology&quot; are
              structurally isomorphic: Individual agents optimize local resource
              use, creating collective degradation through competitive extraction,
              despite long-term harm to all participants.
            </p>
          </div>
        </section>

        {/* The Process */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-8">The Process</h2>

          {/* Step 1 */}
          <div className="mb-10">
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-brown-dark text-cream rounded-full flex items-center justify-center font-mono text-sm mr-4">
                1
              </div>
              <h3 className="text-xl font-serif text-brown mt-1">
                Paper Selection
              </h3>
            </div>
            <div className="ml-14">
              <p className="text-brown/90 mb-3 leading-relaxed">
                Started with <strong>2,021 academic papers</strong> from arXiv
                across 25+ domains (physics, computer science, biology, economics,
                mathematics, etc.).
              </p>
              <p className="text-brown/90 leading-relaxed">
                Used strategic keyword-based selection to identify
                mechanism-rich papers (papers likely to describe causal patterns
                rather than just methods or results).
              </p>
            </div>
          </div>

          {/* Step 2 */}
          <div className="mb-10">
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-brown-dark text-cream rounded-full flex items-center justify-center font-mono text-sm mr-4">
                2
              </div>
              <h3 className="text-xl font-serif text-brown mt-1">
                Mechanism Extraction
              </h3>
            </div>
            <div className="ml-14">
              <p className="text-brown/90 mb-3 leading-relaxed">
                Extracted <strong>54 domain-neutral mechanisms</strong> from
                selected papers using LLM-guided analysis.
              </p>
              <p className="text-brown/90 mb-3 leading-relaxed">
                <strong>Hit rate:</strong> 50% on strategically selected papers
                (vs 22.5% on random papers).
              </p>
              <p className="text-brown/90 leading-relaxed">
                Each mechanism is rewritten in <em>domain-neutral language</em> to
                strip away field-specific jargon and reveal the underlying
                structural pattern.
              </p>
            </div>
          </div>

          {/* Step 3 */}
          <div className="mb-10">
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-brown-dark text-cream rounded-full flex items-center justify-center font-mono text-sm mr-4">
                3
              </div>
              <h3 className="text-xl font-serif text-brown mt-1">
                Semantic Matching
              </h3>
            </div>
            <div className="ml-14">
              <p className="text-brown/90 mb-3 leading-relaxed">
                Generated <strong>384-dimensional semantic embeddings</strong>{' '}
                for each mechanism using sentence-transformers (all-MiniLM-L6-v2).
              </p>
              <p className="text-brown/90 mb-3 leading-relaxed">
                Computed cosine similarity between all cross-domain pairs
                (excluding same-domain matches).
              </p>
              <p className="text-brown/90 leading-relaxed">
                Identified <strong>165 candidate pairs</strong> with similarity
                ≥0.35 (relaxed threshold to capture diverse-domain matches).
              </p>
            </div>
          </div>

          {/* Step 4 */}
          <div className="mb-10">
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-brown-dark text-cream rounded-full flex items-center justify-center font-mono text-sm mr-4">
                4
              </div>
              <h3 className="text-xl font-serif text-brown mt-1">
                Manual Curation
              </h3>
            </div>
            <div className="ml-14">
              <p className="text-brown/90 mb-3 leading-relaxed">
                Manually reviewed all 165 candidates and rated each as{' '}
                <em>excellent</em>, <em>good</em>, <em>weak</em>, or{' '}
                <em>false</em>.
              </p>
              <p className="text-brown/90 mb-3 leading-relaxed">
                Selected <strong>30 verified isomorphisms</strong>: 10 excellent +
                20 good (by similarity score).
              </p>
              <p className="text-brown/90 leading-relaxed">
                Wrote structural explanations for each match, describing exactly
                how the mechanisms are isomorphic.
              </p>
            </div>
          </div>
        </section>

        {/* Quality Metrics */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">
            Quality Metrics
          </h2>
          <div className="bg-teal-light/50 border border-brown/10 rounded-lg p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-mono text-sm text-brown/70 mb-3 uppercase tracking-wide">
                  Overall Precision
                </h3>
                <p className="text-4xl font-serif text-brown-dark mb-2">24%</p>
                <p className="text-sm text-brown/80 leading-relaxed">
                  40 out of 165 candidates rated as good or excellent
                </p>
              </div>
              <div>
                <h3 className="font-mono text-sm text-brown/70 mb-3 uppercase tracking-wide">
                  Top-30 Precision
                </h3>
                <p className="text-4xl font-serif text-brown-dark mb-2">67%</p>
                <p className="text-sm text-brown/80 leading-relaxed">
                  20 out of 30 highest-similarity candidates are genuine
                </p>
              </div>
              <div>
                <h3 className="font-mono text-sm text-brown/70 mb-3 uppercase tracking-wide">
                  Similarity Range
                </h3>
                <p className="text-4xl font-serif text-brown-dark mb-2">
                  0.44 - 0.74
                </p>
                <p className="text-sm text-brown/80 leading-relaxed">
                  Mean: 0.54 (54% cosine similarity)
                </p>
              </div>
              <div>
                <h3 className="font-mono text-sm text-brown/70 mb-3 uppercase tracking-wide">
                  Top Domain Pairs
                </h3>
                <p className="text-sm text-brown/90 mb-2 leading-relaxed">
                  econ ↔ q-bio: 7 matches
                </p>
                <p className="text-sm text-brown/90 mb-2 leading-relaxed">
                  physics ↔ q-bio: 5 matches
                </p>
                <p className="text-sm text-brown/90 leading-relaxed">econ ↔ physics: 4 matches</p>
              </div>
            </div>
          </div>
        </section>

        {/* Limitations */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">Limitations</h2>
          <ul className="space-y-4 text-brown/90">
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                <strong>Small sample size:</strong> 54 mechanisms across 2,021
                papers is a limited sample. Many papers contain mechanisms that
                were not extracted.
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                <strong>Manual curation required:</strong> Semantic embeddings
                generate candidates but cannot reliably distinguish genuine
                isomorphisms from superficial similarity. Human judgment is
                essential.
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                <strong>Domain diversity paradox:</strong> More diverse domain
                pairs (e.g., econ ↔ biology) often have LOWER similarity scores
                than same-domain matches, even when the structural match is
                excellent. This means the best discoveries may have modest scores.
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                <strong>Extraction bias:</strong> Mechanisms are easier to extract
                from certain domains (ecology, economics) than others (theoretical
                physics, pure mathematics).
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                <strong>Selection criteria:</strong> Quality ratings reflect the
                author&apos;s judgment of structural similarity. Different researchers
                might rate matches differently.
              </span>
            </li>
          </ul>
        </section>

        {/* Future Work */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">Future Work</h2>
          <p className="text-brown/90 mb-6 leading-relaxed">
            This is v1 with 30 verified isomorphisms. The goal is to grow this
            to 100-400 discoveries over the next 6 months through expansion
            cycles:
          </p>
          <ul className="space-y-3 text-brown/90">
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                Extract mechanisms from under-represented domains (computer
                science, nonlinear dynamics)
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                Focus on high-precision domain pairs (cs ↔ physics: 100%, econ ↔
                physics: 58%)
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                Target high-performing mechanism types (coevolution: 63%,
                strategic interactions: 56%)
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                Improve extraction efficiency with domain-specific prompts
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                Add external validation by domain experts
              </span>
            </li>
          </ul>
        </section>

        {/* Footer */}
        <div className="border-t border-brown/20 pt-8">
          <p className="text-sm font-mono text-brown/60 text-center">
            For detailed analysis and expansion strategy, see GROWTH_STRATEGY.md in the GitHub repository
          </p>
        </div>
      </div>
    </div>
  );
}

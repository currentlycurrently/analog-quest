import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Methodology',
  description:
    'Learn how Analog Quest discovers cross-domain structural isomorphisms through LLM extraction, semantic embeddings, and manual curation across 2,021 academic papers.',
};

export default function MethodologyPage() {
  return (
    <div className="bg-white min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Methodology
          </h1>
          <p className="text-lg text-gray-600">
            How Analog Quest discovers cross-domain structural isomorphisms
          </p>
        </div>

        {/* What is Analog Quest */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            What is Analog Quest?
          </h2>
          <p className="text-gray-700 mb-4">
            Analog Quest is an AI-assisted research project that maps{' '}
            <strong>structural isomorphisms</strong> across academic domains.
          </p>
          <p className="text-gray-700 mb-4">
            A structural isomorphism occurs when two ideas from different fields
            describe the <em>same underlying mechanism</em>, even though they use
            completely different terminology.
          </p>
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 my-6">
            <p className="text-sm text-gray-700">
              <strong>Example:</strong> The &quot;tragedy of the commons&quot; in
              economics and &quot;resource competition in ecology&quot; are
              structurally isomorphic: Individual agents optimize local resource
              use, creating collective degradation through competitive extraction,
              despite long-term harm to all participants.
            </p>
          </div>
        </section>

        {/* The Process */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">The Process</h2>

          {/* Step 1 */}
          <div className="mb-8">
            <div className="flex items-start mb-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mt-0.5">
                Paper Selection
              </h3>
            </div>
            <div className="ml-11">
              <p className="text-gray-700 mb-2">
                Started with <strong>2,021 academic papers</strong> from arXiv
                across 25+ domains (physics, computer science, biology, economics,
                mathematics, etc.).
              </p>
              <p className="text-gray-700">
                Used strategic keyword-based selection to identify
                mechanism-rich papers (papers likely to describe causal patterns
                rather than just methods or results).
              </p>
            </div>
          </div>

          {/* Step 2 */}
          <div className="mb-8">
            <div className="flex items-start mb-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mt-0.5">
                Mechanism Extraction
              </h3>
            </div>
            <div className="ml-11">
              <p className="text-gray-700 mb-2">
                Extracted <strong>54 domain-neutral mechanisms</strong> from
                selected papers using LLM-guided analysis.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>Hit rate:</strong> 50% on strategically selected papers
                (vs 22.5% on random papers).
              </p>
              <p className="text-gray-700">
                Each mechanism is rewritten in <em>domain-neutral language</em> to
                strip away field-specific jargon and reveal the underlying
                structural pattern.
              </p>
            </div>
          </div>

          {/* Step 3 */}
          <div className="mb-8">
            <div className="flex items-start mb-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mt-0.5">
                Semantic Matching
              </h3>
            </div>
            <div className="ml-11">
              <p className="text-gray-700 mb-2">
                Generated <strong>384-dimensional semantic embeddings</strong>{' '}
                for each mechanism using sentence-transformers (all-MiniLM-L6-v2).
              </p>
              <p className="text-gray-700 mb-2">
                Computed cosine similarity between all cross-domain pairs
                (excluding same-domain matches).
              </p>
              <p className="text-gray-700">
                Identified <strong>165 candidate pairs</strong> with similarity
                ≥0.35 (relaxed threshold to capture diverse-domain matches).
              </p>
            </div>
          </div>

          {/* Step 4 */}
          <div className="mb-8">
            <div className="flex items-start mb-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                4
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mt-0.5">
                Manual Curation
              </h3>
            </div>
            <div className="ml-11">
              <p className="text-gray-700 mb-2">
                Manually reviewed all 165 candidates and rated each as{' '}
                <em>excellent</em>, <em>good</em>, <em>weak</em>, or{' '}
                <em>false</em>.
              </p>
              <p className="text-gray-700 mb-2">
                Selected <strong>30 verified isomorphisms</strong>: 10 excellent +
                20 good (by similarity score).
              </p>
              <p className="text-gray-700">
                Wrote structural explanations for each match, describing exactly
                how the mechanisms are isomorphic.
              </p>
            </div>
          </div>
        </section>

        {/* Quality Metrics */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Quality Metrics
          </h2>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Overall Precision
                </h3>
                <p className="text-3xl font-bold text-blue-600 mb-1">24%</p>
                <p className="text-sm text-gray-600">
                  40 out of 165 candidates rated as good or excellent
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Top-30 Precision
                </h3>
                <p className="text-3xl font-bold text-green-600 mb-1">67%</p>
                <p className="text-sm text-gray-600">
                  20 out of 30 highest-similarity candidates are genuine
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Similarity Range
                </h3>
                <p className="text-3xl font-bold text-purple-600 mb-1">
                  0.44 - 0.74
                </p>
                <p className="text-sm text-gray-600">
                  Mean: 0.54 (54% cosine similarity)
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Top Domain Pairs
                </h3>
                <p className="text-sm text-gray-700 mb-1">
                  econ ↔ q-bio: 7 matches
                </p>
                <p className="text-sm text-gray-700 mb-1">
                  physics ↔ q-bio: 5 matches
                </p>
                <p className="text-sm text-gray-700">econ ↔ physics: 4 matches</p>
              </div>
            </div>
          </div>
        </section>

        {/* Limitations */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Limitations</h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                <strong>Small sample size:</strong> 54 mechanisms across 2,021
                papers is a limited sample. Many papers contain mechanisms that
                were not extracted.
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                <strong>Manual curation required:</strong> Semantic embeddings
                generate candidates but cannot reliably distinguish genuine
                isomorphisms from superficial similarity. Human judgment is
                essential.
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                <strong>Domain diversity paradox:</strong> More diverse domain
                pairs (e.g., econ ↔ biology) often have LOWER similarity scores
                than same-domain matches, even when the structural match is
                excellent. This means the best discoveries may have modest scores.
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                <strong>Extraction bias:</strong> Mechanisms are easier to extract
                from certain domains (ecology, economics) than others (theoretical
                physics, pure mathematics).
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                <strong>Selection criteria:</strong> Quality ratings reflect the
                author&apos;s judgment of structural similarity. Different researchers
                might rate matches differently.
              </span>
            </li>
          </ul>
        </section>

        {/* Future Work */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Future Work</h2>
          <p className="text-gray-700 mb-4">
            This is v1 with 30 verified isomorphisms. The goal is to grow this
            to 100-400 discoveries over the next 6 months through expansion
            cycles:
          </p>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                Extract mechanisms from under-represented domains (computer
                science, nonlinear dynamics)
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                Focus on high-precision domain pairs (cs ↔ physics: 100%, econ ↔
                physics: 58%)
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                Target high-performing mechanism types (coevolution: 63%,
                strategic interactions: 56%)
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                Improve extraction efficiency with domain-specific prompts
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span>
                Add external validation by domain experts
              </span>
            </li>
          </ul>
        </section>

        {/* Footer */}
        <div className="border-t border-gray-200 pt-8">
          <p className="text-sm text-gray-600 text-center">
            For detailed analysis and expansion strategy, see{' '}
            <a
              href="https://github.com/anthropics/analog-quest"
              className="text-blue-600 hover:underline"
            >
              GROWTH_STRATEGY.md
            </a>{' '}
            in the GitHub repository.
          </p>
        </div>
      </div>
    </div>
  );
}

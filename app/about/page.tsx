import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About',
  description:
    'The story behind Analog Quest - 6 weeks, 40+ sessions, and countless iterations to build an AI-assisted system for discovering structural patterns across academic domains.',
};

export default function AboutPage() {
  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-3xl mx-auto px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="mb-16">
          <h1 className="text-4xl font-serif font-normal text-brown mb-6">About</h1>
          <p className="text-lg text-brown/80 leading-relaxed">
            The story behind Analog Quest
          </p>
        </div>

        {/* The Creator */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">
            Who Built This?
          </h2>
          <p className="text-brown/90 mb-6 leading-relaxed">
            I&apos;m <strong>Chuck</strong>, an artist and creative technologist—not
            an academic researcher. I built Analog Quest out of curiosity about a
            simple question:
          </p>
          <div className="bg-teal-light/50 border-l-4 border-brown-dark p-6 my-8">
            <p className="text-brown/90 italic leading-relaxed">
              &quot;Do different fields independently discover the same structural
              patterns, just using different words?&quot;
            </p>
          </div>
          <p className="text-brown/90 mb-6 leading-relaxed">
            Turns out: <em>yes</em>. And mapping these connections is surprisingly
            hard. No human has the patience to read papers across ALL domains and
            compare their underlying mechanisms. But AI does.
          </p>
        </section>

        {/* The Journey */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-8">The Journey</h2>
          <p className="text-brown/90 mb-8 leading-relaxed">
            Analog Quest took <strong>6 weeks</strong> and{' '}
            <strong>42 work sessions</strong> to build. It was a process of
            constant experimentation, failure, and iteration:
          </p>

          <div className="space-y-8">
            {/* Phase 1 */}
            <div className="border-l-4 border-brown-dark/30 pl-6">
              <h3 className="font-serif text-lg text-brown mb-3">
                Phase 1: Keyword Extraction (Sessions 1-30)
              </h3>
              <p className="text-brown/90 mb-3 leading-relaxed">
                Started with a simple idea: extract patterns from papers using
                keywords like &quot;feedback,&quot; &quot;equilibrium,&quot;
                &quot;oscillation.&quot; Built a database of 2,021 papers, extracted
                6,000+ patterns, and matched them using TF-IDF similarity.
              </p>
              <p className="text-brown/90 leading-relaxed">
                <strong>Result:</strong> Found 616 candidate matches, but manual
                review revealed <strong>0% precision</strong> in the
                highest-confidence matches. The algorithm was matching technique
                names (e.g., &quot;graph neural networks&quot;), not structural
                mechanisms.
              </p>
            </div>

            {/* Phase 2 */}
            <div className="border-l-4 border-brown-dark/30 pl-6">
              <h3 className="font-serif text-lg text-brown mb-3">
                Phase 2: Crisis & Pivot (Sessions 31-33)
              </h3>
              <p className="text-brown/90 mb-3 leading-relaxed">
                Discovered the quality crisis and had to make a hard decision:
                abandon 30 sessions of work and start over with a new approach, or
                try to salvage the keyword-based system.
              </p>
              <p className="text-brown/90 leading-relaxed">
                <strong>Decision:</strong> Pivot to LLM-guided extraction with
                manual curation. Quality over quantity.
              </p>
            </div>

            {/* Phase 3 */}
            <div className="border-l-4 border-brown-dark/30 pl-6">
              <h3 className="font-serif text-lg text-brown mb-3">
                Phase 3: LLM Extraction (Sessions 34-36)
              </h3>
              <p className="text-brown/90 mb-3 leading-relaxed">
                Tested LLM-based mechanism extraction on small samples. Discovered
                that semantic embeddings work 4.7x better than TF-IDF, but also
                uncovered the <em>domain diversity paradox</em>: the best
                cross-domain matches have LOWER similarity scores than mediocre
                same-domain matches.
              </p>
              <p className="text-brown/90 leading-relaxed">
                <strong>Result:</strong> Found excellent matches (e.g., tragedy of
                the commons at 0.453 similarity), but realized automated
                thresholds won&apos;t work. Manual curation is essential.
              </p>
            </div>

            {/* Phase 4 */}
            <div className="border-l-4 border-brown-dark/30 pl-6">
              <h3 className="font-serif text-lg text-brown mb-3">
                Phase 4: Manual Curation (Sessions 37-38)
              </h3>
              <p className="text-brown/90 mb-3 leading-relaxed">
                Extracted 54 mechanisms from 2,021 papers, generated 165 candidate
                pairs using semantic embeddings, and manually reviewed ALL of them.
              </p>
              <p className="text-brown/90 leading-relaxed">
                <strong>Result:</strong> 30 verified isomorphisms with structural
                explanations. 67% precision in the top 30 candidates. Ready to
                launch.
              </p>
            </div>

            {/* Phase 5 */}
            <div className="border-l-4 border-brown-dark/30 pl-6">
              <h3 className="font-serif text-lg text-brown mb-3">
                Phase 5: Strategy & Build (Sessions 39-42)
              </h3>
              <p className="text-brown/90 mb-3 leading-relaxed">
                Analyzed precision data to create a growth strategy, designed the
                frontend with a warm, accessible design system, and built this site.
                Total build time: ~15 hours across 4 sessions.
              </p>
              <p className="text-brown/90 leading-relaxed">
                <strong>Result:</strong> You&apos;re looking at it.
              </p>
            </div>
          </div>
        </section>

        {/* Built With */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">
            Built With Claude Code
          </h2>
          <p className="text-brown/90 mb-6 leading-relaxed">
            This entire project—database design, paper processing, mechanism
            extraction, semantic matching, manual curation, frontend build—was
            built in collaboration with{' '}
            <a
              href="https://claude.ai/claude-code"
              className="text-brown-dark hover:text-brown border-b border-brown-dark/30 hover:border-brown-dark transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              Claude Code
            </a>
            , Anthropic&apos;s AI coding assistant.
          </p>
          <p className="text-brown/90 mb-6 leading-relaxed">
            Claude Code acted as both researcher and engineer: it fetched papers,
            extracted patterns, designed algorithms, debugged code, analyzed
            results, and built the website you&apos;re viewing.
          </p>
          <p className="text-brown/90 leading-relaxed">
            This project is a demonstration of <em>human-AI collaboration</em>: I
            provided direction, judgment, and quality standards. Claude Code
            provided execution, analysis, and technical implementation. Together,
            we built something neither could have built alone.
          </p>
        </section>

        {/* Technology Stack */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">
            Technology Stack
          </h2>
          <div className="bg-teal-light/50 border border-brown/10 rounded-lg p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-mono text-sm text-brown/70 mb-4 uppercase tracking-wide">Backend</h3>
                <ul className="space-y-2 text-sm text-brown/90">
                  <li>• Python (data processing)</li>
                  <li>• SQLite (database)</li>
                  <li>• sentence-transformers (embeddings)</li>
                  <li>• arXiv API (paper fetching)</li>
                </ul>
              </div>
              <div>
                <h3 className="font-mono text-sm text-brown/70 mb-4 uppercase tracking-wide">Frontend</h3>
                <ul className="space-y-2 text-sm text-brown/90">
                  <li>• Next.js 15 (React framework)</li>
                  <li>• TypeScript (type safety)</li>
                  <li>• Tailwind CSS (styling)</li>
                  <li>• Vercel (deployment)</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Open Source */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">Open Source</h2>
          <p className="text-brown/90 mb-6 leading-relaxed">
            Analog Quest is open source. All code, data, and methodology are
            available on GitHub:
          </p>
          <a
            href="https://github.com/anthropics/analog-quest"
            className="inline-block px-8 py-3 bg-brown-dark text-cream font-mono text-sm hover:bg-brown transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            view on github
          </a>
          <p className="text-sm text-brown/70 mt-6 leading-relaxed">
            Contributions, feedback, and suggestions are welcome.
          </p>
        </section>

        {/* Contact */}
        <section className="mb-16">
          <h2 className="text-2xl font-serif font-normal text-brown mb-6">
            Contact & Feedback
          </h2>
          <p className="text-brown/90 mb-6 leading-relaxed">
            If you find this project interesting, have questions, or want to
            suggest improvements:
          </p>
          <ul className="space-y-3 text-brown/90">
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>
                Open an issue on{' '}
                <a
                  href="https://github.com/anthropics/analog-quest/issues"
                  className="text-brown-dark hover:text-brown border-b border-brown-dark/30 hover:border-brown-dark transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub
                </a>
              </span>
            </li>
            <li className="flex items-start leading-relaxed">
              <span className="text-brown-dark mr-3 mt-1">•</span>
              <span>Email: feedback@analog.quest (coming soon)</span>
            </li>
          </ul>
        </section>

        {/* Footer */}
        <div className="border-t border-brown/20 pt-8">
          <p className="text-sm font-mono text-brown/60 text-center">
            Built with curiosity, persistence, and Claude Code.
            <br />
            <span className="text-brown/50">© 2026 Analog Quest</span>
          </p>
        </div>
      </div>
    </div>
  );
}

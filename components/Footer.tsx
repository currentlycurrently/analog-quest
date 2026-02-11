import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-cream-mid border-t border-brown/10 mt-24">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* About */}
          <div>
            <h3 className="font-mono text-brown-dark mb-4 text-xs">
              about
            </h3>
            <p className="text-brown/80 text-sm leading-relaxed">
              Discovering structural isomorphisms across academic domains.
              Same ideas, different languages.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="font-mono text-brown-dark mb-4 text-xs">
              explore
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/discoveries"
                  className="text-brown/80 hover:text-brown-dark text-sm transition-colors"
                >
                  Browse Discoveries
                </Link>
              </li>
              <li>
                <Link
                  href="/methodology"
                  className="text-brown/80 hover:text-brown-dark text-sm transition-colors"
                >
                  How It Works
                </Link>
              </li>
              <li>
                <Link
                  href="/about"
                  className="text-brown/80 hover:text-brown-dark text-sm transition-colors"
                >
                  About the Project
                </Link>
              </li>
            </ul>
          </div>

          {/* Built With */}
          <div>
            <h3 className="font-mono text-brown-dark mb-4 text-xs">
              built with
            </h3>
            <ul className="space-y-3">
              <li className="text-brown/80 text-sm">
                <a
                  href="https://claude.com/claude-code"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-brown-dark transition-colors"
                >
                  Claude Code
                </a>
              </li>
              <li className="text-brown/80 text-sm">
                <a
                  href="https://nextjs.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-brown-dark transition-colors"
                >
                  Next.js
                </a>
              </li>
              <li className="text-brown/80 text-sm">
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-brown-dark transition-colors"
                >
                  View on GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-12 pt-8 border-t border-brown/10">
          <p className="text-brown/60 text-sm text-center font-mono">
            © 2026 analog.quest
          </p>
        </div>
      </div>
    </footer>
  );
}

import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              About
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              Discovering structural isomorphisms across academic domains.
              Same ideas, different languages.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Explore
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/discoveries"
                  className="text-gray-600 hover:text-gray-900 text-sm transition-colors"
                >
                  Browse Discoveries
                </Link>
              </li>
              <li>
                <Link
                  href="/methodology"
                  className="text-gray-600 hover:text-gray-900 text-sm transition-colors"
                >
                  How It Works
                </Link>
              </li>
              <li>
                <Link
                  href="/about"
                  className="text-gray-600 hover:text-gray-900 text-sm transition-colors"
                >
                  About the Project
                </Link>
              </li>
            </ul>
          </div>

          {/* Built With */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Built With
            </h3>
            <ul className="space-y-2">
              <li className="text-gray-600 text-sm">
                <a
                  href="https://claude.com/claude-code"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-gray-900 transition-colors"
                >
                  Claude Code
                </a>
              </li>
              <li className="text-gray-600 text-sm">
                <a
                  href="https://nextjs.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-gray-900 transition-colors"
                >
                  Next.js
                </a>
              </li>
              <li className="text-gray-600 text-sm">
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-gray-900 transition-colors"
                >
                  View on GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-gray-500 text-sm text-center">
            © 2026 analog.quest • Built with Claude Code
          </p>
        </div>
      </div>
    </footer>
  );
}

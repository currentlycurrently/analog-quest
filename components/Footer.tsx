import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-cream-mid border-t border-brown/10 mt-24">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row justify-between gap-8">
          <div>
            <p className="font-serif text-brown mb-2">analog.quest</p>
            <p className="text-brown/60 text-sm">Mapping mathematical isomorphisms across science.</p>
          </div>

          <div className="flex gap-12">
            <div>
              <h3 className="font-mono text-xs text-brown-dark mb-3">explore</h3>
              <ul className="space-y-2">
                <li><Link href="/discoveries" className="text-brown/70 hover:text-brown text-sm">discoveries</Link></li>
                <li><Link href="/contribute" className="text-brown/70 hover:text-brown text-sm">contribute</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-mono text-xs text-brown-dark mb-3">open source</h3>
              <ul className="space-y-2">
                <li>
                  <a href="https://github.com/chuckyatsuk/analog-quest"
                     target="_blank" rel="noopener noreferrer"
                     className="text-brown/70 hover:text-brown text-sm">
                    github
                  </a>
                </li>
                <li>
                  <a href="https://analog.quest/api/queue/status"
                     className="text-brown/70 hover:text-brown text-sm">
                    api status
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-brown/10">
          <p className="text-brown/40 text-xs font-mono text-center">MIT License · built with Claude Code</p>
        </div>
      </div>
    </footer>
  );
}

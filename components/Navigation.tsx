import Link from 'next/link';

export default function Navigation() {
  return (
    <nav className="bg-cream border-b border-brown/10 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <Link href="/" className="text-2xl font-serif font-normal text-brown tracking-tight">
            analog.quest
          </Link>

          <div className="flex items-center space-x-10">
            <Link href="/discoveries" className="font-mono text-brown-dark/70 hover:text-brown-dark transition-colors text-sm">
              discoveries
            </Link>
            <Link href="/contribute" className="font-mono text-brown-dark/70 hover:text-brown-dark transition-colors text-sm">
              contribute
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

import Link from 'next/link';

export default function Navigation() {
  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <span className="text-2xl font-bold text-gray-900">
              analog.quest
            </span>
            <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-medium">
              BETA
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-8">
            <Link
              href="/discoveries"
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Discoveries
            </Link>
            <Link
              href="/methodology"
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Methodology
            </Link>
            <Link
              href="/about"
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              About
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Analog Quest - Cross-Domain Isomorphism Explorer",
  description: "Discover structural similarities across academic domains",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="min-h-screen flex flex-col">
          <header className="border-b border-gray-200 dark:border-gray-800">
            <nav className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <Link href="/" className="text-2xl font-bold">
                  Analog Quest
                </Link>
                <div className="flex gap-6">
                  <Link
                    href="/"
                    className="hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/papers"
                    className="hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    Papers
                  </Link>
                  <Link
                    href="/patterns"
                    className="hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    Patterns
                  </Link>
                  <Link
                    href="/isomorphisms"
                    className="hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    Isomorphisms
                  </Link>
                </div>
              </div>
            </nav>
          </header>
          <main className="flex-1 container mx-auto px-4 py-8">
            {children}
          </main>
          <footer className="border-t border-gray-200 dark:border-gray-800 py-6">
            <div className="container mx-auto px-4 text-center text-sm text-gray-600 dark:text-gray-400">
              Building a living map of cross-domain isomorphisms
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}

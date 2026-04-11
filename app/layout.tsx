import type { Metadata } from 'next';
import './globals.css';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  metadataBase: new URL('https://analog.quest'),
  title: {
    default: 'Analog Quest — Mathematical Isomorphisms Across Science',
    template: '%s | Analog Quest',
  },
  description:
    'Finding cases where different scientific fields are solving the exact same equation under different names.',
  keywords: ['structural isomorphisms', 'cross-domain science', 'mathematical equivalence', 'open science', 'Claude Code'],
  authors: [{ name: 'chuckyatsuk' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://analog.quest',
    title: 'Analog Quest — Mathematical Isomorphisms Across Science',
    description: 'Finding cases where different scientific fields are solving the exact same equation.',
    siteName: 'Analog Quest',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Analog Quest',
    description: 'Finding cases where different scientific fields are solving the exact same equation.',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

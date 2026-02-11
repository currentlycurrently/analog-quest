import type { Metadata } from 'next';
import './globals.css';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  metadataBase: new URL('https://analog.quest'),
  title: {
    default: 'Analog Quest - Cross-Domain Structural Isomorphisms',
    template: '%s | Analog Quest',
  },
  description:
    'AI-assisted discovery of structural patterns across 2,021 academic papers. 30 verified cross-domain isomorphisms revealing identical mechanisms in different fields.',
  keywords: [
    'structural isomorphisms',
    'cross-domain patterns',
    'academic research',
    'AI research',
    'mechanism discovery',
    'pattern recognition',
    'knowledge synthesis',
  ],
  authors: [{ name: 'Chuck' }],
  creator: 'Chuck',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://analog.quest',
    title: 'Analog Quest - Cross-Domain Structural Isomorphisms',
    description:
      'AI-assisted discovery of structural patterns across 2,021 academic papers. 30 verified cross-domain isomorphisms.',
    siteName: 'Analog Quest',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Analog Quest - Cross-Domain Structural Isomorphisms',
    description:
      'AI-assisted discovery of structural patterns across 2,021 academic papers. 30 verified cross-domain isomorphisms.',
    creator: '@analogquest',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="https://use.typekit.net/zyv7mik.css" />
      </head>
      <body>
        <Navigation />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

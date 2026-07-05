import Link from 'next/link';

export default function Navigation() {
  return (
    <nav className="border-b border-black/10">
      <div className="max-w-3xl mx-auto px-6 py-6 flex justify-between items-baseline">
        <Link href="/" className="text-base font-semibold no-underline">
          analog.quest
        </Link>
        <div className="flex gap-6 text-sm">
          <Link href="/atlas" className="no-underline hover:underline">atlas</Link>
          <Link href="/contribute" className="no-underline hover:underline">contribute</Link>
        </div>
      </div>
    </nav>
  );
}

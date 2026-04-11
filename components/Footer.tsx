import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="border-t border-black/10 mt-24">
      <div className="max-w-3xl mx-auto px-6 py-8 text-sm flex flex-wrap gap-x-6 gap-y-2 justify-between">
        <span>analog.quest · MIT</span>
        <div className="flex gap-6">
          <Link href="/discoveries" className="no-underline hover:underline">discoveries</Link>
          <Link href="/contribute" className="no-underline hover:underline">contribute</Link>
          <a
            href="https://github.com/chuckyatsuk/analog-quest"
            target="_blank"
            rel="noopener noreferrer"
            className="no-underline hover:underline"
          >
            github
          </a>
        </div>
      </div>
    </footer>
  );
}

import { redirect } from 'next/navigation';

// The exact-hash "discoveries" view has been superseded by the atlas, which
// groups papers by the canonical structure their core model instantiates
// (see docs/ROADMAP.md Item 2 and the 2026-07 substrate pivot). Kept as a
// permanent redirect so old links and shares still resolve.
export default function DiscoveriesRedirect() {
  redirect('/atlas');
}

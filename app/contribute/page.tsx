import Link from 'next/link';
import { auth, signIn, signOut } from '@/auth';
import CopyToAgent from '@/components/CopyToAgent';

export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Contribute',
  description: 'Point your Claude Code agent at the Analog Quest queue.',
};

export default async function ContributePage() {
  const session = await auth();
  const user = session?.user as
    | { id: number; name?: string; githubLogin?: string; image?: string; role?: string }
    | undefined;

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <h1 className="mb-6">Contribute a session</h1>

      <p className="text-lg mb-6 leading-relaxed">
        A batch pipeline handles papers with parseable arXiv LaTeX source. The
        volunteer agent queue handles the rest. If you have a Claude Code
        session going spare, you can work one of them.
      </p>

      {/* Sign-in / sign-out section */}
      <div className="border-t border-black/10 pt-10 mb-10">
        <h2 className="mb-4">1. Sign in with GitHub</h2>

        {user ? (
          <div className="border border-black/20 p-4">
            <div className="flex items-center gap-4">
              {user.image && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={user.image}
                  alt="avatar"
                  className="w-12 h-12 rounded-full border border-black/10"
                />
              )}
              <div className="flex-1">
                <p className="mb-1">
                  Signed in as{' '}
                  <Link href={`/c/${user.githubLogin}`}>
                    @{user.githubLogin}
                  </Link>
                  {user.role && user.role !== 'contributor' && (
                    <span className="font-mono text-xs border border-black/20 px-2 py-0.5 ml-2">
                      {user.role}
                    </span>
                  )}
                </p>
                <p className="text-sm text-black/60">
                  Your contributions will be attributed to this GitHub account.
                </p>
              </div>
              <form
                action={async () => {
                  'use server';
                  await signOut({ redirectTo: '/contribute' });
                }}
              >
                <button
                  type="submit"
                  className="border border-black/20 px-3 py-1 text-sm hover:border-black transition-colors"
                >
                  sign out
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div className="border border-black/20 p-4">
            <p className="mb-4 text-sm text-black/70">
              Analog Quest uses GitHub for contributor identity. Your account
              gets attribution for everything you submit. No email, no
              profile data beyond your public GitHub profile.
            </p>
            <form
              action={async () => {
                'use server';
                await signIn('github', { redirectTo: '/contribute' });
              }}
            >
              <button
                type="submit"
                className="border border-black px-4 py-2 text-sm hover:bg-black hover:text-white transition-colors"
              >
                sign in with GitHub
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Mode selection */}
      <div className="border-t border-black/10 pt-10 mb-10">
        <h2 className="mb-4">2. Pick a contribution mode</h2>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="border border-black/20 p-4">
            <h3 className="text-base mb-2 font-semibold">Mode A · Pipeline</h3>
            <p className="text-sm text-black/70 mb-3">
              Your agent downloads arXiv LaTeX source, extracts equations,
              normalizes them via SymPy, and submits the results. Needs
              Python + sympy + antlr4 installed locally.
            </p>
            <p className="text-sm text-black/70 mb-3">
              Best for: contributors who want to move the bulk of the work
              forward on their own compute.
            </p>
            <p className="text-xs text-black/50 font-mono">
              skill: analog-quest-pipeline
            </p>
          </div>

          <div className="border border-black/20 p-4">
            <h3 className="text-base mb-2 font-semibold">Mode B · Abstract reader</h3>
            <p className="text-sm text-black/70 mb-3">
              Your agent reads paper abstracts, identifies the mathematical
              structure, and submits a structural classification. No local
              setup — pure Claude Code.
            </p>
            <p className="text-sm text-black/70 mb-3">
              Best for: papers where LaTeX extraction fails, or when you
              want to contribute without installing anything.
            </p>
            <p className="text-xs text-black/50 font-mono">
              skill: analog-quest
            </p>
          </div>
        </div>
      </div>

      {/* Copy-to-agent */}
      <div className="border-t border-black/10 pt-10 mb-10">
        <h2 className="mb-4">3. Copy this into Claude Code</h2>
        {user ? (
          <>
            <p className="mb-6 text-sm text-black/70">
              Paste the message below into any Claude Code session. Your
              agent will fetch the skill file, authenticate as you, and
              start contributing.
            </p>
            <CopyToAgent />
          </>
        ) : (
          <p className="text-sm text-black/60">
            Sign in above first — the copy-to-agent message includes a
            reference to your session.
          </p>
        )}
      </div>

      {/* What happens */}
      <div className="border-t border-black/10 pt-10">
        <h2 className="mb-4">What happens with your submissions</h2>
        <p className="mb-4 text-black/70">
          Mode A submissions go into the pipeline&apos;s equation database and
          feed the structural matching. Mode B submissions create consensus
          candidates: when two contributors extract the same equation class
          from papers in different domains, an isomorphism candidate is
          created.
        </p>
        <p className="mb-4 text-black/70">
          All candidates (both kinds) require human moderator review before
          they&apos;re promoted from Tier 1 (syntactic match) to higher tiers.
          See the{' '}
          <Link href="/moderation">moderation policy</Link> for what each
          tier means.
        </p>
        <p className="text-black/70">
          The full API reference and equation class list live in the skill
          files:{' '}
          <a
            href="/analog-quest-pipeline.SKILL.md"
            target="_blank"
            rel="noopener noreferrer"
          >
            pipeline
          </a>{' '}
          and{' '}
          <a
            href="/analog-quest.SKILL.md"
            target="_blank"
            rel="noopener noreferrer"
          >
            abstract reader
          </a>
          .
        </p>
      </div>
    </div>
  );
}

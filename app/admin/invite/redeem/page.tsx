import { redirect } from 'next/navigation';
import { auth } from '@/auth';
import RedeemClient from './RedeemClient';

export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Redeem moderator invite',
};

export default async function RedeemPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;
  const session = await auth();

  if (!session?.user) {
    // Bounce through sign-in, preserving the token in the callback URL
    redirect(`/api/auth/signin?callbackUrl=/admin/invite/redeem?token=${token ?? ''}`);
  }

  if (!token) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20">
        <h1 className="mb-4">Missing invite token</h1>
        <p className="text-black/70">
          This page needs a token query parameter. The link should look like{' '}
          <code className="font-mono">/admin/invite/redeem?token=...</code>.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <h1 className="mb-2">Moderator invite</h1>
      <p className="text-black/70 mb-8">
        You&apos;ve been invited to help review Analog Quest pipeline candidates.
        Clicking the button below will upgrade your account to moderator.
      </p>
      <RedeemClient token={token} />
    </div>
  );
}

import { redirect } from 'next/navigation';
import { auth } from '@/auth';
import ReviewClient from './ReviewClient';

export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Moderator Review',
};

export default async function ReviewPage() {
  const session = await auth();
  const role = (session?.user as any)?.role;

  if (!session?.user) {
    redirect('/api/auth/signin?callbackUrl=/admin/review');
  }

  if (role !== 'moderator' && role !== 'admin') {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20">
        <h1 className="mb-4">Not authorized</h1>
        <p className="text-black/70">
          This page is for moderators. If you think you should have access,
          ask an admin for an invite.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <h1 className="mb-2">Moderator review</h1>
      <p className="text-black/70 mb-8">
        One pending Tier 1 candidate at a time. Promote to a higher tier
        with a written note, or reject with a reason. Every action is
        logged.
      </p>
      <ReviewClient />
    </div>
  );
}

import { redirect } from 'next/navigation';
import { auth } from '@/auth';
import ModeratorsClient from './ModeratorsClient';

export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Moderators',
};

export default async function ModeratorsPage() {
  const session = await auth();
  const role = (session?.user as any)?.role;

  if (!session?.user) {
    redirect('/api/auth/signin?callbackUrl=/admin/moderators');
  }

  if (role !== 'admin') {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20">
        <h1 className="mb-4">Not authorized</h1>
        <p className="text-black/70">
          Only admins can create moderator invites.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <h1 className="mb-2">Moderators</h1>
      <p className="text-black/70 mb-8">
        Create a single-use invite link and send it to the person you want to
        promote. They click the link while signed in with GitHub, and their
        account becomes a moderator.
      </p>
      <ModeratorsClient />
    </div>
  );
}

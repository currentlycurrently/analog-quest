'use client';

interface RebuildNoticeProps {
  status: {
    message: string;
    old_discoveries: number;
    real_isomorphisms: number;
  };
}

export default function RebuildNotice({ status }: RebuildNoticeProps) {
  return (
    <div className="bg-yellow-400 text-brown">
      <div className="max-w-5xl mx-auto px-6 lg:px-8 py-4">
        <div className="flex items-center gap-4">
          <span className="text-2xl">🚧</span>
          <div>
            <p className="font-mono font-semibold text-sm">
              FUNDAMENTAL REBUILD IN PROGRESS
            </p>
            <p className="text-sm">
              Previous {status.old_discoveries} "discoveries" → {status.real_isomorphisms} real mathematical isomorphisms
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
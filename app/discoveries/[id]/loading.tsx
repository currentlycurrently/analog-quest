export default function DiscoveryDetailLoading() {
  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back Link Skeleton */}
        <div className="h-6 w-32 bg-brown/10 rounded mb-8 animate-pulse" />

        {/* Header Skeleton */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="h-10 w-40 bg-brown/10 rounded animate-pulse" />
            <div className="h-10 w-48 bg-brown/10 rounded animate-pulse" />
          </div>
          <div className="h-12 w-2/3 bg-brown/10 rounded mb-4 animate-pulse" />
          <div className="flex items-center gap-3">
            <div className="h-8 w-24 bg-brown/10 rounded animate-pulse" />
            <div className="h-8 w-8 bg-brown/10 rounded animate-pulse" />
            <div className="h-8 w-24 bg-brown/10 rounded animate-pulse" />
          </div>
        </div>

        {/* Content Skeleton */}
        <div className="space-y-6">
          <div className="h-64 bg-brown/10 rounded animate-pulse" />
          <div className="h-32 bg-brown/10 rounded animate-pulse" />
          <div className="h-32 bg-brown/10 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}
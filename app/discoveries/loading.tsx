export default function Loading() {
  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
        <div className="animate-pulse">
          <div className="h-10 bg-brown/10 rounded w-1/3 mb-6"></div>
          <div className="h-6 bg-brown/10 rounded w-2/3 mb-8"></div>

          <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="border border-brown/10 bg-cream p-6 h-64">
                <div className="h-4 bg-brown/10 rounded w-1/4 mb-4"></div>
                <div className="h-6 bg-brown/10 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-brown/10 rounded w-full mb-2"></div>
                <div className="h-4 bg-brown/10 rounded w-5/6"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
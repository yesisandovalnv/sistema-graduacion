/**
 * Skeleton Loader Component
 * Displays animated skeleton UI while content is loading
 * Mimics Stripe-style loading design
 */

const SkeletonLoader = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Encabezado Skeleton */}
      <div className="mb-8">
        <div className="h-10 bg-slate-700/10 rounded-lg w-48 mb-2 animate-pulse"></div>
        <div className="h-5 bg-slate-700/10 rounded-lg w-96 animate-pulse"></div>
      </div>

      {/* Stats Cards Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-slate-700/50 overflow-hidden animate-pulse"
          >
            {/* Gradient Bar */}
            <div className="h-1 bg-slate-700/10"></div>

            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="h-4 bg-slate-700/10 rounded w-24 mb-3"></div>
                  <div className="h-8 bg-slate-700/10 rounded w-16 mb-4"></div>

                  {/* Trend skeleton */}
                  <div className="flex items-center gap-2">
                    <div className="h-4 bg-slate-700/10 rounded w-20"></div>
                    <div className="h-4 bg-slate-700/10 rounded w-32"></div>
                  </div>
                </div>

                {/* Icon skeleton */}
                <div className="w-12 h-12 bg-slate-700/10 rounded-lg flex-shrink-0"></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-slate-700/50 h-[320px] animate-pulse"
          >
            {/* Title */}
            <div className="h-6 bg-slate-700/10 rounded w-48 mb-4"></div>

            {/* Chart Area */}
            <div className="flex flex-col gap-3 mt-6">
              {[...Array(5)].map((_, j) => (
                <div key={j} className="flex items-center gap-2">
                  <div className="h-2 bg-slate-700/10 rounded flex-1"></div>
                  <div className="h-2 bg-slate-700/10 rounded w-12"></div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Table Skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-slate-700/50 p-6 animate-pulse">
        <div className="h-6 bg-slate-700/10 rounded w-48 mb-4"></div>

        {/* Table rows */}
        <div className="space-y-4 mt-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex gap-4">
              <div className="h-8 bg-slate-700/10 rounded flex-1"></div>
              <div className="h-8 bg-slate-700/10 rounded flex-1"></div>
              <div className="h-8 bg-slate-700/10 rounded flex-1"></div>
              <div className="h-8 bg-slate-700/10 rounded flex-1"></div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Skeleton */}
      <div className="h-8 bg-slate-700/10 rounded-lg w-64 animate-pulse"></div>
    </div>
  );
};

export default SkeletonLoader;

/**
 * Table Skeleton Component
 * Displays a skeleton loading state for tables
 * Maintains layout shift prevention by using fixed heights
 */

const TableSkeleton = ({ rows = 10, columns = 4, isDark = false }) => {
  return (
    <div className="rounded-xl shadow-sm border bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700 overflow-hidden">
      {/* Header Section */}
      <div className="p-6 border-b border-gray-200 dark:border-slate-700">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Título */}
          <div className="h-6 w-24 skeleton-shimmer bg-slate-300/50 dark:bg-slate-700/50 rounded"></div>

          {/* Búsqueda */}
          <div className="flex-1 md:max-w-sm">
            <div className="h-10 skeleton-shimmer bg-slate-300/50 dark:bg-slate-700/50 rounded-lg"></div>
          </div>

          {/* Resultados */}
          <div className="h-5 w-20 skeleton-shimmer bg-slate-300/50 dark:bg-slate-700/50 rounded"></div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          {/* Header Row */}
          <thead>
            <tr className="border-b bg-gray-50 dark:bg-slate-900 border-gray-200 dark:border-slate-700">
              {[...Array(columns + 1)].map((_, i) => (
                <th key={i} className="px-6 py-3 text-left">
                  <div className="h-4 w-20 skeleton-shimmer bg-slate-300/50 dark:bg-slate-700/50 rounded"></div>
                </th>
              ))}
            </tr>
          </thead>

          {/* Body Rows */}
          <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
            {[...Array(rows)].map((_, rowIdx) => (
              <tr key={rowIdx} className="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                {[...Array(columns + 1)].map((_, colIdx) => (
                  <td key={colIdx} className="px-6 py-4">
                    <div className="h-5 skeleton-shimmer bg-slate-300/50 dark:bg-slate-700/50 rounded" style={{
                      width: colIdx === 0 ? '100%' : `${60 + Math.random() * 30}%`,
                    }}></div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Skeleton */}
      <div className="px-6 py-4 border-t border-gray-200 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="h-5 w-32 skeleton-shimmer bg-slate-300/50 dark:bg-slate-700/50 rounded"></div>
          <div className="flex gap-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-8 w-8 skeleton-shimmer bg-slate-300/50 dark:bg-slate-700/50 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TableSkeleton;

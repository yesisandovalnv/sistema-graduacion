/**
 * Global Loader Component
 * Displays an overlay with spinner while HTTP requests are in progress
 * Prevents flickering for fast responses (<200ms)
 */

import { useEffect, useState } from 'react';
import { useLoader } from '../../context/LoaderContext';

const GlobalLoader = () => {
  const { isLoading } = useLoader();
  const [showLoader, setShowLoader] = useState(false);

  useEffect(() => {
    let timeout;

    if (isLoading) {
      // Delay showing loader to prevent flicker on fast responses
      timeout = setTimeout(() => {
        setShowLoader(true);
      }, 200);
    } else {
      // Hide loader immediately
      setShowLoader(false);
      clearTimeout(timeout);
    }

    return () => clearTimeout(timeout);
  }, [isLoading]);

  if (!showLoader) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black bg-opacity-30 backdrop-blur-sm">
      {/* Spinner Container */}
      <div className="flex flex-col items-center gap-4">
        {/* Animated Spinner */}
        <div className="w-12 h-12 border-4 border-transparent border-t-blue-500 border-r-blue-400 rounded-full animate-spin"></div>
        
        {/* Loading Text */}
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Cargando...
        </p>
      </div>
    </div>
  );
};

export default GlobalLoader;

/**
 * Loader Context
 * Manages global HTTP request loader state
 * Tracks active requests and provides show/hide methods
 */

import { createContext, useContext, useState } from 'react';

const LoaderContext = createContext();

/**
 * Provider component
 */
export const LoaderProvider = ({ children }) => {
  const [activeRequests, setActiveRequests] = useState(0);

  const increment = () => {
    setActiveRequests((prev) => prev + 1);
  };

  const decrement = () => {
    setActiveRequests((prev) => Math.max(0, prev - 1));
  };

  const isLoading = activeRequests > 0;

  return (
    <LoaderContext.Provider value={{ isLoading, increment, decrement, activeRequests }}>
      {children}
    </LoaderContext.Provider>
  );
};

/**
 * Hook to use loader context
 */
export const useLoader = () => {
  const context = useContext(LoaderContext);
  if (!context) {
    throw new Error('useLoader must be used within LoaderProvider');
  }
  return context;
};

/**
 * Global loader instance to access from non-React code (axios)
 */
let loaderInstance = null;

export const setLoaderInstance = (instance) => {
  loaderInstance = instance;
};

export const getLoaderInstance = () => loaderInstance;

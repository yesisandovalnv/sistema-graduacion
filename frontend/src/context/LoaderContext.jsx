/**
 * Loader Context
 * Manages global HTTP request loader state
 * Tracks active requests and provides show/hide methods
 * Memoized to prevent unnecessary re-renders and multiple interceptor registration
 */

import { createContext, useContext, useState, useMemo, useCallback } from 'react';

const LoaderContext = createContext();

/**
 * Provider component
 */
export const LoaderProvider = ({ children }) => {
  const [activeRequests, setActiveRequests] = useState(0);

  // Use useCallback to maintain stable function references
  const increment = useCallback(() => {
    setActiveRequests((prev) => prev + 1);
  }, []);

  const decrement = useCallback(() => {
    setActiveRequests((prev) => Math.max(0, prev - 1));
  }, []);

  const isLoading = activeRequests > 0;

  // Memoize context value to prevent unnecessary re-renders
  // and ensure LoaderInitializer interceptors register only once
  const value = useMemo(
    () => ({
      isLoading,
      increment,
      decrement,
      activeRequests,
    }),
    [isLoading, increment, decrement, activeRequests]
  );

  return (
    <LoaderContext.Provider value={value}>
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

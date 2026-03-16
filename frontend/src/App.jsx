/**
 * Main App Component
 * Root component with providers
 */

import { useEffect, useRef } from 'react';
import AuthProvider from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { LoaderProvider, useLoader, setLoaderInstance } from './context/LoaderContext';
import AppRouter from './router/AppRouter';
import './styles/index.css';

/**
 * Initializer component
 * Sets up the loader instance for non-React code (axios)
 * Ensures interceptors are registered only once with useRef flag
 */
function LoaderInitializer({ children }) {
  const loader = useLoader();
  const initRef = useRef(false);

  useEffect(() => {
    // Register loader instance only once on mount
    if (!initRef.current) {
      setLoaderInstance(loader);
      initRef.current = true;
    }
  }, [loader]);

  return children;
}

function App() {
  return (
    <LoaderProvider>
      <LoaderInitializer>
        <ThemeProvider>
          <AuthProvider>
            <AppRouter />
          </AuthProvider>
        </ThemeProvider>
      </LoaderInitializer>
    </LoaderProvider>
  );
}

export default App;

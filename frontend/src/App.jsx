/**
 * Main App Component
 * Root component with providers
 */

import { useEffect } from 'react';
import AuthProvider from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { LoaderProvider, useLoader, setLoaderInstance } from './context/LoaderContext';
import AppRouter from './router/AppRouter';
import './styles/index.css';

/**
 * Initializer component
 * Sets up the loader instance for non-React code (axios)
 */
function LoaderInitializer({ children }) {
  const loader = useLoader();

  useEffect(() => {
    setLoaderInstance(loader);
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

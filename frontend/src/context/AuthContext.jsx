/**
 * Authentication Context
 * Provides global authentication state
 */

import { createContext, useState, useCallback, useEffect } from 'react';
import authApi from '../api/authApi';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  /**
   * Initialize auth state from localStorage
   */
  useEffect(() => {
    const initAuth = () => {
      const token = authApi.getAccessToken();
      const currentUser = authApi.getCurrentUser();

      if (token && currentUser) {
        setUser(currentUser);
        setIsAuthenticated(true);
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Multi-tab session synchronization (FASE 2)
   * Detecta cuando otro tab elimina el token de acceso y sincroniza estado
   */
  useEffect(() => {
    const handleStorageChange = (event) => {
      // Detectar si el access_token fue removido en otra pestaña
      if (event.key === 'access_token' && event.newValue === null) {
        console.warn('[AuthContext] Token removido desde otra pestaña - sincronizando sesión');
        setUser(null);
        setIsAuthenticated(false);
      }
    };

    // Agregar listener para cambios en localStorage desde otras pestañas
    window.addEventListener('storage', handleStorageChange);

    // Cleanup: Remover listener cuando componente se desmonta
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  /**
   * Login handler
   */
  const login = useCallback(async (username, password) => {
    setLoading(true);
    try {
      const result = await authApi.login(username, password);

      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        return { success: true };
      } else {
        setUser(null);
        setIsAuthenticated(false);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed' };
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Logout handler
   */
  const logout = useCallback(() => {
    authApi.logout();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  /**
   * Update user info
   */
  const updateUser = useCallback((updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('user_info', JSON.stringify(updatedUser));
  }, []);

  /**
   * Check if user has permission
   */
  const hasPermission = useCallback((permission) => {
    if (!user) return false;
    // For now, check role-based permissions
    // This can be extended with Django permissions
    return true; // Customize based on your needs
  }, [user]);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    updateUser,
    hasPermission,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;

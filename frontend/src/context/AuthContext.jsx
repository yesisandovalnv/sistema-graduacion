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

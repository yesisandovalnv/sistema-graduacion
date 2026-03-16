/**
 * Authentication API Service
 * Handles login, logout, and token management
 */

import axiosInstance from './axios';
import { API_CONFIG } from '../constants/api';

class AuthService {
  /**
   * Login user with username and password
   * @param {string} username
   * @param {string} password
   * @returns {Promise} JWT tokens and user info
   */
  async login(username, password) {
    try {
      const response = await axiosInstance.post(
        API_CONFIG.ENDPOINTS.LOGIN,
        { username, password }
      );

      const { access, refresh, user } = response.data;

      // Store tokens
      localStorage.setItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN, access);
      localStorage.setItem(API_CONFIG.STORAGE_KEYS.REFRESH_TOKEN, refresh);
      localStorage.setItem(API_CONFIG.STORAGE_KEYS.USER_INFO, JSON.stringify(user));

      return { success: true, user, access, refresh };
    } catch (error) {
      console.error('Login Error:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message
      });

      // Extract error message from various response formats
      let message = 'Login failed';
      
      if (error.response?.data?.error) {
        message = error.response.data.error;
      } else if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.non_field_errors) {
        message = Array.isArray(error.response.data.non_field_errors) 
          ? error.response.data.non_field_errors[0] 
          : error.response.data.non_field_errors;
      } else if (error.message) {
        message = error.message;
      }

      return { success: false, error: message };
    }
  }

  /**
   * Logout user and clear tokens
   */
  logout() {
    localStorage.removeItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(API_CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(API_CONFIG.STORAGE_KEYS.USER_INFO);
    return { success: true };
  }

  /**
   * Get current user from localStorage
   * @returns {Object|null} User info or null
   */
  getCurrentUser() {
    const userInfo = localStorage.getItem(API_CONFIG.STORAGE_KEYS.USER_INFO);
    return userInfo ? JSON.parse(userInfo) : null;
  }

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * Get stored access token
   * @returns {string|null}
   */
  getAccessToken() {
    return localStorage.getItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * Get stored refresh token
   * @returns {string|null}
   */
  getRefreshToken() {
    return localStorage.getItem(API_CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
  }

  /**
   * Refresh access token
   * @returns {Promise}
   */
  async refreshAccessToken() {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await axiosInstance.post(
        API_CONFIG.ENDPOINTS.REFRESH_TOKEN,
        { refresh: refreshToken }
      );

      const { access } = response.data;
      localStorage.setItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN, access);

      return { success: true, access };
    } catch (error) {
      this.logout();
      return { success: false, error: 'Token refresh failed' };
    }
  }
}

export default new AuthService();

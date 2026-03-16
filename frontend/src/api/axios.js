/**
 * Axios Instance Configuration
 * Handles JWT token injection and auto-refresh
 * Tracks loading state with global loader
 */

import axios from 'axios';
import { API_CONFIG } from '../constants/api';
import { getLoaderInstance } from '../context/LoaderContext';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * Injects JWT token into Authorization header
 * Shows global loader on request start
 */
axiosInstance.interceptors.request.use(
  (config) => {
    // Show global loader
    const loader = getLoaderInstance();
    if (loader?.increment) {
      loader.increment();
    }
    
    const token = localStorage.getItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log('API Request:', {
        method: config.method.toUpperCase(),
        url: config.url,
        hasAuth: !!token
      });
    }
    
    return config;
  },
  (error) => {
    // Hide loader on request error
    const loader = getLoaderInstance();
    if (loader?.decrement) {
      loader.decrement();
    }
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles 401 errors and token refresh
 * Hides global loader on response complete or error
 */
axiosInstance.interceptors.response.use(
  (response) => {
    // Hide loader on successful response
    const loader = getLoaderInstance();
    if (loader?.decrement) {
      loader.decrement();
    }
    return response;
  },
  async (error) => {
    // Hide loader on error response
    const loader = getLoaderInstance();
    if (loader?.decrement) {
      loader.decrement();
    }

    const originalRequest = error.config;

    // If 401 Unauthorized and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(API_CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
        
        if (!refreshToken) {
          // No refresh token, redirect to login
          localStorage.clear();
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Request new access token
        const response = await axios.post(
          `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REFRESH_TOKEN}`,
          { refresh: refreshToken }
        );

        const { access } = response.data;

        // Save new token
        localStorage.setItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN, access);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear storage and redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;

/**
 * Axios Instance Configuration
 * Handles JWT token injection and auto-refresh
 * Tracks loading state with global loader
 * Shows notifications for HTTP errors
 */

import axios from 'axios';
import { API_CONFIG } from '../constants/api';
import { getLoaderInstance } from '../context/LoaderContext';
import { error as showError } from '../utils/notify.jsx';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Map HTTP status codes to user-friendly error messages
 */
const getErrorMessage = (status, fallbackMessage) => {
  const statusMessages = {
    400: fallbackMessage || 'Solicitud inválida',
    401: 'Sesión expirada - por favor inicia sesión nuevamente',
    403: 'Acceso denegado - no tienes permisos para realizar esta acción',
    404: 'Recurso no encontrado',
    500: 'Error del servidor - intenta de nuevo más tarde',
    502: 'Servidor no disponible',
    503: 'Servicio temporalmente no disponible',
  };

  return statusMessages[status] || fallbackMessage || 'Error en la petición';
};

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
 * Shows notifications for HTTP errors
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
    // Hide loader on error
    const loader = getLoaderInstance();
    if (loader?.decrement) {
      loader.decrement();
    }

    const originalRequest = error.config;
    const status = error.response?.status;

    // Get error message from response or use default
    const errorMessage = 
      error.response?.data?.error || 
      error.response?.data?.detail || 
      getErrorMessage(status);

    // Show error notification (unless it's 401 during token refresh)
    if (status && status !== 401) {
      showError(errorMessage);
    }

    // If 401 Unauthorized and not already retrying
    if (status === 401 && !originalRequest._retry) {
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
        // Show session expired message when token refresh fails
        showError('Sesión expirada - por favor inicia sesión nuevamente');
        
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

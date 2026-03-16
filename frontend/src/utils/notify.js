/**
 * Notification Utilities
 * Global notification helpers using react-hot-toast
 * Easy-to-use wrappers for success, error, and info messages
 */

import toast from 'react-hot-toast';

/**
 * Show success notification
 * @param {string} message - Success message to display
 * @param {object} options - Optional toast options
 */
export const success = (message, options = {}) => {
  toast.success(message, {
    duration: 4000,
    position: 'top-right',
    ...options,
  });
};

/**
 * Show error notification
 * @param {string} message - Error message to display
 * @param {object} options - Optional toast options
 */
export const error = (message, options = {}) => {
  toast.error(message, {
    duration: 4000,
    position: 'top-right',
    ...options,
  });
};

/**
 * Show info notification
 * @param {string} message - Info message to display
 * @param {object} options - Optional toast options
 */
export const info = (message, options = {}) => {
  toast(message, {
    duration: 4000,
    position: 'top-right',
    icon: 'ℹ️',
    ...options,
  });
};

/**
 * Dismiss all notifications
 */
export const dismissAll = () => {
  toast.remove();
};

/**
 * Show loading notification
 * @param {string} message - Loading message to display
 * @returns {string} - Toast ID for later removal
 */
export const loading = (message = 'Cargando...') => {
  return toast.loading(message, {
    position: 'top-right',
  });
};

/**
 * Update a loading notification
 * @param {string} toastId - ID from loading() call
 * @param {object} options - Toast options (message, type, duration, etc)
 */
export const updateToast = (toastId, options = {}) => {
  toast((t) => (
    <span>{options.message || 'Actualizado'}</span>
  ), {
    id: toastId,
    ...options,
  });
};

export default {
  success,
  error,
  info,
  dismissAll,
  loading,
  updateToast,
};

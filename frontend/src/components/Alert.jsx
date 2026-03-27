/**
 * Alert Component
 * Componente reutilizable para mostrar alertas
 */

import React, { useEffect, useState } from 'react';

const Alert = ({ type = 'info', message, onClose, autoClose = true, duration = 5000 }) => {
  const [isVisible, setIsVisible] = useState(!!message);

  useEffect(() => {
    if (!message) {
      setIsVisible(false);
      return;
    }

    setIsVisible(true);

    if (autoClose) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [message, autoClose, duration, onClose]);

  if (!isVisible || !message) return null;

  const alertStyles = {
    success: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      border: 'border-green-400 dark:border-green-800',
      text: 'text-green-700 dark:text-green-400',
      icon: '✓',
    },
    error: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      border: 'border-red-400 dark:border-red-800',
      text: 'text-red-700 dark:text-red-400',
      icon: '✕',
    },
    warning: {
      bg: 'bg-yellow-100 dark:bg-yellow-900/30', 
      border: 'border-yellow-400 dark:border-yellow-800',
      text: 'text-yellow-700 dark:text-yellow-400',
      icon: '⚠',
    },
    info: {
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      border: 'border-blue-400 dark:border-blue-800',
      text: 'text-blue-700 dark:text-blue-400',
      icon: 'ℹ',
    },
  };

  const style = alertStyles[type] || alertStyles.info;

  return (
    <div
      className={`p-4 border-l-4 rounded ${style.bg} ${style.border} ${style.text} flex items-start gap-3 mb-4 animate-in fade-in slide-in-from-top`}
      role="alert"
    >
      <span className="text-lg font-bold flex-shrink-0">{style.icon}</span>
      <div className="flex-1">
        <p className="font-medium">{message}</p>
      </div>
      {!autoClose && (
        <button
          onClick={() => {
            setIsVisible(false);
            onClose?.();
          }}
          className="flex-shrink-0 text-lg opacity-50 hover:opacity-75 transition"
        >
          ✕
        </button>
      )}
    </div>
  );
};

export default Alert;

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
      bg: 'bg-green-100',
      border: 'border-green-400',
      text: 'text-green-700',
      icon: '✓',
    },
    error: {
      bg: 'bg-red-100',
      border: 'border-red-400',
      text: 'text-red-700',
      icon: '✕',
    },
    warning: {
      bg: 'bg-yellow-100',
      border: 'border-yellow-400',
      text: 'text-yellow-700',
      icon: '⚠',
    },
    info: {
      bg: 'bg-blue-100',
      border: 'border-blue-400',
      text: 'text-blue-700',
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

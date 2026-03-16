/**
 * Modal Component
 * Componente reutilizable para modales genéricos
 */

import React from 'react';

const Modal = ({ isOpen, title, children, onClose, onSubmit, submitText = 'Guardar', submitVariant = 'primary', isLoading = false }) => {
  if (!isOpen) return null;

  const handleBackdropMouseDown = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onMouseDown={handleBackdropMouseDown}
    >
      <div
        className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto"
        onMouseDown={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition text-2xl w-8 h-8 flex items-center justify-center"
            disabled={isLoading}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="p-6">{children}</div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
            disabled={isLoading}
          >
            Cancelar
          </button>
          <button
            onClick={onSubmit}
            disabled={isLoading}
            className={`px-4 py-2 text-white rounded-lg transition font-medium flex items-center gap-2 ${
              submitVariant === 'danger'
                ? 'bg-red-600 hover:bg-red-700 disabled:bg-red-400'
                : 'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400'
            }`}
          >
            {isLoading && <span className="animate-spin">⏳</span>}
            {submitText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Modal;

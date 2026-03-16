/**
 * FormField Component
 * Campo de formulario reutilizable con validación
 */

import React from 'react';

const FormField = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error,
  helperText,
  disabled = false,
  options = [], // Para select
  rows, // Para textarea
  className = '',
}) => {
  const baseInputClass =
    'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-100 disabled:cursor-not-allowed';

  const inputClass = error
    ? `${baseInputClass} border-red-500 focus:ring-red-500`
    : `${baseInputClass} border-gray-300`;

  const renderInput = () => {
    switch (type) {
      case 'select':
        return (
          <select
            name={name}
            value={value}
            onChange={onChange}
            disabled={disabled}
            className={inputClass}
          >
            <option value="">{placeholder || 'Seleccionar...'}</option>
            {options.map((opt) => (
              <option key={opt.id || opt.value} value={opt.id || opt.value}>
                {opt.label || opt.nombre || opt.name}
              </option>
            ))}
          </select>
        );

      case 'textarea':
        return (
          <textarea
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            rows={rows || 4}
            className={inputClass}
          />
        );

      case 'checkbox':
        return (
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id={name}
              name={name}
              checked={value}
              onChange={onChange}
              disabled={disabled}
              className="w-4 h-4 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
            />
            <label htmlFor={name} className="text-gray-700 cursor-pointer">
              {label}
            </label>
          </div>
        );

      default:
        return (
          <input
            type={type}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            className={inputClass}
          />
        );
    }
  };

  if (type === 'checkbox') {
    return (
      <div className={className}>
        {renderInput()}
        {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
        {helperText && <p className="text-gray-500 text-xs mt-1">{helperText}</p>}
      </div>
    );
  }

  return (
    <div className={className}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
      )}
      {renderInput()}
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
      {helperText && <p className="text-gray-500 text-xs mt-1">{helperText}</p>}
    </div>
  );
};

export default FormField;

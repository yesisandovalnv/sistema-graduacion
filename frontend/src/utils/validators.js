/**
 * Validators
 * Funciones de validación centralizadas
 */

export const validators = {
  // Email validation
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Required field
  isRequired: (value) => {
    if (typeof value === 'string') return value.trim().length > 0;
    if (typeof value === 'number') return value !== null && value !== undefined;
    return value !== null && value !== undefined;
  },

  // Minimum length
  minLength: (value, min) => {
    return String(value).length >= min;
  },

  // Maximum length
  maxLength: (value, max) => {
    return String(value).length <= max;
  },

  // Phone validation
  isValidPhone: (phone) => {
    const phoneRegex = /^[0-9\-\+\(\)\s]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 7;
  },

  // ID/Cedula validation
  isValidCedula: (cedula) => {
    const cedulaStr = String(cedula).trim();
    return cedulaStr.length > 0 && /^[0-9\-]+$/.test(cedulaStr);
  },

  // URL validation
  isValidUrl: (url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  // Password strength
  isValidPassword: (password) => {
    return password.length >= 8; // Mínimo 8 caracteres
  },

  // Only numbers
  isOnlyNumbers: (value) => {
    return /^\d+$/.test(value);
  },

  // Only letters and spaces
  isOnlyLetters: (value) => {
    return /^[a-zA-ZáéíóúÁÉÍÓÚ\s]+$/.test(value);
  },
};

/**
 * Validate form with error messages
 * @param {object} formData - Data to validate
 * @param {object} schema - Validation schema
 * @returns {object} Errors object
 */
export const validateForm = (formData, schema) => {
  const errors = {};

  Object.keys(schema).forEach((field) => {
    const rules = schema[field];
    const value = formData[field];

    // Required validation
    if (rules.required && !validators.isRequired(value)) {
      errors[field] = `${rules.label || field} es requerido`;
      return;
    }

    if (!validators.isRequired(value)) {
      return; // Skip other validations if not required and empty
    }

    // Email validation
    if (rules.email && !validators.isValidEmail(value)) {
      errors[field] = `${rules.label || field} no es válido`;
    }

    // Min length
    if (rules.minLength && !validators.minLength(value, rules.minLength)) {
      errors[field] = `${rules.label || field} debe tener mínimo ${rules.minLength} caracteres`;
    }

    // Max length
    if (rules.maxLength && !validators.maxLength(value, rules.maxLength)) {
      errors[field] = `${rules.label || field} debe tener máximo ${rules.maxLength} caracteres`;
    }

    // Phone
    if (rules.phone && !validators.isValidPhone(value)) {
      errors[field] = `${rules.label || field} no es válido`;
    }

    // Cedula
    if (rules.cedula && !validators.isValidCedula(value)) {
      errors[field] = `${rules.label || field} no es válido`;
    }

    // Custom validator
    if (rules.custom && !rules.custom(value)) {
      errors[field] = rules.customError || `${rules.label || field} es inválido`;
    }
  });

  return errors;
};

export default validators;

/**
 * useModal Hook
 * Hook personalizado para manejo de estado de modales
 */

import { useState } from 'react';

export const useModal = (initialData = null) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [formData, setFormData] = useState(initialData || {});

  const openModal = (data = null) => {
    if (data) {
      setFormData(data);
      setIsEditMode(true);
    } else {
      setFormData(initialData || {});
      setIsEditMode(false);
    }
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
    setFormData(initialData || {});
    setIsEditMode(false);
  };

  const resetForm = () => {
    setFormData(initialData || {});
  };

  const updateForm = (newData) => {
    setFormData((prev) => ({
      ...prev,
      ...newData,
    }));
  };

  return {
    isOpen,
    isEditMode,
    formData,
    openModal,
    closeModal,
    resetForm,
    updateForm,
    setFormData,
  };
};

export default useModal;

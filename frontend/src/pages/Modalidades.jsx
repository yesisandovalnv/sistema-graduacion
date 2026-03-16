/**
 * Modalidades Page - CRUD Completo
 * Manage graduation modalities
 */

import { useState, useEffect } from 'react';
import { API_CONFIG } from '../constants/api';
import { useCrud } from '../hooks/useCrud';

const Modalidades = () => {
  const {
    data: modalidades,
    loading,
    error,
    setError,
    list,
    refresh,
    create,
    update,
    remove,
  } = useCrud(API_CONFIG.ENDPOINTS.MODALIDADES);
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    activa: true,
  });

  useEffect(() => {
    list({}, { exceptionMessage: 'Error loading modalidades' });
  }, [list]);

  const resetForm = () => {
    setFormData({
      nombre: '',
      descripcion: '',
      activa: true,
    });
    setEditingId(null);
  };

  const openModal = (modalidad = null) => {
    if (modalidad) {
      setFormData(modalidad);
      setEditingId(modalidad.id);
    } else {
      resetForm();
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    resetForm();
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.nombre.trim()) {
      setError('El nombre es requerido');
      return;
    }

    try {
      if (editingId) {
        const result = await update(API_CONFIG.ENDPOINTS.MODALIDAD_DETAIL(editingId), formData);
        if (result.success) {
          setSuccess('Modalidad actualizada exitosamente');
          await refresh({ exceptionMessage: 'Error loading modalidades' });
          closeModal();
        } else {
          setError(result.error || 'Error al actualizar');
        }
      } else {
        const result = await create(formData);
        if (result.success) {
          setSuccess('Modalidad creada exitosamente');
          await refresh({ exceptionMessage: 'Error loading modalidades' });
          closeModal();
        } else {
          setError(result.error || 'Error al crear');
        }
      }
    } catch (err) {
      setError('Error en la operación');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Estás seguro que deseas eliminar esta modalidad?')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const result = await remove(API_CONFIG.ENDPOINTS.MODALIDAD_DETAIL(id));
      if (result.success) {
        setSuccess('Modalidad eliminada exitosamente');
        await refresh({ exceptionMessage: 'Error loading modalidades' });
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error al eliminar modalidad');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Modalidades</h1>
        <button
          onClick={() => openModal()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
        >
          ➕ Nueva Modalidad
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          {success}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modalidades.length > 0 ? (
            modalidades.map((modalidad) => (
              <div key={modalidad.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition border-l-4 border-blue-600">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-bold text-lg text-gray-800">{modalidad.nombre}</h3>
                  <span className={`text-xs px-2 py-1 rounded ${modalidad.activa ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {modalidad.activa ? '✓ Activa' : '✗ Inactiva'}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-4 min-h-12">{modalidad.descripcion}</p>
                <div className="text-xs text-gray-500 mb-4">
                  Creada: {new Date(modalidad.creada_en).toLocaleDateString()}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => openModal(modalidad)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm font-medium"
                  >
                    ✏️ Editar
                  </button>
                  <button
                    onClick={() => handleDelete(modalidad.id)}
                    className="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm font-medium"
                  >
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-8 text-gray-500">
              No hay modalidades registradas
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) {
              closeModal();
            }
          }}
        >
          <div
            className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md"
            onMouseDown={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl font-bold mb-4">
              {editingId ? '✏️ Editar Modalidad' : '➕ Nueva Modalidad'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre *
                </label>
                <input
                  type="text"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Ej: Tesis"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleInputChange}
                  rows="4"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Describe esta modalidad..."
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="activa"
                  checked={formData.activa}
                  onChange={handleInputChange}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm font-medium text-gray-700">
                  Modalidad activa
                </label>
              </div>

              <div className="flex space-x-2 pt-4">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  {editingId ? 'Actualizar' : 'Crear'}
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition font-medium"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Modalidades;

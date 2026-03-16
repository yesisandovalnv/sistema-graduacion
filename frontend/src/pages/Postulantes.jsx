/**
 * Postulantes Page - CRUD Moderno
 * List and manage applicants with modern UI and full CRUD
 */

import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import DataTable from '../components/DataTable';
import { useTheme } from '../context/ThemeContext';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import Alert from '../components/Alert';
import { useModal } from '../hooks/useModal';
import { useCrud } from '../hooks/useCrud';
import { Plus } from 'lucide-react';

const INITIAL_FORM_DATA = {
  nombre: '',
  apellido: '',
  ci: '',
  codigo_estudiante: '',
  usuario: '',
  telefono: '',
  carrera: '',
  facultad: '',
};

const Postulantes = () => {
  const { isDark } = useTheme();
  const {
    data: postulantes,
    loading,
    error,
    setError,
    meta,
    list,
    refresh,
    create,
    patch,
    remove,
  } = useCrud(API_CONFIG.ENDPOINTS.POSTULANTES);
  const [success, setSuccess] = useState('');

  const [usuarios, setUsuarios] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(
    INITIAL_FORM_DATA
  );

  useEffect(() => {
    fetchUsuarios();
    list({});
  }, []);

  const fetchUsuarios = async () => {
    try {
      const result = await api.getAll(API_CONFIG.ENDPOINTS.USUARIOS);
      if (result.success) {
        const data = Array.isArray(result.data) ? result.data : result.data.results || [];
        setUsuarios(data);
      }
    } catch (err) {
      console.error('Error loading usuarios:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'usuario' ? (value ? parseInt(value) : '') : value,
    });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const endpoint = isEditMode
        ? API_CONFIG.ENDPOINTS.POSTULANTE_DETAIL(formData.id)
        : API_CONFIG.ENDPOINTS.POSTULANTES;

      const payload = {
        nombre: formData.nombre,
        apellido: formData.apellido,
        ci: formData.ci,
        codigo_estudiante: formData.codigo_estudiante,
        usuario: formData.usuario,
        telefono: formData.telefono,
        carrera: formData.carrera,
        facultad: formData.facultad,
      };

      const result = isEditMode
        ? await patch(endpoint, payload)
        : await create(payload);

      if (result.success) {
        setSuccess(isEditMode ? 'Postulante actualizado exitosamente' : 'Postulante creado exitosamente');
        await refresh({});
        closeModal();
      } else {
        setError(result.error || 'Error en la operación');
      }
    } catch (err) {
      setError('Error en la operación');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (postulante) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este postulante?')) return;
    
    setError('');
    setSuccess('');

    try {
      const result = await remove(API_CONFIG.ENDPOINTS.POSTULANTE_DETAIL(postulante.id));
      if (result.success) {
        setSuccess('Postulante eliminado exitosamente');
        await refresh({});
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error al eliminar postulante');
    }
  };

  const columns = [
    {
      key: 'nombre',
      label: 'Nombre',
      sortable: true,
      render: (value, row) => `${row.nombre || ''} ${row.apellido || ''}`.trim() || '-',
    },
    {
      key: 'ci',
      label: 'CI',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'codigo_estudiante',
      label: 'Código Estudiante',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'carrera',
      label: 'Carrera',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'telefono',
      label: 'Teléfono',
      sortable: false,
      render: (value) => value || '-',
    },
  ];

  return (
    <Layout>
      <div className="p-4 md:p-8">
        {/* Encabezado */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Postulantes
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Administra los postulantes del sistema
            </p>
          </div>
          <button
            onClick={() => openModal()}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition font-medium shadow"
          >
            <Plus className="w-5 h-5" />
            Nuevo Postulante
          </button>
        </div>

        {/* Alertas */}
        {error && <Alert type="error" message={error} onClose={() => setError('')} autoClose={false} />}
        {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

        {/* Tabla */}
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-500 dark:text-gray-400">Cargando...</p>
            </div>
          </div>
        )}

        {!loading && (
          <DataTable
            data={postulantes || []}
            columns={columns}
            pageSize={10}
            isDark={isDark}
            onEdit={(row) =>
              openModal({
                ...row,
                usuario: row.usuario_id || row.usuario || '',
              })
            }
            onDelete={handleDelete}
          />
        )}

        {/* Modal */}
        <Modal
          isOpen={isOpen}
          title={isEditMode ? '✏️ Editar Postulante' : '➕ Nuevo Postulante'}
          onSubmit={handleSubmit}
          onClose={closeModal}
          submitText={isEditMode ? 'Actualizar' : 'Crear'}
          isLoading={isSubmitting}
        >
          <form className="space-y-4">
            <FormField
              label="Nombre"
              name="nombre"
              type="text"
              value={formData.nombre}
              onChange={handleInputChange}
              placeholder="Juan"
              required
            />

            <FormField
              label="Apellido"
              name="apellido"
              type="text"
              value={formData.apellido}
              onChange={handleInputChange}
              placeholder="Perez"
              required
            />

            <FormField
              label="Teléfono"
              name="telefono"
              type="text"
              value={formData.telefono}
              onChange={handleInputChange}
              placeholder="70000000"
              required
            />

            <FormField
              label="CI"
              name="ci"
              type="text"
              value={formData.ci}
              onChange={handleInputChange}
              placeholder="12345678"
              required
            />

            <FormField
              label="Código de Estudiante"
              name="codigo_estudiante"
              type="text"
              value={formData.codigo_estudiante}
              onChange={handleInputChange}
              placeholder="202412345"
              required
            />

            <FormField
              label="Carrera"
              name="carrera"
              type="text"
              value={formData.carrera}
              onChange={handleInputChange}
              placeholder="Ingenieria"
            />

            <FormField
              label="Facultad"
              name="facultad"
              type="text"
              value={formData.facultad}
              onChange={handleInputChange}
              placeholder="Facultad de Tecnologia"
            />

            <FormField
              label="Usuario"
              name="usuario"
              type="select"
              value={formData.usuario}
              onChange={handleInputChange}
              options={usuarios.map((user) => ({
                id: user.id,
                label: `${user.username} - ${user.first_name || ''} ${user.last_name || ''}`.trim(),
              }))}
              required
            />
          </form>
        </Modal>
      </div>
    </Layout>
  );
};

export default Postulantes;

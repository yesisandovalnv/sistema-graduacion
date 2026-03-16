# Guía: Implementar CRUD Completo en Páginas

Las páginas creadas tienen estructura base pero los botones de CRUD aún necesitan conectarse a operaciones reales. Esta guía muestra cómo implementarlos.

## 📋 Estado Actual

### ✅ Qué Ya Existe
- Servicio API completo (`src/api/api.js`)
- Componentes de UI con botones
- Estados React (useState)
- Handlers vacíos en botones

### ❌ Qué Falta
- Lógica de create (mostrar modal, validar, guardar)
- Lógica de update (cargar datos, editar, guardar)
- Confirmación de delete
- Notificaciones de éxito/error
- Refresh de datos después de acciones
- Validación de formularios

## 🎯 Patrón General CRUD

### 1. Crear (Create)

**Flujo:**
```
1. Usuario hace click en "Nuevo"
   ↓
2. Modal se abre con formulario vacío
   ↓
3. Usuario llena form + click "Guardar"
   ↓
4. Valida datos
   ↓
5. Si válido: POST a backend
   ↓
6. Si éxito: Modal cierra, datos refrescan
   ↓
7. Si error: Muestra error en modal
```

**Código base:**
```javascript
const handleCreate = async (formData) => {
  try {
    setLoading(true);
    const response = await api.create(
      '/api/postulantes/', 
      formData
    );
    
    if (response.success) {
      // Mostrar notificación
      setSuccess('Postulante creado exitosamente');
      
      // Cerrar modal
      setShowModal(false);
      
      // Refrescar lista
      await loadPostulantes();
      
      // Limpiar form
      setFormData({});
    } else {
      setError(response.error);
    }
  } catch (err) {
    setError('Error al crear: ' + err.message);
  } finally {
    setLoading(false);
  }
};

// En botón
<button 
  onClick={() => setShowModal(true)}
  className="btn btn-primary"
>
  + Nuevo Postulante
</button>
```

### 2. Leer (Read)

**Ya existe:** Las páginas cargan automáticamente en `useEffect`.

**Para mejorar:**
```javascript
// Con búsqueda
const handleSearch = async (searchTerm) => {
  setSearchTerm(searchTerm);
  setPage(1);
  
  const response = await api.getAll(
    '/api/postulantes/',
    { search: searchTerm, page: 1 }
  );
  
  if (response.success) {
    setPostulantes(response.results);
    setTotalCount(response.count);
  }
};

// Con filtros
const handleFilter = async (filtroKey, filtroValue) => {
  const params = {
    [filtroKey]: filtroValue,
    page: 1
  };
  
  const response = await api.getAll(
    '/api/postulaciones/',
    params
  );
  
  if (response.success) {
    setPostulaciones(response.results);
  }
};
```

### 3. Actualizar (Update)

**Flujo:**
```
1. Usuario hace click en "Editar" en fila
   ↓
2. Cargar datos actuales del objeto
   ↓
3. Modal se abre con datos pre-llenar
   ↓
4. Usuario modifica + click "Guardar"
   ↓
5. Valida datos
   ↓
6. Si válido: PUT a backend
   ↓
7. Si éxito: Modal cierra, datos refrescan
   ↓
8. Si error: Muestra error en modal
```

**Código:**
```javascript
const [editingId, setEditingId] = useState(null);
const [formData, setFormData] = useState({});

const handleEdit = async (id) => {
  try {
    setLoading(true);
    
    // Cargar datos del objeto
    const response = await api.getById(
      `/api/postulantes/${id}/`
    );
    
    if (response.success) {
      // Pre-llenar form
      setFormData(response);
      setEditingId(id);
      setShowModal(true);
    }
  } catch (err) {
    setError('Error: ' + err.message);
  } finally {
    setLoading(false);
  }
};

const handleUpdate = async (formData) => {
  try {
    setLoading(true);
    
    const response = await api.update(
      `/api/postulantes/${editingId}/`,
      formData
    );
    
    if (response.success) {
      setSuccess('Postulante actualizado exitosamente');
      setShowModal(false);
      setEditingId(null);
      await loadPostulantes();
    } else {
      setError(response.error);
    }
  } catch (err) {
    setError('Error: ' + err.message);
  } finally {
    setLoading(false);
  }
};

// En botón
<button 
  onClick={() => handleEdit(postulante.id)}
  className="btn btn-info btn-sm"
>
  ✏️ Editar
</button>
```

### 4. Eliminar (Delete)

**Flujo:**
```
1. Usuario hace click en "Eliminar" en fila
   ↓
2. Muestra diálogo de confirmación
   ↓
3. Si confirma: DELETE a backend
   ↓
4. Si éxito: Elemento se quita de lista
   ↓
5. Si error: Muestra error
```

**Código:**
```javascript
const handleDelete = async (id) => {
  // Confirmar antes de eliminar
  if (!window.confirm('¿Estás seguro?')) {
    return;
  }
  
  try {
    setLoading(true);
    
    const response = await api.delete(
      `/api/postulantes/${id}/`
    );
    
    if (response.success) {
      setSuccess('Postulante eliminado exitosamente');
      
      // Actualizar lista
      setPostulantes(
        postulantes.filter(p => p.id !== id)
      );
    } else {
      setError(response.error);
    }
  } catch (err) {
    setError('Error: ' + err.message);
  } finally {
    setLoading(false);
  }
};

// En botón
<button 
  onClick={() => handleDelete(postulante.id)}
  className="btn btn-danger btn-sm"
>
  🗑️ Eliminar
</button>
```

## 🎬 Paso a Paso: Completar `Postulantes.jsx`

### Paso 1: Instalar React Hook Form (opcional pero recomendado)
```bash
npm install react-hook-form
```

### Paso 2: Crear Hook para Modal
Crea `src/hooks/useModal.js`:
```javascript
import { useState } from 'react';

export const useModal = (initialState = false) => {
  const [isOpen, setIsOpen] = useState(initialState);
  
  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  const toggle = () => setIsOpen(!isOpen);
  
  return { isOpen, open, close, toggle };
};
```

### Paso 3: Crear Componente Modal Reutilizable
Crea `src/components/Modal.jsx`:
```javascript
export const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children 
}) => {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        {children}
      </div>
    </div>
  );
};
```

### Paso 4: Crear Componente de Notificaciones
Crea `src/components/Alert.jsx`:
```javascript
export const Alert = ({ type, message, onClose }) => {
  if (!message) return null;
  
  const colors = {
    success: 'bg-green-100 text-green-700 border-green-400',
    error: 'bg-red-100 text-red-700 border-red-400',
    info: 'bg-blue-100 text-blue-700 border-blue-400',
  };
  
  return (
    <div className={`border px-4 py-3 rounded ${colors[type]}`}>
      <div className="flex justify-between">
        <span>{message}</span>
        <button onClick={onClose}>✕</button>
      </div>
    </div>
  );
};
```

### Paso 5: Actualizar Postulantes.jsx

```javascript
import { useState, useEffect } from 'react';
import { api } from '../api/api';
import { Modal } from '../components/Modal';
import { Alert } from '../components/Alert';
import { useModal } from '../hooks/useModal';

export default function Postulantes() {
  const [postulantes, setPostulantes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  // Estados de notificación
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  // Estados de modal
  const modal = useModal();
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    ci: '',
    codigo_estudiante: '',
    telefono: '',
    carrera: '',
    facultad: '',
  });

  // Cargar postulantes
  const loadPostulantes = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        search: searchTerm,
      };
      
      const result = await api.getAll('/api/postulantes/', params);
      
      if (result.success) {
        setPostulantes(result.results);
        setTotalCount(result.count);
      } else {
        setError(result.error || 'Error al cargar postulantes');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPostulantes();
  }, [page, searchTerm]);

  // Handlers CRUD
  const handleCreate = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      const result = await api.create(
        '/api/postulantes/',
        formData
      );
      
      if (result.success) {
        setSuccess('Postulante creado exitosamente');
        modal.close();
        setFormData({ nombre: '', apellido: '', ... });
        await loadPostulantes();
      } else {
        setError(result.error || 'Error al crear');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (id) => {
    try {
      setLoading(true);
      
      const result = await api.getById(`/api/postulantes/${id}/`);
      
      if (result.success) {
        setFormData(result);
        setEditingId(id);
        modal.open();
      } else {
        setError('Error al cargar datos');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      const result = await api.update(
        `/api/postulantes/${editingId}/`,
        formData
      );
      
      if (result.success) {
        setSuccess('Postulante actualizado exitosamente');
        modal.close();
        setEditingId(null);
        await loadPostulantes();
      } else {
        setError(result.error || 'Error al actualizar');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar?')) {
      return;
    }
    
    try {
      setLoading(true);
      
      const result = await api.delete(`/api/postulantes/${id}/`);
      
      if (result.success) {
        setSuccess('Postulante eliminado');
        setPostulantes(postulantes.filter(p => p.id !== id));
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setEditingId(null);
    setFormData({
      nombre: '',
      apellido: '',
      ci: '',
      codigo_estudiante: '',
      telefono: '',
      carrera: '',
      facultad: '',
    });
    modal.open();
  };

  const handleSubmitForm = (e) => {
    if (editingId) {
      handleUpdate(e);
    } else {
      handleCreate(e);
    }
  };

  return (
    <div className="p-6">
      <Alert
        type="success"
        message={success}
        onClose={() => setSuccess('')}
      />
      <Alert
        type="error"
        message={error}
        onClose={() => setError('')}
      />

      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Postulantes</h1>
        <button
          onClick={handleOpenCreate}
          className="btn btn-primary"
        >
          + Nuevo Postulante
        </button>
      </div>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Buscar por nombre..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setPage(1);
          }}
          className="input input-bordered w-full"
        />
      </div>

      {loading && <p className="text-center py-4">Cargando...</p>}

      {!loading && (
        <>
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>CI</th>
                  <th>Carrera</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {postulantes.map((postulante) => (
                  <tr key={postulante.id}>
                    <td>
                      {postulante.nombre} {postulante.apellido}
                    </td>
                    <td>{postulante.ci}</td>
                    <td>{postulante.carrera}</td>
                    <td>
                      <button
                        onClick={() => handleEdit(postulante.id)}
                        className="btn btn-sm btn-info mr-2"
                      >
                        ✏️ Editar
                      </button>
                      <button
                        onClick={() => handleDelete(postulante.id)}
                        className="btn btn-sm btn-danger"
                      >
                        🗑️ Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex justify-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="btn"
            >
              ← Anterior
            </button>
            <span className="px-4 py-2">
              Página {page} de {Math.ceil(totalCount / 10)}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(totalCount / 10)}
              className="btn"
            >
              Siguiente →
            </button>
          </div>
        </>
      )}

      {/* Modal para crear/editar */}
      <Modal
        isOpen={modal.isOpen}
        onClose={modal.close}
        title={editingId ? 'Editar Postulante' : 'Nuevo Postulante'}
      >
        <form onSubmit={handleSubmitForm}>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Nombre"
              value={formData.nombre}
              onChange={(e) => 
                setFormData({...formData, nombre: e.target.value})
              }
              required
              className="input input-bordered w-full"
            />
            <input
              type="text"
              placeholder="Apellido"
              value={formData.apellido}
              onChange={(e) => 
                setFormData({...formData, apellido: e.target.value})
              }
              required
              className="input input-bordered w-full"
            />
            <input
              type="text"
              placeholder="Cédula"
              value={formData.ci}
              onChange={(e) => 
                setFormData({...formData, ci: e.target.value})
              }
              required
              className="input input-bordered w-full"
            />
            <input
              type="text"
              placeholder="Código Estudiante"
              value={formData.codigo_estudiante}
              onChange={(e) => 
                setFormData({...formData, codigo_estudiante: e.target.value})
              }
              className="input input-bordered w-full"
            />
            <input
              type="tel"
              placeholder="Teléfono"
              value={formData.telefono}
              onChange={(e) => 
                setFormData({...formData, telefono: e.target.value})
              }
              className="input input-bordered w-full"
            />
            <input
              type="text"
              placeholder="Carrera"
              value={formData.carrera}
              onChange={(e) => 
                setFormData({...formData, carrera: e.target.value})
              }
              className="input input-bordered w-full"
            />
          </div>

          <div className="mt-6 flex justify-end gap-2">
            <button
              type="button"
              onClick={modal.close}
              className="btn"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
```

## 🔁 Aplicar el Mismo Patrón a Otras Páginas

Reemplaza los valores principales en cada página:

### Postulaciones.jsx
```javascript
const endpoint = '/api/postulaciones/';
const formFields = [
  'titulo_trabajo', 'tutor', 'gestion', 'modalidad',
  'observaciones'
];
```

### Documentos.jsx
```javascript
const endpoint = '/api/documentos/';
const formFields = [
  'postulacion', 'tipo_documento', 'archivo', 'observaciones'
];
```

### Usuarios.jsx
```javascript
const endpoint = '/api/usuarios/';
const formFields = [
  'username', 'email', 'first_name', 'last_name', 'role'
];
```

### Modalidades.jsx
```javascript
const endpoint = '/api/modalidades/';
const formFields = ['nombre', 'descripcion'];
```

## ✅ Checklist de Implementación

- [ ] Crear componentes Modal.jsx y Alert.jsx
- [ ] Crear hook useModal.js
- [ ] Actualizar Postulantes.jsx con CRUD completo
- [ ] Actualizar Postulaciones.jsx con CRUD
- [ ] Actualizar Documentos.jsx con CRUD
- [ ] Actualizar Usuarios.jsx con CRUD
- [ ] Actualizar Modalidades.jsx con CRUD
- [ ] Probar create (crear nuevo objeto)
- [ ] Probar read (cargar lista y buscar)
- [ ] Probar update (editar objeto existente)
- [ ] Probar delete (eliminar objeto)
- [ ] Validar respuestas de error del backend
- [ ] Verificar que los tokens se refrescan
- [ ] Prueba con múltiples usuarios

¡Listo! Usa este patrón en todas tus páginas. 🚀

# 🔧 GUÍA DETALLADA DE REMEDIACCIÓN - REACT FRONTEND

---

## PRIORIDAD 1: FIX TOKEN REFRESH RACE CONDITION (4 horas, CRÍTICO)

### Problema Actual (axios.js:110-140)
```javascript
// PROBLEMA: Si 2 requests fallan 401 simultáneamente
if (status === 401 && !originalRequest._retry) {
  originalRequest._retry = true;
  
  // Request A y B ambas ejecutan refresh simultáneamente
  // → Response A actualiza token
  // → Response B intenta refresh con token de Request A
  // → Posible infinite loop
}
```

### Solución Recomendada (Promesa singleton)
**Archivo:** `frontend/src/api/axiosRefreshQueue.js` (NUEVO)

```javascript
/**
 * Token refresh queue - previene double refresh
 */
let refreshPromise = null;

export const getRefreshPromise = async (refreshToken) => {
  // Si ya hay refresh en flight, retornar del mismo
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const response = await axios.post(
        `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REFRESH_TOKEN}`,
        { refresh: refreshToken }
      );
      return response.data.access;
    } finally {
      refreshPromise = null; // Reset para próximo refresh
    }
  })();

  return refreshPromise;
};
```

**Actualizar axios.js:**
```javascript
import { getRefreshPromise } from './axiosRefreshQueue';

// Response interceptor
async (error) => {
  const originalRequest = error.config;
  const status = error.response?.status;

  if (status === 401 && !originalRequest._retry) {
    originalRequest._retry = true;
    
    try {
      const refreshToken = localStorage.getItem(API_CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
      
      if (!refreshToken) {
        // No token → logout
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      // 🔑 CLAVE: Usa singleton promise
      const access = await getRefreshPromise(refreshToken);
      
      localStorage.setItem(API_CONFIG.STORAGE_KEYS.ACCESS_TOKEN, access);
      originalRequest.headers.Authorization = `Bearer ${access}`;
      
      return axiosInstance(originalRequest);
    } catch (refreshError) {
      // Refresh falló → logout
      localStorage.clear();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    }
  }
  
  return Promise.reject(error);
}
```

**Verificación:**
```bash
# Test: 2 requests simultáneos en login expirado
npm test -- axiosRefreshQueue.test.js
```

---

## PRIORIDAD 2: REQUEST TIMEOUT + RETRY (2 horas, ALTO)

### Problema Actual
- axios default timeout = ∞ (infinito)
- Si backend lento (30s), UI cuelga 30s

### Solución
**Archivo:** Actualizar `frontend/src/api/axios.js`

```javascript
const axiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000, // 30 segundos
});

// Request interceptor con retry exponencial
const retryConfig = {
  maxRetries: 3,
  retryDelay: (attemptNumber) => {
    // Exponential backoff: 1s, 2s, 4s
    return Math.pow(2, attemptNumber) * 1000;
  },
  retryableStatuses: [408, 429, 500, 502, 503, 504],
};

// Envolver request con retry logic
const requestWithRetry = async (config, attemptNumber = 0) => {
  try {
    return await axiosInstance.request(config);
  } catch (error) {
    const shouldRetry =
      attemptNumber < retryConfig.maxRetries &&
      (error.code === 'ECONNABORTED' || // timeout
       retryConfig.retryableStatuses.includes(error.response?.status));

    if (shouldRetry) {
      const delay = retryConfig.retryDelay(attemptNumber);
      console.log(`Retry attempt ${attemptNumber + 1}/${retryConfig.maxRetries} after ${delay}ms`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return requestWithRetry(config, attemptNumber + 1);
    }

    throw error;
  }
};
```

---

## PRIORIDAD 3: REFACTOR CRUDs - CREAR useCrudPage HOOK (2-3 días, CRÍTICO)

### Problema Actual
Cada página repite 50+ líneas de lógica:
```javascript
// Postulantes.jsx
const handleSubmit = async () => {
  setIsSubmitting(true);
  setError('');
  setSuccess('');
  
  try {
    const endpoint = isEditMode ? POST_DETAIL(formData.id) : POSTULANTES;
    const result = isEditMode ? await patch(...) : await create(...);
    
    if (result.success) {
      setSuccess(msg);
      await refresh();
      closeModal();
    } else {
      setError(result.error || 'Error');
    }
  } catch (err) {
    setError('Error en operación');
  } finally {
    setIsSubmitting(false);
  }
};
```

### Solución: Crear hook `useCrudPage`
**Archivo:** `frontend/src/hooks/useCrudPage.js` (NUEVO)

```javascript
/**
 * Hook para consolidar lógica CRUD repetida en páginas
 * Típicamente usado en: Postulantes, Usuarios, Postulaciones, Documentos
 */

import { useCallback, useState } from 'react';
import { useCrud } from './useCrud';
import { useModal } from './useModal';

export const useCrudPage = (endpoint, initialFormData = {}) => {
  const crud = useCrud(endpoint);
  const modal = useModal(initialFormData);
  
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = useCallback(async (payload, customMessages = {}) => {
    setIsSubmitting(true);
    crud.setError('');
    setSuccess('');

    try {
      const isEditMode = !!payload.id;
      const submitEndpoint = isEditMode 
        ? `${endpoint}${payload.id}/`
        : endpoint;

      const result = isEditMode
        ? await crud.patch(submitEndpoint, payload)
        : await crud.create(payload);

      if (result.success) {
        const msg = customMessages[isEditMode ? 'updateSuccess' : 'createSuccess']
          || (isEditMode ? 'Actualizado exitosamente' : 'Creado exitosamente');
        setSuccess(msg);
        
        await crud.refresh();
        modal.closeModal();
        
        return { success: true };
      } else {
        const errorMsg = customMessages?.submitError || result.error || 'Error en la operación';
        crud.setError(errorMsg);
        return { success: false, error: errorMsg };
      }
    } catch (err) {
      const errorMsg = customMessages?.exceptionError || 'Error inesperado';
      crud.setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setIsSubmitting(false);
    }
  }, [endpoint, crud, modal, customMessages]);

  const handleDelete = useCallback(async (item, customMessages = {}) => {
    if (!window.confirm(customMessages?.confirmDelete || '¿Está seguro?')) {
      return { success: false };
    }

    crud.setError('');
    setSuccess('');

    try {
      const result = await crud.remove(`${endpoint}${item.id}/`);
      
      if (result.success) {
        const msg = customMessages?.deleteSuccess || 'Eliminado exitosamente';
        setSuccess(msg);
        await crud.refresh();
        return { success: true };
      } else {
        const errorMsg = customMessages?.deleteError || result.error || 'Error al eliminar';
        crud.setError(errorMsg);
        return { success: false, error: errorMsg };
      }
    } catch (err) {
      const errorMsg = customMessages?.exceptionError || 'Error al eliminar';
      crud.setError(errorMsg);
      return { success: false, error: errorMsg };
    }
  }, [endpoint, crud, modal, customMessages]);

  return {
    // CRUD data
    ...crud,
    
    // Modal management
    ...modal,
    
    // Submit handlers
    handleSubmit,
    handleDelete,
    success,
    setSuccess,
    isSubmitting,
  };
};
```

### Uso en Postulantes.jsx (SIMPLIFICADO)
```javascript
// ANTES: 350 LOC
// DESPUÉS: 180 LOC

const Postulantes = () => {
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
    isOpen,
    isEditMode,
    formData,
    openModal,
    closeModal,
    setFormData,
    handleSubmit,
    handleDelete,
    success,
    setSuccess,
    isSubmitting,
  } = useCrudPage(API_CONFIG.ENDPOINTS.POSTULANTES, INITIAL_FORM_DATA);

  useEffect(() => {
    list({});
  }, []);

  const onSubmit = () => {
    handleSubmit(formData, {
      createSuccess: 'Postulante creado',
      updateSuccess: 'Postulante actualizado',
    });
  };

  const onDelete = (postulante) => {
    handleDelete(postulante, {
      confirmDelete: '¿Eliminar postulante?',
      deleteSuccess: 'Postulante eliminado',
    });
  };

  // Rest es igual (renderizar tabla, modal, etc)
};
```

---

## PRIORIDAD 4: MIGRAR POSTULANTES A BÚSQUEDA SERVIDOR (1 día, CRÍTICO)

### Problema Actual
```javascript
// DataTable.jsx - O(n*m) cada keystroke
const filteredData = useMemo(() => {
  return data.filter(item =>
    Object.values(item).some(value =>
      String(value).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );
}, [data, searchTerm]);
```

Con 5000 postulantes = **LAG visible**

### Solución: Cambiar Postulantes.jsx a usar `useListFilters`

```javascript
// CAMBIOS NECESARIOS:

// 1. Remover DataTable, usar Table
- import DataTable from '../components/DataTable';
+ import Table from '../components/Table';

// 2. Agregar useListFilters
const { data: postulantes, loading, error, list, refresh } = useCrud(...);
+ const { search, setSearch, page, setPage } = useListFilters(list);

// 3. En JSX, cambiar DataTable → Table
- <DataTable data={postulantes} columns={columns} pageSize={10} />
+ <Table data={postulantes} columns={columns} />

// 4. Agregar search bar (copy Usuarios.jsx)
+ <input
+   type="text"
+   placeholder="Buscar..."
+   value={search}
+   onChange={(e) => setSearch(e.target.value)}
+ />
```

**Resultado:** 
- ❌ O(n*m) local → ✅ O(log n) servidor
- 5000 registros OK
- URL sincronizada con búsqueda

---

## PRIORIDAD 5: UNIFICAR DataTable + Table (1 día, ALTO)

### Crear: SmartTable.jsx (NUEVO)
```javascript
/**
 * SmartTable - Tabla unificada género (cliente o servidor)
 * Reemplaza DataTable.jsx + Table.jsx
 */

const SmartTable = ({
  data = [],
  columns = [],
  searchStrategy = 'none', // 'none' | 'client' | 'server'
  searchTerm = '',
  onSearch = () => {},
  loading = false,
  onEdit,
  onDelete,
  onView,
  pageSize = 10,
  pageMeta = null, // Para server-side: { count, next, previous }
  onPageChange = () => {},
}) => {
  if (searchStrategy === 'client') {
    // DataTable behavior - search local
    return <DataTableImpl data={data} columns={columns} {...props} />;
  } else if (searchStrategy === 'server') {
    // Table + búsqueda servidor
    return <TableWithSearch data={data} columns={columns} {...props} />;
  } else {
    // Simple table sin búsqueda
    return <TableImpl data={data} columns={columns} {...props} />;
  }
};
```

### Migración:
```javascript
// Postulantes.jsx - client-side (temporario, después server)
<SmartTable 
  data={postulantes}
  searchStrategy="client"
  columns={columns}
  onEdit={handleEdit}
/>

// Usuarios.jsx - server-side
<SmartTable 
  data={usuarios}
  searchStrategy="server"
  searchTerm={search}
  onSearch={setSearch}
  pageMeta={meta}
  onPageChange={setPage}
/>
```

---

## PRIORIDAD 6: CACHE DROPDOWNS (8 horas, ALTO)

### Problema
```javascript
// Documentos.jsx - carga TODO cada modal open
const fetchDropdownData = async () => {
  const [tiposRes, postRes] = await Promise.all([
    api.getAll(API_CONFIG.ENDPOINTS.TIPOS_DOCUMENTO),
    api.getAll(API_CONFIG.ENDPOINTS.POSTULACIONES),
  ]);
};
```

Con 10k postulaciones = **5s+ espera cada modal**

### Solución: Crear `useDropdownCache`
**Archivo:** `frontend/src/hooks/useDropdownCache.js` (NUEVO)

```javascript
/**
 * Hook para cachear datos de dropdowns
 * Invalida solo en create/delete
 */

import { useEffect, useState, useRef } from 'react';
import api from '../api/api';

const dropdownCache = {}; // Memoria compartida

export const useDropdownCache = (endpoint, key) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const isFetchingRef = useRef(false);

  const fetchData = async (invalidate = false) => {
    // Si ya cacheado y no invalidate, retornar
    if (dropdownCache[key] && !invalidate) {
      setData(dropdownCache[key]);
      return;
    }

    // Si ya fetching, esperar
    if (isFetchingRef.current) {
      // Poll until ready
      const checkInterval = setInterval(() => {
        if (dropdownCache[key]) {
          setData(dropdownCache[key]);
          clearInterval(checkInterval);
        }
      }, 100);
      return;
    }

    isFetchingRef.current = true;
    setLoading(true);

    try {
      const result = await api.getAll(endpoint);
      const normalizedData = Array.isArray(result.data) 
        ? result.data 
        : result.data.results || [];
      
      dropdownCache[key] = normalizedData;
      setData(normalizedData);
    } catch (err) {
      setError(err.message);
    } finally {
      isFetchingRef.current = false;
      setLoading(false);
    }
  };

  const invalidate = () => fetchData(true);

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, invalidate };
};

// Global invalidator (usar después de create/delete)
export const invalidateDropdowns = (...keys) => {
  keys.forEach(key => {
    delete dropdownCache[key];
  });
};
```

### Uso en Documentos.jsx
```javascript
const Documentos = () => {
  const { data: tiposDocumento } = useDropdownCache(
    API_CONFIG.ENDPOINTS.TIPOS_DOCUMENTO,
    'tipos-documento'
  );
  const { data: postulaciones } = useDropdownCache(
    API_CONFIG.ENDPOINTS.POSTULACIONES,
    'postulaciones'
  );

  const handleCreate = async (payload) => {
    const result = await create(payload);
    if (result.success) {
      invalidateDropdowns('postulaciones'); // Invalidar después crear
    }
  };
};
```

---

## PRIORIDAD 7: REPORTES - EXTRACT COMPONENTS (2 días, ALTO)

### Problema Actual (500 LOC monolítico)
```javascript
const Reportes = () => {
  return (
    <div>
      {activeTab === 'general' && renderGeneralStats()}
      {activeTab === 'tutores' && renderTutores()}
      {activeTab === 'carreras' && renderCarreras()}
    </div>
  );
};

// 3 funciones render inline = 150+ LOC no modularizado
```

### Solución: Extraer componentes

**Archivo:** `frontend/src/components/ReportCard.jsx` (NUEVO)
```javascript
const ReportCard = ({ title, value, icon, color = 'blue' }) => (
  <div className="p-6 rounded-xl border bg-white dark:bg-gray-800">
    <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
    <p className={`text-3xl font-bold mt-2 text-${color}-600`}>{value}</p>
    <div className="text-4xl mt-4">{icon}</div>
  </div>
);

export default ReportCard;
```

**Archivo:** `frontend/src/components/GeneralReportTab.jsx` (NUEVO)
```javascript
const GeneralReportTab = ({ reportData, loading }) => {
  if (loading) return <TableSkeleton />;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <ReportCard 
        title="Total Postulantes"
        value={reportData.total_postulantes}
        icon="👥"
      />
      <ReportCard 
        title="Total Postulaciones"
        value={reportData.total_postulaciones}
        icon="📋"
      />
      {/* ... más cards ... */}
    </div>
  );
};
```

**Actualizar Reportes.jsx:**
```javascript
const Reportes = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('general');

  useEffect(() => {
    fetchReportData();
  }, [activeTab]);

  return (
    <div>
      <TabSwitcher 
        tabs={['general', 'tutores', 'carreras']}
        active={activeTab}
        onChange={setActiveTab}
      />
      
      {activeTab === 'general' && <GeneralReportTab reportData={reportData} />}
      {activeTab === 'tutores' && <TutoresReportTab reportData={reportData} />}
      {activeTab === 'carreras' && <CarrerasReportTab reportData={reportData} />}
    </div>
  );
};
```

---

## PRIORIDAD 8: ROLE CHECK FIX (2 horas, ALTO)

**Archivo:** Actualizar `frontend/src/components/ProtectedRoute.jsx`

```javascript
const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole) {
    // 🔧 FIX: Manejar role undefined
    const userRole = user?.role 
      || (user?.is_superuser ? 'admin' : null)
      || (user?.is_staff ? 'staff' : null);

    // Si no tiene role pero requiredRole existe
    if (!userRole) {
      console.warn('User role is undefined', user);
      return <AccessDenied reason="Usuario sin rol asignado" />;
    }

    const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    
    // 🔧 FIX: Case-insensitive comparison
    const isAllowed = allowedRoles.some(role => 
      userRole.toLowerCase() === role.toLowerCase()
    );

    if (!isAllowed) {
      return <AccessDenied reason={`Se requiere rol: ${allowedRoles.join(' o ')}`} />;
    }
  }

  return children;
};
```

---

## CHECKLIST DE IMPLEMENTACIÓN

```
SEMANA 1:
☐ Token refresh race condition (4h)
☐ Request timeout (2h)
☐ useCrudPage hook (16h)
☐ Aplicar useCrudPage a Postulantes, Usuarios (8h)

SEMANA 2:
☐ Migrar Postulantes búsqueda servidor (8h)
☐ SmartTable unificada (8h)
☐ Dropdown cache (8h)
☐ Load testing 50 users

SEMANA 3:
☐ Reportes extract components (16h)
☐ Unit tests useCrudPage, useModal (12h)
☐ JSDoc completo

SEMANA 4:
☐ Role check fix (2h)
☐ CSRF token header (4h)
☐ Error boundary (4h)
☐ Final testing
```

---

## 📊 IMPACTO ESPERADO

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **LOC Duplicado** | ~300 | ~50 | -83% |
| **Postulantes búsqueda lag** | 500ms con 1000 items | 100ms | -80% |
| **Modal dropdown wait** | 5s+ | <500ms | -90% |
| **Token refresh bugs** | 2-3 al mes | 0 | -100% |
| **Component tamaño promedio** | 350 LOC | 200 LOC | -43% |
| **Error handling coverage** | 60% | 85% | +25% |

---

*Documento: Guía implementación remediacción*  
*Fecha: 23 de marzo de 2026*  
*Estado: Listo para desarrollo*

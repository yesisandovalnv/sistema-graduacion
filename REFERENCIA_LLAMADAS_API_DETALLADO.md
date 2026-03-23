# REFERENCIA RÁPIDA: LLAMADAS API FRONTEND vs DEFINIDAS

**Análisis binario: ✅ = Usado, ❌ = No usado, ⚠️ = Error**

---

## MAPA DE ENDPOINTS

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CONFIGURACIÓN API (api.js)                                              │
├─────────────────────────────────────────────────────────────────────────┤
│ Total Endpoints Definidos: 24                                           │
│ Endpoints Usados: 17 (71%)                                              │
│ Endpoints Huérfanos: 7 (29%)                                            │
│ Endpoints Con Errores: 1 (export Reportes)                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## TABLA DETALLADA

### 🔐 AUTENTICACIÓN (2/2)
```
✅  POST /api/auth/login/                       → authApi.login()
✅  POST /api/auth/refresh/                     → axios interceptor + authApi.refreshAccessToken()
```

### 👥 POSTULANTES (2/2) 
```
✅  GET    /api/postulantes/                    → Postulantes.jsx (useCrud.list)
✅  POST   /api/postulantes/                    → Postulantes.jsx (useCrud.create)
✅  PATCH  /api/postulantes/:id/                → Postulantes.jsx (useCrud.patch)
✅  DELETE /api/postulantes/:id/                → Postulantes.jsx (useCrud.remove)
✅  GET    /api/postulantes/:id/                → (implícito en PATCH/DELETE)

Llamadas Adicionales:
✅  GET    /api/usuarios/                       → Postulantes.jsx (dropdown)
```

### 📋 POSTULACIONES (2/4)
```
✅  GET    /api/postulaciones/                  → Postulaciones.jsx (useCrud.list)
✅  POST   /api/postulaciones/                  → Postulaciones.jsx (useCrud.create)
✅  PATCH  /api/postulaciones/:id/              → Postulaciones.jsx (useCrud.patch)
✅  DELETE /api/postulaciones/:id/              → Postulaciones.jsx (useCrud.remove)

HUÉRFANOS:
❌  GET    /api/postulaciones/:id/avanzar-etapa/ → NINGÚN ARCHIVO USA
❌  GET    /api/postulaciones/:id/historial/    → NINGÚN ARCHIVO USA

Llamadas Adicionales:
✅  GET    /api/postulantes/                    → Postulaciones.jsx (dropdown)
✅  GET    /api/modalidades/                    → Postulaciones.jsx (dropdown)
```

### 📄 DOCUMENTOS (3/3)
```
✅  GET    /api/documentos/                     → Documentos.jsx (useCrud.list)
✅  POST   /api/documentos/                     → Documentos.jsx (useCrud.create)
✅  PUT    /api/documentos/:id/                 → Documentos.jsx (con FormData)
✅  DELETE /api/documentos/:id/                 → Documentos.jsx (useCrud.remove)

Llamadas Adicionales:
✅  GET    /api/tipos-documento/                → Documentos.jsx (dropdown)
✅  GET    /api/postulaciones/                  → Documentos.jsx (dropdown)
```

### 🎓 MODALIDADES (2/4)
```
✅  GET    /api/modalidades/                    → Modalidades.jsx (useCrud.list)
✅  POST   /api/modalidades/                    → Modalidades.jsx (useCrud.create)
✅  PUT    /api/modalidades/:id/                → Modalidades.jsx (useCrud.update)
✅  DELETE /api/modalidades/:id/                → Modalidades.jsx (useCrud.remove)

HUÉRFANOS:
❌  GET    /api/etapas/                         → NINGÚN ARCHIVO USA
❌  GET    /api/etapas/:id/                     → NINGÚN ARCHIVO USA
```

### 👤 USUARIOS (2/2)
```
✅  GET    /api/usuarios/                       → Usuarios.jsx (useCrud.list)
✅  POST   /api/usuarios/                       → Usuarios.jsx (useCrud.create)
✅  PATCH  /api/usuarios/:id/                   → Usuarios.jsx (useCrud.patch)
✅  DELETE /api/usuarios/:id/                   → Usuarios.jsx (useCrud.remove)

Reutilizado:
✅  GET    /api/usuarios/                       → Postulantes.jsx (dropdown)
```

### 📊 REPORTES (4/4)
```
✅  GET    /api/reportes/dashboard-general/     → Dashboard.jsx, Reportes.jsx
✅  GET    /api/reportes/estadisticas-tutores/  → Reportes.jsx  
✅  GET    /api/reportes/eficiencia-carreras/   → Reportes.jsx

⚠️  GET    /api/reportes/estadisticas-tutores/exportar/ 
    → Reportes.jsx INTENTA USAR pero:
       - Usa: api.axiosInstance.get()
       - PROBLEMA: api.js NO exporta axiosInstance
       - RESULTADO: Falla con "Cannot read property 'get' of undefined"
```

### 🔧 NO USADOS (5)
```
❌  GET    /api/auditoria/                      → Definido pero no usado
❌  GET    /api/schema/                         → Definido pero no usado  
❌  GET    /api/docs/                           → Definido pero no usado
```

---

## ANÁLISIS POR ARCHIVO

### ✅ Postulantes.jsx
```javascript
Imports:
  - api
  - API_CONFIG
  - useCrud hook

Endpoints que LLAMA:
  1️⃣  GET    /api/postulantes/              → list()
  2️⃣  GET    /api/usuarios/                 → fetchUsuarios() [dropdown]
  3️⃣  POST   /api/postulantes/              → create()
  4️⃣  PATCH  /api/postulantes/:id/          → patch()
  5️⃣  DELETE /api/postulantes/:id/          → remove()

Métodos de API:
  - api.getAll()    → GET
  - api.create()    → POST  
  - api.patch()     → PATCH
  - api.delete()    → DELETE
```

### ✅ Postulaciones.jsx
```javascript
Imports:
  - api
  - API_CONFIG
  - useCrud hook

Endpoints que LLAMA:
  1️⃣  GET    /api/postulaciones/            → list()
  2️⃣  GET    /api/postulantes/              → fetchData() [dropdown]
  3️⃣  GET    /api/modalidades/              → fetchData() [dropdown]
  4️⃣  POST   /api/postulaciones/            → create()
  5️⃣  PATCH  /api/postulaciones/:id/        → patch()
  6️⃣  DELETE /api/postulaciones/:id/        → remove()

NUNCA LLAMA:
  ❌ /api/postulaciones/:id/avanzar-etapa/
  ❌ /api/postulaciones/:id/historial/
```

### ✅ Documentos.jsx
```javascript
Imports:
  - api
  - API_CONFIG
  - axiosInstance (directamente)  ⚠️ Mixed pattern
  - useCrud hook

Endpoints que LLAMA:
  1️⃣  GET    /api/documentos/                → list()
  2️⃣  GET    /api/tipos-documento/           → fetchDropdownData() [dropdown]
  3️⃣  GET    /api/postulaciones/             → fetchDropdownData() [dropdown]
  4️⃣  POST   /api/documentos/ (FormData)     → axiosInstance.post()
  5️⃣  PUT    /api/documentos/:id/ (FormData) → axiosInstance.put()
  6️⃣  DELETE /api/documentos/:id/            → remove()

Métodos de API:
  - api.getAll()    → GET
  - api.delete()    → DELETE
  - axiosInstance   → POST/PUT con FormData
```

### ✅ Modalidades.jsx
```javascript
Imports:
  - API_CONFIG
  - useCrud hook

Endpoints que LLAMA:
  1️⃣  GET    /api/modalidades/              → list()
  2️⃣  POST   /api/modalidades/              → create()
  3️⃣  PUT    /api/modalidades/:id/          → update() ⚠️ Usa PUT, no PATCH
  4️⃣  DELETE /api/modalidades/:id/          → remove()

NUNCA LLAMA:
  ❌ /api/etapas/
  ❌ /api/etapas/:id/
```

### ✅ Usuarios.jsx
```javascript
Imports:
  - api
  - API_CONFIG
  - useCrud hook

Endpoints que LLAMA:
  1️⃣  GET    /api/usuarios/                 → list()
  2️⃣  POST   /api/usuarios/                 → create()
  3️⃣  PATCH  /api/usuarios/:id/             → patch()
  4️⃣  DELETE /api/usuarios/:id/             → remove()
```

### ⚠️ Dashboard.jsx
```javascript
Imports:
  - api
  - API_CONFIG

Endpoints que LLAMA:
  1️⃣  GET    /api/reportes/dashboard-general/ → api.getAll()
  2️⃣  GET    /api/postulantes/ (limit=5)      → api.getAll()

Métodos de API:
  - api.getAll()    → GET
```

### ❌ Reportes.jsx - TIENE ERRORES
```javascript
Imports:
  - api
  - API_CONFIG
  ⚠️ FALTA: import axiosInstance from '../api/axios'

Endpoints que INTENTA LLAMAR:
  1️⃣  GET    /api/reportes/dashboard-general/  ✅ Funciona
  2️⃣  GET    /api/reportes/estadisticas-tutores/ ✅ Funciona
  3️⃣  GET    /api/reportes/eficiencia-carreras/ ✅ Funciona
  4️⃣  GET    /api/reportes/estadisticas-tutores/exportar/  ❌ FALLA

ERROR EN LÍNEA 53:
  const response = await api.axiosInstance.get(
    API_CONFIG.ENDPOINTS.EXPORTAR_ESTADISTICAS,
    { responseType: 'blob' }
  );

PROBLEMA: api.js NO exporta axiosInstance
RESULTADO: api.axiosInstance === undefined
EFECTO:   Cuando usuario hace click en export, falla silenciosamente

CORRECCIÓN:
  import axiosInstance from '../api/axios';
  
  const response = await axiosInstance.get(...)
```

### ✅ authApi.js
```javascript
Endpoints que LLAMA:
  1️⃣  POST /api/auth/login/          → login()
  2️⃣  POST /api/auth/refresh/        → refreshAccessToken()

También implementa:
  - logout()
  - getCurrentUser()
  - isAuthenticated()
  - getAccessToken()
  - getRefreshToken()
```

---

## DESGLOSE DE MÉTODOS HTTP USADOS

### GET
- `/api/postulantes/` (list)
- `/api/usuarios/` (list + dropdown)
- `/api/postulaciones/` (list)
- `/api/modalidades/` (list)
- `/api/documentos/` (list)
- `/api/tipos-documento/` (dropdown)
- `/api/reportes/dashboard-general/` (dashboard + reportes)
- `/api/reportes/estadisticas-tutores/` (reportes)
- `/api/reportes/eficiencia-carreras/` (reportes)

### POST
- `/api/auth/login/`
- `/api/postulantes/` (create)
- `/api/postulaciones/` (create)
- `/api/documentos/` (create with FormData)
- `/api/modalidades/` (create)
- `/api/usuarios/` (create)
- `/api/auth/refresh/` (token refresh)

### PATCH
- `/api/postulantes/:id/` (update)
- `/api/postulaciones/:id/` (update)
- `/api/usuarios/:id/` (update)

### PUT
- `/api/documentos/:id/` (update with FormData)
- `/api/modalidades/:id/` (update)

### DELETE
- `/api/postulantes/:id/`
- `/api/postulaciones/:id/`
- `/api/documentos/:id/`
- `/api/modalidades/:id/`
- `/api/usuarios/:id/`

---

## ESTADO DE CADA CRUD

### 1. Postulantes: ✅ COMPLETO
```
Funcionalidad: CRUD Completo
Status: Operativo
Endpoints: 4/4 usados
Problemas: Ninguno detectado
```

### 2. Postulaciones: ⚠️ PARCIAL
```
Funcionalidad: CRUD Base
Status: Operativo pero incompleto
Endpoints: 4/6 usados
Problemas:
  - avanzar-etapa/ definido pero no usado
  - historial/ definido pero no usado
  - ¿Son estos endpoints necesarios?
```

### 3. Documentos: ✅ COMPLETO
```
Funcionalidad: CRUD Completo con Upload
Status: Operativo
Endpoints: 3/3 usados
Notas: Usa axiosInstance directamente para FormData
```

### 4. Modalidades: ⚠️ INCOMPLETO
```
Funcionalidad: CRUD Base
Status: Operativo pero incompleto
Endpoints: 2/4 usados
Problemas:
  - etapas/ definido pero no usado
  - ¿Dónde está la UI de etapas?
```

### 5. Usuarios: ✅ COMPLETO
```
Funcionalidad: CRUD Completo
Status: Operativo
Endpoints: 2/2 usados
Problemas: Ninguno detectado
```

---

## ENDPOINTS HUÉRFANOS (Definido pero no usado)

### Critical Path
```
❌ /api/postulaciones/:id/avanzar-etapa/
   - Razón: No hay botón en UI para cambiar etapa
   - Impacto: Feature incompleta o no requerida
   - Acción: Verificar requerimientos
```

### Secondary Features
```
❌ /api/postulaciones/:id/historial/
   - Razón: No hay UI para ver historial
   - Impacto: Auditoría no visible
   - Acción: Pendiente de implementar

❌ /api/etapas/
❌ /api/etapas/:id/
   - Razón: No hay CRUD de etapas, solo referenciadas
   - Impacto: Gestión de etapas en backend sin UI
   - Acción: Verificar si es admin-only

❌ /api/auditoria/
   - Razón: No hay UI de auditoría
   - Impacto: Logs no accesibles desde frontend
   - Acción: Pendiente de implementar

❌ /api/schema/
❌ /api/docs/
   - Razón: Endpoints de documentación API
   - Impacto: Solo útiles para desarrollo
   - Acción: Esperado (sin UI)
```

---

## CHECKLIST DE VALIDACIÓN

```
✅ BASE_URL configurado correctamente
✅ Todos los endpoints básicos definidos
⚠️ Algunos endpoints huérfanos
✅ Interceptores implementados (JWT, auto-refresh)
⚠️ Error en Reportes.jsx (axiosInstance)
✅ 5 CRUDs funcionales (aunque algunos incompletos)
✅ Manejo de 401 con auto-refresh
⚠️ Sin timeout configurado
⚠️ Sin retry automático para 5xx
✅ Token storage en localStorage
✅ Mensajes de error traducidos
❌ Export de estadísticas roto
```

---

## ARCHIVOS A REVISAR

### Para Reparar
1. `frontend/src/pages/Reportes.jsx` - Línea 53, error axiosInstance

### Para Documentar
1. **¿Por qué existen estos endpoints pero no se usan?**
   - `/api/postulaciones/:id/avanzar-etapa/`
   - `/api/postulaciones/:id/historial/`
   - `/api/etapas/`
   - `/api/etapas/:id/`
   - `/api/auditoria/`

### Para Mejorar
1. `frontend/src/api/axios.js` - Agregar timeout
2. `frontend/src/api/axios.js` - Agregar retry logic para 5xx
3. `frontend/src/api/api.js` - Exportar axiosInstance o crear método wrapper para blob


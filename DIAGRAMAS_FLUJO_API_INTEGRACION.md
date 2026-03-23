# DIAGRAMA DE FLUJO: INTEGRACIÓN API FRONTEND-BACKEND

---

## 1. FLUJO DE AUTENTICACIÓN

```
┌─────────────────────────────────────────────────────────────────────────┐
│ USUARIO INICIA SESIÓN                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Login.jsx                     │
                    │ authApi.login(user, pass)     │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ POST /api/auth/login/         │
                    │ Payload: {username, password} │
                    └───────────────────────────────┘
                                    │
              ┌─────────────────────┴─────────────────────┐
              │                                           │
        ✅ 200 OK                                    ❌ 401/400
              │                                           │
              ▼                                           ▼
    ┌──────────────────────┐                ┌──────────────────────┐
    │ Response Data:       │                │ errorResponse        │
    │ {                    │                │ {error, detail}      │
    │   access,            │                │ ↓                    │
    │   refresh,           │                │ showError(msg)       │
    │   user               │                │ Stay on /login       │
    │ }                    │                └──────────────────────┘
    └──────────────────────┘
              │
              ▼
    ┌──────────────────────────────────────┐
    │ localStorage.setItem:                │
    │ - access_token = '...'               │
    │ - refresh_token = '...'              │
    │ - user_info = {id, username, ...}    │
    └──────────────────────────────────────┘
              │
              ▼
    ┌──────────────────────────────────────┐
    │ Navigate to /dashboard               │
    │ User is authenticated                │
    └──────────────────────────────────────┘
```

---

## 2. FLUJO DE CADA REQUEST API

```
┌─────────────────────────────────────────────────────────────────────────┐
│ OPERACIÓN EN COMPONENTE (ej: Postulantes.jsx)                           │
│ const result = await api.getAll(endpoint, params)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │ REQUEST INTERCEPTOR               │
                    │ (axios.js)                        │
                    ├───────────────────────────────────┤
                    │ 1. loader.increment()             │
                    │ 2. get token from localStorage    │
                    │ 3. set Authorization header       │
                    │ 4. log en desarrollo              │
                    └───────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │ HTTP Request                      │
                    │ GET /api/endpoint/                │
                    │ Header: Authorization: Bearer X   │
                    └───────────────────────────────────┘
              ┌─────────────────────┬─────────────────────┬─────────────────────┐
              │                     │                     │                     │
        ✅ 2xx                  ✅ 3xx                ⚠️ 401              ❌ Others
              │                     │                     │                     │
              ▼                     ▼                     ▼                     ▼
    ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐    ┌──────────────┐
    │ 200 Success  │    │ 304 Not Mod  │    │ 401 Unauthorized  │    │ 400/403/5xx  │
    └──────────────┘    └──────────────┘    └───────────────────┘    └──────────────┘
              │                     │                     │                     │
              └─────────────────────┤─────────────────────┤─────────────────────┘
                                    │                     │
                        ┌───────────┴──────────────┐      │
                        │ RESPONSE INTERCEPTOR     │      │
                        │ (axios.js)               │      │
                        └──────────────────────────┘      │
                                    │                     │
                    (Si SUCCESS)    │     (Si 401)       │
                        ┌───────────┴──────────────┐      │
                        │                          │      │
                        ▼                          ▼      ▼
                ┌───────────────────┐    ┌──────────────────────┐
                │ loader.decrement()│    │ ¿_retry = true?      │
                │ return response   │    └──────────────────────┘
                └───────────────────┘            │
                                       ┌────────┴────────┐
                                       │                 │
                                    NO │                 │ YES
                                       │                 │
                                       ▼                 ▼
                                ┌────────────┐    ┌──────────────┐
                                │ showError()│    │ showError()  │
                                │ continue   │    │ reload page  │
                                └────────────┘    └──────────────┘

        ┌──────────────────────────────────┐
        │ SI 401 Y !_retry:                │
        │ _retry = true                    │
        ├──────────────────────────────────┤
        │ 1. get refresh_token             │
        │ 2. if !refresh_token             │
        │    → localStorage.clear()        │
        │    → redirect /login             │
        │    → reject                      │
        │ 3. POST /api/auth/refresh/       │
        │    {refresh: token}              │
        │ 4. if success:                   │
        │    → save new access_token       │
        │    → retry original request      │
        │ 5. if error:                     │
        │    → showError(msg)              │
        │    → localStorage.clear()        │
        │    → redirect /login             │
        │    → reject                      │
        └──────────────────────────────────┘
```

---

## 3. FLUJO POR TIPO DE OPERACIÓN

### GET (Listar)
```
Component
    │
    ▼
useCrud.list() 
    │
    ▼
api.getAll(endpoint, params)
    │
    ▼
axiosInstance.get(endpoint, {params})
    │
    ▼
[REQUEST INTERCEPTOR] ─ Inyecta token
    │
    ▼ HTTP GET
Backend
    │
    ├── ✅ 200: return {success:true, data: [...]}
    │
    └── ❌ Error: manejo según status
```

### POST (Crear)
```
Component (formulario)
    │
    ▼
handleSubmit()
    │
    ├─ Validación de fields
    │
    ▼
useCrud.create(payload)
    │
    ▼
api.create(endpoint, data)
    │
    ▼
axiosInstance.post(endpoint, data)
    │
    ▼
[REQUEST INTERCEPTOR] ─ Inyecta token, set Content-Type
    │
    ▼ HTTP POST
Backend
    │
    ├── ✅ 201: return {success:true, data: newObject}
    │
    └── ❌ 400: return {success:false, error: fields}
```

### PATCH (Actualizar parcial)
```
Component
    │
    ▼
useCrud.patch(endpointWithId, payload)
    │
    ▼
api.patch(endpoint, data)
    │
    ▼
axiosInstance.patch(endpoint, data)
    │
    ▼
[REQUEST INTERCEPTOR]
    │
    ▼ HTTP PATCH
Backend
    │
    ├── ✅ 200: return {success:true, data: updatedObject}
    │
    └── ❌ Error handling
```

### DELETE (Eliminar)
```
Component
    │
    ├─ window.confirm()
    │
    ▼
useCrud.remove(endpointWithId)
    │
    ▼
api.delete(endpoint)
    │
    ▼
axiosInstance.delete(endpoint)
    │
    ▼
[REQUEST INTERCEPTOR]
    │
    ▼ HTTP DELETE
Backend
    │
    ├── ✅ 204: return {success:true}
    │
    └── ❌ Error
```

### MULTIPART (Documento upload)
```
Component (Documentos.jsx)
    │
    ├─ File input capture: setArchivoFile()
    │
    ▼
handleSubmit()
    │
    ├─ Validación
    │
    ├─ ¿archivoFile?
    │  YES ▼
    │  const formData = new FormData()
    │  formData.append('archivo', file)
    │  formData.append('postulacion', id)
    │  formData.append('tipo_documento', id)
    │
    ▼
axiosInstance.put(endpoint, formData, {
  headers: {'Content-Type': 'multipart/form-data'}
})
    │
    ▼ HTTP PUT
Backend
    │
    ├── ✅ 200: return {success:true}
    │
    └── ❌ Error
```

---

## 4. ÁRBOL DE COMPONENTES Y ENDPOINTS

```
App
├── Login
│   └── POST /api/auth/login/
│
├── Dashboard
│   ├── GET /api/reportes/dashboard-general/
│   └── GET /api/postulantes/ (limit=5)
│
├── Postulantes (CRUD)
│   ├── GET /api/postulantes/
│   ├── GET /api/usuarios/ (dropdown)
│   ├── POST /api/postulantes/
│   ├── PATCH /api/postulantes/:id/
│   └── DELETE /api/postulantes/:id/
│
├── Postulaciones (CRUD)
│   ├── GET /api/postulaciones/
│   ├── GET /api/postulantes/ (dropdown)
│   ├── GET /api/modalidades/ (dropdown)
│   ├── POST /api/postulaciones/
│   ├── PATCH /api/postulaciones/:id/
│   └── DELETE /api/postulaciones/:id/
│   ❌ (No usa: avanzar-etapa, historial)
│
├── Documentos (CRUD con upload)
│   ├── GET /api/documentos/
│   ├── GET /api/tipos-documento/ (dropdown)
│   ├── GET /api/postulaciones/ (dropdown)
│   ├── POST /api/documentos/
│   ├── PUT /api/documentos/:id/ [FormData]
│   └── DELETE /api/documentos/:id/
│
├── Modalidades (CRUD)
│   ├── GET /api/modalidades/
│   ├── POST /api/modalidades/
│   ├── PUT /api/modalidades/:id/
│   └── DELETE /api/modalidades/:id/
│   ❌ (No usa: etapas)
│
├── Usuarios (CRUD)
│   ├── GET /api/usuarios/
│   ├── POST /api/usuarios/
│   ├── PATCH /api/usuarios/:id/
│   └── DELETE /api/usuarios/:id/
│
└── Reportes
    ├── GET /api/reportes/dashboard-general/
    ├── GET /api/reportes/estadisticas-tutores/
    ├── GET /api/reportes/eficiencia-carreras/
    └── ❌ GET /api/reportes/estadisticas-tutores/exportar/ [ERROR]
```

---

## 5. CICLO DE VIDA DE SESIÓN

```
START
  │
  ├─ User logs in
  │  └─ POST /api/auth/login/ → {access, refresh, user}
  │     └─ localStorage:
  │        - access_token (expira 1hr)
  │        - refresh_token (expira 7 días)
  │        - user_info
  │
  ├─ User activo en app (requests)
  │  ├─ REQUEST INTERCEPTOR ─ add Authorization: Bearer access_token
  │  └─ ✅ Todas las requests funcionan
  │
  ├─ [DESPUÉS DE 1 HORA]
  │  └─ access_token expira
  │
  ├─ Siguiente request
  │  ├─ REQUEST INTERCEPTOR ─ busca access_token (no válido)
  │  ├─ Response: 401 Unauthorized
  │  ├─ RESPONSE INTERCEPTOR:
  │  │  ├─ Revisa si refresh_token existe
  │  │  ├─ POST /api/auth/refresh/ {refresh: token}
  │  │  ├─ Recibe nuevo access_token
  │  │  ├─ localStorage.setItem(access_token, nuevo)
  │  │  └─ REINTENTA original request
  │  └─ ✅ Request completado exitosamente
  │
  ├─ User logs out OR
  ├─ [DESPUÉS DE 7 DÍAS]
  │  └─ refresh_token expira
  │
  ├─ Siguiente request después de expiración refresh
  │  ├─ 401 Unauthorized
  │  ├─ RESPONSE INTERCEPTOR:
  │  │  ├─ Intenta refresh → falla
  │  │  ├─ localStorage.clear()
  │  │  └─ window.location.href = '/login'
  │  └─ ❌ Redirigido a login
  │
  └─ END (Sesión finalizada)
```

---

## 6. MAPA DE ERRORES Y ACCIONES

```
┌──────────────────────────────────────────────────────────────────────┐
│ HTTP STATUS CODE → RESPUESTA DEL FRONTEND                            │
├──────────────────────────────────────────────────────────────────────┤
│ 200 OK                  → {success: true, data: response.data}       │
│ 201 Created             → {success: true, data: response.data}       │
│ 204 No Content          → {success: true}                            │
├──────────────────────────────────────────────────────────────────────┤
│ 400 Bad Request         → showError("Solicitud inválida")            │
│                           {success: false, error: mensaje}            │
│ 401 Unauthorized        → RETRY con refresh token                    │
│                           Si falla: redirect /login                  │
│ 403 Forbidden           → showError("Acceso denegado...")            │
│ 404 Not Found           → showError("Recurso no encontrado")         │
│ 409 Conflict            → showError(mensaje del servidor)            │
├──────────────────────────────────────────────────────────────────────┤
│ 500 Server Error        → showError("Error del servidor...")         │
│ 502 Bad Gateway         → showError("Servidor no disponible")        │
│ 503 Service Unavailable → showError("Servicio temporalmente...")     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 7. ESTADO DE IMPLEMENTACIÓN VISUAL

```
✅ = Completamente implementado
⚠️  = Parcialmente implementado / Tiene problemas
❌ = No implementado

┌────────────────────────────────────────────────────────────┐
│ FUNCIONALIDAD                                              │
├────────────────────────────────────────────────────────────┤
│ ✅ Autenticación (Login)                                  │
│ ✅ Token Storage (localStorage)                           │
│ ✅ Inyección de Authorization header                      │
│ ✅ Auto-refresh en 401                                    │
│ ✅ Manejo de 401 → redirect /login                        │
│ ✅ Mensajes de error traducidos                           │
│ ✅ Global loader (progress indicator)                     │
│ ✅ CRUD Postulantes (completo)                            │
│ ⚠️  CRUD Postulaciones (base, sin avanzar-etapa)          │
│ ✅ CRUD Documentos (con upload FormData)                  │
│ ⚠️  CRUD Modalidades (sin gestión de etapas)              │
│ ✅ CRUD Usuarios (completo)                               │
│ ✅ Dashboard (stats básicos)                              │
│ ⚠️  Reportes (export roto - axiosInstance error)          │
│ ❌ Timeout configurado                                    │
│ ❌ Retry automático para 5xx                              │
│ ❌ Refresh proactivo de user info                         │
│ ❌ Gestión de Auditoria                                   │
│ ❌ Gestión de Etapas                                      │
└────────────────────────────────────────────────────────────┘
```

---

## 8. MATRIZ DE VALIDACIÓN DE ENDPOINTS

```
MÓDULO          │ Total │ Usado │ ✓ % │ Estado
────────────────┼───────┼───────┼─────┼──────────────
Autenticación   │   2   │   2   │100% │ ✅ OK
Postulantes     │   2   │   2   │100% │ ✅ OK
Postulaciones   │   6   │   4   │67%  │ ⚠️  PARCIAL
Documentos      │   3   │   3   │100% │ ✅ OK
Modalidades     │   4   │   2   │50%  │ ⚠️  PARCIAL
Usuarios        │   2   │   2   │100% │ ✅ OK
Reportes        │   4   │   3*  │75%  │ ⚠️  EXPORT ROTO
Otros           │   3   │   0   │0%   │ ❌ NO USADOS
────────────────┼───────┼───────┼─────┼──────────────
TOTALES         │  26   │  18   │69%  │ ⚠️  FUNCIONAL
```

*Reportes: 3 funcionan, 1 falla (export)

---

## 9. REFERENCIA DE HOOKS Y SERVICIOS

```
┌─────────────────────────────────────────────────────────────┐
│ HOOKS DISPONIBLES                                           │
├─────────────────────────────────────────────────────────────┤
│ useCrud(endpoint)                                           │
│ ├─ data: [items]                                            │
│ ├─ loading: bool                                            │
│ ├─ error: string                                            │
│ ├─ meta: {count, next, previous}                            │
│ └─ methods:                                                 │
│    ├─ list(params)    → api.getAll()                       │
│    ├─ refresh()       → repeat last params                 │
│    ├─ create(data)    → api.create()                       │
│    ├─ update(ep, dt)  → api.update()                       │
│    ├─ patch(ep, dt)   → api.patch()                        │
│    └─ remove(ep)      → api.delete()                       │
│                                                             │
│ useModal(initialData)                                       │
│ ├─ isOpen: bool                                             │
│ ├─ isEditMode: bool                                         │
│ ├─ formData: object                                         │
│ └─ methods:                                                 │
│    ├─ openModal(data?)                                     │
│    ├─ closeModal()                                         │
│    └─ setFormData(data)                                    │
│                                                             │
│ useListFilters(list, init, options)                        │
│ ├─ search: string                                           │
│ ├─ setSearch()                                              │
│ ├─ page: number                                             │
│ └─ setPage()                                                │
│                                                             │
│ useTheme()                                                  │
│ └─ isDark: bool                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SERVICIOS API                                               │
├─────────────────────────────────────────────────────────────┤
│ api.getAll(endpoint, params)                                │
│ api.getById(endpoint)                                       │
│ api.create(endpoint, data)                                  │
│ api.update(endpoint, data)    ← PUT                         │
│ api.patch(endpoint, data)     ← PATCH                       │
│ api.delete(endpoint)                                        │
│                                                             │
│ authApi.login(username, password)                           │
│ authApi.logout()                                            │
│ authApi.getCurrentUser()                                    │
│ authApi.isAuthenticated()                                   │
│ authApi.getAccessToken()                                    │
│ authApi.getRefreshToken()                                   │
│ authApi.refreshAccessToken()                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. COMPARATIVA: DEFINIDO vs USADO

```
DEFINIDO EN API_CONFIG        │  USADO DESDE FRONTEND
──────────────────────────────┼──────────────────────────
LOGIN                         │  ✅ authApi.login()
REFRESH_TOKEN                 │  ✅ axios interceptor
POSTULANTES                   │  ✅ Postulantes.jsx
POSTULANTE_DETAIL             │  ✅ Postulantes.jsx
POSTULACIONES                 │  ✅ Postulaciones.jsx
POSTULACION_DETAIL            │  ✅ Postulaciones.jsx
POSTULACION_AVANZAR_ETAPA     │  ❌ NUNCA USADO
POSTULACION_HISTORIAL         │  ❌ NUNCA USADO
DOCUMENTOS                    │  ✅ Documentos.jsx
DOCUMENTO_DETAIL              │  ✅ Documentos.jsx
TIPOS_DOCUMENTO               │  ✅ Documentos.jsx
MODALIDADES                   │  ✅ Modalidades.jsx
MODALIDAD_DETAIL              │  ✅ Modalidades.jsx
ETAPAS                        │  ❌ NUNCA USADO
ETAPA_DETAIL                  │  ❌ NUNCA USADO
USUARIOS                      │  ✅ Usuarios.jsx + Postulantes.jsx
USUARIO_DETAIL                │  ✅ Usuarios.jsx
AUDITORIA                     │  ❌ NUNCA USADO
DASHBOARD_GENERAL             │  ✅ Dashboard.jsx, Reportes.jsx
ESTADISTICAS_TUTORES          │  ✅ Reportes.jsx
EXPORTAR_ESTADISTICAS         │  ⚠️  Reportes.jsx (ERROR)
EFICIENCIA_CARRERAS           │  ✅ Reportes.jsx
SCHEMA                        │  ❌ NUNCA USADO
DOCS                          │  ❌ NUNCA USADO
──────────────────────────────┼──────────────────────────
✅ 17/26 endpoints    │  69% cobertura
❌ 7/26 endpoints     │  31% huérfanos
```


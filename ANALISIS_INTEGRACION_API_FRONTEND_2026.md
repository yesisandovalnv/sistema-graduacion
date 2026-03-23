# ANÁLISIS INTEGRACIÓN BACKEND - FRONTEND (SIN MODIFICAR)
**Fecha:** 23 de Marzo de 2026  
**Scope:** Solo lectura, verificación de arquitectura y consistencia

---

## 1. CONFIGURACIÓN DE API (API_CONFIG.js)

### BASE_URL
```javascript
// Archivo: frontend/src/constants/api.js
const isDevelopment = import.meta.env.DEV;
let baseUrl;
if (isDevelopment) {
  baseUrl = '';  // Usa proxy de Vite (localhost:5173 -> localhost:8000)
} else {
  baseUrl = import.meta.env.VITE_API_URL || 'http://localhost';
}
```
✅ **Estado:** CORRECTO
- En desarrollo usa rutas relativas (proxy configurado en Vite)
- En producción usa `VITE_API_URL` o default `http://localhost`

### ENDPOINTS DEFINIDOS
Total: **24 endpoints** organizados por módulo:

#### 🔐 Autenticación (2)
```
✅ LOGIN: '/api/auth/login/'
✅ REFRESH_TOKEN: '/api/auth/refresh/'
```

#### 👥 Postulantes (2)
```
✅ POSTULANTES: '/api/postulantes/'
✅ POSTULANTE_DETAIL: (id) => `/api/postulantes/${id}/`
```

#### 📋 Postulaciones (4)
```
✅ POSTULACIONES: '/api/postulaciones/'
✅ POSTULACION_DETAIL: (id) => `/api/postulaciones/${id}/`
❓ POSTULACION_AVANZAR_ETAPA: (id) => `/api/postulaciones/${id}/avanzar-etapa/` [NO USADO]
❓ POSTULACION_HISTORIAL: (id) => `/api/postulaciones/${id}/historial/` [NO USADO]
```

#### 📄 Documentos (3)
```
✅ DOCUMENTOS: '/api/documentos/'
✅ DOCUMENTO_DETAIL: (id) => `/api/documentos/${id}/`
✅ TIPOS_DOCUMENTO: '/api/tipos-documento/'
```

#### 🎓 Modalidades (4)
```
✅ MODALIDADES: '/api/modalidades/'
✅ MODALIDAD_DETAIL: (id) => `/api/modalidades/${id}/`
✅ ETAPAS: '/api/etapas/' [DEFINIDO PERO NO USADO]
✅ ETAPA_DETAIL: (id) => `/api/etapas/${id}/` [DEFINIDO PERO NO USADO]
```

#### 👤 Usuarios (2)
```
✅ USUARIOS: '/api/usuarios/'
✅ USUARIO_DETAIL: (id) => `/api/usuarios/${id}/`
```

#### 📊 Reportes (4)
```
✅ DASHBOARD_GENERAL: '/api/reportes/dashboard-general/'
✅ ESTADISTICAS_TUTORES: '/api/reportes/estadisticas-tutores/'
✅ EXPORTAR_ESTADISTICAS: '/api/reportes/estadisticas-tutores/exportar/'
✅ EFICIENCIA_CARRERAS: '/api/reportes/eficiencia-carreras/'
```

#### 🔧 Sistema (3)
```
✅ AUDITORIA: '/api/auditoria/' [DEFINIDO PERO NO USADO]
✅ SCHEMA: '/api/schema/' [DEFINIDO PERO NO USADO]
✅ DOCS: '/api/docs/' [DEFINIDO PERO NO USADO]
```

### Storage Keys
```javascript
STORAGE_KEYS: {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
}
```

---

## 2. SERVICIO DE API (axios.js + api.js)

### axios.js - Instancia configurada
✅ **BaseURL:** Configurado desde API_CONFIG
✅ **Headers:** `'Content-Type': 'application/json'`

#### Métodos implementados (api.js):
```javascript
✅ getAll(endpoint, params)    // GET con parámetros
✅ getById(endpoint)           // GET por ID
✅ create(endpoint, data)      // POST
✅ update(endpoint, data)      // PUT
✅ patch(endpoint, data)       // PATCH
✅ delete(endpoint)            // DELETE
```

### Manejo de errores

#### Request Interceptor
```javascript
✅ Inyecta token JWT en header: Authorization: Bearer ${token}
✅ Muestra loader global (LoaderContext)
✅ Log en console en desarrollo
⚠️ Limpia loader si hay error en request
```

#### Response Interceptor
```javascript
✅ Oculta loader en respuesta exitosa
✅ Manejo específico de 401 (Unauthorized):
   - Retry automático con token refresh
   - Si falla refresh → localStorage.clear() + redirect /login
✅ Muestra notificaciones de error (toast) para status ≠ 401
✅ Mapeo de status codes a mensajes amigables:
   - 400: "Solicitud inválida"
   - 401: "Sesión expirada - por favor inicia sesión nuevamente"
   - 403: "Acceso denegado - no tienes permisos"
   - 404: "Recurso no encontrado"
   - 500: "Error del servidor - intenta de nuevo más tarde"
   - 502/503: "Servidor no disponible"
```

#### Error Handling en api.js
```javascript
✅ Extrae mensajes de error desde:
   1. error.response.data.error
   2. error.response.data.detail
   3. Errores de validación por campo (serializer)
   4. non_field_errors
✅ Detalles de errores de validación: "campo: valor"
✅ Retorna formato consistente: { success: bool, error?: string, status?: number }
```

### Interceptores implementados
✅ Request interceptor: Inyección de token
✅ Response interceptor: Manejo de 401 + auto-refresh
⚠️ **NO hay:** Retry automático para otros errores (500, 502, 503)
⚠️ **NO hay:** Timeout configurado explícitamente

---

## 3. LLAMADAS A API REALES (5 CRUDS)

### CRUD 1: Postulantes (✅ COMPLETO)
**Archivo:** `frontend/src/pages/Postulantes.jsx`

Endpoints utilizados:
```javascript
✅ GET    /api/postulantes/                     (list)
✅ POST   /api/postulantes/                     (create)
✅ PATCH  /api/postulantes/${id}/               (update)
✅ DELETE /api/postulantes/${id}/               (delete)
✅ GET    /api/usuarios/                        (fetch dropdown)
```

Métodos de api usados:
```javascript
- useCrud(API_CONFIG.ENDPOINTS.POSTULANTES)
  - list() → api.getAll()
  - create() → api.create()
  - patch() → api.patch()
  - remove() → api.delete()
- Carga de usuarios para dropdown
```

### CRUD 2: Postulaciones (✅ COMPLETO)
**Archivo:** `frontend/src/pages/Postulaciones.jsx`

Endpoints utilizados:
```javascript
✅ GET    /api/postulaciones/                   (list)
✅ POST   /api/postulaciones/                   (create)
✅ PATCH  /api/postulaciones/${id}/             (update)
✅ DELETE /api/postulaciones/${id}/             (delete)
✅ GET    /api/postulantes/                     (fetch dropdown)
✅ GET    /api/modalidades/                     (fetch dropdown)
```

❌ **ENDPOINTS DEFINIDOS PERO NO USADOS:**
```javascript
❌ /api/postulaciones/${id}/avanzar-etapa/      (ORPHANED)
❌ /api/postulaciones/${id}/historial/          (ORPHANED)
```

### CRUD 3: Documentos (✅ COMPLETO)
**Archivo:** `frontend/src/pages/Documentos.jsx`

Endpoints utilizados:
```javascript
✅ GET    /api/documentos/                      (list)
✅ POST   /api/documentos/                      (create)
✅ PUT    /api/documentos/${id}/                (update con FormData)
✅ DELETE /api/documentos/${id}/                (delete)
✅ GET    /api/tipos-documento/                 (fetch dropdown)
✅ GET    /api/postulaciones/                   (fetch dropdown)
```

⚠️ **NOTA:** Usa `axiosInstance` directamente en handleSubmit para upload FormData

### CRUD 4: Modalidades (✅ COMPLETO)
**Archivo:** `frontend/src/pages/Modalidades.jsx`

Endpoints utilizados:
```javascript
✅ GET    /api/modalidades/                     (list)
✅ POST   /api/modalidades/                     (create)
✅ PUT    /api/modalidades/${id}/               (update)
✅ DELETE /api/modalidades/${id}/               (delete)
```

### CRUD 5: Usuarios (✅ COMPLETO)
**Archivo:** `frontend/src/pages/Usuarios.jsx`

Endpoints utilizados:
```javascript
✅ GET    /api/usuarios/                        (list)
✅ POST   /api/usuarios/                        (create)
✅ PATCH  /api/usuarios/${id}/                  (update)
✅ DELETE /api/usuarios/${id}/                  (delete)
```

### OTRAS PÁGINAS

#### Dashboard.jsx
```javascript
✅ GET /api/reportes/dashboard-general/         (stats)
✅ GET /api/postulantes/                        (recent, limit=5)
```

#### Reportes.jsx
```javascript
✅ GET /api/reportes/dashboard-general/         (general tab)
✅ GET /api/reportes/estadisticas-tutores/      (tutores tab)
✅ GET /api/reportes/eficiencia-carreras/       (carreras tab)
❌ GET /api/reportes/estadisticas-tutores/exportar/ [usa api.axiosInstance - ERROR POTENCIAL]
```

---

## 4. ANÁLISIS DE MANEJO DE ERRORES

### 401 Unauthorized (Sesión Expirada)
✅ **Implementado:** Auto-refresh de token
```javascript
// Cuando 401 y !_retry:
1. Obtiene refresh_token de localStorage
2. POST /api/auth/refresh/ con refresh token
3. Si éxito: Guarda nuevo access_token, reintenta request original
4. Si falla: Limpia localStorage, redirige a /login
```

### 403 Forbidden (Sin Permisos)
✅ **Implementado:** Muestra toast error "Acceso denegado - no tienes permisos para realizar esta acción"
⚠️ **NO hay:** Lógica específica (no hay redireccionamiento)

### 500 Server Error
✅ **Implementado:** Muestra toast error "Error del servidor - intenta de nuevo más tarde"
⚠️ **NO hay:** Retry automático

### 502/503 Service Unavailable
✅ **Implementado:** Muestra toast error genérico
⚠️ **NO hay:** Retry automático o fallback

### Errores silenciosos
⚠️ **CRÍTICO:** En Reportes.jsx línea 53:
```javascript
const response = await api.axiosInstance.get(...)
```
❌ **PROBLEMA:** `api.js` NO exporta `axiosInstance`
❌ **Efecto:** `api.axiosInstance` es `undefined`
❌ **Resultado:** Fallaría silenciosamente con "Cannot read property 'get' of undefined"

---

## 5. GESTIÓN DE TOKENS Y AUTENTICACIÓN

### Token Storage
```javascript
localStorage.setItem(ACCESS_TOKEN, 'JWT_STRING')      ✅
localStorage.setItem(REFRESH_TOKEN, 'JWT_STRING')    ✅
localStorage.setItem(USER_INFO, JSON.stringify(user)) ✅
```

### Token Envío
```javascript
✅ Header: Authorization: Bearer ${access_token}
✅ Se inyecta en request interceptor automáticamente
✅ Se valida presencia de token antes de enviar
```

### Token Expiración
```javascript
API_CONFIG.TOKEN_EXPIRY = {
  ACCESS: 3600,    // 1 hora
  REFRESH: 604800  // 7 días
}
```
⚠️ **NOTA:** Estos valores están definidos pero NO se usan:
- No hay contador de expiración frontend
- No hay redirect proactivo antes de expirar
- Depende del error 401 reactivamente

### Refresh Token
✅ **Automático en interceptor:** Si 401, intenta refresh
✅ **Manual:** AuthService.refreshAccessToken() disponible
✅ **Logout:** AuthService.logout() limpia localStorage

---

## 6. INCONSISTENCIAS Y PROBLEMAS ENCONTRADOS

### 🔴 CRÍTICOS

#### 1. **Reportes.jsx usa `api.axiosInstance` que no existe**
- **Línea:** 53
- **Código:** `const response = await api.axiosInstance.get(...)`
- **Problema:** api.js solo exporta `ApiService()`, no `axiosInstance`
- **Impacto:** Export de estadísticas falla silenciosamente
- **Solución sugerida:** Importar `axiosInstance` desde `../api/axios` directamente

#### 2. **Endpoints huérfanos definidos pero no usados**
- `/api/postulaciones/${id}/avanzar-etapa/` - No llamado en frontend
- `/api/postulaciones/${id}/historial/` - No llamado en frontend

#### 3. **Endpoints definidos pero UI no los usa**
- `/api/etapas/` - Definido pero nunca llamado
- `/api/etapa/${id}/` - Definido pero nunca llamado
- `/api/auditoria/` - Definido pero nunca llamado
- `/api/schema/` - Definido pero nunca llamado
- `/api/docs/` - Definido pero nunca llamado

### 🟡 ADVERTENCIAS

#### 1. **Sin retry automático para errores no-401**
- 500, 502, 503 muestran error pero no reintentan
- Podría ser esperado, pero es un riesgo en producción

#### 2. **Sin timeout explícito en axios**
- axios timeout por defecto es "unlimited"
- Peticiones pueden quedar colgadas indefinidamente

#### 3. **LoaderContext puede no estar sincronizado**
- Si una petición falla en request interceptor, el loader se registra pero después se decrementa
- Potencial para que el loader se quede "stuck"

#### 4. **Token refresh sin validación en frontend**
- No valida que el refresh token sea válido antes de hacer POST
- Si ambos están expirados, hace 2 peticiones innecesarias

#### 5. **User info nunca se refrescar**
- Después de login, user info se guarda en localStorage
- Nunca se actualiza, incluso si cambia en backend
- No hay endpoint para obtener current user

### 🟢 ACIERTOS

✅ Implementación consistente de error handling  
✅ Interceptores bien estructurados  
✅ Separación clara de API config, axios y servicios  
✅ useCrud hook normaliza operaciones comunes  
✅ Manejo de FormData para uploads de documentos  
✅ Token refresh automático en 401  
✅ localStorage para persistencia de sesión  
✅ Mensajes de error traducidos al español  

---

## 7. RESUMEN DE ENDPOINTS REALES vs DEFINIDOS

### Matriz de Cobertura

| Endpoint | ¿Definido? | ¿Usado? | Módulo | Estado |
|----------|:----------:|:-------:|--------|--------|
| /api/auth/login/ | ✅ | ✅ | Auth | ✅ OK |
| /api/auth/refresh/ | ✅ | ✅ | Auth | ✅ OK |
| /api/postulantes/ | ✅ | ✅ | Postulantes | ✅ OK |
| /api/postulantes/{id}/ | ✅ | ✅ | Postulantes | ✅ OK |
| /api/postulaciones/ | ✅ | ✅ | Postulaciones | ✅ OK |
| /api/postulaciones/{id}/ | ✅ | ✅ | Postulaciones | ✅ OK |
| /api/postulaciones/{id}/avanzar-etapa/ | ✅ | ❌ | Postulaciones | ⚠️ HUÉRFANO |
| /api/postulaciones/{id}/historial/ | ✅ | ❌ | Postulaciones | ⚠️ HUÉRFANO |
| /api/documentos/ | ✅ | ✅ | Documentos | ✅ OK |
| /api/documentos/{id}/ | ✅ | ✅ | Documentos | ✅ OK |
| /api/tipos-documento/ | ✅ | ✅ | Documentos | ✅ OK |
| /api/modalidades/ | ✅ | ✅ | Modalidades | ✅ OK |
| /api/modalidades/{id}/ | ✅ | ✅ | Modalidades | ✅ OK |
| /api/etapas/ | ✅ | ❌ | Modalidades | ⚠️ HUÉRFANO |
| /api/etapas/{id}/ | ✅ | ❌ | Modalidades | ⚠️ HUÉRFANO |
| /api/usuarios/ | ✅ | ✅ | Usuarios | ✅ OK |
| /api/usuarios/{id}/ | ✅ | ✅ | Usuarios | ✅ OK |
| /api/auditoria/ | ✅ | ❌ | Auditoria | ⚠️ HUÉRFANO |
| /api/reportes/dashboard-general/ | ✅ | ✅ | Reportes | ✅ OK |
| /api/reportes/estadisticas-tutores/ | ✅ | ✅ | Reportes | ✅ OK |
| /api/reportes/estadisticas-tutores/exportar/ | ✅ | ❌* | Reportes | ❌ ERROR |
| /api/reportes/eficiencia-carreras/ | ✅ | ✅ | Reportes | ✅ OK |
| /api/schema/ | ✅ | ❌ | Sistema | ⚠️ HUÉRFANO |
| /api/docs/ | ✅ | ❌ | Sistema | ⚠️ HUÉRFANO |

*Reportes.jsx intenta usar pero hay error de referencia

---

## 8. RECOMENDACIONES CRÍTICAS

### INMEDIATO (Bloquea funcionalidad)
1. ⚠️ **Reportes.jsx:** Corregir `api.axiosInstance` → importar directo de axios.js
2. ⚠️ **Verificar si endpoints huérfanos deben removerse o usarse**

### CORTO PLAZO (Mejora estabilidad)
1. Agregar timeout explícito en axios: `timeout: 30000` (30 segundos)
2. Implementar retry automático para errores 5xx
3. Agregar refresh proactivo de user info después de login
4. Validar refresh token antes de intentar refresh

### MEDIANO PLAZO (Arquitectura)
1. Crear servicio de endpoints específicos para acciones complejas (avanzar-etapa, historial)
2. Documentar qué endpoints son realmente parte de la API pública
3. Agregar manejo de 403 más específico (permiso denegado)

---

## CONCLUSION

**Estado General:** 🟡 **FUNCIONAL CON RIESGOS**

✅ **Fortalezas:**
- Arquitectura de API bien organizada
- Interceptores implementados correctamente
- Error handling en 401 automático
- 5 CRUDs implementados y funcionando

❌ **Debilidades:**
- Error crítico en Reportes.jsx (export falla)
- Endpoints huérfanos que pueden confundir
- Sin timeout explícito
- Sin retry automático para errores 5xx
- Sesión de usuario nunca se refresca

⚠️ **Riesgo Operacional:** MEDIO
- Si backend cae (500), frontend no lo detecta bien
- Export de estadísticas está roto
- Sin mecanismo de fallback


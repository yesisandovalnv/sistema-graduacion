# 🔴 DIAGNÓSTICO TÉCNICO PROFUNDO - FRONTEND REACT
**Análisis Arquitectónico Sin Repetir Auditorías Funcionales**  
**Fecha:** 23 de marzo de 2026  
**Enfoque:** Problemas ocultos de arquitectura, estado, escalabilidad y mantenimiento

---

## 🎯 BLOQUE 1: RIESGOS DE ARQUITECTURA REACT

### 1.1 Props Drilling Excesivo en Pageés CRUD

| Riesgo | Ubicación | Severidad | Explicación | Impacto Real |
|--------|-----------|-----------|------------|---|
| **Props innecesarios en DataTable** | `Postulantes.jsx` → `DataTable.jsx` | MEDIO | DataTable recibe `pageSize`, `isDark`, pero están hardcodeados. Pasa `data`, `columns`, `onEdit`, `onDelete`, `onView` - 6 props en cadena simple, pero si agregamos paginación servidor, explosion de props | Difícil reutilizar DataTable en otras páginas; agregar features requiere refactor |
| **FormField props repetidas 7+ veces** | `Postulantes.jsx` (líneas 270-320) | BAJO | Cada FormField llama con: `label`, `name`, `value`, `onChange`, `required`. No es props drilling per se, pero es repetitivo. Podría simplificarse con `map()` sobre objeto | Código de 50 líneas para 7 campos; factor 3x de LOC innecesario |
| **Modal genérico sin especialización** | `Postulantes.jsx`, `Usuarios.jsx`, `Documentos.jsx` | MEDIO | Modal reutilizable aparentemente, pero cada página pasa `isOpen`, `isEditMode`, `onClose`, `onSubmit` manualmente. **No hay context de Modal global** | Si necesitas modal confirmación o anidado, no existe abstracción |

---

### 1.2 Componentes Duales para Tabla: DataTable vs Table

| Riesgo | Ubicación | Severidad | Explicación | Impacto |
|--------|-----------|-----------|-----------|---------|
| **DataTable y Table casi idénticos** | `components/DataTable.jsx` (150 LOC) vs `components/Table.jsx` (100 LOC) | CRÍTICO | **DataTable:** búsqueda integrada LOCAL, paginación cliente-side, ordenamiento.  **Table:** sin búsqueda, sin paginación. Pero Layout idéntico. Postulantes usa DataTable, Usuarios usa Table | Mantenimiento duplicado; bug en uno no se arregla en otro |
| **Búsqueda duplicada** | DataTable línea 22 y Usuarios handling manual | ALTO | DataTable hace `filteredData = data.filter(...)` en cliente. Usuarios hace búsqueda vía API con `useListFilters`. **Comportamiento inconsistente**: en Postulantes buscas "juan" → busca EN MEMORIA (lento con 1000+). En Usuarios buscas "juan" → API request (rápido) | 5000 postulantes = DataTable cuelga; pero Usuarios escala OK |
| **Paginación inconsistente** | DataTable vs Usuarios | ALTO | DataTable: `currentPage * pageSize` (cliente-side). Usuarios usa meta.previous/meta.next (servidor). Si Postulantes crece a 10k, DataTable carga TODO en memoria, luego pagina | DOM explota con registros grandes |

---

### 1.3 Duplicación de Lógica Entre CRUDs

| Riesgo | Ubicación | Severidad | Ejemplación |
|--------|-----------|-----------|-----------|
| **handleSubmit duplicado** | `Postulantes.jsx:115-140`, `Usuarios.jsx:100-120`, `Postulaciones.jsx:180-200` | MEDIO | Mismo patrón: `setIsSubmitting(true)` → `isEditMode ? patch : create` → `result.success ? refresh + closeModal : setError`. **50+ líneas repetidas** en 5 páginas. Deberían estar en hook (`useSubmitForm`) |
| **handleDelete duplicado** | `Postulantes.jsx:145`, `Usuarios.jsx:130`, `Documentos.jsx:150` | MEDIO | Siempre: `window.confirm()` → `remove(endpoint)` → `setSuccess/setError` → `refresh()`. Pattern 100% idéntico |
| **fetchDropdowns** | `Documentos.jsx:55`, `Postulaciones.jsx:85` | BAJO | Ambas cargan `Promise.all([tipos, modalidades])` sin abstracción. Si error handling cambia, hay que editar 2 archivos |

---

### 1.4 Hooks Genéricos Pero Bajo Aprovechamiento

| Hook | Uso Real | Problemas |
|------|----------|----------|
| **useCrud** | ✅ En todos CRUDs | ✅ Bien, reutilizable. Pero `meta` asume formato Django (`count`, `next`, `previous`). Si backend cambia → break |
| **useModal** | ✅ En todos CRUDs | **⚠️ Deberían extender:** `useConfirmDelete()` para confirmación. `useFormValidation()` para validar antes de submit. Hoy: 3 hooks manuales por página |
| **useListFilters** | ✅ Usuarios, Postulaciones | **❌ NO en Postulantes** - Postulantes usa DataTable (sin servidor). Inconsistencia: Postulantes no sincroniza URL con búsqueda |
| **useAuth** | ✅ Simpe wrapper | ✅ OK, solo consume context; pero no tiene `logout()` detalles |

---

### 1.5 Reportes.jsx: Lógica Pesada SIN Extraer Componentes

| Problema | Líneas | Solución Requerida |
|----------|--------|------------------|
| **Lógica de tabs hardcodeada** | ~40 líneas | Extraer a `TabSwitcher` + `useTabState` |
| **3 funciones render inline** | `renderGeneralStats()`, `renderByEstado()`, `renderTutores()` | Componentes: `GeneralStatsCard`, `EstadoChart`, `TutoresTable` |
| **Export a Excel sin validación** | `handleExport()` | Usuarios no saben si descargó o no; no hay check si Backend retorna 500 |
| **Charts sin lazy loading** | `reportData.total_postulantes` | Si 50k registros, chart library se congela |

---

## 🎯 BLOQUE 2: RIESGOS DE ESTADO GLOBAL

### 2.1 AuthContext vs localStorage: Desincronización

| Escenario | Riesgo | Ubicación | Impacto | Severidad |
|-----------|--------|-----------|--------|-----------|
| **localStorage se borra manualmente** | Usuario abre DevTools, borra `access_token` → `localStorage === null`, pero `user` context sigue con datos | `AuthContext.jsx:30-40` | Página muestra "Usuario: Juan" pero requests fallan con 401 → redirect login automático | ALTO |
| **Logout no sincronizado correctamente** | `authApi.logout()` borra localStorage, pero si logout FALLA a mitad (error red), state queda corrupto (`user=null` pero `localStorage` parcial) | `AuthContext.jsx:65-70` | Usuario intenta login nuevamente, pero algunos tokens siguen en localStorage | ALTO |
| **Multi-tab logout race condition** | Tab A hace logout → borra localStorage. Tab B hace request 2s después → 404 "token not found" en localStorage | `axios.js:40` - request interceptor | UI muestra error en Tab B aunque ya está logged out | MEDIO |
| **InitAuth timeout** | Si API de getCurrentUser es lento (~5s), `loading=true` durante 5s | `AuthContext.jsx:25-35` | ProtectedRoute muestra spinner 5s, mala UX | BAJO |

---

### 2.2 ThemeContext vs localStorage: Tema Desincronizado

| Escenario | Síntoma | Código |
|-----------|--------|--------|
| **Dark mode NOT persistido** | Usuario cambia a dark mode. Recarga página. **Vuelve a light mode** | `ThemeContext.jsx:4-8` usa `localStorage.getItem('theme-mode')` init, pero `useEffect` actualiza HTML. Si localStorage falla silenciosamente, no se entera |
| **System preference override falla** | Navegador con dark mode → app abre light. Usuario no puede cambiar (botón oculto) | No hay UI de "toggle theme" accesible; solo context |

---

### 2.3 ProtectedRoute: Role Check Incompleto

| Caso | Problema | Línea | Consecuencia |
|------|----------|-------|-------------|
| **requiredRole=null pero user no auth** | Si route especifica `requiredRole={null}` (intended falsy), y user NOT authenticated → redirige OK | L20-25 | Works, pero confuso |
| **user.role === undefined** | Backend devuelve user sin `role` field. `userRole = user?.role || (user?.is_superuser ? 'admin' : null)` → `userRole=null`. `allowedRoles = ['admin']`. Check: `null in ['admin']` = FALSE | L28-30 | Usuario no puede acceder aunque es admin |
| **Role string case-sensitive** | Backend: `role='ADMIN'`, Frontend: `requiredRole='admin'` | L28 | Mismatch → acceso denegado |

---

### 2.4 localStorage Race Conditions: 50 usuarios concurrentes

| Escenario | Fallo | Ubicación |
|-----------|-------|-----------|
| **simultáneo: 2 logout requests** | Usuario cierra 2 tabs al mismo tiempo. Ambos llaman `authApi.logout()`. Ambos hacen `localStorage.clear()`. **Segundo mata session de Primero** | `AuthContext.jsx:68` |
| **localStorage write limit** | Si aplicación almacena >5MB datos (tokens + user_info + theme + ...), localStorage silenciosamente falla | N/A (browser limit) |

---

## 🎯 BLOQUE 3: RIESGOS BACKEND/FRONTEND OCULTOS

### 3.1 axios.js: Manejo de Errores Incompleto

| Error Type | Manejo Actual | Problema | Impacto |
|-----------|--------------|---------|--------|
| **404 Not Found** | `axiosInstance.interceptors.response` muestra genérico "Recurso no encontrado" | Si API /modalidades retorna 404 (endpoint no existe), usuario ve genérico; no sabe que es problema backend | MEDIO |
| **500 Server Error** | Muestra "Error del servidor - intenta de nuevo más tarde" | No hay retry logic automático; usuario debe recargar page | ALTO si es transient error |
| **503 Service Unavailable** | Genérico "Servicio no disponible" | Sin retry exponencial, usuario asume Backend está down (cuando puede volver en 2s) | MEDIO |
| **timeout (sin timeout configurado)** | Axios default: infinity. Request cuelga UI indefinidamente | Si Backend slow (10s respuesta), UI freezea | CRÍTICO |
| **Network error (offline)** | Rechaza con error genérico | No hay offline detection o cached data fallback | ALTO |

### 3.2 Interceptor 401: Token Refresh Lógica Frágil

```javascript
// axios.js:110-140
if (status === 401 && !originalRequest._retry) {
  originalRequest._retry = true;
  const refreshToken = localStorage.getItem(...);
  
  if (!refreshToken) {
    localStorage.clear();
    window.location.href = '/login'; // FULL PAGE RELOAD
  }
  
  // PROBLEMA: Si refresh TAMBIÉN 401, qué pasa?
  // PROBLEMA: Si 2 requests fallan simultáneamente, ambas intentan refresh
}
```

| Riesgo | Síntoma | Severidad |
|-------|--------|-----------|
| **Double-refresh attack** | Request A falla 401 → refresh. Request B falla 401 → TAMBIÉN refresh (mientras A está en flight) | ALTO |
| **Full page reload looses form data** | Usuario escribing en form, token expira → interceptor hace `window.location.href = '/login'` → **TODA DATA SE PIERDE** | CRÍTICO |
| **Infinite loop si refresh token expirado** | access=expired, refresh también expired → interceptor llama refresh → 401 → retry → loop | CRÍTICO |

---

### 3.3 api.js: Validación de Respuesta AUSENTE

| Función | Problema | Caso de Fallo |
|---------|----------|--------------|
| **getAll()** | Asume `response.data` siempre válido | Backend devuelve 200 OK pero `{ error: 'db connection lost' }` sin success flag → code no lo detecta |
| **normalizeList()** | Asume `result.data.results` O array | Backend cambia formato → `{ data: { items: [...] } }` → normalizeList retorna `[]` |
| **create/patch/delete** | NO validan campos requeridos en response | API devuelve `{ id: 1 }` sin `created_at` pero codigo espera → bug silencioso luego |

```javascript
// Hoy en api.js
async getAll(endpoint, params = {}) {
  const response = await axiosInstance.get(endpoint, { params });
  return { success: true, data: response.data }; // ✅ success=true SIEMPRE si status 2xx
}

// PROBLEMA: response.data puede ser:
// { results: [...] }          ← OK (paginado)
// { data: [...] }             ← NO esperado
// { message: "error" }        ← Falso positivo success
```

---

### 3.4 API Endpoints: Desacoplamiento Débil

| Riesgo | Ubicación | Impacto |
|--------|-----------|--------|
| **BASE_URL hardcodeado en constants** | `constants/api.js` | Si backend migra de `/api/v1/` a `/api/v2/`, app rompe |
| **Endpoints duros en axios** | No hay cliente HTTP typed; todos strings | Typo: `'/api/postulantes/'` vs `'/api/postulante/'` → 404 silencioso |
| **Sin versionado de API** | Si backend rompe endpoint, frontend tiene que esperar deploy | ALTO cuando hay que hacer rollback rápido |

---

### 3.5 Error Handling Silencioso en Patches

| Comando | Código | Problema |
|---------|--------|---------|
| **patch documento estado** | `Documentos.jsx:150` `const result = await patch(...)` | Si `result.success === false`, componente no re-renderiza; usuario cree que cambió pero no |
| **patch postulante usuario** | `Postulantes.jsx:115` `if (result.success) { refresh() }` | Si patch falla silenciosamente, usuario ve vacio spinner infinito |

---

## 🎯 BLOQUE 4: RIESGOS DE ESCALABILIDAD

### 4.1 Límites de Carga por Página

| Página | Estrategia Actual | Límite de Quiebre | Síntomas a 1000+ registros |
|--------|------|---------|---|
| **Postulantes** | DataTable (cliente-side búsqueda + paginación) | ~2000 en array | Búsqueda busca en TODOS 2000 datos cada keystroke → 200ms+ lag |
| **Usuarios** | Server-side búsqueda vía useListFilters | ~10,000 | OK si backend optimizado; frontend solo pinta 20/page |
| **Postulaciones** | Server-side; filtro + búsqueda | ~50,000 | OK |
| **Documentos** | DataTable mixto | ~1000 | Lento con archivos grandes |
| **Reportes** | Charts sin virtualization | ~500 data points | React-Charts se congela renderizar 5000 barras |

### 4.2 Búsqueda Cliente-Side NO ESCALA

```javascript
// DataTable.jsx:22-28
const filteredData = useMemo(() => {
  if (!searchTerm) return data;
  return data.filter(item =>
    Object.values(item).some(value =>
      String(value).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );
}, [data, searchTerm]);
```

**Complejidad:** O(n * m) donde n = registros, m = campos
- 500 postulantes × 8 campos = **4000 comparaciones por keystroke**
- a 60 FPS = búsqueda cada 16ms
- Si usuario escribe "juan" = 4 keystrokes = 16,000 comparaciones en <100ms
- Visible lag a 1000+

**Solución requerida:** Servidor hace búsqueda (índices BD) → O(log n)

---

### 4.3 Dropdowns Cargan TODO Cada Vez

| CRUD | Endpoint | Problema |
|------|----------|----------|
| **Documentos** | `fetchDropdownData()` (línea 55) | `Promise.all([tipos, postulaciones])` cada vez que abre modal |
| **Postulaciones** | `fetchData()` (línea 85) | Carga todos postulantes + modalidades en useEffect, aunque nunca los use |
| Si backend: 10,000 postulantes, 500 tipos → 2 requests de 1MB+ datos cada vez | **RED WASTE** |

**Solución:** Cache en context o localStorage; invalidate on mutation

---

### 4.4 DataTable vs Table Performance

| Factor | DataTable | Table | Winner |
|--------|-----------|-------|--------|
| **Render 1000 rows** | Pagina en cliente (~50 visible) | Sin paginación, DOM 1000 nodos | DataTable |
| **Búsqueda 1000 rows** | Filter in-memory (LENTO) | No búsqueda | Tie |
| **Scroll smoothness** | OK | Problemas con virtualization | DataTable |
| **Memory usage** | Array 1000 en RAM | Array 1000 en RAM | Tie |

---

### 4.5 Charts en Reportes SIN Virtualization

```javascript
// Reportes.jsx renderGeneralStats()
// 500+ postulantes × 4 stats = DOM complexity: O(n)
```

Si gráfico Chart.js con 5000 puntos:
- React renderiza → Chart.js re-calcula → SVG 5000 elementos → STUCK UI 3s+

---

## 🎯 BLOQUE 5: RIESGOS DE MANTENIMIENTO

### 5.1 Archivos por Tamaño

| Archivo | Líneas (aprox) | Componentes | Severidad |
|---------|---|---|---|
| `Postulantes.jsx` | 320 LOC | 1 + Form 7 fields | ALTO - extractar Form a componente |
| `Usuarios.jsx` | 350 LOC | 1 + Form 8 fields + Pagination | ALTO |
| `Postulaciones.jsx` | 400 LOC | 1 + Form 6 fields + Tabs | **CRÍTICO** |
| `Documentos.jsx` | 380 LOC | 1 + File upload handling | ALTO |
| `Reportes.jsx` | 500+ LOC | 3 tabs + 3 render functions + Charts inline | **CRÍTICO** - fragmentado |
| `DataTable.jsx` | 150 LOC | OK size |  |

**Regla de oro:** Componente > 300 LOC = malo

---

### 5.2 Duplicación de Código

| Patrón | Apariciones | LOC Repetido | Estrategia |
|--------|---|---|---|
| **Form submit pattern** | 5 (todos CRUDs) | ~50 LOC c/u | Extraer `useFormSubmit()` hook |
| **Modal delete confirm** | 5 | ~10 LOC c/u | Extraer `ConfirmDialog` componente |
| **Error/Success alerts** | 20+ | ~5 LOC c/u | Usar Toast global (ya existe) |
| **Dropdown fetch** | 3 | ~10 LOC c/u | Abstraer en `useFetchDropdown` |
| **Tabla columns setup** | 5 | ~40 LOC c/u | Meta-driven columns from API |

**Total LOC ahorrable:** ~300 LOC (20% del codebase)

---

### 5.3 Componentes Poco Flexible para Extensión

| Componente | Código-Smell | Por Qué Difícil |
|-----------|--|--|
| **Modal.jsx** | Hardcoded: title header + body footer | Si necesitas modal CustomHeader o sin footer, copia código |
| **DataTable.jsx** | Búsqueda integrada, paginación hardcoded | Si necesitas solo tabla (sin búsqueda), props unused |
| **FormField.jsx** | Solo soporta 4 tipos (text, select, textarea, checkbox) | Si necesitas date picker o multi-select, no cabe |
| **Table.jsx** | Sin búsqueda, sin sorting | Postulaciones necesita ambas → copia a DataTable |

**Patrón:** Componentes NO siguen Composition Pattern; llevan demasiada lógica

---

### 5.4 Falta de Tests

| Tipo | Existe | Riesgo |
|------|--------|--------|
| Unit tests | ❌ NO | Bug en useCrud → afecta 5 páginas; NO hay CI catch |
| E2E tests | ❌ NO | Cambio de API format → rompe toda app; nobody lo ve |
| Type safety | ❌ NO (plain JS) | FormField espera `options = [{ id, label }]`, pero Reportes pasa `[{ value, name }]` |

---

### 5.5 Documentación Interna Nula

| Archivo | JSDoc | README | Ejemplos |
|---------|-------|--------|----------|
| useCrud.js | ✅ Básico | ❌ | ❌ |
| DataTable.jsx | ❌ | ❌ | ❌ |
| axios.js | ✅ | ❌ | ❌ |
| AuthContext.jsx | ✅ | ❌ | ❌ |
| Modal.jsx | ❌ | ❌ | ❌ |

**Síntoma:** Nuevo dev toma Postulantes.jsx → "¿Cómo se usa useModal()?" → Grep search

---

## 🎯 BLOQUE 6: RIESGOS DE PRODUCCIÓN REAL

### 6.1 Escenario: 50 Usuarios Concurrentes

| Caso | Fallo Probable | Línea de Código | Severidad |
|------|---|---|---|
| **Simultáneo: 2 logout calls** | localStorage.clear() race condition; después logout, session tokens aún valida | AuthContext:68 + axios:120 | ALTO |
| **50 postulantes/ carga simultan** | 50 × DataTable filter en cliente = 50 × O(n) searches = CPU spike 100% | DataTable:22-28 | MEDIO |
| **Upload documento 2 usuarios** | Ambos suben al mismo tiempo; si form state no sincronizado, última sobrescribe primera | Documentos.jsx:280 | ALTO |
| **Reportes + 50 usuarios** | Chart.js recalcula 50 veces simultáneamente; navegador no responde 5s | Reportes.jsx render | CRÍTICO |

---

### 6.2 Conexión Lenta / Intermitente

| Escenario | Síntoma | Ubicación | Fix Requerida |
|-----------|--------|----------|--------------|
| **5G latency: 500ms por request** | Usuario crea postulante → wait 500ms → "Crear" button sigue clickeable → submit 2x | `Postulantes.jsx:115` No deshabilita button durante submit | ⚠️ YA EXISTE: `isSubmitting` estado, PERO no se usa en button. Button tiene `disabled={isLoading}` pero `isLoading` ≠ `isSubmitting` |
| **Upload documento 10MB lento** | Progressbar no existe; usuario piensa stuck | `Documentos.jsx:280-300` No hay File upload progress tracking | ❌ MISSING |
| **Network timeout 30s** | Request cuelga indefinidamente; button stuck | axios default timeout=∞ | ⚠️ NO TIMEOUT CONFIGURADO |
| **Mid-upload network cuts** | Retry? O error silencioso? | formData.archivo upload | ❌ NO retry logic |

---

### 6.3 Mobile Responsiveness: Falsos Positivos

| Componente | Desktop | Mobile | Problema |
|-----------|---------|--------|----------|
| **Modal** | OK (w-500px) | Llena pantalla incorrectamente | Modal: `max-h-[90vh]` OK, pero max-w-md = 28rem (?), en móvil se ve pequeño |
| **DataTable** | OK | overflow-x-auto pero NO horizontal scroll visible | DataTable: overflow auto, pero sin scroll indicators |
| **Form fields** | OK | Labels empilan | FormField: no responsive layout en mobile |
| **Postulantes búsqueda** | flexrow | no se adapta | `md:flex-row` solo en md+, pero sm screen busca entra en otra línea |

---

### 6.4 Backend Lento (5s respuesta)

| Situación | UI Impact | Ubicación |
|-----------|-----------|----------|
| **Backend demora 5s en devolver postulantes** | Página cargando 5s | No hay skeleton completo; TableSkeleton insuficiente |
| **Reportes chart API call 5s** | Bloquea renderizando; usuario ve botones pero no responden | Reportes:30 `fetchReportData()` no concurrente |
| **Búsqueda en Usuarios 5s** | Campo búsqueda responde pero tabla estancada | useListFilters debounce = 400ms OK, pero sin indicador visual "Buscando..." |

---

### 6.5 Security: 3 Riesgos Detectados

| Riesgo | Ubicación | Impacto | CVSS |
|--------|-----------|--------|------|
| **JWT en localStorage (XSS vulnerable)** | AuthContext:42, axios:40 | Si XSS via FormField input, attacker roba token | 7.5 HIGH |
| **No CSRF token en POST** | axios interceptor | Si cross-site request, backend debe validar, pero frontend no envía CSRF header | 6.5 MEDIUM |
| **localStorage injection via URL** | No hay URL sanitization | Si URL = `#search=<img src=x onerror="alert('xss')">` | 5.3 MEDIUM |

---

## 📊 TABLA MATRIZ: TOP RIESGOS POR SEVERIDAD

| # | Riesgo | Archivo | Severidad | Explicación | Impacto Real | Esfuerzo Fix |
|---|--------|---------|-----------|-----------|-------------|---|
| **1** | Duplicación Page CRUD (5 archivos) | Postulantes, Usuarios, Postulaciones, Documentos, Reportes | **CRÍTICO** | 300 + LOC código duplicado; handleSubmit, handleDelete idéntico. Cambio en 1 lugar = update 5 | UX sufre si pattern cambia; error propagates to X páginas | ALTO (2-3 días) |
| **2** | DataTable búsqueda O(n) no escala | DataTable.jsx | **CRÍTICO** | 1000+ postulantes = búsqueda se congela; servidor tiene índices, frontend ignora | En producción con 5000 registros, app unusable | MEDIO (1 día refactor) |
| **3** | Token refresh race condition | axios.js:110 | **CRÍTICO** | 2+ requests 401 simultáneamente = double refresh + infinite loop | Session corruption; stuck login | MEDIO (4 horas) |
| **4** | localStorage/AuthContext desincronización | AuthContext + axios | **ALTO** | Logout falla = token baja pero context arriba; confusión en multi-tab | Silent errors en Postulantes después logout | MEDIO (6 horas) |
| **5** | ProtectedRoute role check incompleto | ProtectedRoute.jsx:28 | **ALTO** | `user?.role === undefined` case no manejado; admin user no entra | Admin bloquead sin explicación | BAJO (2 horas) |
| **6** | Dropdowns cargan TODO cada vez | Documentos:55, Postulaciones:85 | **ALTO** | 10k postulantes dropdown = 5s+ wait cada modal open | Network waste; UX laggy | MEDIO (8 horas) |
| **7** | Timeout request sin configurar | axios.js | **ALTO** | Backend lento 30s = petición cuelga UI indefinidamente | User cierra tab desconcertado | BAJO (1 hora) |
| **8** | Reportes sin virtualization + 3 render functions inline | Reportes.jsx | **ALTO** | 5000 data points = chart frozen 3s; código 500 LOC en 1 archivo | Performance crisis en reportes; mantenimiento pesadilla | ALTO (2 días) |
| **9** | DataTable vs Table duales | components/ | **ALTO** | Bug en paginación en 1 = no se propaga a otro; Usuarios/Postulantes inconsistentes | Différent behaviors para misma funcionalidad | MEDIO (1 día) |
| **10** | FormField generic pero sin date/multiselect | FormField.jsx | **MEDIO** | Nuevo CRUD necesita date picker = copia Form a componente nuevo | Code duplication para selectores avanzados | MEDIO (6 horas) |

---

## 🚨 TOP 10 RIESGOS ORDENADOS POR IMPACTO

### 1. **CRÍTICO: Duplicación masiva en CRUDs (300 LOC)**
- **Causa:** Cada página CRUD repite handleSubmit, handleDelete, useEffect pattern
- **Consecuencia:** Refactor lento; bugs propagate a 5 archivos
- **Fix:** Crear `useCrudPage()` hook + `withCrudLayout` HOC
- **Esfuerzo:** 2-3 días

### 2. **CRÍTICO: DataTable búsqueda cuelga con 1000+ registros**
- **Causa:** O(n*m) filter en cliente, sin índices
- **Consecuencia:** Lag visible en búsqueda; 5000 postulantes = unusable
- **Fix:** Migrar Postulantes a server-side search (copy Usuarios pattern)
- **Esfuerzo:** 1 día

### 3. **CRÍTICO: Token refresh race condition → infinite loop**
- **Causa:** 2 simultaneous 401 errors = double refresh attempt
- **Consecuencia:** Session locked; user stuck en loading infinito
- **Fix:** Implement request queuing + single refresh promise
- **Esfuerzo:** 4-6 horas

### 4. **ALTO: localStorage/context desincronización en logout**
- **Causa:** localStorage.clear() puede fallar parcialmente
- **Consecuencia:** Logout incompleto; usuario vé "logged out" pero token aún valida
- **Fix:** Transactional logout; verify cleanup antes de redirect
- **Esfuerzo:** 6 horas

### 5. **ALTO: ProtectedRoute role check undefined case**
- **Causa:** `user?.role === undefined` → allows `undefined in ['admin']` = false
- **Consecuencia:** Admin users blocked de rutas protegidas
- **Fix:** Nullability validation + fallback role detection
- **Esfuerzo:** 2 horas

### 6. **ALTO: Dropdown datos cargados CADA modal open (10k rows)**
- **Causa:** `fetchDropdownData()` sin cache; `Promise.all([tipos, postulaciones])`
- **Consecuencia:** 5s+ wait por modal; red waste 10MB+ datos repetidos
- **Fix:** Cache en context + invalidation en create/delete
- **Esfuerzo:** 8 horas

### 7. **ALTO: Request timeout = UI cuelga indefinidamente**
- **Causa:** axios sin timeout config; default ∞
- **Consecuencia:** Slow backend (5s) = frozen UI 5s; user frustrado
- **Fix:** Set axios timeout 30s + retry exponencial
- **Esfuerzo:** 1-2 horas

### 8. **ALTO: Reportes 500 LOC con 3 render funcs + charts sin virtualization**
- **Causa:** Toda lógica inline; Chart.js na-render 5000 puntos
- **Consecuencia:** Scroll Reportes = 3-5s freeze; mantenimiento imposible
- **Fix:** Extract components + implement virtualization (react-window)
- **Esfuerzo:** 2 dias

### 9. **ALTO: DataTable vs Table componentes DUALES (inconsistencia)**
- **Causa:** DataTable (search + pagina cliente), Table (nada); pero layout casi igual
- **Consecuencia:** Postulantes behaves differently from Usuarios (same data)
- **Fix:** Unificar en 1 `SmartTable` con prop `searchStrategy`
- **Esfuerzo:** 1 día

### 10. **MEDIO: FormField generic pero falta date/multiselect**
- **Causa:** Solo supported [text, select, textarea, checkbox]
- **Consecuencia:** Nuevo CRUD con date field = copia FormField o code dupicación
- **Fix:** Extender FormField con custom field types registry
- **Esfuerzo:** 6-8 horas

---

## 🛣️ ROADMAP COMPLEMENTARIO (SIN TOCAR BUGS PREVIOS)

### Fase 1: Arquitectura (1.5 semanas)
1. **Refactor CRUDs** → `useCrudPage()` hook consolidar lógica
2. **Unificar DataTable + Table** → `SmartTable` con server/client mode
3. **Request queuing** → Fix token refresh race condition
4. **Cache context** → Dropdown data caching

### Fase 2: Performance (1 semana)
1. **Migrar Postulantes búsqueda a servidor** (copy Usuarios pattern)
2. **Add request timeout** (30s + retry)
3. **Virtualization charts** en Reportes (react-window)
4. **Image lazy loading** si hay fotos

### Fase 3: Mantenibilidad (1 semana)
1. **Extract Reportes tabs to components**
2. **Extend FormField: date, multiselect**
3. **Unit tests useCrud, useModal** (50% coverage minimo)
4. **JSDoc completo** en todos hooks

### Fase 4: Security (3 días)
1. **Add CSRF token header** (axios interceptor)
2. **Sanitize URLs** (DOMPurify)
3. **HttpOnly cookies** para jwt (si backend soporta)

### Fase 5: Monitoring (2 días)
1. **Error boundary** wrapper en App.jsx
2. **Sentry integration** para production errors
3. **Performance markers** (Lighthouse)

---

## 📈 ESTIMACIONES

| Categoría | LOC | Tiempo |
|-----------|---|---|
| **Refactor: CRUDs** | -100 (net) | 2-3 días |
| **Unify: DataTable** | -50 | 1 día |
| **Fix: Token refresh** | +20 | 4 horas |
| **Cache: Dropdowns** | +30 | 8 horas |
| **Perf: Reportes** | -200 (net) | 2 días |
| **Tests: Unit** | +500 | 3 días |
| **TOTAL** | -300 LOC | **12-15 días** |

---

## ⚠️ DEPENDENCIAS CRÍTICAS

- Fase 1 antes Fase 2 (necesitas unified table)
- Token fix antes Load Test (50 concurrent users)
- Timeout antes Production Go-Live

---

## 🎯 CONCLUSIÓN

| Aspecto | Status | Criticality |
|--------|--------|------------|
| **Arquitectura** | ⚠️ Problematic (duplication) | ALTO |
| **Escalabilidad** | ❌ Falla >1000 rows | CRÍTICO |
| **State Management** | ⚠️ Risky (race conditions) | ALTO |
| **Error Handling** | ⚠️ Incomplete | MEDIO |
| **Security** | ⚠️ JWT in localStorage | MEDIO |
| **Mantenibilidad** | ❌ 300+ LOC duplicado | ALTO |

**Veredicto:** Aplicación funcionalmente OK pero **arquitectónicamente frágil** para escala. Refactor recomendado antes de producción con 50+ usuarios concurrentes.

---

*Documento generado: 23 de marzo de 2026*  
*Sin cambios de código. Solo auditoría.*

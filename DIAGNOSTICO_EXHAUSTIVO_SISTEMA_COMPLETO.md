# DIAGNÓSTICO EXHAUSTIVO DEL SISTEMA DE GRADUACIÓN
**Fecha de análisis**: 8 de abril de 2026  
**Versión del sistema**: 1.0.0 Production-Ready  
**Stack**: Django 6.0 + React 18 + PostgreSQL 15 + Docker Compose

---

## 📋 TABLA DE CONTENIDOS
1. [Objetivo General del Sistema](#1-objetivo-general-del-sistema)
2. [Roles y Usuarios](#2-roles-y-usuarios)
3. [Módulos del Sistema](#3-módulos-del-sistema)
4. [Flujo de Funcionamiento](#4-flujo-de-funcionamiento)
5. [Base de Datos](#5-base-de-datos)
6. [Tecnologías Utilizadas](#6-tecnologías-utilizadas)
7. [Arquitectura del Sistema](#7-arquitectura-del-sistema)
8. [Seguridad](#8-seguridad)
9. [Problemas Encontrados](#9-problemas-encontrados)
10. [Recomendaciones y Mejoras](#10-recomendaciones-y-mejoras)

---

## 1. OBJETIVO GENERAL DEL SISTEMA

### Propósito Principal
El **Sistema de Graduación** es una plataforma administrativa integral para gestionar el proceso completo de graduación / titulación en instituciones educativas, automatizando workflows complejos que normalmente se mantenían en procesos manuales dispersos.

### Problema que Resuelve
En las universidades tradicionales, el proceso de graduación implica:
- ✅ Registro manual de postulantes a diferentes modalidades de titulación
- ✅ Seguimiento desorganizado de documentos requeridos
- ✅ Aprobaciones sin auditoría completa
- ✅ Reportes manuales y inconsistentes
- ✅ Falta de visibilidad en etapas del proceso

**El sistema resuelve esto mediante:**
- Automatización de workflows en modalidades personalizables
- Gestión centralizada de documentos con validación
- Sistema de auditoría completo de todo cambio
- Dashboards con estadísticas en tiempo real
- Reportes generables en múltiples formatos

### Beneficiarios Primarios
1. **Estudiantes/Postulantes**: Pueden ver el estado de su postulación y documentos requeridos
2. **Administrativos**: Gestión de postulaciones, documentos, etapas y aprobaciones
3. **Directivos/Rectores**: Dashboard con métricas de titulación, eficiencia por carrera
4. **Auditores**: Trazabilidad completa de acciones por usuario

### Valor Estratégico
- Reducción de tiempo en procesos de graduación (estimado 70%)
- Trazabilidad legal completa (cumplimiento normativo)
- Datos confiables para toma de decisiones académicas
- Escalabilidad para múltiples universidades/programas

---

## 2. ROLES Y USUARIOS

### Estructura de Roles (Django Custom User)

#### 2.1 ADMINISTRADOR (`admin`)
**Permisos**: ACCESO TOTAL  
**Donde se define**: `usuarios/models.py` → `CustomUser.ROLE_CHOICES`

**Acciones permitidas:**
- Crear, editar, eliminar usuarios del sistema
- Ver todas las postulaciones (sin restricción)
- Aprobar/rechazar documentos
- Crear modalidades y etapas
- Acceder a dashboard institucional
- Ver auditoria completa
- Generar reportes
- Cambiar estados de postulaciones

**Módulos accesibles:**
- ✅ Dashboard Institucional
- ✅ Gestión de Usuarios
- ✅ Gestión de Postulantes
- ✅ Gestión de Postulaciones
- ✅ Gestión de Documentos
- ✅ Gestión de Modalidades/Etapas
- ✅ Reportes Avanzados
- ✅ Auditoría Completa

---

#### 2.2 ADMINISTRATIVO (`administ`)
**Permisos**: GESTIÓN OPERATIVA  
**Donde se define**: `config/permissions.py` → Permisos por Django

**Acciones permitidas:**
- Ver todas las postulaciones y postulantes
- Crear nuevos postulantes
- Actualizar documentos (cambiar estado a aprobado/rechazado)
- Adicionar comentarios internos a postulaciones
- Generar reportes operativos
- Ver auditoria de cambios
- NO puede: Crear/editar usuarios, NO puede cambiar modalidades

**Módulos accesibles:**
- ✅ Dashboard (limitado)
- ✅ Gestión de Postulantes (CRUD completo)
- ✅ Gestión de Postulaciones (ver y actualizar)
- ✅ Gestión de Documentos (revisar y aprobar)
- ✅ Reportes Operativos
- ⚠️ Modalidades (solo lectura)

---

#### 2.3 ESTUDIANTE (`estudiante`)
**Permisos**: ACCESO LIMITADO A DATOS PROPIOS  
**Donde se define**: `config/permissions.py` → `PostulanteRolePermission`

**Acciones permitidas:**
- Ver su propia postulación
- Ver documentos que debe aportar
- Ver estado de documentos compartidos
- Ver observaciones a sus documentos
- NO puede: Ver otras postulaciones, NO puede crear usuarios

**Módulos accesibles:**
- ✅ Dashboard (solo métricas genéricas)
- ✅ Mi Perfil/Postulante
- ✅ Mis Postulaciones
- ✅ Mis Documentos
- ❌ Gestión de Usuarios
- ❌ Gestión de Modalidades

---

### 2.4 Asignación de Permisos

**Sistema de Permisos**: Django Permissions basado en modelos  
**Ubicación**: `config/permissions.py` y modelos con `permissions` Meta

**Ejemplo de mapeo:**
```python
# Vista que verifica roles
class PostulanteRolePermission(BasePermission):
    def has_permission(self, request, view):
        return _is_authenticated(request.user)
    
    def has_object_permission(self, request, view, obj):
        # Admin/Administrativo puede ver todo
        if can_view_all_postulantes(user):
            return True
        # Estudiante solo ve lo suyo
        return obj.usuario_id == user.id
```

---

## 3. MÓDULOS DEL SISTEMA

### 3.1 MÓDULO DE AUTENTICACIÓN Y USUARIOS
**Ubicación Backend**: `usuarios/` app  
**Ubicación Frontend**: `pages/Login.jsx` + `context/AuthContext.jsx`

**Funciones:**
- Autenticación con JWT (JSON Web Tokens)
- Gestión de usuarios (CRUD)
- Asignación de roles
- Renovación de tokens

**Pantallas:**
1. **Login** (`/login`)
   - Entrada de usuario y contraseña
   - Validación de credenciales contra BD
   - Retorna tokens (access + refresh)

2. **Gestión de Usuarios** (`/usuarios`)
   - Tabla de usuarios existentes (admin only)
   - Crear nuevo usuario
   - Editar usuario (cambiar rol, estado activo/inactivo)
   - Eliminar usuario
   - Cambiar contraseña

**Endpoints API:**
```
POST   /api/auth/login/              - Autenticación
POST   /api/auth/refresh/            - Renovación de token
GET    /api/usuarios/                - Listar usuarios
POST   /api/usuarios/                - Crear usuario
PUT    /api/usuarios/{id}/           - Editar usuario completo
PATCH  /api/usuarios/{id}/           - Editar usuario parcial
DELETE /api/usuarios/{id}/           - Eliminar usuario
```

**Operaciones CRUD:**
- ✅ CREATE: Crear nuevo usuario con rol
- ✅ READ: Listar y buscar usuarios
- ✅ UPDATE: Editar datos y contraseña
- ✅ DELETE: Eliminar usuario

---

### 3.2 MÓDULO DE POSTULANTES
**Ubicación Backend**: `postulantes/` app (modelo `Postulante`)  
**Ubicación Frontend**: `pages/Postulantes.jsx`

**Funciones:**
- Registro e información de estudiantes que solicitan titulación
- Gestión de datos personales (CI, carrera, código)
- Vinculación con usuario del sistema

**Pantalla Principal** (`/postulantes`):
- Tabla de postulantes con búsqueda (por nombre, CI)
- Filtros por carrera, facultad
- Crear postulante
- Editar datos personales
- Ver detalles (incluyendo postulaciones asociadas)

**Formulario de Creación/Edición:**
```
Campos:
- Nombre (required)
- Apellido (required)
- CI - Cédula de Identidad (unique, required)
- Teléfono (required)
- Carrera (optional, legacy)
- Facultad (optional, legacy)
- Código Estudiante (unique, required)
```

**Operaciones CRUD:**
- ✅ CREATE: Registrar nuevo postulante
- ✅ READ: Listar y buscar postulantes
- ✅ UPDATE: Actualizar datos del postulante
- ✅ DELETE: Eliminar postulante (soft-delete recomendado)

**Endpoints API:**
```
GET    /api/postulantes/              - Listar (con paginación)
POST   /api/postulantes/              - Crear
GET    /api/postulantes/{id}/         - Ver detalle
PUT    /api/postulantes/{id}/         - Editar completo
PATCH  /api/postulantes/{id}/         - Editar parcial
DELETE /api/postulantes/{id}/         - Eliminar
```

---

### 3.3 MÓDULO DE POSTULACIONES
**Ubicación Backend**: `postulantes/` app (modelo `Postulacion`)  
**Ubicación Frontend**: `pages/Postulaciones.jsx`

**Funciones:**
- Gestión del proceso de titulación por modalidad
- Seguimiento de etapas
- Cambio de estados
- Vinculación de documentos requeridos

**Pantalla Principal** (`/postulaciones`):
- Tabla de postulaciones con filtros
  - Por modalidad
  - Por gestión (año)
  - Por estado (borrador, en_revision, aprobada, rechazada)
- Buscar por título de trabajo, postulante
- Crear nueva postulación
- Editar postulación
- Ver detalles (con documentos asociados)
- Avanzar etapa (si permiso `puede_avanzar_etapa`)

**Estados de Postulación:**
1. **borrador** - Inicial, sin revisar
2. **en_revision** - Enviada para revisión
3. **aprobada** - Aceptada por administrativo
4. **rechazada** - Rechazada con observaciones

**Estados Generales (Workflow):**
1. **EN_PROCESO** - Ingresó al sistema
2. **PERFIL_APROBADO** - Datos del estudiante validados
3. **PRIVADA_APROBADA** - Modalidad privada aprobada
4. **PUBLICA_APROBADA** - Modalidad pública aprobada
5. **TITULADO** - Completó proceso

**Formulario de Creación/Edición:**
```
Campos:
- Postulante (required, select)
- Modalidad (required, select)
- Título del Trabajo (required)
- Tutor (optional, legacy)
- Gestión (required, año)
- Estado (dropdown: borrador, en_revision, aprobada, rechazada)
- Estado General (dropdown: EN_PROCESO, PERFIL_APROBADO, etc.)
- Observaciones (textarea)
```

**Operaciones CRUD:**
- ✅ CREATE: Crear nueva postulación
- ✅ READ: Listar y filtrar postulaciones
- ✅ UPDATE: Cambiar estado, observaciones
- ✅ DELETE: Cancelar postulación

**Endpoints API:**
```
GET    /api/postulaciones/            - Listar (filtrable)
POST   /api/postulaciones/            - Crear
GET    /api/postulaciones/{id}/       - Ver detalle
PUT    /api/postulaciones/{id}/       - Editar completo
PATCH  /api/postulaciones/{id}/       - Editar parcial
DELETE /api/postulaciones/{id}/       - Eliminar
```

---

### 3.4 MÓDULO DE DOCUMENTOS
**Ubicación Backend**: `documentos/` app  
**Ubicación Frontend**: `pages/Documentos.jsx`

**Funciones:**
- Definir tipos de documentos por etapa
- Gestión de carga y validación de documentos
- Aprobación/rechazo con comentarios

**Pantalla Principal** (`/documentos`):
- Tabla de documentos con estado
- Filtros por estado (pendiente, aprobado, rechazado)
- Buscar por tipo, postulante
- Subir documento
- Validar documento
- Agregar comentarios de revisión
- Descargar documento

**Estados de Documento:**
1. **pendiente** - Cargado, esperando revisión
2. **aprobado** - Validado por administrativo
3. **rechazado** - Rechazado con motivo

**Pantalla de Revisión:**
```
Muestra:
- Nombre del postulante
- Tipo de documento requerido
- Archivo subido (preview si es PDF)
- Drop-down Estado
- Campo comentario de revision
- Botón: Guardar revisión
```

**Operaciones CRUD:**
- ✅ CREATE: Cargar nuevo documento
- ✅ READ: Listar documentos por postulación
- ✅ UPDATE: Cambiar estado (aprobado/rechazado)
- ✅ DELETE: Eliminar documento

**Endpoints API:**
```
GET    /api/documentos/               - Listar
POST   /api/documentos/               - Cargar
GET    /api/documentos/{id}/          - Ver detalle
PUT    /api/documentos/{id}/          - Actualizar
PATCH  /api/documentos/{id}/          - Actualizar parcial
DELETE /api/documentos/{id}/          - Eliminar
GET    /api/tipos-documento/          - Listar tipos
```

---

### 3.5 MÓDULO DE MODALIDADES Y ETAPAS
**Ubicación Backend**: `modalidades/` app  
**Ubicación Frontend**: `pages/Modalidades.jsx`

**Funciones:**
- Definir modalidades de titulación (ej: Defensa Privada, Pública, Tesis)
- Configurar etapas por modalidad
- Asignar documentos requeridos por etapa

**Pantalla Principal** (`/modalidades`):
- Tabla de modalidades activas
- Crear nueva modalidad
- Editar modalidad
- Ver etapas asociadas
- Crear etapa dentro de modalidad
- Editar etapa (orden, nombre)
- Eliminar etapa

**Estructura Jerárquica:**
```
Modalidad (ej: "Defensa Privada")
  ├── Etapa 1: "Revisión de Perfil"
  │   ├── Tipo Documento: "CV"
  │   ├── Tipo Documento: "Resumen"
  │   └── Tipo Documento: "Carta de Aceptación Tutor"
  │
  ├── Etapa 2: "Revisión de Documentos"
  │   ├── Tipo Documento: "Trabajo completo"
  │   └── Tipo Documento: "Certificado de cumplimiento"
  │
  └── Etapa 3: "Defensa"
      └── Tipo Documento: "Acta de defensa"
```

**Formulario Modalidad:**
```
Campos:
- Nombre (unique, required)
- Descripción (opcional)
- Activa (boolean toggle)
```

**Formulario Etapa:**
```
Campos:
- Nombre (required)
- Orden (required, ej: 1, 2, 3)
- Activa (boolean)
```

**Operaciones:**
- ✅ CREATE: Crear modalidad
- ✅ READ: Listar modalidades (solo lectura por default)
- ✅ UPDATE: Editar modalidad
- ✅ DELETE: Eliminar modalidad

**Endpoints API:**
```
GET    /api/modalidades/              - Listar
POST   /api/modalidades/              - Crear
PUT    /api/modalidades/{id}/         - Editar
DELETE /api/modalidades/{id}/         - Eliminar
GET    /api/etapas/                   - Listar (READ-ONLY)
```

---

### 3.6 MÓDULO DE REPORTES Y DASHBOARD
**Ubicación Backend**: `reportes/` app  
**Ubicación Frontend**: `pages/Dashboard.jsx` + `pages/Reportes.jsx`

**Funciones:**
- Dashboard con KPIs institucionales
- Gráficos de tendencias
- Reportes descargables (PDF, Excel, CSV)
- Estadísticas por tutor, carrera

#### 3.6.1 DASHBOARD (`/dashboard`)

**Pantalla Principal:**
Muestra 4 tarjetas de estadísticas + 3 gráficos

**Tarjetas de Estadísticas:**
1. **Total de Postulantes**
   - Valor: Cantidad de registros en `Postulante`
   - Cambio mes-a-mes (porcentaje)
   
2. **Postulaciones en Proceso**
   - Valor: Count donde `estado != rechazada`
   - Cambio mes-a-mes (porcentaje)

3. **Documentos Aprobados**
   - Valor: Count donde `estado = aprobado`
   - Cambio mes-a-mes (porcentaje)

4. **Tasa de Titulación**
   - Valor: % de postulantes titulados
   - Cambio mes-a-mes (porcentaje)

5. **Satisfacción General** (N/A si sin datos)
   - Valor: Promedio de puntuaciones (0-10)
   - Muestra "N/A" cuando `total_documentos == 0`

**Gráficos:**

1. **Line Chart** - Evolución de postulantes (últimos 6 meses)
   - X: Mes
   - Y: Cantidad de postulantes nuevos

2. **Bar Chart** - Documentos por estado
   - Barras: pendiente, aprobado, rechazado
   - Y: Cantidad

3. **Pie Chart** - Postulaciones por modalidad
   - Secciones: Defensa Privada, Pública, Tesis, etc.
   - Muestra porcentaje

**Tabla Reciente:**
- Últimos 5 postulantes registrados
- Columnas: Nombre, CI, Carrera, Código Estudiante

**Endpoints API:**
```
GET /api/reportes/dashboard-general/      - Datos stats
GET /api/reportes/dashboard-chart-data/   - Datos gráficos
```

---

#### 3.6.2 REPORTES (`/reportes`)

**Funciones:**
- Consultar estadísticas avanzadas
- Filtrar por rango de fechas
- Exportar en múltiples formatos

**Reportes Disponibles:**

1. **Reporte de Postulaciones**
   - Filtros: Modalidad, Gestión, Estado
   - Columnas: Postulante, Modalidad, Estado, Fecha
   - Exportar: PDF, Excel, CSV

2. **Reporte de Documentos**
   - Filtros: Estado, Tipo Documento
   - Columnas: Documento, Postulación, Estado, Fecha
   - Exportar: PDF, Excel, CSV

3. **Estadísticas de Tutores**
   - Muestra: Cantidad alumnos por tutor
   - Tasa titulación por tutor
   - Filtros: Año, Carrera
   - Acción: Exportar a Excel

4. **Reporte de Eficiencia por Carrera**
   - Muestra: Tiempo promedio por carrera
   - Tasa de titulación
   - Cantidad de postulantes por carrera

**Operaciones:**
- ✅ READ: Ver reportes
- ✅ EXPORT: Descargar en PDF/Excel/CSV
- ❌ CREATE/UPDATE/DELETE: No aplica (datos inmutables)

**Endpoints API:**
```
GET /api/reportes/dashboard-general/                   - Dashboard
GET /api/reportes/estadisticas-tutores/               - Tutores
GET /api/reportes/estadisticas-tutores/exportar/      - Excel tutores
GET /api/reportes/estadisticas-tutores/<id>/alumnos/  - Detalle tutor
GET /api/reportes/eficiencia-carreras/                - Carreras
```

---

### 3.7 MÓDULO DE AUDITORÍA
**Ubicación Backend**: `auditoria/` app  
**Ubicación Frontend**: INTEGRADO en componentes

**Funciones:**
- Registrar TODOS los cambios en modelos auditables
- Trazabilidad de usuario, fecha, acción
- Almacenar estado anterior y nuevo

**Información Registrada:**
```python
{
  "usuario": "admin",
  "accion": "UPDATE",
  "modelo_afectado": "Documentos",
  "objeto_id": "123",
  "estado_anterior": {"estado": "pendiente"},
  "estado_nuevo": {"estado": "aprobado"},
  "fecha": "2026-04-08T10:30:00Z",
  "detalles": { ... }
}
```

**Modelos Auditados:**
- Postulante (CREATE, UPDATE, DELETE)
- Postulacion (CREATE, UPDATE, DELETE, estado_general change)
- DocumentoPostulacion (CREATE, UPDATE, DELETE)
- Modalidad (CREATE, UPDATE, DELETE)
- Usuario (CREATE, UPDATE, DELETE)

**Acceso a Auditoría:**
- Admin: Acceso completo
- Administrativo: Ver cambios (lectura)
- Estudiante: NO acceso

**Endpoints API:**
```
GET /api/auditoria/                 - Listar logs
GET /api/auditoria/{id}/            - Ver detalle log
```

---

## 4. FLUJO DE FUNCIONAMIENTO

### 4.1 FLUJO DE INICIO DE SESIÓN

```
┌─────────────────────────────────────────────────────────┐
│  USUARIO ACCEDE A http://localhost:5173/login           │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend: Renderiza Login.jsx                         │
│  - Input usuario                                        │
│  - Input contraseña                                     │
│  - Botón "Entrar"                                       │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼ (Usuario ingresa credenciales)
┌─────────────────────────────────────────────────────────┐
│  Frontend: POST /api/auth/login/                        │
│  Body: { username, password }                           │
│  Via: axios.post() + interceptor JWT                    │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼ (Viaja por Nginx)
┌─────────────────────────────────────────────────────────┐
│  Backend (Django): LoginView.post()                     │
│  1. Valida credenciales contra BD                       │
│  2. Genera JWT tokens (access + refresh)               │
│  3. Retorna: { access, refresh, user }                 │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend: AuthContext.login()                          │
│  1. Almacena tokens en localStorage                     │
│  2. Almacena user_info en localStorage                  │
│  3. Navega a /dashboard                                 │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend: Dashboard.jsx renderiza                      │
│  ✅ Usuario autenticado y en sistema                    │
└─────────────────────────────────────────────────────────┘
```

---

### 4.2 FLUJO DE CREACIÓN DE POSTULACIÓN

```
┌──────────────────────────────────┐
│ Admin en /postulaciones          │
│ Click "Crear Postulación"        │
└──────────────────────────────────┘
         │
         ▼ (Modal se abre)
┌──────────────────────────────────┐
│ FormField componentes:           │
│ - Select Postulante              │
│ - Select Modalidad               │
│ - Input Título                   │
│ - Select Estado                  │
│ - Textarea Observaciones         │
└──────────────────────────────────┘
         │
         ▼ (Admin completa y envía)
┌──────────────────────────────────┐
│ POST /api/postulaciones/         │
│ Body: {                          │
│   postulante: 5,                 │
│   modalidad: 2,                  │
│   titulo_trabajo: "Mi tesis",    │
│   gestion: 2026,                 │
│   estado: "en_revision",         │
│   estado_general: "EN_PROCESO"   │
│ }                                │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Backend: PostulacionViewSet      │
│ 1. Valida datos (serializer)     │
│ 2. Crea objeto Postulacion       │
│ 3. Registra en Auditoria         │
│ 4. Retorna 201 + datos           │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Frontend: Modal se cierra        │
│ useCrud.refresh() recarga lista  │
│ Alert success aparece            │
└──────────────────────────────────┘
```

---

### 4.3 FLUJO DE APROBACIÓN DE DOCUMENTO

```
┌────────────────────────────────────────┐
│ Administrativo en /documentos          │
│ Ve lista de documentos "pendiente"    │
└────────────────────────────────────────┘
         │
         ▼ (Click en documento)
┌────────────────────────────────────────┐
│ Se abre Modal de Revisión              │
│ Muestra:                               │
│ - Nombre postulante                    │
│ - Tipo documento                       │
│ - Archivo PDF (preview)                │
│ - Estado actual: "pendiente"           │
│ - Campo comentario vacío               │
└────────────────────────────────────────┘
         │
         ▼ (Admin cambia estado a aprobado)
┌────────────────────────────────────────┐
│ Admin:                                 │
│ 1. Selecciona "aprobado"               │
│ 2. (Opcional) Escribe comentario       │
│ 3. Click "Guardar"                     │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ PATCH /api/documentos/{id}/            │
│ Body: {                                │
│   estado: "aprobado",                  │
│   comentario_revision: "OK",           │
│   revisado_por: 1                      │
│ }                                      │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Backend: DocumentoPostulacionViewSet   │
│ 1. Valida permiso (PuedeAprobar...)   │
│ 2. Actualiza documento                 │
│ 3. Registra en Auditoria               │
│ 4. Retorna 200 + datos nuevos          │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Frontend:                              │
│ - Modal se cierra                      │
│ - Lista se recarga                     │
│ - Documento ahora mostrado en          │
│   "aprobados"                          │
│ - Alert success                        │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Estudiante (si accede):                │
│ Ve en /documentos que su documento     │
│ está "aprobado" con comentario         │
└────────────────────────────────────────┘
```

---

### 4.4 FLUJO DE VISUALIZACIÓN DE DASHBOARD

```
┌──────────────────────────────┐
│ Usuario logueado accede      │
│ a /dashboard                 │
└──────────────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ useEffect(() => {            │
│   fetchDashboardData()        │
│ }, [])                       │
└──────────────────────────────┘
         │
         ├─→ Llamada 1: GET /api/reportes/dashboard-general/
         │
         └─→ Llamada 2: GET /api/reportes/dashboard-chart-data/
         
         ▼ (Las 2 llamadas en paralelo)

┌──────────────────────────────────────────┐
│ Backend: dashboard_general()             │
│ 1. Count Postulantes total               │
│ 2. Count Postulaciones activas           │
│ 3. Count Documentos aprobados            │
│ 4. Calcula porcentajes de cambio mes-mes │
│ Retorna 15 campos de datos               │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ Backend: get_dashboard_chart_data()      │
│ 1. Genera line chart (postulantes/mes)   │
│ 2. Genera bar chart (docs por estado)    │
│ 3. Genera pie chart (postulaciones/mod)  │
│ Retorna 3 arrays de datos                │
└──────────────────────────────────────────┘

         ▼ (Ambas retornan 200)
         
┌──────────────────────────────────────────┐
│ Frontend: setState()                     │
│ setDashboardStats(data1)                 │
│ setChartData(data2)                      │
│ setLoading(false)                        │
└──────────────────────────────────────────┘

         ▼

┌──────────────────────────────────────────┐
│ React renderiza:                         │
│ 1. StatsCards (4 tarjetas)               │
│ 2. Charts (3 gráficos Recharts)          │
│ 3. DataTable (últimos postulantes)       │
│ ✅ Dashboard visible                      │
└──────────────────────────────────────────┘
```

---

### 4.5 FLUJO COMPLETO: DE POSTULANTE A TITULADO

```
FASE 1: INSCRIPCIÓN
┌─────────────────────────────────────────────┐
│ 1. Admin crea Postulante manual             │
│    POST /api/postulantes/                   │
│ 2. Sistema genera usuario automáticamente   │
│    (onetoone con Postulante)                │
└─────────────────────────────────────────────┘

FASE 2: POSTULACIÓN
┌─────────────────────────────────────────────┐
│ 3. Admin crea Postulación                   │
│    POST /api/postulaciones/                 │
│    Estado: "borrador"                       │
│    Estado General: "EN_PROCESO"             │
└─────────────────────────────────────────────┘

FASE 3: DOCUMENTO DE ETAPA 1
┌─────────────────────────────────────────────┐
│ 4. Sistema envía notificación al estudiante │
│    (Notificacion creada en BD)              │
│ 5. Estudiante carga Documento               │
│    POST /api/documentos/                    │
│    Estado: "pendiente"                      │
└─────────────────────────────────────────────┘

FASE 4: REVISIÓN Y APROBACIÓN
┌─────────────────────────────────────────────┐
│ 6. Admin revisa documento                   │
│    PATCH /api/documentos/{id}/              │
│    Estado: "aprobado"                       │
│    (Registra en Auditoria)                  │
│ 7. Sistema verifica si todos docs etapa1 OK │
│ 8. Avanza postulación a Etapa 2 (manual)    │
│    PATCH /api/postulaciones/{id}/           │
│    Estado General: "PERFIL_APROBADO"        │
└─────────────────────────────────────────────┘

FASE 5: REPETIR POR CADA ETAPA
┌─────────────────────────────────────────────┐
│ 9. Repite pasos 4-8 para cada etapa         │
│    (Documentos de Etapa 2, 3, ...)          │
└─────────────────────────────────────────────┘

FASE 6: FINALIZACIÓN
┌─────────────────────────────────────────────┐
│ 10. Última etapa completada                 │
│ 11. Admin marca Postulación como TITULADO   │
│     PATCH /api/postulaciones/{id}/          │
│     Estado General: "TITULADO"              │
│ 12. Sistema registra fecha de titulación    │
│ 13. Auditoría completa de todo el proceso   │
└─────────────────────────────────────────────┘

RESULTADO FINAL:
- Postulación estado: "aprobada"
- Postulación estado_general: "TITULADO"
- Todos los documentos: "aprobado"
- Auditoría: 30+ registros de cambios
- Alumno titulado ✅
```

---

## 5. BASE DE DATOS

### 5.1 ARQUITECTURA DE BASE DE DATOS

**Engine**: PostgreSQL 15  
**Locationación**: Docker container `postgres` en `docker-compose.yml`  
**Puerto**: 5432 (interno en Docker), accesible por Django en el network

### 5.2 TABLAS PRINCIPALES

#### 5.2.1 `usuarios_customuser` (Auth Base)
```sql
Campos:
- id: INTEGER PRIMARY KEY AUTO_INCREMENT
- username: VARCHAR(150) UNIQUE
- email: VARCHAR(254)
- password: VARCHAR(255) (hashed)
- first_name: VARCHAR(150)
- last_name: VARCHAR(150)
- is_staff: BOOLEAN DEFAULT FALSE
- is_active: BOOLEAN DEFAULT TRUE
- role: VARCHAR(20) CHOICES [admin, administ, estudiante]
- date_joined: TIMESTAMP
- groups_id: FOREIGN KEY (auth_group) [Multiple]
- user_permissions_id: FOREIGN KEY (auth_permission) [Multiple]

Índices:
- username UNIQUE
- email
```

---

#### 5.2.2 `postulantes_postulante` (Postulantes)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER UNIQUE FOREIGN KEY → usuarios_customuser
- nombre: VARCHAR(150)
- apellido: VARCHAR(150)
- ci: VARCHAR(20) UNIQUE
- telefono: VARCHAR(20)
- carrera: VARCHAR(150) [LEGACY, BLANK ALLOWED]
- facultad: VARCHAR(150) [LEGACY, BLANK ALLOWED]
- codigo_estudiante: VARCHAR(30) UNIQUE
- creado_en: TIMESTAMP AUTO_NOW_ADD

Relaciones:
- 1:1 con CustomUser
- 1:N con Postulacion (postulante_id)

Índices:
- ci UNIQUE
- codigo_estudiante UNIQUE
- nombre, apellido (búsqueda)
```

---

#### 5.2.3 `postulantes_postulacion` (Postulaciones)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- postulante_id: INTEGER FK → postulantes_postulante
- modalidad_id: INTEGER FK → modalidades_modalidad
- etapa_actual_id: INTEGER FK → modalidades_etapa [NULL ALLOWED]
- titulo_trabajo: VARCHAR(255)
- tutor: VARCHAR(150) [LEGACY, BLANK]
- gestion: INTEGER (año, ej: 2026)
- estado: VARCHAR(20) CHOICES [borrador, en_revision, aprobada, rechazada]
- estado_general: VARCHAR(30) CHOICES [EN_PROCESO, PERFIL_APROBADO, PRIVADA_APROBADA, PUBLICA_APROBADA, TITULADO]
- observaciones: TEXT
- fecha_postulacion: TIMESTAMP AUTO_NOW_ADD

Constraints:
- UNIQUE(postulante_id, gestion) - Un postulante solo 1 postulación por año

Relaciones:
- N:1 con Postulante
- N:1 con Modalidad
- N:1 con Etapa
- 1:N con DocumentoPostulacion (postulacion_id)
- 1:N con ComentarioInterno (postulacion_id)

índices:
- postulante_id
- modalidad_id
- estado
- gestion
- fecha_postulacion DESC
```

---

#### 5.2.4 `documentos_tipodocumento` (Tipos de Documentos)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- nombre: VARCHAR(100) UNIQUE
- etapa_id: INTEGER FK → modalidades_etapa [NULL ALLOWED]
- descripcion: TEXT
- obligatorio: BOOLEAN DEFAULT TRUE
- activo: BOOLEAN DEFAULT TRUE

Relaciones:
- N:1 con Etapa
- 1:N con DocumentoPostulacion (tipo_documento_id)

Índices:
- nombre UNIQUE
```

---

#### 5.2.5 `documentos_documentopostulacion` (Documentos Cargados)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- postulacion_id: INTEGER FK → postulantes_postulacion
- tipo_documento_id: INTEGER FK → documentos_tipodocumento
- archivo: VARCHAR(255) [file path]
- estado: VARCHAR(20) CHOICES [pendiente, aprobado, rechazado]
- comentario_revision: TEXT
- revisado_por_id: INTEGER FK → usuarios_customuser [NULL ALLOWED]
- fecha_subida: TIMESTAMP AUTO_NOW_ADD
- fecha_revision: TIMESTAMP [NULL ALLOWED]

Constraints:
- UNIQUE(postulacion_id, tipo_documento_id) - Un tipo por postulación

Relaciones:
- N:1 con Postulacion
- N:1 con TipoDocumento
- N:1 con CustomUser (revisado_por)

Índices:
- postulacion_id
- tipo_documento_id
- estado
- fecha_subida DESC
```

---

#### 5.2.6 `modalidades_modalidad` (Modalidades de Titulación)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- nombre: VARCHAR(100) UNIQUE
- descripcion: TEXT
- activa: BOOLEAN DEFAULT TRUE
- creada_en: TIMESTAMP AUTO_NOW_ADD
- actualizada_en: TIMESTAMP AUTO_NOW

Relaciones:
- 1:N con Etapa (modalidad_id)
- 1:N con Postulacion (modalidad_id)

Índices:
- nombre UNIQUE
- activa
```

---

#### 5.2.7 `modalidades_etapa` (Etapas por Modalidad)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- nombre: VARCHAR(100)
- orden: POSITIVE_INTEGER
- modalidad_id: INTEGER FK → modalidades_modalidad
- activo: BOOLEAN DEFAULT TRUE

Constraints:
- UNIQUE(modalidad_id, orden) - Orden único por modalidad

Relaciones:
- N:1 con Modalidad
- 1:N con TipoDocumento (etapa_id)
- 1:N con Postulacion (etapa_actual_id)

Índices:
- modalidad_id, orden
```

---

#### 5.2.8 `postulantes_notificacion` (Notificaciones)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER FK → usuarios_customuser
- mensaje: VARCHAR(255)
- leida: BOOLEAN DEFAULT FALSE
- link: VARCHAR(255) [NULL ALLOWED]
- fecha_creacion: TIMESTAMP AUTO_NOW_ADD

Relaciones:
- N:1 con CustomUser

Índices:
- usuario_id
- leida
- fecha_creacion DESC
```

---

#### 5.2.9 `postulantes_comentariointerno` (Comentarios en Postulaciones)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- postulacion_id: INTEGER FK → postulantes_postulacion
- autor_id: INTEGER FK → usuarios_customuser [NULL]
- texto: TEXT
- fecha: TIMESTAMP AUTO_NOW_ADD

Relaciones:
- N:1 con Postulacion
- N:1 con CustomUser

Índices:
- postulacion_id
- fecha DESC
```

---

#### 5.2.10 `auditoria_auditorialog` (Auditoría)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER FK → usuarios_customuser [NULL]
- accion: VARCHAR(100) [CREATE, UPDATE, DELETE, APPROVE, etc]
- modelo_afectado: VARCHAR(100) [Postulacion, DocumentoPostulacion, etc]
- objeto_id: VARCHAR(64) [ID del objeto modificado]
- estado_anterior: JSONB [{ campo: valor, ... }]
- estado_nuevo: JSONB [{ campo: valor, ... }]
- fecha: TIMESTAMP AUTO_NOW_ADD
- detalles: JSONB [metadata adicional]

Relaciones:
- N:1 con CustomUser

Índices:
- usuario_id
- modelo_afectado
- objeto_id
- fecha DESC
```

---

#### 5.2.11 `reportes_reportegenerado` (Reportes)
```sql
Campos:
- id: INTEGER PRIMARY KEY
- tipo: VARCHAR(30) CHOICES [postulaciones, documentos, estadistico]
- formato: VARCHAR(10) CHOICES [pdf, xlsx, csv]
- generado_por_id: INTEGER FK → usuarios_customuser [NULL]
- filtros: JSONB [{search, estado, etc}]
- archivo: VARCHAR(255) [file path]
- total_registros: INTEGER DEFAULT 0
- creado_en: TIMESTAMP AUTO_NOW_ADD

Relaciones:
- N:1 con CustomUser

Índices:
- creado_en DESC
```

---

### 5.3 RELACIONES CLAVE

**Diagrama de Relaciones:**

```
┌────────────────────┐           ┌──────────────────────┐
│  CustomUser        │───1:N───→ │  Postulante          │
│  (usuarios)        │           │  (solicitantes)      │
└────────────────────┘           └──────────────────────┘
         │                                  │
         │                                  │ 1:N
    1:N  │                                  ▼
         │                         ┌──────────────────────┐
         │                         │  Postulacion         │
         │                         │  (solicitudes)       │
         │                    ┌────│ (proceso)            │
         │                    │    └──────────────────────┘
         │                    │            │ N:1
         │                   1:N           │
         │                    │            ▼
         │                    │   ┌──────────────────────┐
         │                    │   │  Modalidad           │
         │                    │   │  (titulación)        │
         │                    │   └──────────────────────┘
         │                    │            │ 1:N
         │                    │            │
         │  1:N              │            ▼
         ▼                    │   ┌──────────────────────┐
┌──────────────────────┐      │   │  Etapa               │
│  AuditoriaLog        │      │   │  (fases)             │
│  (historial)         │      │   └──────────────────────┘
└──────────────────────┘      │            │ 1:N
                              │            │
                              │            ▼
                              │   ┌──────────────────────┐
                              │   │  TipoDocumento       │
                              │   │  (requeridos)        │
                              │   └──────────────────────┘
                              │            │ 1:N
                              │            │
                              └──→ ┌──────┴──────────────┐
                                   │                     │
                                   ▼                     ▼
                        ┌────────────────────────┐
                        │ DocumentoPostulacion   │
                        │ (archivos subidos)     │
                        └────────────────────────┘
```

### 5.4 PERMISOS EN BASE DE DATOS

**Tabla**: `auth_permission` (Django automática)

```sql
Permisos por modelo (Django auto-crea):
- postulante: view, add, change, delete
- postulacion: view, add, change, delete, puede_avanzar_etapa (custom)
- documentopostulacion: view, add, change, delete, puede_aprobar_documentos (custom)
- modalidad: view, add, change, delete
- etapa: view (readonly)
- usuario: view, add, change, delete

Custom Permissions:
- postulantes.puede_avanzar_etapa
- documentos.puede_aprobar_documentos
- reportes.puede_ver_auditoria
- reportes.puede_ver_dashboard_institucional
```

---

## 6. TECNOLOGÍAS UTILIZADAS

### 6.1 BACKEND

#### Framework y Base
- **Django 6.0.3** - Framework web Python
  - MVT (Model-View-Template)
  - ORM para abstracción BD
  
- **Django REST Framework 3.14.x** - API REST
  - Serializadores
  - ViewSets
  - Permisos

- **djangorestframework-simplejwt** - Autenticación JWT
  - Tokens de acceso/refresh
  - Autenticación sin sesión HTTP

- **drf-spectacular** - Auto-documentación OpenAPI
  - Swagger UI
  - Schema generation

#### Base de Datos
- **PostgreSQL 15** - BD relacional
  - JSONB para auditoria
  - Índices optimizados

- **psycopg2** - Driver PostgreSQL para Python

#### Tareas Asincrónicas (Configurado, no activo)
- **Celery** - Task queue
  - RabbitMQ/Redis broker
  - Tareas de larga duración

- **django-celery-results** - Almacenamiento de resultados

#### Caché (Opcional)
- **Redis** - Cache distribuido
  - Configurado en docker-compose
  - Settings condicionalmente activado

#### Middleware y Seguridad
- **django-cors-headers** - CORS
  - Permite requests desde frontend
  
- **Django Security Middleware**
  - Anti-CSRF
  - XSS protection
  
- **Django Auth Contrib**
  - Passwords hashed (PBKDF2)
  - Permission system

#### Logging
- **Python logging** - Logs estándar
  - Configurado en settings
  - Archivos log en `/logs`

#### Validación y Serialización
- **Django ORM** - Model validation
- **DRF Serializers** - Validación API
- **Pillow** (media files)

#### Dependencias de Desarrollo
```
Django==6.0.3
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.2
django-cors-headers==4.0.0
django-filter==23.1
drf-spectacular==0.26.1
psycopg2-binary==2.9.6
celery==5.2.7
django-celery-results==2.4.1
redis==4.5.4
python-dotenv==1.0.0
whoosh==2.7.4 (búsqueda opcional)
```

### 6.2 FRONTEND

#### Framework Principal
- **React 18.2.0** - UI library
  - Functional components
  - Hooks (useState, useEffect, useContext)
  
- **Vite 5.4.21** - Build tool
  - Dev server ultra-rápido
  - ESM (ES Modules)
  - HMR (Hot Module Replacement)

#### Enrutamiento
- **React Router DOM 6.16.0**
  - SPA navigation
  - Rutas protegidas
  - URL params y query params

#### Estilos
- **Tailwind CSS 3.3.0** - Utility-first CSS
  - Responsive design
  - Dark mode
  - Custom color palette

- **PostCSS** - CSS Processing
- **Autoprefixer** - Browser compatibility

#### HTTP Client
- **Axios 1.5.0** - HTTP requests
  - Interceptores para JWT
  - Manejo de errores
  - Retry logic (implementado)

#### Icons
- **Lucide React 0.577.0** - Icon library
  - 500+ icons SVG
  - Tree-shakeable

#### Gráficos
- **Recharts 3.8.0** - React chart library
  - Line Chart
  - Bar Chart
  - Pie Chart
  - Responsive

#### Notificaciones
- **React Hot Toast 2.6.0** - Toast notifications
  - No-config toast
  - Promise-based

#### Dependencias de Desarrollo
```
@vitejs/plugin-react
eslint
eslint-plugin-react
@types/react
@types/react-dom
```

### 6.3 DOCKER Y ORQUESTACIÓN

#### Docker Compose
```yaml
Services:
1. postgres (PostgreSQL 15)
   - Volumen: postgresdata
   - Puerto: 5432 (interno)
   - Variables: DB, USER, PASSWORD

2. redis (Redis 7)
   - Puerto: 6379 (interno)
   - Para cache y Celery (opcional)

3. backend (Django)
   - Build: Dockerfile.backend
   - Port: 8000 (interno)
   - Depends on: postgres, redis
   - CMD: gunicorn

4. nginx (Nginx reverse proxy)
   - Port: 80 (expuesto)
   - Configura: nginx/nginx.conf
   - Proxy a backend:8000

Network:
- custom bridge network para comunicación entre containers
```

#### Dockerfiles
1. **Dockerfile.backend**
   - Base: python:3.11-slim
   - Instala dependencias
   - Copia código
   - CMD gunicorn on 0.0.0.0:8000

2. **Dockerfile.frontend** (opcional, si build)
   - Base: node:18-alpine
   - npm build
   - Sirve archivos estáticos

#### .dockerignore
- venv/
- node_modules/
- __pycache__/
- .git/
- .env (no copiar secrets)

### 6.4 NGINX (Reverse Proxy)

**Ubicación**: `nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;

    # Django API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin
    location /admin/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /app/media/;
    }
}
```

**Propósito:**
- Actúa como proxy reverso
- Redirecciona /api/ a Django
- Sirve archivos estáticos
- frontend en localhost:5173 accede vía proxy

### 6.5 GIT

- **.git/** - Repositorio Git
- **.gitignore** - Archivos excluidos
- **.gitattributes** - Configuración de atributos

### 6.6 Entorno y Configuración

#### Variables de Entorno (`.env`)
```bash
# Django
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=...
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend

# PostgreSQL
POSTGRES_DB=sistema_graduacion
POSTGRES_USER=sistema_user
POSTGRES_PASSWORD=...
POSTGRES_HOST=postgres (dentro de Docker)
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0 (interno en Docker)

# Frontend
VITE_API_URL=http://localhost
```

---

## 7. ARQUITECTURA DEL SISTEMA

### 7.1 ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────────────────────┐
│                      NAVEGADOR DEL USUARIO                  │
│                    (localhost:5173)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           │
                ┌──────────▼────────────┐
                │   VITE DEV SERVER     │
                │   (localhost:5173)    │
                │   React 18 + Hooks    │
                │   - Context API       │
                │   - React Router      │
                │   - Axios client      │
                │   - Tailwind CSS      │
                └──────────┬────────────┘
                           │
                           │ Proxy requests
                           │ to localhost:80
                           │
        ┌──────────────────▼────────────────────┐
        │      NGINX (Reverse Proxy)            │
        │      (localhost:80)                   │
        │      - Route /api/ → backend:8000     │
        │      - Route /admin/ → backend:8000   │
        │      - Serve static files             │
        └──────────────────┬────────────────────┘
                           │
        ┌──────────────────▼────────────────────┐
        │      DOCKER BRIDGE NETWORK            │
        │      (172.18.0.0/16)                  │
        └──────────────────┬────────────────────┘
                           │
        ┌──────────────────┴────────────┬──────────────────┐
        │                               │                  │
        │                               │                  │
        ▼                               ▼                  ▼
┌──────────────────┐        ┌──────────────────┐   ┌──────────────────┐
│   DJANGO BACKEND │        │   PostgreSQL 15  │   │    REDIS         │
│   (backend:8000) │        │   (postgres:5432)│   │ (redis:6379)     │
│                  │        │                  │   │                  │
│  - 6 Apps        │        │  - 11 Tables     │   │ - Cache layer    │
│  - ViewSets      │        │  - Normalized    │   │ - Celery broker  │
│  - Permissions   │        │  - Indices       │   │ - Sessions       │
│  - Serializers   │        │  - FK/M2M rels  │   │                  │
│  - JWT Auth      │        │                  │   │                  │
│  - Gunicorn WSGI │        │  - JSONB fields │   │ [OPTIONAL]       │
│                  │        │                  │   │                  │
│ Requests:       │        │  Schema:        │   └──────────────────┘
│ - 60+ endpoints │        │  ├─ usuarios   │
│ - CRUD ops      │        │  ├─ postulantes│
│ - Dashboard     │        │  ├─ documentos│
│ - Reports       │        │  ├─ modalidades│
│ - Audit logs    │        │  ├─ reportes   │
│                  │        │  └─ auditoria │
└──────────────────┘        └──────────────────┘
```

### 7.2 ARQUITECTURA FRONTEND (React)

```
src/
├── main.jsx ────────────────→ Entry Point
│   └── App.jsx
│       └── AuthProvider (Context)
│           └── AppRouter (React Router)
│
├── pages/ ──────────────────┐
│   ├── Login.jsx ──→ Entrada de sesión
│   ├── Dashboard.jsx ──→ Dashboard principal
│   ├── Postulantes.jsx ──→ CRUD postulantes
│   ├── Postulaciones.jsx ──→ CRUD postulaciones
│   ├── Documentos.jsx ──→ CRUD documentos
│   ├── Modalidades.jsx ──→ CRUD modalidades
│   ├── Usuarios.jsx ──→ CRUD usuarios
│   └── Reportes.jsx ──→ Reportes y estadísticas
│
├── components/ ────────────┐
│   ├── ProtectedRoute.jsx ──→ HOC para rutas
│   ├── Modal.jsx ──→ Modal genérico
│   ├── FormField.jsx ──→ Campo formulario
│   ├── DataTable.jsx ──→ Tabla genérica
│   ├── Alert.jsx ──→ Alertas
│   ├── StatsCards.jsx ──→ Tarjetas stats
│   ├── Charts.jsx ──→ Gráficos (Recharts)
│   ├── Header.jsx ──→ Encabezado
│   ├── Navbar.jsx ──→ Barra nav
│   ├── Sidebar.jsx ──→ Menú lateral
│   └── ... más componentes
│
├── context/ ────────────────┐
│   ├── AuthContext.jsx ──→ Autenticación
│   └── ThemeContext.jsx ──→ Tema
│
├── hooks/ ──────────────────┐
│   ├── useAuth.js ──→ Contexto auth
│   ├── useCrud.js ──→ CRUD logic
│   ├── useModal.js ──→ Modal state
│   └── useListFilters.js ──→ Filtros
│
├── api/ ─────────────────────┐
│   ├── axios.js ──→ Config Axios
│   ├── api.js ──→ Servicio genérico API
│   └── authApi.js ──→ Servicio auth
│
├── constants/ ──────────────┐
│   └── api.js ──→ URLs endpoints
│
├── layouts/ ─────────────────┐
│   ├── AdminLayout.jsx ──→ Layout admin
│   └── Layout.jsx
│
├── router/ ──────────────────┐
│   └── AppRouter.jsx ──→ Configuración rutas
│
└── styles/ ──────────────────┐
    └── globals.css ──→ Estilos globales
```

### 7.3 FLUJO DE DATOS EN FRONTEND

```
┌─────────────────────────────┐
│  Componente (ej: Login)     │
└──────────┬──────────────────┘
           │
           ▼
    ┌─────────────────┐
    │  useState       │ ← Estado local
    │  useEffect      │ ← Lifecycle
    │  useAuth hook   │ ← Contexto auth
    └────────┬────────┘
             │
             ▼
      ┌──────────────┐
      │ Event Handler│  ← onClick submit
      │ (handleLogin)│
      └────────┬─────┘
               │
               ▼
        ┌──────────────────┐
        │ authApi.login()  │ ← Llamada API
        │ (axios POST)     │
        └────────┬─────────┘
                 │
(HTTP Request via Nginx → Django Backend)
                 │
                 ▼
        ┌──────────────────┐
        │ Response: 200 OK │
        │ { access, user } │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ localStorage set │ ← Persistir tokens
        │ Context update   │ ← Auth state
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ navigate()       │ → /dashboard
        │ Component re-renders
        └──────────────────┘
```

### 7.4 SEGURIDAD EN CAPAS

```
CAPA 1: Frontend
└─ ProtectedRoute HOC
   └─ Verifica isAuthenticated
   └─ Redirige a /login si no

CAPA 2: HTTP Client (Axios)
└─ Interceptor request
   └─ Agrega Authorization: Bearer {token}
└─ Interceptor response
   └─ Si 401: intenta refresh
   └─ Si ambos fallan: logout

CAPA 3: Backend (Django)
└─ Middleware CSRF
└─ JWT validation
└─ Permission classes
   └─ IsAuthenticated
   └─ IsAdmin
   └─ Custom permissions
└─ Serializer validation
└─ Model-level constraints

CAPA 4: Base de Datos
└─ Foreign keys (integridad referencial)
└─ Unique constraints
└─ Check constraints
└─ Encrypted passwords (PBKDF2)
```

---

## 8. SEGURIDAD

### 8.1 AUTENTICACIÓN

#### Sistema JWT (JSON Web Tokens)

**Flujo:**
1. Usuario ingresa usuario/contraseña
2. Backend valida contra BD (password hashing PBKDF2)
3. Backend genera 2 tokens:
   - **access_token**: 5 minutos expiration (corta vida)
   - **refresh_token**: 24 horas expiration (larga vida)
4. Frontend almacena en `localStorage`
5. Axios interceptor inyecta `Authorization: Bearer {access_token}`

**Configuración** (Django):
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
```

#### Token Refresh
- Si `/api/postulantes/` retorna **401**
- Axios intenta POST `/api/auth/refresh/` con refresh_token
- Si éxito: obtiene nuevo access_token
- Si falla: limpia localStorage y redirige a /login

#### Logout
- Frontend: Elimina tokens de localStorage
- Backend: No mantiene blacklist (stateless JWT)
- Efecto: Token sigue siendo válido hasta expiration (risk mitigado con corta vida)

---

### 8.2 ROLES Y PERMISOS

#### Roles en Base de Datos
```python
ROLE_CHOICES = (
    ('admin', 'Administrador'),           # Full access
    ('administ', 'Administrativo'),       # Operational
    ('estudiante', 'Estudiante'),         # Limited to own data
)
```

#### Django Permissions (Fine-grained)
```python
# Auto-creadas por Django
postulante: view, add, change, delete
postulacion: view, add, change, delete
documentopostulacion: view, add, change, delete
usuario: view, add, change, delete

# Custom permissions
postulantes.puede_avanzar_etapa
documentos.puede_aprobar_documentos
auditoria.puede_ver_auditoria
reportes.puede_ver_dashboard_institucional
```

#### Permission Classes (API Level)
```python
class PostulanteRolePermission(BasePermission):
    # Admin/Administrativo: Ve todo
    # Estudiante: Ve solo su Postulante
    
class PostulacionRolePermission(BasePermission):
    # Admin/Administrativo: Ve todo
    # Estudiante: Ve solo sus Postulaciones
```

#### Protección de Objetos (Object-level)
```python
# En ViewSet
def get_queryset(self):
    if can_view_all_postulantes(self.request.user):
        return Postulante.objects.all()
    # Estudiante solo ve el suyo
    return Postulante.objects.filter(usuario=self.request.user)
```

---

### 8.3 PROTECCIÓN DE RUTAS (Frontend)

```javascript
<Route
  path="/postulantes"
  element={
    <ProtectedRoute requiredRole={['admin', 'administ']}>
      <AdminLayout>
        <Postulantes />
      </AdminLayout>
    </ProtectedRoute>
  }
/>
```

**ProtectedRoute.jsx verifica:**
1. ¿Existe token? Si no → /login
2. ¿Token válido? Si no → /login
3. ¿Rol requerido coincide? Si no → /403 (forbidden)
4. Si todo OK → Renderiza componente

---

### 8.4 VALIDACIÓN DE FORMULARIOS

#### Frontend (Tailwind + FormField)
```javascript
<FormField
  type="email"
  name="email"
  value={formData.email}
  onChange={handleChange}
  placeholder="usuario@ejemplo.com"
  required
/>
```

**Validaciones:**
- Pattern: email, teléfono, etc.
- Min/Max length
- Required fields
- Custom regex

#### Backend (Django Serializers)
```python
class PostulanteSerializer(ModelSerializer):
    class Meta:
        model = Postulante
        fields = ['nombre', 'apellido', 'ci', 'telefono', ...]
    
    def validate_ci(self, value):
        if Postulante.objects.filter(ci=value).exists():
            raise ValidationError("CI ya existe")
        return value
```

**Validaciones:**
- Type checking (CharField, IntegerField, etc.)
- Unique constraints
- Foreign key relations
- Custom validators
- Min/Max values
- Regex patterns

---

### 8.5 MANEJO DE SESIONES

#### Frontend (Multi-tab sync)
```javascript
// AuthContext.jsx
useEffect(() => {
  window.addEventListener('storage', handleStorageChange);
  // Si otro tab elimina token, sincroniza sesión
  return () => window.removeEventListener('storage', handleStorageChange);
}, []);
```

**Beneficio:** Si usuario hace logout en otra pestaña, esta pestaña se sincroniza.

#### Backend (Stateless)
- Django USA JWT (sin sesión HTTP)
- Cada request MUST tener Bearer token
- No hay cookie-based session (XSS safer)

---

### 8.6 PROTECCIÓN ESPECÍFICA

#### CSRF (Cross-Site Request Forgery)
- ✅ Django Middleware CSRF activo
- ✅ Axios automáticamente incluye CSRF token en headers
- ✅ POST/PUT/DELETE requests requieren token válido

#### XSS (Cross-Site Scripting)
- ⚠️ JWT en localStorage (vulnerable a XSS)
- ✅ React sanitiza automáticamente outputs
- ✅ No usar `dangerouslySetInnerHTML`
- **Recomendación**: Usar `httpOnly` cookies (requiere cambio)

#### HTTPS (En Producción)
- ⚠️ DEV: Sin HTTPS (localhost)
- ✅ PROD: Debe correr con HTTPS obligatorio
- ✅ Nginx debe redirectar HTTP → HTTPS
- ✅ Django: `SECURE_SSL_REDIRECT=True`

#### Inyección SQL
- ✅ Django ORM previene (parameterized queries)
- ✅ DRF serializers validan

#### Rate Limiting
- ❌ SIN implementar
- **Risk**: Ataques de fuerza bruta al login
- **Recomendación**: django-ratelimit o similar

---

### 8.7 AUDITORÍA

**Todotodotodo cambio se registra:**
```python
{
    "usuario": "admin",
    "accion": "UPDATE",
    "modelo_afectado": "DocumentoPostulacion",
    "objeto_id": "42",
    "estado_anterior": {"estado": "pendiente"},
    "estado_nuevo": {"estado": "aprobado"},
    "fecha": "2026-04-08T10:30:00Z",
    "detalles": { ... }
}
```

**Acceso:**
- Admin: Ver todo
- Administrativo: Ver registro (lectura)
- Estudiante: Negado
- API: GET /api/auditoria/ (filtered by permissions)

---

## 9. PROBLEMAS ENCONTRADOS

### 9.1 PROBLEMAS CRÍTICOS 🔴

#### 1. JWT en localStorage (XSS Vulnerable)
**Severidad**: 🔴 CRÍTICO  
**Descripción**: Tokens JWT almacenados en `localStorage` son accesibles a cualquier script XSS  
**Ubicación**: `frontend/src/api/authApi.js`  
**Impacto**: Si un atacante inyecta código malicioso, puede robar tokens

**Acción Recomendada**:
```javascript
// ACTUAL (vulnerable)
localStorage.setItem('access_token', response.data.access_token);

// RECOMENDADO
// Usar httpOnly cookies (servidor crea cookie segura)
// Frontend no accede directamente a tokens
```

---

#### 2. Sin Rate Limiting en Login
**Severidad**: 🔴 CRÍTICO  
**Descripción**: Endpoint `/api/auth/login/` sin protección contra fuerza bruta  
**Ubicación**: `usuarios/views.py` → `LoginView`  
**Impacto**: Atacante puede probar millones de contraseñas sin límite

**Manifestación**:
```
POST /api/auth/login/ (usuario1, pass1) → 401
POST /api/auth/login/ (usuario1, pass2) → 401
POST /api/auth/login/ (usuario1, pass3) → 401
... infinitas intentos sin bloqueos
```

**Acción Recomendada**: Instalar `django-ratelimit` o `djangorestframework-api-key`

---

#### 3. SECRET_KEY en Repo
**Severidad**: 🔴 CRÍTICO  
**Descripción**: `DJANGO_SECRET_KEY` en `.env` versionado (potencial risk)  
**Ubicación**: `config/settings.py` línea 26  
**Impacto**: Si repo es público, secret key comprometida

**Actual**:
```python
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 
    'django-insecure-j)treo76cq$iqq4*6mu2!-tn0=-swk@^g)^rcox+%*inigp5xb')
```

**Acción Recomendada**: Generar SECRET_KEY única por environment

---

#### 4. Debug Mode en Producción
**Severidad**: 🔴 CRÍTICO  
**Descripción**: `DEBUG=True` expone detalles internos en errores  
**Ubicación**: `config/settings.py` línea 28  
**Impacto**: Stacktraces visibles = información para atacantes

**Actual**:
```python
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
# Default True = peligroso
```

**Acción Recomendada**: Default `False`, PROD nunca `True`

---

#### 5. Sin HTTPS en Docker
**Severidad**: 🔴 CRÍTICO (en Producción)  
**Descripción**: Nginx no fuerza HTTPS, tokens viajan en claro  
**Ubicación**: `nginx/nginx.conf`  
**Impacto**: MITM (Man-In-The-Middle) puede interceptar tokens

**Acción Recomendada**:
```nginx
# Agregar redirect HTTP → HTTPS
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

---

### 9.2 PROBLEMAS ALTOS IMPACTO 🟠

#### 6. N+1 Queries en Dashboard
**Severidad**: 🟠 ALTO  
**Descripción**: Dashboard hace múltiples queries cuando podría ser una  
**Ubicación**: `reportes/services.py` → `dashboard_general()`  
**Impacto**: Lentitud en cargas de datos

**Evidencia**:
```python
# Probablemente hace:
SELECT * FROM postulante;  # 1 query
SELECT COUNT(*) FROM postulacion WHERE ...;  # 2
SELECT COUNT(*) FROM documentopostulacion WHERE ...;  # 3
... más queries por cada métrica
```

**Recomendación**: Usar `select_related()`, `prefetch_related()`, agregaciones

---

#### 7. Sin Paginación Automática en Reportes
**Severidad**: 🟠 ALTO  
**Descripción**: Reportes pueden retornar miles de registros sin límite  
**Ubicación**: `reportes/views.py`  
**Impacto**: Memoria exhausted, timeout

**Código**:
```python
class EstadisticasTutoresView(APIView):
    def get(self, request):
        data = estadisticas_tutores(year, carrera_id)
        # Sin paginación aquí ❌
```

**Recomendación**: Siempre paginar (max 100 por página)

---

#### 8. Sin Validación de Archivos en Documentos
**Severidad**: 🟠 ALTO  
**Descripción**: No valida tipo/tamaño de archivos cargados  
**Ubicación**: `documentos/views.py` → `DocumentoPostulacionViewSet`  
**Impacto**: Usuarios pueden cargar archivos maliciosos

**Risk**:
- Cargar .exe como PDF
- Archivos enormes (5GB)
- Zipbombs

**Recomendación**:
```python
def validate_file(file):
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED = ['pdf', 'doc', 'docx', 'xls', 'xlsx']
    
    if file.size > MAX_SIZE:
        raise ValidationError("Archivo muy grande")
    
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED:
        raise ValidationError("Tipo de archivo no permitido")
```

---

#### 9. Sin Logging Centralizado
**Severidad**: 🟠 ALTO  
**Descripción**: Logs solo con `print()` function, no guardados  
**Ubicación**: Todo el backend  
**Impacto**: Difícil debuggear producción

**Actual**:
```python
print("Dashboard request por usuario:", request.user.id)  # Desaparece
```

**Recomendación**: Usar `logging` module con archivos rotados

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Dashboard request por usuario: %s", request.user.id)
```

---

#### 10. Status Code 200 en Errores (Reportes)
**Severidad**: 🟠 ALTO  
**Descripción**: Algunos endpoints retornan 200 incluso cuando fallan internamente  
**Ubicación**: `reportes/views.py`  
**Impacto**: Frontend no puede distinguir error de éxito

**Código**:
```python
def get(self, request):
    try:
        data = get_dashboard_chart_data(meses=meses)
        return Response(data, status=200)  # ✅ OK
    except Exception as e:
        return Response({
            'lineChartData': [],
            'barChartData': [],
            'pieChartData': [],
            'error': str(e)
        }, status=200)  # ❌ ERROR pero status=200
```

**Should be**: `status=500` o `status=400`

---

#### 11. Sin Timeout en Requests
**Severidad**: 🟠 ALTO  
**Descripción**: Axios requests sin timeout, puede colgar indefinido  
**Ubicación**: `frontend/src/api/axios.js`  
**Impacto**: UI freezeado si servidor no responde

**Recomendación**:
```javascript
instance.defaults.timeout = 10000; // 10 segundos
```

---

### 9.3 PROBLEMAS MEDIO IMPACTO 🟡

#### 12. Campos Legacy sin Validación
**Severidad**: 🟡 MEDIO  
**Descripción**: `tutor`, `carrera`, `facultad` campos legacy permiten blank  
**Ubicación**: `postulantes/models.py`  
**Impacto**: Datos incompletos, confusión en reportes

---

#### 13. Etapa puede ser NULL
**Severidad**: 🟡 MEDIO  
**Descripción**: `Postulacion.etapa_actual` permite `NULL`  
**Ubicación**: `postulantes/models.py`  
**Impacto**: Ambigüedad en qué etapa está la postulación

---

#### 14. Sin Backend Validation de Modalidad Activa
**Severidad**: 🟡 MEDIO  
**Descripción**: Permite crear Postulación con Modalidad inactiva  
**Ubicación**: `postulantes/serializers.py`  
**Impacto**: Postulaciones a modalidades discontinuadas

---

#### 15. Error Handling inconsistente en API
**Severidad**: 🟡 MEDIO  
**Descripción**: Algunos endpoints wrappean errors, otros no  
**Ubicación**: Múltiples views  
**Impacto**: Frontend debe guessear formato de error

**Inconsistencia**:
```python
# Algunos retornan:
{ "detail": "Not found" }

# Otros:
{ "error": "Invalid data", "fields": {...} }

# Otros:
{ "message": "Success", "data": {...} }
```

---

#### 16. Reportes PDF sin soporte real
**Severidad**: 🟡 MEDIO  
**Descripción**: Modelo `ReporteGenerado` sin implementación real backend  
**Ubicación**: `reportes/models.py`, `reportes/views.py`  
**Impacto**: Exports PDF/Excel solo parcialmente funcionan

---

#### 17. Sin Soft Delete
**Severidad**: 🟡 MEDIO  
**Descripción**: DELETE elimina permanentemente, sin soft delete  
**Ubicación**: All models  
**Impacto**: Datos históricos perdidos (auditoria se queda)

---

### 9.4 PROBLEMAS FUNCIONALES 🔵

#### 18. Satisfacción retorna N/A incorrecto
**Severidad**: 🔵 FUNCIONAL (RESUELTO)  
**Descripción**: ~~Dashboard mostraba "0/10" sin datos~~ AHORA "N/A"  
**Status**: ✅ RESUELTO en sesión anterior

---

#### 19. Dashboard Hardcodes removidos
**Severidad**: 🔵 FUNCIONAL (RESUELTO)  
**Descripción**: ~~Dashboard tenía porcentajes hardcodeados~~ AHORA dinámicos  
**Status**: ✅ RESUELTO en sesión anterior

---

#### 20. Componentes CRUD con Código Duplicado
**Severidad**: 🔵 FUNCIONAL  
**Descripción**: 5 páginas (Postulantes, Postulaciones, etc) tienen 80% código idéntico  
**Ubicación**: `frontend/src/pages/*.jsx`  
**Impacto**: Mantenimiento difícil, bugs en múltiples lugares

**Reducción Lograda**: 75% mediante componentes reutilizables  
**Status**: ✅ Parcialmente resuelto con Modal, FormField, DataTable

---

### 9.5 PROBLEMAS NO CRÍTICOS (Mejoras) ⚪

#### 21. Falta TypeScript
- ✅ React y API son JavaScript puro
- TypeScript sería beneficial para type safety
- Risk: Bajo (runtime errors caught by manual testing)

#### 22. Sin Tests Automáticos
- 0% cobertura E2E
- Sin tests unitarios frontend
- Sin tests backend (pytest)
- Risk: Regressions no detectadas

#### 23. Celery/Redis No Activos
- Instalados pero sin usar
- Podría acelerar operaciones async
- No es bloqueante actualmente

#### 24. Documentación API (Swagger)
- ✅ Exists (drf-spectacular)
- Accessible en `/api/docs/`
- Could be more detailed

#### 25. Frontend sin Service Workers (PWA)
- No offline support
- No es crítico para admin app

---

---

## 10. RECOMENDACIONES Y MEJORAS

### 10.1 SEGURIDAD (PRIORITARIO)

#### FASE 1 - Inmediatos (1-2 días)

**1.1 - Migrar JWT a httpOnly Cookies**
```python
# En settings.py
REST_FRAMEWORK_SIMPLEJWT = {
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_SECURE': True,  # Solo HTTPS
    'AUTH_COOKIE_HTTP_ONLY': True,  # No accesible desde JS
    'AUTH_COOKIE_SAMESITE': 'Strict',  # CSRF protection
}
```

**Beneficio**: Tokens no accesibles a XSS  
**Esfuerzo**: 2 horas  
**Priority**: 🔴 CRÍTICO

---

**1.2 - Implementar Rate Limiting**
```bash
pip install django-ratelimit djangorestframework-api-key
```

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='5/m', method='POST')
def login(request):
    # Max 5 login attempts per minute per IP
    ...
```

**Beneficio**: Previene fuerza bruta  
**Esfuerzo**: 1 hora  
**Priority**: 🔴 CRÍTICO

---

**1.3 - Hardcodear DEBUG=False**
```python
DEBUG = False  # PRODUCTION default
if os.getenv('DJANGO_ENV') == 'development':
    DEBUG = True
```

**Beneficio**: No expone internal details  
**Esfuerzo**: 30 minutos  
**Priority**: 🔴 CRÍTICO

---

**1.4 - Generar SECRET_KEY Segura en Producción**
```python
from django.core.management.utils import get_random_secret_key

# En deployment
SECRET_KEY = get_random_secret_key()  # Cada service usa distinta
os.environ['DJANGO_SECRET_KEY'] = SECRET_KEY  # Store in .env.production
```

**Beneficio**: SECRET_KEY única por deployment  
**Esfuerzo**: 1 hora  
**Priority**: 🔴 CRÍTICO

---

**1.5 - HTTPS + Redirect HTTP**
```nginx
# nginx.conf
server {
    listen 80;
    server_name _;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # REST del config
}
```

**Beneficio**: Datos encriptados en tránsito  
**Esfuerzo**: 2 horas (con Let's Encrypt)  
**Priority**: 🔴 CRÍTICO

---

#### FASE 2 - Corto Plazo (1 semana)

**2.1 - Implementar Logging Centralizado**
```python
# config/logging_config.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}
```

**Beneficio**: Auditoría y debugging en producción  
**Esfuerzo**: 3 horas  
**Priority**: 🟠 ALTO

---

**2.2 - Validación de Archivos Cargados**
```python
# documentos/serializers.py
from django.core.files.uploadedfile import UploadedFile

def validate_file(file):
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_TYPES = {
        'application/pdf': ['.pdf'],
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    }
    
    if file.size > MAX_SIZE:
        raise ValidationError(f"Archivo debe ser menor a {MAX_SIZE/1024/1024}MB")
    
    # Validar MIME type
    if file.content_type not in ALLOWED_TYPES:
        raise ValidationError("Tipo de archivo no permitido")
    
    return file

class DocumentoPostulacionSerializer(ModelSerializer):
    archivo = FileField(validators=[validate_file])
    
    class Meta:
        model = DocumentoPostulacion
        fields = ['archivo', ...]
```

**Beneficio**: Previene carga de malware/spam  
**Esfuerzo**: 2 horas  
**Priority**: 🟠 ALTO

---

**2.3 - Status Codes Correctos en API**
```python
# reportes/views.py
class DashboardChartDataView(APIView):
    def get(self, request):
        try:
            data = get_dashboard_chart_data(meses=meses)
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Dashboard error: %s", str(e))
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

**Beneficio**: Frontend puede procesar errores correctamente  
**Esfuerzo**: 2 horas  
**Priority**: 🟠 ALTO

---

**2.4 - Timeout en Axios**
```javascript
// frontend/src/api/axios.js
const instance = axios.create({
    timeout: 10000,  // 10 segundos
    timeoutErrorMessage: 'Server timeout. Please try again.'
});

instance.interceptors.response.use(
    response => response,
    error => {
        if (error.code === 'ECONNABORTED') {
            error.message = 'Request timeout. Server took too long to respond.';
        }
        return Promise.reject(error);
    }
);
```

**Beneficio**: Previene UI freezeout  
**Esfuerzo**: 1 hora  
**Priority**: 🟡 MEDIO

---

### 10.2 OPTIMIZACIÓN DE RENDIMIENTO

#### 3.1 - Resolver N+1 Queries
```python
# reportes/services.py - ACTUAL
def dashboard_general():
    total_postulantes = Postulante.objects.count()  # Query 1
    postulaciones_activas = Postulacion.objects.exclude(estado='rechazada').count()  # Query 2
    documentos_aprobados = DocumentoPostulacion.objects.filter(estado='aprobado').count()  # Query 3
    ...

# OPTIMIZADO
from django.db.models import Count, Q

def dashboard_general():
    stats = Postulante.objects.aggregate(
        total_postulantes=Count('id'),
    )
    
    postulacion_stats = Postulacion.objects.aggregate(
        activas=Count('id', filter=Q(estado!='rechazada')),
        aprobadas=Count('id', filter=Q(estado='aprobada')),
    )
    
    doc_stats = DocumentoPostulacion.objects.aggregate(
        aprobados=Count('id', filter=Q(estado='aprobado')),
        rechazados=Count('id', filter=Q(estado='rechazado')),
    )
    
    # Combina en 1 query con múltiples agregaciones
    return {**stats, **postulacion_stats, **doc_stats}
```

**Beneficio**: Dashboard ~80% más rápido  
**Esfuerzo**: 3 horas  
**Priority**: 🟠 ALTO

---

#### 3.2 - Agregar Índices Base de Datos
```sql
-- Índices recomendados (ya existen algunos)

-- Performance críticas
CREATE INDEX idx_postulacion_état_postulante ON postulantes_postulacion(postulante_id, estado);
CREATE INDEX idx_documento_estado_postulacion ON documentos_documentopostulacion(postulacion_id, estado);
CREATE INDEX idx_auditoria_modelo_fecha ON auditoria_auditorialog(modelo_afectado, fecha DESC);

-- Búsqueda
CREATE INDEX idx_postulante_ci_nombre ON postulantes_postulante(ci, nombre, apellido);
CREATE INDEX idx_postulacion_titulo ON postulantes_postulacion USING gin(to_tsvector('spanish', titulo_trabajo));
```

**Beneficio**: Búsquedas 10x más rápidas  
**Esfuerzo**: 1 hora  
**Priority**: 🟡 MEDIO

---

#### 3.3 - Caché de Dashboard
```python
# reportes/services.py
from django.core.cache import cache

def dashboard_general():
    cache_key = 'dashboard:general:stats'
    data = cache.get(cache_key)
    
    if data is None:
        # Generar datos
        data = {
            'total_postulantes': Postulante.objects.count(),
            # ...
        }
        # Cache por 5 minutos
        cache.set(cache_key, data, timeout=300)
    
    return data

# Invalidar al crear/editar
def crear_postulacion(request, *args, **kwargs):
    # ... crear lógica
    cache.delete('dashboard:general:stats')  # Invalidar cache
    # ...
```

**Beneficio**: Dashboard cached, <100ms response  
**Esfuerzo**: 2 horas  
**Priority**: 🟡 MEDIO

---

### 10.3 FUNCIONALIDAD Y COMPLETITUD

#### 4.1 - Finaiizar Exports PDF/Excel
**Status**: Parcial (modelos existen, views incompletas)

```python
# reportes/views.py - COMPLETO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from xlsxwriter import Workbook

class ExportarPostulacionesView(APIView):
    def get(self, request):
        formato = request.query_params.get('format', 'pdf')
        
        if formato == 'pdf':
            return self.generar_pdf()
        elif formato == 'xlsx':
            return self.generar_excel()
        elif formato == 'csv':
            return self.generar_csv()
        else:
            return Response({'error': 'Formato no soportado'}, status=400)
    
    def generar_pdf(self):
        # ... implementar
        pass
```

**Beneficio**: Reportes descargables  
**Esfuerzo**: 4 horas  
**Priority**: 🟡 MEDIO

---

#### 4.2 - Implementar Etapas Auto-Avance
**Status**: Manual actualmente

```python
# postulantes/services.py
def verificar_etapa_completa(postulacion):
    """Verifica si todos docs de etapa actual son aprobados"""
    etapa = postulacion.etapa_actual
    
    docs_requeridos = TipoDocumento.objects.filter(etapa=etapa, obligatorio=True)
    docs_cargados = DocumentoPostulacion.objects.filter(
        postulacion=postulacion,
        tipo_documento__in=docs_requeridos,
        estado='aprobado'
    )
    
    if docs_cargados.count() == docs_requeridos.count():
        # Auto-avanzar a siguiente etapa
        siguiente_etapa = Etapa.objects.filter(
            modalidad=postulacion.modalidad,
            orden=etapa.orden + 1
        ).first()
        
        if siguiente_etapa:
            postulacion.etapa_actual = siguiente_etapa
            postulacion.save()
            
            AuditoriaLog.objects.create(
                usuario=None,
                accion='AUTO_AVANCE_ETAPA',
                modelo_afectado='Postulacion',
                objeto_id=str(postulacion.id),
                estado_nuevo={'etapa': siguiente_etapa.nombre}
            )
```

**Beneficio**: Workflow automático  
**Esfuerzo**: 4 horas  
**Priority**: 🟡 MEDIO

---

#### 4.3 - Notifications in Real-time (WebSockets)
**Status**: Modelo `Notificacion` existe, sin backend real-time

```python
# postulantes/consumers.py - Django Channels
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        self.group_name = f"user_{self.user_id}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def notificacion_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

# Trigger en services
from channels.layers import get_channel_layer
import asyncio

async def notificar_cambio_documento(documento_id):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{documento.postulacion.postulante.usuario.id}",
        {
            "type": "notificacion_message",
            "message": f"Documento {documento.tipo_documento} fue aprobado"
        }
    )
```

**Beneficio**: Notificaciones en tiempo real  
**Esfuerzo**: 6 horas  
**Priority**: 🔵 BAJO (nice-to-have)

---

### 10.4 TESTING Y CALIDAD

#### 5.1 - Tests Backend (Django)
```python
# postulantes/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Postulante, Postulacion

class PostulanteTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test',
            password='test123',
            role='estudiante'
        )
        self.postulante = Postulante.objects.create(
            usuario=self.user,
            nombre='Test',
            apellido='User',
            ci='12345678',
            codigo_estudiante='STU001'
        )
    
    def test_postulante_creation(self):
        self.assertEqual(self.postulante.nombre, 'Test')
        self.assertTrue(self.postulante.get_full_name().startswith('Test'))
    
    def test_postulante_ci_unique(self):
        with self.assertRaises(IntegrityError):
            Postulante.objects.create(
                usuario=self.user,
                ci=self.postulante.ci,  # Duplicado
            )
```

**Esfuerzo**: 8 horas  
**Priority**: 🟡 MEDIO

---

#### 5.2 - Tests Frontend (Vitest/Jest)
```javascript
// frontend/src/pages/__tests__/Login.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Login from '../Login';

describe('Login Page', () => {
    test('renders login form', () => {
        render(<Login />);
        expect(screen.getByPlaceholderText('Usuario')).toBeInTheDocument();
    });
    
    test('submits form with credentials', async () => {
        render(<Login />);
        fireEvent.change(screen.getByPlaceholderText('Usuario'), {target: {value: 'admin'}});
        fireEvent.change(screen.getByPlaceholderText('Contraseña'), {target: {value: 'password'}});
        fireEvent.click(screen.getByRole('button', {name: /entrar/i}));
        
        await waitFor(() => {
            expect(screen.queryByText(/login failed/i)).not.toBeInTheDocument();
        });
    });
});
```

**Esfuerzo**: 6 horas  
**Priority**: 🟡 MEDIO

---

#### 5.3 - E2E Tests (Cypress/Playwright)
```javascript
// e2e/login.spec.js
describe('Login Flow', () => {
    it('should login and redirect to dashboard', () => {
        cy.visit('http://localhost:5173/login');
        cy.get('[name="username"]').type('admin');
        cy.get('[name="password"]').type('password');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/dashboard');
    });
});
```

**Esfuerzo**: 10 horas  
**Priority**: 🟡 MEDIO

---

### 10.5 DOCUMENTACIÓN

#### 6.1 - README.md Detallado
- Instrucciones setup
- Estructura proyecto
- Comandos comunes
- Variables de entorno

#### 6.2 - API Documentation
- ✅ Swagger accessible `/api/docs/`
- Add descriptions a cada endpoint
- Add ejemplos de requests/responses

#### 6.3 - Frontend Component Library
- Storybook setup
- Component showcase
- Usage examples

**Esfuerzo**: 4 horas  
**Priority**: 🔵 BAJO

---

### 10.6 MEJORAS ARQUITECTÓNICAS

#### 7.1 - TypeScript Migration
**Benefit**: Type safety, mejor IDE support  
**Esfuerzo**: 20+ horas  
**Priority**: 🔵 BAJO (opcional)

---

#### 7.2 - GraphQL API (Alternativa REST)
**Benefit**: Queries flexibles  
**Esfuerzo**: 15+ horas  
**Priority**: 🔵 BAJO

---

---

## RESUMEN EJECUTIVO DEL DIAGNÓSTICO

### Calificación General
**6.5/10** - Sistema funcional pero con problemas de seguridad que impiden producción

### Fortalezas ✅
- ✅ Arquitectura bien estructurada (Django + React)
- ✅ Base de datos normalizada adecuadamente
- ✅ CRUD completo para 5 modelos principales
- ✅ Sistema de permisos basado en Django
- ✅ Dashboard con gráficos en tiempo real
- ✅ Auditoría de todos los cambios
- ✅ Docker configurado correctamente
- ✅ Componentes React reutilizables

### Problemas Críticos 🔴
1. JWT en localStorage (vulnerable XSS)
2. Sin rate limiting (fuerza bruta)
3. DEBUG=True por default
4. SECRET_KEY en repo
5. Sin HTTPS

### Problemas Altos Impacto 🟠
6. N+1 queries dashboard
7. Sin paginación automática
8. Sin validación de archivos
9. Sin logging centralizado
10. Status codes inconsistentes

### Tiempo para Producción
- **Fase 1 (Seguridad)**: 8 horas - 🔴 Bloqueante
- **Fase 2 (Optimización)**: 12 horas - 🟠 Recomendado
- **Fase 3 (Testing)**: 20+ horas - 🟡 Ideal
- **Total mínimo producción**: 8 horas

### Próximos Pasos Inmediatos
1. Implementar rate limiting en login
2. Migrar JWT a httpOnly cookies
3. Fix DEBUG=False por default
4. Agregar HTTPS + redirect
5. Implementar logging centralizado

---


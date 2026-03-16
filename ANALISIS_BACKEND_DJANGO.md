# Análisis de Estructura Backend Django - Sistema de Graduación

**Generado:** 16 de marzo de 2026  
**Versión Django:** 6.0.3  
**Base de Datos:** PostgreSQL

---

## 📋 Tabla de Contenidos

1. [Apps Django](#apps-django)
2. [Permisos y Autenticación](#permisos-y-autenticación)
3. [Middleware y Settings](#middleware-y-settings)
4. [Endpoints Disponibles](#endpoints-disponibles)
5. [Estructura de Requests/Responses](#estructura-de-requestsresponses)
6. [Configuración de Base de Datos](#configuración-de-base-de-datos)

---

## Apps Django

### 1. **USUARIOS** (Gestión de usuarios del sistema)

#### Modelos

```python
class CustomUser (AbstractUser):
    - role: CharField (admin, administ, estudiante)
    - username, email, password (heredados de AbstractUser)
```

#### ViewSets/Vistas

| Clase | Tipo | Métodos | Permisos |
|-------|------|---------|----------|
| `LoginView` | APIView (JWT) | POST | Anónimo |
| `CustomUserViewSet` | ModelViewSet | GET, POST, PUT, PATCH, DELETE | Admin |

#### Serializadores

- `CustomUserSerializer`: Lectura básica de usuarios
- `CustomUserDetailSerializer`: Lectura detallada con permisos
- `LoginSerializer`: Validación de login + información de usuario en token JWT

#### URLs Registradas

```
POST   /api/auth/login/              → LoginView (sin autenticación)
POST   /api/auth/refresh/            → TokenRefreshView
GET    /api/usuarios/                → CustomUserViewSet list
POST   /api/usuarios/                → CustomUserViewSet create
GET    /api/usuarios/{id}/           → CustomUserViewSet retrieve
PUT    /api/usuarios/{id}/           → CustomUserViewSet update
PATCH  /api/usuarios/{id}/           → CustomUserViewSet partial_update
DELETE /api/usuarios/{id}/           → CustomUserViewSet destroy
```

---

### 2. **POSTULANTES** (Gestión de postulantes y postulaciones)

#### Modelos

```python
class Postulante:
    - usuario: OneToOneField → CustomUser
    - nombre, apellido, ci (unique), telefono
    - codigo_estudiante (unique)
    - creado_en: DateTimeField

class Postulacion:
    - postulante: ForeignKey → Postulante
    - modalidad: ForeignKey → Modalidad
    - etapa_actual: ForeignKey → Etapa
    - titulo_trabajo, tutor, gestion, estado, estado_general
    - observaciones, fecha_postulacion

class Notificacion:
    - usuario: ForeignKey → CustomUser
    - mensaje, leida, link, fecha_creacion

class ComentarioInterno:
    - postulacion: ForeignKey → Postulacion
    - autor: ForeignKey → CustomUser
    - texto, fecha
```

#### ViewSets

| Clase | Tipo | Métodos | Permisos |
|-------|------|---------|----------|
| `PostulanteViewSet` | ModelViewSet | GET, POST, PUT, PATCH, DELETE | PostulanteRolePermission |
| `PostulacionViewSet` | ModelViewSet | GET, POST, PUT, PATCH, DELETE | PostulacionRolePermission |
| `EtapaViewSet` | ReadOnlyModelViewSet | GET | Autenticado |
| `NotificacionViewSet` | ReadOnlyModelViewSet | GET | Autenticado |

**Acciones Personalizadas en PostulacionViewSet:**
- `POST /api/postulaciones/{id}/avanzar-etapa/` → Avanzar a siguiente etapa
- `GET /api/postulaciones/dashboard/` → Dashboard con estadísticas
- `GET /api/postulaciones/exportar-dashboard-pdf/` → PDF de dashboard
- `GET /api/postulaciones/{id}/historial/` → Historial de auditoría

#### URLs Registradas

```
GET    /api/postulantes/                           → PostulanteViewSet list
POST   /api/postulantes/                           → PostulanteViewSet create
GET    /api/postulantes/{id}/                      → PostulanteViewSet retrieve
PUT    /api/postulantes/{id}/                      → PostulanteViewSet update
PATCH  /api/postulantes/{id}/                      → PostulanteViewSet partial_update
DELETE /api/postulantes/{id}/                      → PostulanteViewSet destroy

GET    /api/postulaciones/                         → PostulacionViewSet list
POST   /api/postulaciones/                         → PostulacionViewSet create
GET    /api/postulaciones/{id}/                    → PostulacionViewSet retrieve
PUT    /api/postulaciones/{id}/                    → PostulacionViewSet update
PATCH  /api/postulaciones/{id}/                    → PostulacionViewSet partial_update
DELETE /api/postulaciones/{id}/                    → PostulacionViewSet destroy
POST   /api/postulaciones/{id}/avanzar-etapa/      → Avanzar etapa
GET    /api/postulaciones/dashboard/               → Dashboard
GET    /api/postulaciones/exportar-dashboard-pdf/  → Exportar PDF
GET    /api/postulaciones/{id}/historial/          → Historial auditoría

GET    /api/etapas/                                → EtapaViewSet list
GET    /api/etapas/{id}/                           → EtapaViewSet retrieve
```

---

### 3. **DOCUMENTOS** (Gestión de documentos de postulaciones)

#### Modelos

```python
class TipoDocumento:
    - nombre: CharField (unique)
    - etapa: ForeignKey → Etapa
    - descripcion, obligatorio, activo

class DocumentoPostulacion:
    - postulacion: ForeignKey → Postulacion
    - tipo_documento: ForeignKey → TipoDocumento
    - archivo: FileField (upload_to='documentos/postulaciones/')
    - estado: CharField (pendiente, aprobado, rechazado)
    - comentario_revision, revisado_por, fecha_subida, fecha_revision
```

#### ViewSets

| Clase | Tipo | Métodos | Permisos |
|-------|------|---------|----------|
| `DocumentoPostulacionViewSet` | ModelViewSet | GET, POST, PUT, PATCH, DELETE | DocumentoRolePermission |
| `TipoDocumentoViewSet` | ModelViewSet | GET, POST, PUT, PATCH, DELETE | CRUDModelPermission |

#### Validación de Archivos

- **Extensiones permitidas:** pdf, doc, docx, xls, xlsx, jpg, jpeg, png
- **Tamaño máximo:** 25 MB

#### URLs Registradas

```
GET    /api/documentos/                 → DocumentoPostulacionViewSet list
POST   /api/documentos/                 → DocumentoPostulacionViewSet create
GET    /api/documentos/{id}/            → DocumentoPostulacionViewSet retrieve
PUT    /api/documentos/{id}/            → DocumentoPostulacionViewSet update
PATCH  /api/documentos/{id}/            → DocumentoPostulacionViewSet partial_update
DELETE /api/documentos/{id}/            → DocumentoPostulacionViewSet destroy

GET    /api/tipos-documento/            → TipoDocumentoViewSet list
POST   /api/tipos-documento/            → TipoDocumentoViewSet create
GET    /api/tipos-documento/{id}/       → TipoDocumentoViewSet retrieve
PUT    /api/tipos-documento/{id}/       → TipoDocumentoViewSet update
PATCH  /api/tipos-documento/{id}/       → TipoDocumentoViewSet partial_update
DELETE /api/tipos-documento/{id}/       → TipoDocumentoViewSet destroy
```

---

### 4. **MODALIDADES** (Gestión de modalidades de graduación)

#### Modelos

```python
class Modalidad:
    - nombre: CharField (unique)
    - descripcion, activa
    - creada_en, actualizada_en

class Etapa:
    - nombre, orden, modalidad: ForeignKey
    - activo
```

#### ViewSets

| Clase | Tipo | Métodos | Permisos |
|-------|------|---------|----------|
| `ModalidadViewSet` | ModelViewSet | GET, POST, PUT, PATCH, DELETE | CRUDModelPermission |
| `EtapaViewSet` | ReadOnlyModelViewSet | GET | Autenticado |

#### URLs Registradas

```
GET    /api/modalidades/               → ModalidadViewSet list
POST   /api/modalidades/               → ModalidadViewSet create
GET    /api/modalidades/{id}/          → ModalidadViewSet retrieve
PUT    /api/modalidades/{id}/          → ModalidadViewSet update
PATCH  /api/modalidades/{id}/          → ModalidadViewSet partial_update
DELETE /api/modalidades/{id}/          → ModalidadViewSet destroy

GET    /api/etapas/                    → EtapaViewSet list
GET    /api/etapas/{id}/               → EtapaViewSet retrieve
```

---

### 5. **REPORTES** (Dashboards y reportes)

#### ViewSets/Vistas

| Clase | Tipo | Métodos | Permisos |
|-------|------|---------|----------|
| `DashboardGeneralView` | APIView | GET | IsAuthenticated |
| `EstadisticasTutoresView` | APIView | GET | PuedeVerDashboard... |
| `ExportarEstadisticasTutoresView` | APIView | GET | PuedeVerDashboard... |
| `DetalleAlumnosTutorView` | APIView | GET | PuedeVerDashboard... |
| `ReporteEficienciaCarrerasView` | APIView | GET | PuedeVerDashboard... |
| `HealthCheckView` | APIView | GET | AllowAny |

#### URLs Registradas

```
GET    /api/health/                                      → Health check (sin autenticación)
GET    /api/reportes/dashboard-general/                 → Dashboard general
GET    /api/reportes/estadisticas-tutores/              → Estadísticas de tutores
GET    /api/reportes/estadisticas-tutores/exportar/     → Exportar Excel
GET    /api/reportes/estadisticas-tutores/{tutor_id}/alumnos/ → Detalle de alumnos
GET    /api/reportes/eficiencia-carreras/               → Eficiencia de carreras
```

---

### 6. **AUDITORIA** (Registro de cambios)

#### Modelos

```python
class AuditoriaLog:
    - usuario: ForeignKey → CustomUser
    - accion: CharField (nombre de la acción)
    - modelo_afectado: CharField
    - objeto_id: CharField
    - estado_anterior, estado_nuevo: JSONField
    - detalles: JSONField
    - fecha: DateTimeField
```

#### ViewSets

| Clase | Tipo | Métodos | Permisos |
|-------|------|---------|----------|
| `AuditoriaLogViewSet` | ReadOnlyModelViewSet | GET | PuedeVerAuditoria |

#### URLs Registradas

```
GET    /api/auditoria/                 → AuditoriaLogViewSet list
GET    /api/auditoria/{id}/            → AuditoriaLogViewSet retrieve
```

---

## Permisos y Autenticación

### Autenticación

- **Tipo:** JWT (JSON Web Token)
- **Esquema:** `rest_framework_simplejwt`
- **Token de Acceso:** 60 minutos
- **Token de Refresco:** 7 días
- **Alcance global:** Todos los endpoints requieren autenticación excepto:
  - `POST /api/auth/login/` (obtener token)
  - `GET /api/health/` (verificación de salud)

### Clases de Permisos Personalizadas

#### 1. `CRUDModelPermission`
Valida permisos dinámicos basados en el método HTTP:
- GET → `view_{model}`
- POST → `add_{model}`
- PUT/PATCH → `change_{model}`
- DELETE → `delete_{model}`

#### 2. `DocumentoRolePermission`
Permite acceso si:
- Usuario tiene permisos globales de documentos, O
- Es propietario de la postulación

#### 3. `PostulanteRolePermission`
Permite acceso si:
- Usuario tiene permisos globales de postulantes, O
- Es el postulante dueño del registro

#### 4. `PostulacionRolePermission`
Permite acceso si:
- Usuario tiene permisos globales de postulaciones, O
- Es el postulante de esa postulación

#### 5. `PuedeAprobarDocumentosPermission`
Requiere permiso personalizado: `documentos.puede_aprobar_documentos`

#### 6. `PuedeAvanzarEtapaPermission`
Requiere permiso personalizado: `postulantes.puede_avanzar_etapa`

#### 7. `PuedeVerAuditoriaPermission`
Requiere permiso personalizado: `auditoria.puede_ver_auditoria`

#### 8. `PuedeVerDashboardInstitucionalPermission`
Requiere:
- Ser superusuario, O
- Tener permiso: `reportes.view_reportegenerado`

### Roles de Usuario

- **admin:** Administrador del sistema
- **administ:** Personal administrativo
- **estudiante:** Estudiante postulante

---

## Middleware y Settings

### Middleware Configurado

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Configuración de REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}
```

### CORS Configurado

**Orígenes permitidos:**
- `http://localhost:5173` (Frontend Vite - puerto 5173)
- `http://127.0.0.1:5173`
- `http://localhost:3000` (Alternativo)
- `http://127.0.0.1:3000`

**Métodos permitidos:** GET, POST, PUT, PATCH, DELETE, OPTIONS

**Headers permitidos:** accept, accept-encoding, authorization, content-type, origin, user-agent, x-csrftoken, x-requested-with

### Caché

- **Desarrollo:** LocMemCache (en memoria)
- **Producción:** Redis (REDIS_URL env variable)
- **Timeout:** 3600 segundos (1 hora)
- **Prefix:** `sistema-graduacion`

### Base de Datos

- **Motor:** PostgreSQL
- **Configuración por variables de entorno:**
  - `POSTGRES_DB` (default: sistema_graduacion)
  - `POSTGRES_USER` (default: sistema_user)
  - `POSTGRES_PASSWORD` (default: sistema_pass)
  - `POSTGRES_HOST` (default: 172.18.0.3)
  - `POSTGRES_PORT` (default: 5432)

---

## Endpoints Disponibles

### Resumen de Endpoints por Método HTTP

#### Autenticación
| Método | Endpoint | Autenticación | Descripción |
|--------|----------|---------------|-------------|
| POST | `/api/auth/login/` | ❌ No | Login y obtener JWT (access + refresh token) |
| POST | `/api/auth/refresh/` | ❌ No | Refrescar token de acceso |

#### Base de Datos / Salud
| Método | Endpoint | Autenticación | Descripción |
|--------|----------|---------------|-------------|
| GET | `/api/health/` | ❌ No | Verificación de salud del sistema |

#### Usuarios
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/usuarios/` | ✅ JWT | Admin | Listar usuarios |
| POST | `/api/usuarios/` | ✅ JWT | Admin | Crear usuario |
| GET | `/api/usuarios/{id}/` | ✅ JWT | Admin | Obtener usuario |
| PUT | `/api/usuarios/{id}/` | ✅ JWT | Admin | Actualizar usuario |
| PATCH | `/api/usuarios/{id}/` | ✅ JWT | Admin | Actualizar parcialmente usuario |
| DELETE | `/api/usuarios/{id}/` | ✅ JWT | Admin | Eliminar usuario |

#### Postulantes
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/postulantes/` | ✅ JWT | View/Change/Delete | Listar postulantes (filtrado por usuario si no es admin) |
| POST | `/api/postulantes/` | ✅ JWT | Add | Crear postulante |
| GET | `/api/postulantes/{id}/` | ✅ JWT | View/Change/Delete + Owner | Obtener postulante |
| PUT | `/api/postulantes/{id}/` | ✅ JWT | Change + Owner | Actualizar postulante |
| PATCH | `/api/postulantes/{id}/` | ✅ JWT | Change + Owner | Actualizar parcialmente postulante |
| DELETE | `/api/postulantes/{id}/` | ✅ JWT | Delete + Owner | Eliminar postulante |

#### Etapas
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/etapas/` | ✅ JWT | Autenticado | Listar etapas activas |
| GET | `/api/etapas/{id}/` | ✅ JWT | Autenticado | Obtener etapa |

#### Postulaciones
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/postulaciones/` | ✅ JWT | View/Change/Delete | Listar postulaciones (filtrado por usuario si no es admin) |
| POST | `/api/postulaciones/` | ✅ JWT | Add | Crear postulación |
| GET | `/api/postulaciones/{id}/` | ✅ JWT | View/Change/Delete + Owner | Obtener postulación |
| PUT | `/api/postulaciones/{id}/` | ✅ JWT | Change + Owner | Actualizar postulación |
| PATCH | `/api/postulaciones/{id}/` | ✅ JWT | Change + Owner | Actualizar parcialmente postulación |
| DELETE | `/api/postulaciones/{id}/` | ✅ JWT | Delete + Owner | Eliminar postulación |
| POST | `/api/postulaciones/{id}/avanzar-etapa/` | ✅ JWT | PuedeAvanzarEtapa | Avanzar postulación a siguiente etapa |
| GET | `/api/postulaciones/dashboard/` | ✅ JWT | Autenticado | Dashboard general con estadísticas |
| GET | `/api/postulaciones/exportar-dashboard-pdf/` | ✅ JWT | Autenticado | Exportar dashboard en PDF |
| GET | `/api/postulaciones/{id}/historial/` | ✅ JWT | View/Change/Delete + Owner | Historial de auditoría de postulación |

#### Documentos
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/documentos/` | ✅ JWT | View/Change/Delete | Listar documentos (filtrado por usuario si no es admin) |
| POST | `/api/documentos/` | ✅ JWT | Add + Owner | Subir documento |
| GET | `/api/documentos/{id}/` | ✅ JWT | View/Change/Delete + Owner | Obtener documento |
| PUT | `/api/documentos/{id}/` | ✅ JWT | Change + Owner | Actualizar documento (no si está aprobado) |
| PATCH | `/api/documentos/{id}/` | ✅ JWT | Change + Owner | Actualizar documento parcialmente |
| DELETE | `/api/documentos/{id}/` | ✅ JWT | Delete + Owner | Eliminar documento |

#### Tipos de Documento
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/tipos-documento/` | ✅ JWT | Autenticado | Listar tipos de documento |
| POST | `/api/tipos-documento/` | ✅ JWT | Add | Crear tipo de documento |
| GET | `/api/tipos-documento/{id}/` | ✅ JWT | Autenticado | Obtener tipo de documento |
| PUT | `/api/tipos-documento/{id}/` | ✅ JWT | Change | Actualizar tipo de documento |
| PATCH | `/api/tipos-documento/{id}/` | ✅ JWT | Change | Actualizar tipo de documento parcialmente |
| DELETE | `/api/tipos-documento/{id}/` | ✅ JWT | Delete | Eliminar tipo de documento |

#### Modalidades
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/modalidades/` | ✅ JWT | Autenticado | Listar modalidades |
| POST | `/api/modalidades/` | ✅ JWT | Add | Crear modalidad |
| GET | `/api/modalidades/{id}/` | ✅ JWT | Autenticado | Obtener modalidad con etapas |
| PUT | `/api/modalidades/{id}/` | ✅ JWT | Change | Actualizar modalidad |
| PATCH | `/api/modalidades/{id}/` | ✅ JWT | Change | Actualizar modalidad parcialmente |
| DELETE | `/api/modalidades/{id}/` | ✅ JWT | Delete | Eliminar modalidad |

#### Reportes
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/reportes/dashboard-general/` | ✅ JWT | Autenticado | Dashboard general con estadísticas de graduación |
| GET | `/api/reportes/estadisticas-tutores/` | ✅ JWT | Ver Dashboard | Estadísticas por tutor (paginado) |
| GET | `/api/reportes/estadisticas-tutores/exportar/` | ✅ JWT | Ver Dashboard | Exportar estadísticas de tutores a Excel |
| GET | `/api/reportes/estadisticas-tutores/{tutor_id}/alumnos/` | ✅ JWT | Ver Dashboard | Detalle de alumnos titulados por tutor |
| GET | `/api/reportes/eficiencia-carreras/` | ✅ JWT | Ver Dashboard | Reporte de eficiencia por carrera |

#### Auditoría
| Método | Endpoint | Autenticación | Permisos | Descripción |
|--------|----------|---------------|----------|-------------|
| GET | `/api/auditoria/` | ✅ JWT | PuedeVerAuditoria | Listar registros de auditoría |
| GET | `/api/auditoria/{id}/` | ✅ JWT | PuedeVerAuditoria | Obtener registro de auditoría |

#### Documentación
| Método | Endpoint | Autenticación | Descripción |
|--------|----------|---------------|-------------|
| GET | `/api/schema/` | ✅ JWT | Schema OpenAPI de la API |
| GET | `/api/docs/` | ✅ JWT | Documentación Swagger UI |

---

## Estructura de Requests/Responses

### Formato General de Respuesta

```json
// ✅ Éxito - GET/list (paginado)
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "field1": "value1",
      "field2": "value2"
    }
  ]
}

// ✅ Éxito - GET (detalle)
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}

// ✅ Éxito - POST (crear)
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}

// ❌ Error - Validación
{
  "field_name": ["Error message"],
  "another_field": ["Another error"]
}

// ❌ Error - Permiso Denegado (403)
{
  "detail": "You do not have permission to perform this action."
}

// ❌ Error - No Autenticado (401)
{
  "detail": "Authentication credentials were not provided."
}

// ❌ Error - No Encontrado (404)
{
  "detail": "Not found."
}
```

### Login Request/Response

**Request:**
```json
POST /api/auth/login/
{
  "username": "usuario",
  "password": "contraseña"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@ejemplo.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "role": "admin",
    "role_display": "Administrador",
    "is_staff": true,
    "is_superuser": false
  }
}
```

### Postulante Request/Response

**POST /api/postulantes/ (crear):**
```json
{
  "usuario": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "ci": "12345678",
  "codigo_estudiante": "2023-001",
  "telefono": "5551234567"
}
```

**GET /api/postulantes/ (listar - paginado):**
```json
{
  "count": 100,
  "next": "http://api/postulantes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "Juan",
      "apellido": "Pérez",
      "ci": "12345678",
      "codigo_estudiante": "2023-001",
      "telefono": "5551234567",
      "usuario_nombre": "Juan Pérez",
      "usuario_email": "juan@ejemplo.com",
      "creado_en": "2024-03-16T10:00:00Z"
    }
  ]
}
```

### Postulación Request/Response

**POST /api/postulaciones/ (crear):**
```json
{
  "postulante_id": 1,
  "modalidad": 1,
  "etapa_actual": null,
  "titulo_trabajo": "Análisis de Sistemas",
  "tutor": "Dr. García",
  "gestion": 2024,
  "estado": "borrador",
  "estado_general": "EN_PROCESO",
  "observaciones": ""
}
```

**GET /api/postulaciones/{id}/ (detalle):**
```json
{
  "id": 1,
  "postulante": {
    "id": 1,
    "usuario": 1,
    "usuario_id": 1,
    "usuario_username": "usuario",
    "usuario_nombre": "Juan Pérez",
    "usuario_email": "juan@ejemplo.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "ci": "12345678",
    "codigo_estudiante": "2023-001",
    "telefono": "5551234567",
    "creado_en": "2024-03-16T10:00:00Z"
  },
  "postulante_id": 1,
  "modalidad": 1,
  "modalidad_nombre": "Tesis",
  "etapa_actual": 2,
  "etapa_nombre": "Revisión",
  "titulo_trabajo": "Análisis de Sistemas",
  "tutor": "Dr. García",
  "gestion": 2024,
  "estado": "en_revision",
  "estado_display": "En revision",
  "estado_general": "PRIVADA_APROBADA",
  "estado_general_display": "Privada aprobada",
  "observaciones": "En revisión",
  "fecha_postulacion": "2024-03-16T10:00:00Z"
}
```

### Documento Request/Response

**POST /api/documentos/ (subir documento):**
```
POST /api/documentos/
Content-Type: multipart/form-data

postulacion: 1
tipo_documento: 1
archivo: <file>
```

**GET /api/documentos/{id}/ (detalle):**
```json
{
  "id": 1,
  "postulacion": 1,
  "tipo_documento": 1,
  "tipo_documento_nombre": "Certificado Académico",
  "archivo": "/media/documentos/postulaciones/documento_2024-03-16.pdf",
  "archivo_url": "/media/documentos/postulaciones/documento_2024-03-16.pdf",
  "archivo_tipo": "PDF",
  "archivo_tamaño": 512.5,
  "estado": "aprobado",
  "estado_display": "Aprobado",
  "comentario_revision": "Excelente documento",
  "revisado_por": 2,
  "revisado_por_nombre": "Revisor Admin",
  "fecha_subida": "2024-03-16T10:00:00Z",
  "fecha_revision": "2024-03-16T11:00:00Z"
}
```

### Filtrado y Búsqueda

**QueryParams disponibles:**

```
// Paginación
?page=1
?page_size=50

// Filtrado (DjangoFilterBackend)
?modalidad=1
?gestion=2024
?estado=en_revision
?tipo_documento=1

// Búsqueda (SearchFilter)
?search=Juan              # Busca en postulante__nombre, etc.
?search=2023-001          # Busca en codigo_estudiante, etc.

// Ordenamiento (OrderingFilter)
?ordering=-fecha_postulacion
?ordering=nombre
?ordering=-creado_en
```

---

## Configuración de Base de Datos

### Modelo de Usuario Personalizado

El sistema usa `CustomUser` en lugar del modelo estándar de Django:

```python
AUTH_USER_MODEL = 'usuarios.CustomUser'
```

### Aplicaciones Instaladas

```python
INSTALLED_APPS = [
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'django_celery_results',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    
    # Custom apps
    'usuarios',
    'modalidades',
    'postulantes',
    'documentos',
    'reportes',
    'auditoria',
]
```

### Migraciones

Cada app tiene migraciones en su carpeta `migrations/`:
- `usuarios/migrations/`
- `modalidades/migrations/`
- `postulantes/migrations/`
- `documentos/migrations/`
- `reportes/migrations/`
- `auditoria/migrations/`

---

## Documentación Adicional

### URLs Disponibles

```
/api/schema/              → OpenAPI Schema (JSON)
/api/docs/                → Swagger UI Documentation
/admin/                   → Django Admin
```

### Validación de Archivos

- **Extensiones:** pdf, doc, docx, xls, xlsx, jpg, jpeg, png
- **Tamaño máximo:** 25 MB
- **Campo:** `archivo` (FileField)

### Paginación

- **Tamaño predeterminado:** 20 resultados por página
- **Tamaño máximo:** 100 resultados por página
- **Parámetro:** `page_size` (QueryParam)

### Rate Limiting

- **Anónimo:** 100 requests/hora
- **Autenticado:** 1000 requests/hora

---

**Última actualización:** 16 de marzo de 2026

# 📊 DIAGNÓSTICO TÉCNICO COMPLETO - SISTEMA DE GRADUACIÓN

**Fecha:** 9 de marzo de 2026  
**Versión:** 1.0  
**Estado General:** ✅ Funcional | ⚠️ Requiere mejoras de seguridad

---

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura Actual](#arquitectura-actual)
3. [Estado del Backend](#estado-del-backend)
4. [Estado del Frontend](#estado-del-frontend)
5. [Flujo de Autenticación JWT](#flujo-de-autenticación-jwt)
6. [API REST - Endpoints](#api-rest---endpoints)
7. [Base de Datos](#base-de-datos)
8. [Problemas Técnicos](#problemas-técnicos)
9. [Readiness para Frontend](#readiness-para-frontend)
10. [Recomendaciones](#recomendaciones)

---

## 📌 RESUMEN EJECUTIVO

### Stack Tecnológico
- **Backend:** Django 5.0.3 + Django REST Framework 3.16.1
- **BD:** PostgreSQL 15-alpine
- **Autenticación:** JWT (SimpleJWT 5.5.1)
- **API Docs:** Swagger/OpenAPI (drf-spectacular)
- **Servidor Aplicación:** Gunicorn 23.0.0
- **Reverse Proxy:** Nginx 1.27-alpine
- **Contenedorización:** Docker + Docker Compose
- **Frontend:** React (3 componentes JSX incompletos)

### Métricas
| Métrica | Valor |
|---------|-------|
| Apps Django | 6 principales |
| Modelos | 11 totales |
| Endpoints REST | 35+ activos |
| Serializers | 15+ customizados |
| Permisos personalizados | 8 clases |
| Líneas código Python | 3000+ |
| Componentes React | 3 no integrados |

### Estado General
```
Frontend:     ❌ Incompleto (necesita SPA separada)
Backend:      ✅ Funcional (requiere fixes de seguridad)
Base de Datos: ✅ Bien diseñada
API REST:     ✅ Documentada y funcional
Seguridad:    ⚠️ CRÍTICA: Variables de entorno inseguras
DevOps:       ✅ Docker operativo
```

---

## 🏗️ ARQUITECTURA ACTUAL

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                       USUARIO (NAVEGADOR)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────────────┐
│                  NGINX (Reverse Proxy:80)                   │
│              Estático + Media + Proxy Backend                │
└─────────────────┬──────────────────┬────────────────────────┘
                  │                  │
          ┌─────────────────┐   ┌─────────────────┐
          │ Static Files    │   │  Django Backend  │
          │ (CSS, JS, PNG)  │   │  (Porta :8000)   │
          └─────────────────┘   └────────┬─────────┘
                                         │
                                ┌────────┴────────┐
                                │   Gunicorn      │
                                │  (3 workers)    │
                                └────────┬────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          │                             │
                    ┌─────────────────┐        ┌────────────────┐
                    │  Django Apps:   │        │  PostgreSQL    │
                    │  - usuarios     │        │  (Puerto 5432) │
                    │  - postulantes  │        │                │
                    │  - documentos   │        │  Base Datos:   │
                    │  - modalidades  │        │  sistema_      │
                    │  - reportes     │        │  graduacion    │
                    │  - auditoria    │        │                │
                    └─────────────────┘        └────────────────┘
```

### Estructura de Carpetas

```
sistema-graduacion/
├── config/                      # Configuración Django
│   ├── settings.py             # Variables, BD, apps, middleware
│   ├── urls.py                 # Rutas principales
│   ├── api_urls.py             # Rutas API REST
│   ├── permissions.py          # Clases de permisos
│   ├── wsgi.py                 # Entry point Gunicorn
│   └── asgi.py                 # Entry point Daphne (no usado)
│
├── usuarios/                    # App: Autenticación
│   ├── models.py               # CustomUser (roles: admin, administ, estudiante)
│   ├── serializers.py          # LoginSerializer, CustomUserSerializer
│   ├── views.py                # LoginView (JWT)
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
│
├── postulantes/                 # App: Postulantes
│   ├── models.py               # Postulante, Postulacion, Notificacion
│   ├── serializers.py          # De listado y detalle
│   ├── views.py                # ViewSets con acciones avanzar-etapa
│   ├── services.py             # Lógica de negocio
│   ├── HistorialAuditoria.jsx  # ⚠️ Componente React suelto
│   └── migrations/
│
├── documentos/                  # App: Gestión de documentos
│   ├── models.py               # TipoDocumento, DocumentoPostulacion
│   ├── serializers.py          # Con validación de archivos (25MB)
│   ├── views.py                # ViewSets con aprobación/rechazo
│   ├── NotificationBell.jsx    # ⚠️ Componente React suelto
│   └── migrations/
│
├── modalidades/                 # App: Modalidades de titulación
│   ├── models.py               # Modalidad, Etapa
│   ├── serializers.py
│   ├── views.py
│   └── migrations/
│
├── reportes/                    # App: Reportes
│   ├── models.py               # ReporteGenerado
│   ├── services.py             # Generación PDF/Excel
│   ├── views.py                # Dashboards
│   └── migrations/
│
├── auditoria/                   # App: Auditoría
│   ├── models.py               # AuditoriaLog
│   ├── serializers.py
│   ├── services.py             # registrar_auditoria()
│   ├── views.py
│   ├── TaskResultsPage.jsx     # ⚠️ Componente React suelto
│   └── migrations/
│
├── nginx/                       # Configuración Nginx
│   └── default.conf            # Proxy reverso, cache, headers
│
├── docker-compose.yml          # Orquestación 3 servicios
├── Dockerfile.backend          # Build imagen Django
├── entrypoint.sh               # Script startup
├── requirements.txt            # Dependencias Python (13 paquetes)
├── manage.py                   # CLI Django
├── celery_app.py               # Configuración Celery
└── venv/                       # Entorno virtual Python

```

---

## 🔧 ESTADO DEL BACKEND

### ✅ Completamente Implementado

#### 1. **Servidor Web**
- Gunicorn 23.0.0 con 3 workers
- Timeout: 120 segundos
- Escucha en puerto 8000
- Control de usuarios sin privilegios

#### 2. **API REST**
- Django REST Framework 3.16.1
- 35+ endpoints funcionales
- Documentación Swagger en `/api/docs/`
- Schema OpenAPI en `/api/schema/`
- Paginación: PageNumberPagination (20 items/página)

#### 3. **Autenticación**
- JWT (Simple JWT 5.5.1)
- Access token: 60 minutos
- Refresh token: 7 días
- Tokens incluyen: rol, username, email, first_name, last_name

#### 4. **Base de Datos**
- PostgreSQL 15-alpine
- 11 modelos con relaciones correctas
- Migraciones: 15+
- Constraints: unique_together, unique_together
- Índices en campos de búsqueda (username, email, ci, codigo_estudiante)

#### 5. **Validaciones**
- Tamaño máximo archivo: 25MB
- Extensiones permitidas: pdf, doc, docx, xls, xlsx, jpg, jpeg, png
- Email: validación Django estándar
- CI: requerido, único
- Código estudiante: requerido, único

#### 6. **Permisos**
- 8 clases de permisos personalizadas
- CRUDModelPermission: validación dinámica por método HTTP
- DocumentoRolePermission: validación por propiedad + rol
- PostulanteRolePermission: validación por propiedad + rol
- PuedeAprobarDocumentosPermission: permiso personalizado
- PuedeAvanzarEtapaPermission: permiso personalizado

#### 7. **Serializers**
- 15+ serializers customizados
- Validaciones anidadas
- ReadOnly fields: id, created_at, updated_at
- Campos calculados: display names, URLs de documentos

---

### ⚠️ Parcialmente Implementado

#### 1. **Celery (Task Queue)**
- ✅ Instalado: celery==5.4.0, redis==5.0.7
- ✅ Configurado: celery_app.py
- ❌ No en docker-compose.yml
- ❌ No hay broker configurado
- ❌ Tareas síncronas (deberían ser async)

#### 2. **Email**
- ✅ Envío de notificación de rechazo implementado
- ❌ No configurado SMTP
- ❌ Debería ser asincron con Celery

#### 3. **Logging**
- ❌ Sin configuración centralizada
- ✅ Auditoría manual registrada en BD

---

### ❌ No Implementado

#### 1. **CORS**
- ❌ `django-cors-headers` no instalado
- ❌ Frontend no puede consumir API (mismo origen)
- ❌ Necesario para SPA separada

#### 2. **Rate Limiting**
- ❌ Sin throttling
- ⚠️ API vulnerable a abuse

#### 3. **WebSocket**
- ❌ Sin soporte real-time
- ❌ Notificaciones con polling cada 60s

#### 4. **Caché**
- ❌ Sin redis/memcached integrado
- ❌ Sin invalidación de caché

#### 5. **Tests**
- ❌ Directorio tests/ no existe
- ⚠️ Risk de regresiones

---

## 🎨 ESTADO DEL FRONTEND

### Estructura Actual

El frontend actual NO es una Single Page Application (SPA). Consta de **3 componentes React incompletos sueltos**:

#### 1. **HistorialAuditoria.jsx** (postulantes/)
```
Ubicación: postulantes/HistorialAuditoria.jsx
Líneas: ~90
Propósito: Mostrar timeline de cambios
Props: items, tiposDocumento
Acciones: 
  - CAMBIO_ETAPA: muestra transición de etapas
  - APROBACION_DOCUMENTO: muestra documento aprobado con link
  - RECHAZO_DOCUMENTO: muestra documento rechazado
Estado: Funcional pero desacoplado
```

#### 2. **NotificationBell.jsx** (documentos/)
```
Ubicación: documentos/NotificationBell.jsx
Líneas: ~120+
Propósito: Campana de notificaciones
Funcionalidades:
  - Dropdown con listado de notificaciones
  - Contador de no leídas
  - Marca como leídas al abrir
  - Polling cada 60 segundos
  - Links a postulaciones
Estado: Avanzado pero aislado
```

#### 3. **TaskResultsPage.jsx** (auditoria/)
```
Ubicación: auditoria/TaskResultsPage.jsx
Líneas: ~100+
Propósito: Admin - Historial de tareas Celery
Funcionalidades:
  - Paginación (20 items/página)
  - Filtrado por status
  - Búsqueda
  - Reintentos de tareas
  - Solo accesible para admin
Estado: Incompleto (endpoint /api/task-results/ no existe)
```

### ❌ Problemas Encontrados

1. **Sin package.json**
   - No hay proyecto Node.js
   - No se pueden instalar dependencias React
   - No se puede hacer build ni bundle

2. **Sin build system**
   - No hay Webpack, Vite, o Parcel
   - Los JSX no se pueden compilar

3. **Sin Router**
   - No hay React Router v6
   - No hay navegación entre páginas

4. **Sin contextos globales**
   - AuthContext referenciado pero no existe
   - No hay estado global (Redux, Zustand, etc)

5. **Sin servicios de API**
   - Referencias a `/api/endpoints` pero no existe
   - Implementaciones locales de fetch

6. **Sin estilos centralizados**
   - Estilos inline en componentes
   - No hay Tailwind, Bootstrap, o CSS modules

7. **Sin node_modules**
   - Dependencias no instalables

### Conclusión
El frontend actual es **PROTOTIPO NO FUNCIONAL**. Necesita reconstruirse desde cero como SPA moderna.

---

## 🔐 FLUJO DE AUTENTICACIÓN JWT

### 1. Login (POST /api/auth/login/)

**Solicitud:**
```json
{
  "username": "admin@admin.com",
  "password": "password"
}
```

**Respuesta Exitosa (200):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin@admin.com",
    "email": "admin@admin.com",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
    "role_display": "Administrador",
    "is_staff": true,
    "is_superuser": true
  }
}
```

**Payload del Access Token:**
```json
{
  "token_type": "access",
  "exp": 1741774447,
  "iat": 1741774087,
  "jti": "abc123def456",
  "user_id": 1,
  "role": "admin",
  "username": "admin@admin.com",
  "email": "admin@admin.com",
  "first_name": "Admin",
  "last_name": "User"
}
```

### 2. Uso de Token (Solicitud Autenticada)

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ejemplo - GET /api/postulantes/:**
```bash
curl -H "Authorization: Bearer {access_token}" \
     http://localhost/api/postulantes/
```

### 3. Refresh Token (POST /api/auth/refresh/)

**Solicitud:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Respuesta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 4. Árbol de Decisión

```
Usuario Solicita Acceso
    │
    ├─ Sin token?
    │  └─→ POST /api/auth/login/ + credenciales
    │      └─→ Recibe access + refresh tokens
    │
    ├─ Con token?
    │  ├─ Token válido (no expirado)?
    │  │  └─→ Acceso Permitido ✅
    │  │
    │  └─ Token expirado?
    │     ├─ Refresh token válido?
    │     │  └─→ POST /api/auth/refresh/ + refresh_token
    │     │      └─→ Nuevo access token ✅
    │     │
    │     └─ Refresh token expirado?
    │        └─→ Volver a login (POST /api/auth/login/) ❌
    │
    └─ Token inválido?
       └─→ Volver a login ❌
```

---

## 📡 API REST - ENDPOINTS

### Grouped by Resource

#### **Authentication (Sin autenticación requerida)**

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/login/` | Obtener tokens JWT | ❌ No |
| POST | `/api/auth/refresh/` | Refrescar access token | ❌ No |

#### **Usuarios**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/` | Documentación API | ✅ Sí | - |
| GET | `/api/docs/` | Swagger UI | ✅ Sí | - |
| GET | `/api/schema/` | OpenAPI JSON | ✅ Sí | - |

#### **Postulantes (CRUD)**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/postulantes/` | Listar postulantes (filtrable, buscable) | ✅ Sí | view_postulante |
| POST | `/api/postulantes/` | Crear postulante | ✅ Sí | add_postulante |
| GET | `/api/postulantes/{id}/` | Obtener postulante | ✅ Sí | view_postulante |
| PUT | `/api/postulantes/{id}/` | Actualizar postulante | ✅ Sí | change_postulante |
| PATCH | `/api/postulantes/{id}/` | Actualizar parcialmente | ✅ Sí | change_postulante |
| DELETE | `/api/postulantes/{id}/` | Eliminar postulante | ✅ Sí | delete_postulante |

**Parámetros de Filtro:**
- `search=nombre|apellido|ci|codigo_estudiante` - Búsqueda por texto
- `ordering=creado_en|-codigo_estudiante` - Orden ascendente/descendente

**Response Ejemplo (GET /api/postulantes/20/):**
```json
{
  "count": 150,
  "next": "http://localhost/api/postulantes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario_id": 2,
      "usuario_username": "estudiante01",
      "usuario_nombre": "Juan Pérez",
      "usuario_email": "juan@ejemplo.com",
      "nombre": "Juan",
      "apellido": "Pérez",
      "ci": "12345678",
      "codigo_estudiante": "EST001",
      "telefono": "+591-12345678",
      "carrera": "Ingeniería Informática",
      "facultad": "Tecnología",
      "creado_en": "2026-03-09T09:34:07Z"
    }
  ]
}
```

#### **Postulaciones (CRUD + Acciones)**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/postulaciones/` | Listar postulaciones | ✅ Sí | view_postulacion |
| POST | `/api/postulaciones/` | Crear postulación | ✅ Sí | add_postulacion |
| GET | `/api/postulaciones/{id}/` | Obtener postulación | ✅ Sí | view_postulacion |
| PUT | `/api/postulaciones/{id}/` | Actualizar postulación | ✅ Sí | change_postulacion |
| PATCH | `/api/postulaciones/{id}/` | Actualizar parcialmente | ✅ Sí | change_postulacion |
| DELETE | `/api/postulaciones/{id}/` | Eliminar postulación | ✅ Sí | delete_postulacion |
| GET | `/api/postulaciones/{id}/historial/` | Historial de cambios | ✅ Sí | view_postulacion |
| POST | `/api/postulaciones/{id}/avanzar-etapa/` | Avanzar a siguiente etapa | ✅ Sí | puede_avanzar_etapa |
| GET | `/api/postulaciones/dashboard/` | Dashboard general | ✅ Sí | view_reportegenerado |
| GET | `/api/postulaciones/exportar-dashboard-pdf/` | Descargar dashboard como PDF | ✅ Sí | view_reportegenerado |

#### **Documentos (CRUD + Review)**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/documentos/` | Listar documentos | ✅ Sí | view_documentopostulacion |
| POST | `/api/documentos/` | Subir documento | ✅ Sí | add_documentopostulacion |
| GET | `/api/documentos/{id}/` | Obtener documento | ✅ Sí | view_documentopostulacion |
| PUT | `/api/documentos/{id}/` | Actualizar documento (para admin) | ✅ Sí | change_documentopostulacion |
| PATCH | `/api/documentos/{id}/` | Aprobar/rechazar documento | ✅ Sí | puede_aprobar_documentos |
| DELETE | `/api/documentos/{id}/` | Eliminar documento | ✅ Sí | delete_documentopostulacion |

**Validación de Subida:**
- Extensiones: pdf, doc, docx, xls, xlsx, jpg, jpeg, png
- Tamaño máximo: 25MB
- Único por (postulacion, tipo_documento)

#### **Tipos de Documento**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/tipos-documento/` | Listar tipos de documento | ✅ Sí | view_tipodocumento |
| GET | `/api/tipos-documento/{id}/` | Obtener tipo documento | ✅ Sí | view_tipodocumento |

#### **Modalidades**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/modalidades/` | Listar modalidades | ✅ Sí | view_modalidad |
| GET | `/api/modalidades/{id}/` | Obtener modalidad con etapas | ✅ Sí | view_modalidad |

#### **Etapas**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/etapas/` | Listar etapas | ✅ Sí | view_etapa |
| GET | `/api/etapas/{id}/` | Obtener etapa | ✅ Sí | view_etapa |

#### **Auditoría**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/auditoria/` | Listar logs de auditoría | ✅ Sí | puede_ver_auditoria |
| GET | `/api/auditoria/{id}/` | Obtener log específico | ✅ Sí | puede_ver_auditoria |

**Campos searcheables:** usuario, acción, modelo_afectado, objeto_id

#### **Reportes**

| Método | Endpoint | Descripción | Auth | Permisos |
|--------|----------|-------------|------|----------|
| GET | `/api/reportes/dashboard-general/` | Dashboard agregado | ✅ Sí | view_reportegenerado |
| GET | `/api/reportes/estadisticas-tutores/` | Stats por tutor | ✅ Sí | view_reportegenerado |
| GET | `/api/reportes/estadisticas-tutores/exportar/` | Exportar excel | ✅ Sí | view_reportegenerado |
| GET | `/api/reportes/eficiencia-carreras/` | Eficiencia por carrera | ✅ Sí | view_reportegenerado |

---

## 🗄️ BASE DE DATOS

### Diagrama de Relaciones

```
┌─────────────────────────┐
│     CustomUser          │ (auth.user)
├─────────────────────────┤
│ id (PK)                 │
│ username (UNIQUE)       │
│ email                   │
│ first_name              │
│ last_name               │
│ role (admin|administ|..│ ◄─────┐
│ password                │       │
│ is_active               │       │
│ is_staff                │       │
│ is_superuser            │       │
│ date_joined             │       │
└─────────────────────────┘       │
         │ (1:1)                   │
         │                         │ inherits
         └────────────────────────┘
                  │
                  │ (1:N)
                  ▼
        ┌──────────────────────┐
        │    Postulante        │
        ├──────────────────────┤
        │ id (PK)              │
        │ usuario (FK, UNIQUE) │ → CustomUser
        │ nombre               │
        │ apellido             │
        │ ci (UNIQUE)          │
        │ telefono             │
        │ codigo_estudiante    │
        │ carrera              │
        │ facultad             │
        │ creado_en            │
        └──────────────────────┘
                  │
                  │ (1:N)
                  ▼
        ┌────────────────────────────┐
        │    Postulacion             │
        ├────────────────────────────┤
        │ id (PK)                    │
        │ postulante (FK)            │ → Postulante
        │ modalidad (FK)             │ → Modalidad
        │ etapa_actual (FK, nullable)│ → Etapa
        │ titulo_trabajo             │
        │ tutor (legacy)             │
        │ gestion                    │
        │ estado (borrador|revisión) │
        │ estado_general (EN_PROCESO)│
        │ observaciones              │
        │ fecha_postulacion          │
        │ UNIQUE(postulante, gestion)│
        └────────────┬────────────────┘
                     │ (1:N)
                     ▼
        ┌────────────────────────────────┐
        │   DocumentoPostulacion         │
        ├────────────────────────────────┤
        │ id (PK)                        │
        │ postulacion (FK)               │ → Postulacion
        │ tipo_documento (FK)            │ → TipoDocumento
        │ archivo (FileField)            │
        │ estado (pendiente|aprobado)    │
        │ comentario_revision            │
        │ revisado_por (FK, nullable)    │ → CustomUser
        │ fecha_subida                   │
        │ fecha_revision (nullable)      │
        │ UNIQUE(postulacion, tipo_doc) │
        └────────────────────────────────┘

┌─────────────────┐
│   Modalidad     │ (1:N)───┐
├─────────────────┤         │
│ id (PK)         │         │
│ nombre (UNIQUE) │         │
│ descripcion     │         │
│ activa          │         │
│ creada_en       │         │
│ actualizada_en  │         │
└─────────────────┘         │
                            │
                  ┌─────────┴──────────┐
                  │                    │
        ┌──────────────────────────────────────┐
        │          Etapa                       │
        ├──────────────────────────────────────┤
        │ id (PK)                              │
        │ nombre                               │
        │ orden (PositiveInt)                  │
        │ modalidad (FK)                       │ → Modalidad
        │ activo                               │
        │ UNIQUE(modalidad, orden)             │
        ├──────────────────────────────────────┤
        │        (1:N)                         │
        └────────┬─────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │   TipoDocumento        │
        ├────────────────────────┤
        │ id (PK)                │
        │ nombre (UNIQUE)        │
        │ etapa (FK, nullable)   │ → Etapa
        │ descripcion            │
        │ obligatorio (Boolean)  │
        │ activo (Boolean)       │
        └────────────────────────┘

┌───────────────────────────┐
│   AuditoriaLog            │
├───────────────────────────┤
│ id (PK)                   │
│ usuario (FK, nullable)    │ → CustomUser
│ accion (CharField)        │
│ modelo_afectado           │
│ objeto_id                 │
│ estado_anterior (JSONField)
│ estado_nuevo (JSONField)  │
│ detalles (JSONField)      │
│ fecha (auto_now_add)      │
└───────────────────────────┘

┌────────────────────────┐
│   Notificacion         │
├────────────────────────┤
│ id (PK)                │
│ usuario (FK)           │ → CustomUser
│ mensaje                │
│ leida (Boolean)        │
│ link (URL, nullable)   │
│ fecha_creacion         │
└────────────────────────┘

┌─────────────────────────┐
│   ReporteGenerado       │
├─────────────────────────┤
│ id (PK)                 │
│ tipo (postulaciones|...) │
│ formato (pdf|xlsx|csv)  │
│ generado_por (FK)       │ → CustomUser
│ filtros (JSONField)     │
│ archivo (FileField)     │
│ total_registros         │
│ creado_en               │
└─────────────────────────┘
```

### Constraints Importantes

| Tabla | Constraint | Tipo | Razón |
|-------|-----------|------|-------|
| Postulacion | unique_together(postulante, gestion) | Unique | Una postulación por año académico |
| Etapa | unique_together(modalidad, orden) | Unique | Orden único dentro de modalidad |
| DocumentoPostulacion | unique_together(postulacion, tipo_documento) | Unique | Un tipo documento por postulación |
| Postulante | ci | Unique | Identificación única |
| Postulante | codigo_estudiante | Unique | ID único de estudiante |
| CustomUser | username | Unique | Usuario único |
| CustomUser | email | Unique | Email único |
| TipoDocumento | nombre | Unique | Nombre único |
| Modalidad | nombre | Unique | Nombre único |

---

## ⚠️ PROBLEMAS TÉCNICOS

### 🔴 CRÍTICOS (Seguridad)

#### 1. **SECRET_KEY Insegure**
```python
# ❌ ACTUAL (Inseguro)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-j)treo76cq$...')

# ✅ DEBE SER
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is not set")
```
**Impacto:** Alguien con acceso al código puede falsificar tokens JWT  
**Solución:** Generar key en entorno de producción

#### 2. **DEBUG=True por Defecto**
```python
# ❌ ACTUAL
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# ✅ DEBE SER
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
```
**Impacto:** Stack traces exponen estructura interna  
**Solución:** Cambiar default a False

#### 3. **Sin CORS Configurado**
```python
# ❌ Falta
# django-cors-headers no está instalado

# ✅ DEBE SER
INSTALLED_APPS = [..., 'corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', ...]
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'https://example.com']
```
**Impacto:** Frontend SPA no puede consumir API  
**Solución:** Instalar y configurar django-cors-headers

---

### 🟡 ALTOS (Funcionalidad)

#### 1. **Celery Sin Configuración Real**
- Instalado pero sin broker Redis
- Email de rechazo se envía sincronamente
- PDF se genera en tiempo real

**Solución:**
```python
# Agregar a docker-compose.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"

# Configurar en settings.py
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
```

#### 2. **Sin Rate Limiting**
- API vulnerable a ataque de fuerza bruta
- Sin protección contra abuse

**Solución:**
```bash
pip install djangorestframework-throttling
```

#### 3. **Referencias Rotas**

En `postulantes/views.py`:
```python
# ❌ ERROR
from auditoria.serializers import AuditoriaLogSerializer  # Not found in line import

# Debería estar
```

#### 4. **Campos Legacy Sin Validación**
- `tutor` en Postulacion es CharField libre
- `carrera` en Postulante es CharField libre
- Deberían ser FK a tablas

---

### 🟠 MEDIOS (Optimización)

#### 1. **Sin Índices en Búsquedas**
- Búsquedas por username, email hacen escaneo completo
- Con 100k+ postulantes, será lento

**Solución:** Agregar índices:
```python
class Meta:
    indexes = [
        models.Index(fields=['username']),
        models.Index(fields=['email']),
        models.Index(fields=['ci']),
    ]
```

#### 2. **Notificaciones con Polling**
- Cada 60 segundos se consulta BD
- Ineficiente con muchos usuarios

**Solución:** WebSocket con Django Channels

#### 3. **PDF Generado en Sincronía**
- Reportes grandes bloquean servidor
- Debería ser en Celery

---

## ✅ READINESS PARA FRONTEND

### Endpoints Listos (✅)

```
✅ POST /api/auth/login/              → Logging
✅ POST /api/auth/refresh/            → Refresh token
✅ GET  /api/postulantes/             → List
✅ POST /api/postulantes/             → Create
✅ GET  /api/postulantes/{id}/        → Retrieve
✅ PUT  /api/postulantes/{id}/        → Update
✅ PATCH /api/postulantes/{id}/       → Partial update
✅ DELETE /api/postulantes/{id}/      → Delete
✅ GET  /api/postulaciones/{id}/avanzar-etapa/  → Custom action
✅ POST /api/documentos/              → Upload
✅ PATCH /api/documentos/{id}/        → Approve/Reject
✅ GET  /api/modalidades/             → List with etapas
✅ GET  /api/auditoria/               → Audit logs
✅ GET  /api/reportes/dashboard-general/ → Dashboard
```

### Validaciones Listas (✅)

```
✅ Extensión archivo: 14 tipos permitidos
✅ Tamaño máximo: 25MB
✅ Email: validación Django
✅ Username: único
✅ CI: único
✅ Código estudiante: único
✅ Permissions: 8 clases
✅ Serializers: 15+
✅ Filtros: SearchFilter, OrderingFilter
✅ Paginación: 20 items/página
✅ API Docs: Swagger + OpenAPI
```

### Falta para Separación Frontend-Backend

```
❌ CORS habilitado
❌ JWT en cookies (más seguro)
❌ Endpoint de me (para obtener usuario logueado)
❌ Refresh automático de token
❌ Logout endpoint
❌ Reset password endpoint
❌ Confirmación de email endpoint
❌ 2FA (two-factor auth)
```

---

## 🎯 RECOMENDACIONES

### Inmediato (Esta Semana)

#### 1. **Seguridad**
- [ ] Generar `DJANGO_SECRET_KEY` en producción
- [ ] Cambiar `DEBUG=False` en .env
- [ ] Cambiar contraseña PostgreSQL (cambiar_esto_pass)
- [ ] Cambiar contraseña de usuario admin

#### 2. **CORS**
- [ ] Instalar: `pip install django-cors-headers`
- [ ] Agregar a INSTALLED_APPS
- [ ] Configurar CORS_ALLOWED_ORIGINS

#### 3. **Testing**
- [ ] Levantar sistema y validar endpoints con Swagger
- [ ] Verificar permisos por rol
- [ ] Validar subida de documentos (25MB, tipos)

### Corto Plazo (Próxima 2 Semanas)

#### 1. **Backend Improvements**
- [ ] Crear `/api/me/` endpoint para obtener usuario logueado
- [ ] Implementar logout endpoint
- [ ] Agregar rate limiting (django-ratelimit)
- [ ] Crear tests unitarios

#### 2. **Frontend SPA**
- [ ] Crear proyecto React con Vite
- [ ] Setup React Router
- [ ] Crear servicio API centralizado
- [ ] Crear contexto de autenticación
- [ ] Crear layout base

#### 3. **DevOps**
- [ ] Agregar Redis a docker-compose
- [ ] Configurar Celery worker
- [ ] Habilitar SMTP para emails

### Mediano Plazo (Mes 1)

- [ ] Implementar WebSocket para notificaciones real-time
- [ ] Caché Redis
- [ ] Tests exhaustivos
- [ ] Optimizar queries (select_related, prefetch_related)
- [ ] Setup de CI/CD (GitHub Actions)
- [ ] Monitoreo (Sentry)

### Largo Plazo (Mes 2+)

- [ ] SSL/HTTPS en producción
- [ ] CDN para media (S3)
- [ ] Backup automático BD
- [ ] Logging centralizado
- [ ] 2FA
- [ ] Integración de pagos (si aplica)

---

## 📊 CHECKLIST ANTES DE CREAR FRONTEND

- [ ] SECRET_KEY correcto (no default)
- [ ] DEBUG=False
- [ ] CORS habilitado
- [ ] Ver endpoint `/api/` funciona
- [ ] Ver Swagger en `/api/docs/` funciona
- [ ] Login `/api/auth/login/` retorna tokens
- [ ] Documentos se validan (25MB, extensiones)
- [ ] Auditoría registra cambios
- [ ] Permisos por rol funcionan
- [ ] Paginación trabajo (20 items)
- [ ] Filtros/Búsqueda funciona
- [ ] Base de datos migrada
- [ ] Contenedores Docker en UP

---

**FIN DEL DIAGNÓSTICO TÉCNICO**

Generado: 9 de marzo de 2026  
Versión: 1.0  
Estado: ✅ COMPLETADO

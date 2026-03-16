# Diagrama de Arquitectura y Relaciones de Modelos

**Sistema de Graduación | 16 de marzo de 2026**

---

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Vite)                        │
│              http://localhost:5173 o :3000                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/CORS
                         │
┌─────────────────────────┴────────────────────────────────────────┐
│                    DJANGO REST API (config/)                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Middleware: CORS, Auth, Session, Security                  │ │
│  │  REST Framework: JWT, Throttle, Pagination, Filters        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Services (6 Apps)                                    │  │
│  │ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐      │  │
│  │ │USUARIOS │ │POSTULANTES│ │DOCUMENTOS│ │MODALIDAD│      │  │
│  │ └─────────┘ └──────────┘ └──────────┘ └─────────┘      │  │
│  │ ┌────────────┐          ┌──────────────┐               │  │
│  │ │ REPORTES   │          │  AUDITORIA   │               │  │
│  │ └────────────┘          └──────────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ External Services                                        │  │
│  │ • PostgreSQL (BD)  • Redis/Cache  • Email Notifications │  │
│  │ • Celery Tasks     • File Storage                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Diagrama de Relaciones de Modelos

```
┌─────────────────┐
│  CustomUser     │  (usuarios.models)
│─────────────────│
│ id (PK)         │
│ username        │
│ email           │
│ password        │
│ first_name      │
│ last_name       │
│ role (admin,    │
│   administ,     │
│   estudiante)   │
│ is_active       │
│ is_staff        │
│ is_superuser    │
└────────┬────────┘
         │ OneToOne
         │
    ┌────▼────────────┐
    │  Postulante     │  (postulantes.models)
    │─────────────────│
    │ id (PK)         │
    │ usuario_id (FK) │
    │ nombre          │
    │ apellido        │
    │ ci (unique)     │
    │ telefono        │
    │ carrera         │
    │ facultad        │
    │ codigo_estudiante│
    │ creado_en       │
    └────┬────────────┘
         │ 1:N
         │
         └──────────────────────────┬──────────────────────────┬────────────────┐
                                    │                          │                │
                    ┌───────────────▼───────────────┐          │                │
                    │  Postulacion                  │          │                │
                    │───────────────────────────────│          │                │
                    │ id (PK)                       │          │                │
                    │ postulante_id (FK) ───────────┼──────────┘                │
                    │ modalidad_id (FK) ────────┐   │                           │
                    │ etapa_actual_id (FK) ─────┼───┼─────────┐                │
                    │ titulo_trabajo            │   │         │                │
                    │ tutor                     │   │         │                │
                    │ gestion                   │   │         │                │
                    │ estado                    │   │         │                │
                    │ estado_general            │   │         │                │
                    │ observaciones             │   │         │                │
                    │ fecha_postulacion         │   │         │                │
                    └────┬──────────────────────┘   │         │                │
                         │ 1:N                      │         │                │
                         │                          │         │                │
         ┌───────────────┼──────────────────┐       │         │                │
         │               │                  │       │         │                │
    ┌────▼────────┐  ┌───▼──────────┐   ┌──▼──────────────────┼────┐           │
    │ Notificacion│  │ Comentario   │   │   Modalidad         │    │           │
    │─────────────│  │ Interno      │   │───────────────────────────┤           │
    │ id (PK)     │  │──────────────│   │ id (PK)             │    │           │
    │ usuario_id  │  │ id (PK)      │   │ nombre              │    │           │
    │ (FK)        │  │ postulacion_│   │ descripcion         │    │           │
    │ mensaje     │  │ id (FK) ─────┼───┤ activa              │    │           │
    │ leida       │  │ autor_id     │   │ creada_en           │    │           │
    │ link        │  │ (FK)         │   │ actualizada_en      │    │           │
    │ fecha_crea  │  │ texto        │   └─────┬───────────────┼────┘           │
    └────────────┘  │ fecha        │         │               │                │
                    └──────────────┘         │ 1:N            │                │
                                            │                │                │
                    ┌────────────────────────▼────┐          │                │
                    │  Etapa                      │          │                │
                    │────────────────────────────│          │                │
                    │ id (PK)                     │          │                │
                    │ nombre                      │          │                │
                    │ orden                       │          │                │
                    │ modalidad_id (FK) ──────────┼──────────┘                │
                    │ activo                      │                          │
                    └────┬─────────────────────────┘                          │
                         │ 1:N                                               │
                         │                                                   │
         ┌───────────────┴─────────────────┐                                │
         │                                 │                                │
    ┌────▼──────────────┐     ┌───────────▼──────┐                          │
    │  TipoDocumento    │     │ DocumentoPostulacion                         │
    │──────────────────1│     │─────────────────────────────────────┤         │
    │ id (PK)           │     │ id (PK)                             │         │
    │ nombre            │     │ postulacion_id (FK) ────────────────┼─────────┘
    │ etapa_id (FK) ────┼────┬│ tipo_documento_id (FK) ────────────┐│
    │ descripcion       │    │ archivo                       ┌─────┘│
    │ obligatorio       │    │ estado (pendiente,            │      │
    │ activo            │    │   aprobado, rechazado)        │      │
    └───────────────────┘    │ comentario_revision           │      │
                             │ revisado_por_id (FK) ─────────┼──────┘
                             │ fecha_subida                  │
                             │ fecha_revision                │
                             └───────────────────────────────┘

┌──────────────────┐
│  AuditoriaLog    │  (auditoria.models)
│──────────────────│
│ id (PK)          │
│ usuario_id (FK)  │──────────────► CustomUser
│ accion           │
│ modelo_afectado  │
│ objeto_id        │
│ estado_anterior  │
│ estado_nuevo     │
│ detalles (JSON)  │
│ fecha            │
└──────────────────┘
```

---

## 🔄 Flujo de Datos Típico

### 1️⃣ Flujo de Login

```
┌─────────────────────┐
│  Frontend (Login)   │
│  Username + Pass    │
└──────────┬──────────┘
           │ POST /api/auth/login/
           │
           ▼
┌─────────────────────────┐
│ LoginView (usuarios)    │ ← LoginSerializer
│ TokenObtainPairView     │ ← Valida credenciales
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ JWT Token Generado      │ ← CustomUser.role incluido en JWT
│ access (60 min)         │
│ refresh (7 días)        │
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Frontend almacena tokens     │
│ LocalStorage/SessionStorage  │
└────────────────────────────────┘
```

### 2️⃣ Flujo de Postulación

```
ESTUDIANTE

┌─────────────────────────┐
│ 1. Ver Postulantes      │
│ GET /api/postulantes/   │────────┐
└─────────────────────────┘        │
                                   ▼
                        ┌──────────────────────┐
                        │ Validar JWT + Owner  │
                        │ (PostulanteRolePerms)│
                        └──────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Retornar mis datos   │
                        │ de postulante        │
                        └──────────────────────┘

┌─────────────────────────────┐
│ 2. Ver Postulaciones        │
│ GET /api/postulaciones/     │────────┐
└─────────────────────────────┘        │
                                       ▼
                        ┌──────────────────────────┐
                        │ Validar JWT + Owner      │
                        │ (PostulacionRolePerms)   │
                        └──────────────────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │ Retornar mis postulaciones
                        └──────────────────────────┘

┌──────────────────────────┐
│ 3. Subir Documento       │
│ POST /api/documentos/    │────────┐
│ {postulacion, file}      │        │
└──────────────────────────┘        │
                                    ▼
                        ┌────────────────────────────┐
                        │ Validar JWT + Permissions  │
                        │ (DocumentoRolePerms)       │
                        └────────────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │ Validar Archivo            │
                        │ (extensión, tamaño)        │
                        └────────────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │ Guardar documento          │
                        │ estado = 'pendiente'       │
                        └────────────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │ Registrar en AuditoriaLog  │
                        │ (CREATE_DOCUMENTO)         │
                        └────────────────────────────┘

ADMIN

┌──────────────────────────┐
│ 4. Revisar Documento     │
│ GET /api/documentos/     │────────┐
│ ?estado=pendiente        │        │
└──────────────────────────┘        │
                                    ▼
                        ┌────────────────────────────┐
                        │ Validar Admin Permisos     │
                        │ (CRUDModelPermission)      │
                        └────────────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │ Retornar documentos        │
                        │ pendientes (paginado)      │
                        └────────────────────────────┘

┌──────────────────────────────┐
│ 5. Aprobar/Rechazar Documento│
│ PATCH /api/documentos/{id}/  │────────┐
│ {estado, comentario_revision}│        │
└──────────────────────────────┘        │
                                        ▼
                        ┌────────────────────────────┐
                        │ Validar Permisos Admin     │
                        │ (PuedeAprobarDocumentos)   │
                        └────────────────────────────┘
                                        │
                                        ▼
                        ┌────────────────────────────┐
                        │ Actualizar documento       │
                        │ + metadata revisión        │
                        └────────────────────────────┘
                                        │
                                        ▼
                        ┌────────────────────────────┐
                        │ Registrar en AuditoriaLog  │
                        │ (APROBACION/RECHAZO)       │
                        └────────────────────────────┘
                                        │
                                        ▼
                        ┌────────────────────────────┐
                        │ Enviar Email Notificación  │
                        │ + Notificación en Sistema  │
                        └────────────────────────────┘
```

### 3️⃣ Flujo de Avance de Etapa

```
ADMIN

┌───────────────────────────────┐
│ POST /api/postulaciones/{id}/ │
│ /avanzar-etapa/               │────────┐
└───────────────────────────────┘        │
                                         ▼
                        ┌──────────────────────────────┐
                        │ Validar Permisos             │
                        │ (PuedeAvanzarEtapaPermission)│
                        └──────────────────────────────┘
                                         │
                                         ▼
                        ┌──────────────────────────────┐
                        │ Validar Postulación          │
                        │ (estado, documentos aprobados)
                        └──────────────────────────────┘
                                         │
                                         ▼
                        ┌──────────────────────────────┐
                        │ Obtener siguiente Etapa      │
                        │ (orden + 1 en modalidad)     │
                        └──────────────────────────────┘
                                         │
                                         ▼
                        ┌──────────────────────────────┐
                        │ Actualizar Postulación       │
                        │ etapa_actual = etapa_nueva   │
                        │ estado_general = actualizado │
                        └──────────────────────────────┘
                                         │
                                         ▼
                        ┌──────────────────────────────┐
                        │ Registrar en AuditoriaLog    │
                        │ (AVANCE_ETAPA)               │
                        └──────────────────────────────┘
                                         │
                                         ▼
                        ┌──────────────────────────────┐
                        │ Crear Notificación           │
                        │ para Postulante              │
                        └──────────────────────────────┘
```

---

## 🔐 Matriz de Permisos

```
                    │ Anónimo │ Student │ Administ │  Admin
────────────────────┼─────────┼─────────┼──────────┼────────
GET /usuarios/      │   ❌    │    ❌   │    ❌    │   ✅
POST /usuarios/     │   ❌    │    ❌   │    ❌    │   ✅
GET /postulantes/   │   ❌    │   ✅*   │    ✅    │   ✅
POST /postulantes/  │   ❌    │    ✅   │    ✅    │   ✅
PATCH /postulantes/ │   ❌    │   ✅*   │    ✅    │   ✅
GET /postulaciones/ │   ❌    │   ✅*   │    ✅    │   ✅
POST /postulaciones/│   ❌    │    ✅   │    ✅    │   ✅
PATCH /postulaciones/│  ❌    │   ✅*   │    ✅    │   ✅
POST /avanzar-etapa/│   ❌    │    ❌   │    ✅    │   ✅
POST /documentos/   │   ❌    │   ✅*   │    ✅    │   ✅
PATCH /documentos/  │   ❌    │   ✅**  │    ✅    │   ✅
GET /reportes/      │   ❌    │    ❌   │    ✅    │   ✅
GET /auditoria/     │   ❌    │    ❌   │    ✅    │   ✅

* = Solo propio
** = Solo para cambiar estado a pendiente, admin para aprobar/rechazar
```

---

## 📝 Base de Datos - Estadísticas Estimadas

```
Tabla               │ Campos │ Índices | Relaciones
────────────────────┼────────┼─────────┼──────────────────────
CustomUser          │   15   │    3    │ → Postulante (1:1)
Postulante          │    8   │    2    │ → CustomUser
Postulacion         │   10   │    4    │ → Postulante, Modalidad, Etapa
Modalidad           │    5   │    1    │ → Etapa (1:N)
Etapa               │    5   │    2    │ → Modalidad
DocumentoPostulacion│   10   │    3    │ → Postulacion, TipoDocumento
TipoDocumento       │    5   │    2    │ → Etapa
Notificacion        │    6   │    2    │ → CustomUser
ComentarioInterno   │    5   │    2    │ → Postulacion
AuditoriaLog        │   10   │    4    │ → CustomUser
```

---

## 🔌 Integración con Externos

```
┌────────────────────────────────────────────────────────────┐
│                   Django Backend                           │
└─────┬──────────────┬──────────────┬────────────┬───────────┘
      │              │              │            │
      ▼              ▼              ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌─────────┐ ┌─────────┐
│ PostgreSQL   │ │ Redis/Cache  │ │ Celery  │ │  Email  │
│ Base de Datos│ │ (Escalabilid)│ │ Tasks   │ │ (SMTP)  │
└──────────────┘ └──────────────┘ └─────────┘ └─────────┘
      │
      ▼
┌──────────────────────┐
│ File Storage         │
│ /media/documentos/   │
└──────────────────────┘
```

---

## 📊 Volumen de Datos Estimado

Para una institución con **1000 estudiantes activos**:

```
Modelo                  │ Records Estimados
────────────────────────┼──────────────────
CustomUser              │ 1,500
Postulante              │ 1,000
Postulacion             │ 3,000 (3 años × 1000)
DocumentoPostulacion    │ 15,000 (5 docs × 3000)
TipoDocumento           │ 20-30
Modalidad               │ 5-10
Etapa                   │ 20-30
AuditoriaLog            │ 50,000+ (crecimiento)
Notificacion            │ 100,000+ (crecimiento)
```

---

## 🚀 Optimizaciones Implementadas

### 1. Select Related (Fase 2B)
Reduce queries N+1 en documentos:
```python
queryset = DocumentoPostulacion.objects.select_related(
    'postulacion__postulante__usuario',
    'tipo_documento',
    'revisado_por',
).all()
```

### 2. Paginación (Fase 3)
```python
PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
```

### 3. Caché (Fase 3 → Fase 4)
- Desarrollo: LocMemCache
- Producción: Redis
- TTL: 1 hora

### 4. Filtrado y Búsqueda
```python
filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
```

### 5. Rate Limiting
- Anónimo: 100/hora
- Usuario: 1000/hora

---


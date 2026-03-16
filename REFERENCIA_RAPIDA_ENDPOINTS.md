# Referencia Rápida de Endpoints - API Django

**Sistema de Graduación | 16 de marzo de 2026**

---

## 🔑 Autenticación

```bash
# 1. Obtener Token
POST /api/auth/login/
{
  "username": "usuario",
  "password": "contraseña"
}
→ Retorna: { "access": "...", "refresh": "...", "user": {...} }

# 2. Refrescar Token
POST /api/auth/refresh/
{
  "refresh": "token_refresh"
}
→ Retorna: { "access": "nuevo_token" }

# 3. Usar Token en Headers
Authorization: Bearer <token_access>
```

---

## 📊 Endpoints Rápidos

### **USUARIOS** (Solo Admin)

```bash
GET    /api/usuarios/                    # Listar usuarios (paginado)
POST   /api/usuarios/                    # Crear usuario
GET    /api/usuarios/{id}/               # Obtener usuario
PATCH  /api/usuarios/{id}/               # Actualizar usuario
DELETE /api/usuarios/{id}/               # Eliminar usuario

# Crear usuario (example)
POST /api/usuarios/
{
  "username": "nuevo_user",
  "email": "user@example.com",
  "password": "contraseña",
  "first_name": "Juan",
  "last_name": "Pérez",
  "role": "estudiante",
  "is_active": true
}
```

### **POSTULANTES**

```bash
GET    /api/postulantes/                 # Listar (filtrado por usuario si NO admin)
POST   /api/postulantes/                 # Crear postulante
GET    /api/postulantes/{id}/            # Obtener postulante
PATCH  /api/postulantes/{id}/            # Actualizar
DELETE /api/postulantes/{id}/            # Eliminar

# Crear postulante
POST /api/postulantes/
{
  "usuario": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "ci": "12345678",
  "codigo_estudiante": "2023-001",
  "telefono": "5551234567"
}
```

### **POSTULACIONES** (Principal)

```bash
GET    /api/postulaciones/                                  # Listar
POST   /api/postulaciones/                                  # Crear
GET    /api/postulaciones/{id}/                             # Obtener
PATCH  /api/postulaciones/{id}/                             # Actualizar
DELETE /api/postulaciones/{id}/                             # Eliminar

# 🔵 ACCIONES PERSONALIZADAS
POST   /api/postulaciones/{id}/avanzar-etapa/               # Avanzar a siguiente etapa
GET    /api/postulaciones/dashboard/                        # Ver dashboard  
GET    /api/postulaciones/{id}/historial/                   # Ver historial auditoría

# Crear postulación
POST /api/postulaciones/
{
  "postulante_id": 1,
  "modalidad": 1,
  "titulo_trabajo": "Mi Tesis",
  "tutor": "Dr. García",
  "gestion": 2024,
  "estado": "borrador"
}

# Filtros disponibles
GET /api/postulaciones/?modalidad=1&gestion=2024&estado=en_revision
GET /api/postulaciones/?search=Juan                         # Buscar por nombre
```

### **DOCUMENTOS**

```bash
GET    /api/documentos/                  # Listar documentos
POST   /api/documentos/                  # Subir documento
GET    /api/documentos/{id}/             # Obtener documento
PATCH  /api/documentos/{id}/             # Actualizar documento
DELETE /api/documentos/{id}/             # Eliminar documento

# Subir documento (multipart/form-data)
POST /api/documentos/
postulacion: 1
tipo_documento: 1
archivo: <archivo.pdf>

# Aprobar/Rechazar documento (solo admin)
PATCH /api/documentos/{id}/
{
  "estado": "aprobado",
  "comentario_revision": "Documento aprobado"
}

# o rechazado
{
  "estado": "rechazado",
  "comentario_revision": "Falta firma"
}
```

### **TIPOS DE DOCUMENTO** (Admin)

```bash
GET    /api/tipos-documento/             # Listar tipos
POST   /api/tipos-documento/             # Crear tipo
GET    /api/tipos-documento/{id}/        # Obtener tipo
PATCH  /api/tipos-documento/{id}/        # Actualizar
DELETE /api/tipos-documento/{id}/        # Eliminar

# Crear tipo de documento
POST /api/tipos-documento/
{
  "nombre": "Certificado Académico",
  "descripcion": "Certificado de calificaciones",
  "obligatorio": true,
  "activo": true
}
```

### **MODALIDADES** (Admin)

```bash
GET    /api/modalidades/                 # Listar modalidades
POST   /api/modalidades/                 # Crear modalidad
GET    /api/modalidades/{id}/            # Obtener (con etapas)
PATCH  /api/modalidades/{id}/            # Actualizar
DELETE /api/modalidades/{id}/            # Eliminar

# Crear modalidad
POST /api/modalidades/
{
  "nombre": "Tesis",
  "descripcion": "Modalidad de tesis de grado",
  "activa": true
}
```

### **ETAPAS** (Solo lectura)

```bash
GET    /api/etapas/                      # Listar etapas
GET    /api/etapas/{id}/                 # Obtener etapa

# Filtrar por modalidad
GET /api/etapas/?modalidad=1
```

### **REPORTES**

```bash
GET    /api/reportes/dashboard-general/                # Dashboard general
GET    /api/reportes/estadisticas-tutores/             # Estadísticas tutores
GET    /api/reportes/estadisticas-tutores/exportar/    # Exportar Excel
GET    /api/reportes/estadisticas-tutores/{id}/alumnos/ # Alumnos por tutor
GET    /api/reportes/eficiencia-carreras/              # Eficiencia carreras

# Con parámetros
GET /api/reportes/estadisticas-tutores/?year=2024
GET /api/reportes/eficiencia-carreras/?year=2024
```

### **AUDITORÍA**

```bash
GET    /api/auditoria/                   # Listar registros (requerido permiso)
GET    /api/auditoria/{id}/              # Obtener registro

# Filtros
GET /api/auditoria/?accion=APROBACION_DOCUMENTO
GET /api/auditoria/?modelo_afectado=Postulacion
GET /api/auditoria/?search=usuario_name
GET /api/auditoria/?ordering=-fecha     # Ordenar por fecha desc
```

### **SALUD**

```bash
GET    /api/health/                      # Health check (sin autenticación)
→ Retorna: { "status": "healthy", ... }
```

---

## 🔐 Permisos Requeridos

| Endpoint | Admin | Administ | Estudiante | Propietario |
|----------|-------|----------|-----------|------------|
| GET `/api/postulantes/` | ✅ | ✅ | ❌ | Solo propio |
| POST `/api/postulantes/` | ✅ | ❌ | ✅ | - |
| GET `/api/postulaciones/` | ✅ | ✅ | ❌ | Solo propio |
| POST `/api/documentos/` | ✅ | ✅ | ✅ | Solo propio |
| PATCH `/api/documentos/{id}/` (aprobar) | ✅ | ✅ | ❌ | - |
| POST `/api/postulaciones/{id}/avanzar-etapa/` | ✅ | ✅ | ❌ | - |
| GET `/api/reportes/...` | ✅ | ✅ | ❌ | - |
| GET `/api/auditoria/` | ✅ | ✅ | ❌ | - |

---

## 🔍 Parámetros de Query (QueryParams)

```bash
# Paginación
?page=1
?page_size=50              # Max: 100

# Filtrado
?modalidad=1
?gestion=2024
?estado=en_revision
?tipo_documento=1

# Búsqueda de texto
?search=Juan               # Busca global en campos definidos
?search=2023-001

# Ordenamiento
?ordering=nombre
?ordering=-creado_en       # Descendente con -

# Combinados
GET /api/postulaciones/?page=1&page_size=20&modalidad=1&ordering=-fecha_postulacion
```

---

## 📨 Estados de Respuesta HTTP

| Código | Significado | Cuando |
|--------|-------------|--------|
| **200** | OK | GET, PATCH exitoso |
| **201** | Created | POST exitoso |
| **204** | No Content | DELETE exitoso |
| **400** | Bad Request | Validación fallida |
| **401** | Unauthorized | Token faltante o expirado |
| **403** | Forbidden | Permisos insuficientes |
| **404** | Not Found | Recurso no existe |
| **500** | Server Error | Error interno |

---

## 🛠️ Casos de Uso Comunes

### Caso 1: Estudiante sube documentos

```bash
# 1. Login
POST /api/auth/login/
{ "username": "student", "password": "pass" }
→ Obtener access token

# 2. Ver mis postulaciones
GET /api/postulaciones/
Authorization: Bearer <token>

# 3. Subir documento
POST /api/documentos/
Authorization: Bearer <token>
{
  postulacion: 1,
  tipo_documento: 1,
  archivo: <file>
}
```

### Caso 2: Admin aprueba documentos

```bash
# 1. Login como admin
POST /api/auth/login/
{ "username": "admin", "password": "pass" }

# 2. Listar documentos pendientes
GET /api/documentos/?estado=pendiente
Authorization: Bearer <token>

# 3. Aprobar documento
PATCH /api/documentos/1/
Authorization: Bearer <token>
{
  "estado": "aprobado",
  "comentario_revision": "OK"
}
```

### Caso 3: Ver dashboard

```bash
# 1. Login
POST /api/auth/login/
{ "username": "admin", "password": "pass" }

# 2. Ver dashboard
GET /api/reportes/dashboard-general/
Authorization: Bearer <token>

# 3. Exportar estadísticas a Excel
GET /api/reportes/estadisticas-tutores/exportar/?year=2024
Authorization: Bearer <token>
```

---

## 🐛 Debugging

```bash
# Ver schema OpenAPI
GET /api/schema/
Authorization: Bearer <token>

# Swagger UI
GET /api/docs/
Authorization: Bearer <token>

# Admin Django
GET /admin/
(requiere login en sesión)
```

---

## ⏱️ Límites y Configuración

| Setting | Valor |
|---------|-------|
| Token de Acceso TTL | 60 minutos |
| Token de Refresco TTL | 7 días |
| Tamaño de página | 20 (max 100) |
| Tamaño máx. documento | 25 MB |
| Rate limit (anónimo) | 100/hora |
| Rate limit (usuario) | 1000/hora |
| Cache timeout | 1 hora |

---

## 📝 Notas Importantes

1. **Autenticación:** Todos los endpoints excepto `/api/auth/login/` y `/api/health/` requieren JWT
2. **Propiedad:** Estudiantes solo ven sus propios postulantes/postulaciones/documentos
3. **Archivos:** Se guardan en `/media/documentos/postulaciones/`
4. **Filtrableo:** Usa los filtros disponibles para reducir carga de datos
5. **Paginación:** Siempre pagina para mejor rendimiento
6. **Permisos:** Son combinación de rol Django + propiedad del recurso

---

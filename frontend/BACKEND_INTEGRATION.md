# Integración Frontend - Backend Django

## 🔗 Compatibilidad

Este frontend está diseñado específicamente para el backend **Django REST Framework** del Proyecto Sistema de Graduación.

### Backend Tecnologías
- ✅ Django 6.0.3
- ✅ Django REST Framework 3.16.1
- ✅ SimpleJWT 5.5.1 (JWT Authentication)
- ✅ PostgreSQL
- ✅ Nginx reverse proxy
- ✅ Docker + Docker Compose

### Frontend Tecnologías
- ✅ React 18.2.0
- ✅ Vite 5.0.0
- ✅ Tailwind CSS 3.3.0
- ✅ React Router 6.16.0
- ✅ Axios 1.5.0

## 📡 Comunicación API

### Base URL
```
Development:  http://localhost
Production:   https://tudominio.com
```

### Authentication
```
Method: JWT (JSON Web Token)
Header: Authorization: Bearer <access_token>
Storage: localStorage
```

### Token Endpoints
```
POST   /api/auth/login/         → Obtener tokens
POST   /api/auth/refresh/       → Refrescar token
```

## 📋 Endpoints Disponibles

### Autenticación
```javascript
POST /api/auth/login/
  Input:  { username, password }
  Output: { access, refresh, user }

POST /api/auth/refresh/
  Input:  { refresh: <token> }
  Output: { access: <token> }
```

### Postulantes
```javascript
GET    /api/postulantes/               → Listar all
GET    /api/postulantes/?search=nombre → Buscar
GET    /api/postulantes/{id}/          → Detalle
POST   /api/postulantes/               → Crear
PUT    /api/postulantes/{id}/          → Actualizar
DELETE /api/postulantes/{id}/          → Eliminar
```

### Postulaciones
```javascript
GET    /api/postulaciones/                      → Listar
GET    /api/postulaciones/?estado=aprobada      → Filtrar
GET    /api/postulaciones/{id}/                 → Detalle
POST   /api/postulaciones/                      → Crear
PUT    /api/postulaciones/{id}/                 → Actualizar
DELETE /api/postulaciones/{id}/                 → Eliminar
POST   /api/postulaciones/{id}/avanzar-etapa/   → Acción
GET    /api/postulaciones/{id}/historial/       → Historial
```

### Documentos
```javascript
GET    /api/documentos/                → Listar
GET    /api/documentos/?estado=pendiente → Filtrar
GET    /api/documentos/{id}/           → Detalle
POST   /api/documentos/                → Subir
PUT    /api/documentos/{id}/           → Actualizar
DELETE /api/documentos/{id}/           → Eliminar
```

### Otros
```javascript
GET/POST /api/modalidades/
GET/POST /api/etapas/
GET/POST /api/tipos-documento/
GET      /api/auditoria/
GET      /api/reportes/dashboard-general/
GET      /api/reportes/estadisticas-tutores/
GET      /api/reportes/estadisticas-tutores/exportar/
GET      /api/reportes/eficiencia-carreras/
```

## 🔄 Flujo de Integración

```
1. Usuario abre frontend (React)
   ↓
2. Redirige a /login (no autenticado)
   ↓
3. Usuario ingresa credenciales
   ↓
4. Frontend envía POST /api/auth/login/
   ↓
5. Backend (Django) retorna:
   {
     "access": "eyJ0...",
     "refresh": "eyJ0...",
     "user": {
       "id": 1,
       "username": "admin",
       "email": "admin@example.com",
       "role": "admin",
       "role_display": "Administrador",
       "first_name": "Admin",
       "last_name": "User"
     }
   }
   ↓
6. Frontend guarda tokens en localStorage
   ↓
7. AuthContext.Provider actualiza estado
   ↓
8. Redirige a /dashboard (autenticado)
   ↓
9. Navbar muestra "Bienvenido, Admin User"
   ↓
10. Sidebar muestra menú según role
```

## 🔐 Seguridad JWT

### Access Token
- Duración: 60 minutos
- Usado para autenticar requests
- Se envía en header: `Authorization: Bearer <token>`

### Refresh Token
- Duración: 7 días
- Usado para obtener nuevo access token
- Almacenado en localStorage

### Auto-Refresh
En `src/api/axios.js`:
```javascript
// Si recibe 401:
// 1. Intenta refrescar el token
// 2. Si refresh falla: Redirige a login
// 3. Si refresh funciona: Reintentas request original
```

## 📊 Response Format

### Success Response (2xx)
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "García",
  "email": "juan@example.com"
}
```

O para listas:
```json
{
  "count": 100,
  "next": "http://localhost/api/postulantes/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "nombre": "Juan" },
    { "id": 2, "nombre": "María" }
  ]
}
```

### Error Response (4xx/5xx)
```json
{
  "detail": "Authentication credentials were not provided.",
  "error": "Mensage de error específico"
}
```

## 🔄 CRUD Operations

### Crear (POST)
```javascript
// Frontend
const result = await api.create(
  '/api/postulantes/',
  { nombre: 'Juan', apellido: 'García', ci: '123456' }
);

// Backend recibe JSON en body
// Valida según model
// Retorna creado o error 400
```

### Leer (GET)
```javascript
// Con paginación
const result = await api.getAll(
  '/api/postulantes/',
  { page: 1, search: 'Juan' }
);

// Retorna { count, next, previous, results }
```

### Actualizar (PUT)
```javascript
// Actualiza todo el objeto
const result = await api.update(
  '/api/postulantes/1/',
  { nombre: 'Nueva', apellido: 'Actualizado', ci: '123456' }
);

// Backend valida, actualiza, retorna actualizado
```

### Eliminar (DELETE)
```javascript
// Elimina objeto
const result = await api.delete('/api/postulantes/1/');

// Backend elimina, retorna 204 No Content
```

## 🎭 Roles y Permisos

### Tipos de Rol
```
- admin           → Acceso total
- administ        → Acceso administrativo
- estudiante      → Acceso limitado
```

### Role-Based Access
En `src/components/Sidebar.jsx`:
```javascript
const menuItems = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    roles: ['admin', 'administ']  // Solo estos roles ven esto
  },
  // ...
];

const visibleItems = menuItems.filter(item =>
  item.roles.includes(user?.role)
);
```

## 🔢 Enums / Choices

### Estados de Postulación
```
'borrador'      → Borrador
'en_revision'   → En Revisión
'aprobada'      → Aprobada
'rechazada'     → Rechazada
```

### Estados de Documento
```
'pendiente'     → Pendiente de revisión
'aprobado'      → Aprobado
'rechazado'     → Rechazado
```

### Estados Generales
```
'EN_PROCESO'           → En Proceso
'PERFIL_APROBADO'      → Perfil Aprobado
'PRIVADA_APROBADA'     → Privada Aprobada
'PUBLICA_APROBADA'     → Pública Aprobada
'TITULADO'             → Titulado
```

## 📐 Data Models

### User (CustomUser)
```json
{
  "id": 1,
  "username": "estudiante",
  "email": "est@example.com",
  "first_name": "Juan",
  "last_name": "García",
  "role": "estudiante",
  "role_display": "Estudiante",
  "is_staff": false,
  "is_superuser": false,
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

### Postulante
```json
{
  "id": 1,
  "usuario_id": 1,
  "usuario_username": "estudiante",
  "usuario_nombre": "Juan García",
  "usuario_email": "est@example.com",
  "nombre": "Juan",
  "apellido": "García",
  "ci": "123456789",
  "codigo_estudiante": "EST001",
  "telefono": "555-1234",
  "carrera": "Ingeniería",
  "facultad": "Ingeniería",
  "creado_en": "2024-01-01T00:00:00Z"
}
```

### Postulación
```json
{
  "id": 1,
  "postulante": {...},
  "postulante_id": 1,
  "modalidad": 1,
  "modalidad_nombre": "Tesis",
  "etapa_actual": 1,
  "etapa_nombre": "Revisión",
  "titulo_trabajo": "Mi Proyecto",
  "tutor": "Dr. Garcia",
  "gestion": 2024,
  "estado": "en_revision",
  "estado_display": "En Revisión",
  "estado_general": "EN_PROCESO",
  "estado_general_display": "En Proceso",
  "observaciones": "Pendiente revisión",
  "fecha_postulacion": "2024-01-15T10:00:00Z"
}
```

## 💾 Persistencia

### localStorage
```javascript
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_info": {
    "id": 1,
    "username": "admin",
    // ... user data
  }
}
```

Al logout, se limpian todos los tokens.

## 🔄 Pagination

Todos los endpoints de lista soportan paginación:

```javascript
GET /api/postulantes/?page=1  // Primera página
```

Response:
```json
{
  "count": 100,
  "next": "http://.../postulantes/?page=2",
  "previous": null,
  "results": [...]
}
```

## 🔎 Búsqueda

En `src/api/api.js` y componentes pages:

```javascript
const params = {
  search: 'Juan',  // Para campos searchable
  page: 1
};

api.getAll('/api/postulantes/', params);
```

Backend busca en `search_fields` configu

rados.

## 🔒 Validación

### Frontend
En pages y forms:
```javascript
if (!username || !password) {
  setError('Usuario y contraseña requeridos');
  return;
}
```

### Backend
Django models y serializers validan:
```python
# En Django
class Postulante(models.Model):
  ci = models.CharField(unique=True)  # Validación
```

## 🐛 Error Handling

### Frontend
```javascript
const result = await api.getAll(endpoint);

if (!result.success) {
  setError(result.error);  // Muestra error al usuario
  console.error(result);    // Log para debugging
}
```

### Backend
Retorna error detail:
```json
{
  "detail": "Not found."
}
```

## ✅ Checklist de Integración

- [ ] Backend Django corriendo
- [ ] CORS configurado en Django
- [ ] Tokens JWT funcionales
- [ ] Frontend puede hacer login
- [ ] localStorage guarda tokens
- [ ] Auto-refresh de tokens
- [ ] Endpoints del CRUD trabajan
- [ ] Paginación funciona
- [ ] Búsqueda funciona
- [ ] Filtros funcionan
- [ ] Logout limpia storage
- [ ] Roles limitan acceso en UI
- [ ] Errores se muestran al usuario

## 📞 Troubleshooting

### "Cannot GET /api/..."
- Backend no está corriendo
- CORS no habilitado
- Proxy mal configurado en vite.config.js

### "token_not_valid"
- Token expirado
- Token inválido
- Secreto de Django cambió

### "Authentication credentials were not provided"
- No hay header Authorization
- Token no está en localStorage
- Axiosinstance no agrega header

### "CRUD Operations No Funcionan"
- Revisar permisos Django
- Usuario no autenticado
- Body no es JSON válido
- Violación de constraints

¡Integración lista! 🚀

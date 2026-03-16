# Frontend Architecture - Sistema de Graduación

## 📋 Descripción General

Este es un frontend React moderno y escalable para el Sistema de Graduación, diseñado para funcionar con un backend Django REST Framework.

## 🏗️ Arquitectura

### Capas

```
┌─────────────────────────────────────┐
│      Pages (Componentes de página)   │
├─────────────────────────────────────┤
│      Layouts (Wrapper de páginas)    │
├─────────────────────────────────────┤
│      Components (Comp. reutilizables)│
├─────────────────────────────────────┤
│      Hooks (useAuth, custom hooks)  │
├─────────────────────────────────────┤
│      Context (Estado global)         │
├─────────────────────────────────────┤
│      API Services (axios instance)   │
├─────────────────────────────────────┤
│      Constants (Configuración)       │
└─────────────────────────────────────┘
```

## 📁 Estructura de Carpetas

```
frontend/
│
├── src/
│   ├── api/                    # API communication layer
│   │   ├── axios.js            # Axios instance con interceptores
│   │   ├── authApi.js          # Authentication endpoints
│   │   └── api.js              # Generic CRUD operations
│   │
│   ├── components/             # Reusable components
│   │   ├── Navbar.jsx          # Top navigation
│   │   ├── Sidebar.jsx         # Side navigation
│   │   └── ProtectedRoute.jsx  # Route protection
│   │
│   ├── layouts/
│   │   └── AdminLayout.jsx     # Main app layout
│   │
│   ├── pages/                  # Page components
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Postulantes.jsx
│   │   ├── Postulaciones.jsx
│   │   ├── Documentos.jsx
│   │   ├── Modalidades.jsx
│   │   ├── Usuarios.jsx
│   │   └── Reportes.jsx
│   │
│   ├── context/
│   │   └── AuthContext.jsx     # Global auth state
│   │
│   ├── hooks/
│   │   └── useAuth.js          # Custom auth hook
│   │
│   ├── router/
│   │   └── AppRouter.jsx       # Route configuration
│   │
│   ├── styles/
│   │   └── index.css           # Tailwind + custom CSS
│   │
│   ├── constants/
│   │   └── api.js              # API endpoints
│   │
│   ├── utils/                  # Utility functions
│   ├── App.jsx
│   └── main.jsx
│
├── public/
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── .env.example
├── .eslintrc.cjs
└── README.md
```

## 🔐 Autenticación

### Flujo de Login

```
Usuario → Ingresa credenciales
   ↓
Login.jsx → authApi.login()
   ↓
axiosInstance POST /api/auth/login/
   ↓
Backend retorna: { access, refresh, user }
   ↓
Guardar en localStorage
   ↓
AuthContext.Provider actualiza estado
   ↓
Redirige a /dashboard
```

### Token Management

- **Access Token**: 60 minutos
- **Refresh Token**: 7 días
- Almacenado en `localStorage`
- Auto-refresh en axiosInstance cuando expira

## 🔄 Flujo de Datos

### GET Request

```
Component → useAuth() → api.getAll()
   ↓
axiosInstance.get() → Agrega header Authorization
   ↓
Si 401: Intenta refresh automático
   ↓
Backend responde con datos
   ↓
Component actualiza estado ui
```

### POST/PUT/DELETE

```
Component → formulario.submit()
   ↓
api.create/update/delete()
   ↓
axiosInstance con interceptores
   ↓
Backend procesa
   ↓
Retorna respuesta
   ↓
Component actualiza UI o redirige
```

## 🎯 Context API (AuthContext)

Proporciona:
- `user`: Usuario actual
- `isAuthenticated`: Si está autenticado
- `loading`: Estado de carga
- `login()`: Función para login
- `logout()`: Función para logout
- `updateUser()`: Actualizar info de usuario
- `hasPermission()`: Verificar permisos

## 🛣️ Rutas

```
/login                  → Página de login (pública)
/dashboard              → Dashboard (protegida)
/postulantes            → Gestor de postulantes (protegida)
/postulaciones          → Gestor de postulaciones (protegida)
/documentos             → Gestor de documentos (protegida)
/modalidades            → Gestor de modalidades (protegida)
/usuarios               → Gestor de usuarios (protegida)
/reportes               → Reportes y analytics (protegida)
/                       → Redirige a /dashboard
*                       → Redirige a /dashboard (404)
```

## 🎨 Estilos (Tailwind CSS)

### Configuración

- **Colors**: Blue (primary), Green (success), Red (danger)
- **Responsive**: Mobile-first design
- **Components**: Custom CSS classes en index.css

### Clases Personalizadas

```css
.btn              /* Base buttons */
.btn-primary      /* Blue button */
.btn-danger       /* Red button */
.btn-success      /* Green button */

.card             /* Container cards */
.card-lg          /* Large cards */

.input            /* Input styling */

.badge            /* Small labels */
.badge-primary
.badge-success
.badge-danger
.badge-warning
```

## 🚀 Performance

- **Code Splitting**: React Router lazy loading
- **Bundle Size**: Tree-shaking con Vite
- **State Management**: Context API (mínimo overhead)
- **API Caching**: Implementar con useMemo si es necesario

## 🔒 Seguridad

- ✅ JWT en localStorage
- ✅ Auto-refresh de tokens
- ✅ ProtectedRoute para rutas privadas
- ✅ Logout al expirar refresh token
- ✅ CORS habilitado en backend

## 📦 Dependencies

- **react**: 18.2.0
- **react-router-dom**: 6.16.0
- **axios**: 1.5.0
- **tailwindcss**: 3.3.0

## 🛠️ Desarrollo

### Agregar Nueva Página

1. Crear `src/pages/NombrePagina.jsx`
2. Agregar ruta en `src/router/AppRouter.jsx`
3. Agregar link en `src/components/Sidebar.jsx`
4. Usar `api.getAll()` para peticiones

### Agregar Nuevo Endpoint

1. Editar `src/constants/api.js`
2. Agregar en `ENDPOINTS` object
3. Usar en componentes con `api.getAll(endpoint)`

### Componentes Reutilizables

Cualquier componente usado más de 2 veces debe ir en `src/components/`

## 🔌 Integración con Backend

### Baseado en:
- Django REST Framework
- SimpleJWT para autenticación
- CORS habilitado
- API versionado en `/api/`

### Endpoints Esperados
Ver `src/constants/api.js` para lista completa

## 📊 Estado Global

Solo `AuthContext` usa estado global.
Otros datos usan estado local con `useState`.

Para estado más complejo, considerar Zustand o Redux.

## 🧪 Testing (Futuro)

Implementar:
- Jest para unit tests
- React Testing Library para components
- MSW para mock API

## 📝 Logs y Debugging

- Console.log en desarrollo
- Error boundaries para crashes
- Network tab en DevTools

## 🚢 Deployment

### Build
```bash
npm run build
```

### Output
`dist/` folder listo para servir con Nginx/Apache

### Environment Variables
Copiar `.env.example` a `.env` y configurar:
- `VITE_API_URL`

## 📝 Notas Importantes

1. **Modularidad**: Cada componente responsable de una cosa
2. **Reutilización**: Maximizar reutilización de componentes
3. **Performance**: Memoización donde sea necesario
4. **Accesibilidad**: Usar semántica HTML correcta
5. **Responsiveness**: Testear en móvil

## 🔄 Sync Con Backend

La arquitectura está diseñada para integración perfecta con:
- Django REST Framework
- PostgreSQL database
- Nginx reverse proxy
- Docker deployments

# Setup Frontend - Sistema de Graduación

## ✅ Requisitos Previos

- Node.js >= 18.0.0
- npm o yarn
- Backend Django corriendo en `http://localhost`
- Git

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
cd /ruta/del/proyecto
```

### 2. Instalar Dependencias

```bash
cd frontend
npm install
```

O con yarn:
```bash
yarn install
```

### 3. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Editar `.env`:
```env
VITE_API_URL=http://localhost
VITE_API_TIMEOUT=30000
```

Para producción:
```env
VITE_API_URL=https://tudominio.com
```

## 🚀 Desarrollo

### Iniciar Servidor de Desarrollo

```bash
npm run dev
```

Abrirá en: `http://localhost:5173`

### Acceder a la Aplicación

1. Ir a `http://localhost:5173/login`
2. Ingresar credenciales (demo):
   - Usuario: `admin`
   - Contraseña: `password`
3. Explorar dashboard

## 🏗️ Build para Producción

```bash
npm run build
```

Genera carpeta `dist/` lista para deployment.

## 📝 Estructura de Archivos

Ver `ARCHITECTURE.md` para detalles completos.

## 🔧 Configuración

### API Endpoints

Todos en `src/constants/api.js`:

```javascript
API_CONFIG.ENDPOINTS.LOGIN           // POST /api/auth/login/
API_CONFIG.ENDPOINTS.POSTULANTES     // GET /api/postulantes/
API_CONFIG.ENDPOINTS.POSTULACIONES   // GET /api/postulaciones/
// ... ver archivo para todos
```

### Tailwind CSS

Config en `tailwind.config.js`:

```javascript
export default {
  theme: {
    extend: {
      colors: { /* custom colors */ },
      // ...
    }
  }
}
```

### Vite Config

En `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost',
    changeOrigin: true,
  }
}
```

## 🔐 Autenticación

### Login Flow

1. Usuario ingresa credenciales en Login.jsx
2. `authApi.login()` envía POST a `/api/auth/login/`
3. Backend retorna tokens + user info
4. Se guardan en localStorage
5. AuthContext actualiza estado
6. Redirige a /dashboard

### Token Auto-Refresh

En `src/api/axios.js`:
- Si 401: Intenta refrescar token automáticamente
- Si refresh falla: Redirige a login
- Reinstenta request original con nuevo token

## 📱 Responsive Design

- Mobile first approach
- Breakpoints: sm, md, lg
- Sidebar colapsable en móvil
- Tablas en scroll en móvil

## 🎨 Componentes

### Reutilizables

- **Navbar**: Navegación superior + logout
- **Sidebar**: Menú lateral con rol-based access
- **ProtectedRoute**: Protege rutas autenticadas
- **Tables**: Listados con paginación
- **Forms**: Inputs y validación

### Páginas

- **Login**: Autenticación
- **Dashboard**: Resumen y estadísticas
- **Postulantes**: CRUD de postulantes
- **Postulaciones**: Gestión de postulaciones
- **Documentos**: Gestión de documentos
- **Modalidades**: CRUD de modalidades
- **Usuarios**: Gestión de usuarios
- **Reportes**: Analytics y exportación

## 🐛 Debugging

### En Desarrollo

1. Abrir DevTools (F12)
2. Network tab para ver requests
3. Console para logs
4. React DevTools extension

### Errores Comunes

**404 en /api/**
- ✅ Backend debe estar corriendo
- ✅ CORS debe estar habilitado
- ✅ Verificar proxy en vite.config.js

**401 Unauthorized**
- ✅ Token expirado, intenta logout/login
- ✅ Verificar que access_token esté en localStorage
- ✅ Ver interceptores en axios.js

**CORS Error**
- ✅ Backend debe tener CORS_ALLOWED_ORIGINS correctos
- ✅ En dev: incluir localhost:5173
- ✅ Ver config Django settings.py

**Problema con Módulos**
```bash
# Limpiar cache de node
npm cache clean --force
rm -rf node_modules
npm install
```

## 🚢 Deployment

### Con Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Con Nginx

```nginx
server {
  listen 80;
  server_name tudominio.com;

  root /var/www/dist;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api/ {
    proxy_pass http://backend:8000;
  }
}
```

### Vercel (Recomendado)

1. Conectar repositorio a Vercel
2. Automático build y deploy
3. Environment variables en Vercel UI
4. Cambiar VITE_API_URL a producción

## 📚 Recursos

- [React Docs](https://react.dev)
- [React Router](https://reactrouter.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite](https://vitejs.dev)
- [Axios](https://axios-http.com)

## 💬 Soporte

Para problemas:
1. Revisar arquitectura en ARCHITECTURE.md
2. Check console errors
3. Verificar backend está corriendo
4. Revisar network requests en DevTools

## 🎓 Próximos Pasos

1. ✅ Setup completado
2. Explorar páginas (click en Sidebar)
3. Implementar modales para crear/editar
4. Agregar validación de formularios
5. Implementar paginación real
6. Agregar búsqueda/filtros avanzados
7. Testing con Jest + React Testing Library
8. Deployment a producción

## 📋 Checklist Antes de Producción

- [ ] Backend en HTTPS
- [ ] VITE_API_URL actualizado
- [ ] npm run build sin warnings
- [ ] Testear en Chrome, Firefox, Safari
- [ ] Responsive en móvil
- [ ] Validación de formularios completa
- [ ] Error handling mejorado
- [ ] Loading states en todas partes
- [ ] Permissions verificadas
- [ ] Logout funciona correctamente

¡Listo para comenzar! 🚀

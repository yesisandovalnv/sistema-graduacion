# Guía de Debugging: Login Failed

Si el login está mostrando "Login failed", usa esta guía para identificar y resolver el problema.

## 🔍 Paso 1: Verificar Conexión del Backend

```bash
# Terminal 1: Verificar que Django está corriendo
cd c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion
python manage.py runserver 0.0.0.0:8000

# Debería ver:
# Starting development server at http://127.0.0.1:8000/
```

### ✅ Backend corriendo:
```bash
# Terminal 2: Probar endpoint de login directamente
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Respuesta esperada:
# {
#   "refresh": "eyJ0eXAi...",
#   "access": "eyJ0eXAi...",
#   "user": {
#     "id": 1,
#     "username": "admin",
#     "email": "admin@example.com",
#     "first_name": "Admin",
#     "last_name": "User",
#     "role": "admin",
#     "role_display": "Administrador"
#   }
# }
```

## 🔍 Paso 2: Verificar Frontend Configuración

### Opción A: Revisar el .env
```bash
# Verificar que c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion\frontend\.env existe

# Contenido esperado:
# VITE_API_URL=http://localhost:8000
# VITE_API_TIMEOUT=30000
```

### Opción B: Reiniciar Vite Dev Server
```bash
# Si cambiaste el .env, necesitas reiniciar
cd c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion\frontend
npm run dev

# Debería mostrar:
# ➜ Local: http://localhost:5173/
```

## 🔍 Paso 3: Abrir Console del Navegador (F12)

### ✅ Si ves en la console:
```
API Request: { method: 'POST', url: '/api/auth/login/', hasAuth: false }
Login Error: {
  status: 401,
  data: { detail: 'No active account found with the given credentials' }
}
```

**Interpretación:**
- ✅ La request llegó al backend
- ❌ Las credenciales son incorrectas
- **Solución:** Usa credenciales correctas o crea nuevo user

```bash
# En terminal del backend:
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: password
```

### ❌ Si ves error de CORS:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/auth/login/' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Problema:** Backend no acepta requests de localhost:5173

**Solución:** Verificar CORS en config/settings.py

```bash
# En c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion\config\settings.py

# Debe contener:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost",
]

# Si no está, agregarlo y reiniciar Django
```

### ❌ Si ves Network Error o "failed to fetch":
```
TypeError: Failed to fetch
# o
ERR_EMPTY_RESPONSE
```

**Problema:** El proxy de Vite no está funcionando

**Solución 1:** Verificar que vite.config.js tiene proxy correcto
```javascript
// Debe tener:
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

**Solución 2:** Reiniciar Vite Dev Server
```bash
# Ctrl+C para detener
# npm run dev para iniciar de nuevo
```

### ❌ Si ves "Cannot read property 'success' of undefined":
**Problema:** Response no tiene estructura esperada

**Solución:** Verificar que el LoginView en Django está retornando el formato correcto

```python
# usuarios/views.py debe tener:
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

# usuarios/serializers.py > LoginSerializer.validate() debe retornar:
{
  "refresh": "...",
  "access": "...",
  "user": { ... }
}
```

## 🔍 Paso 4: Verificar LocalStorage

```javascript
// Abre la console del navegador y ejecuta:

// Después de intentar login fallido:
localStorage.getItem('access_token');  // Debe ser null
localStorage.getItem('refresh_token'); // Debe ser null
localStorage.getItem('user_info');     // Debe ser null

// Después de login exitoso:
localStorage.getItem('access_token');  // Debe ser "eyJ0eXAi..."
localStorage.getItem('refresh_token'); // Debe ser "eyJ0eXAi..."
localStorage.getItem('user_info');     // Debe ser '{"id":1,"username":"admin"...}'
```

## 🔍 Paso 5: Verificar Tamaño de Token

```javascript
// En console:
const token = localStorage.getItem('access_token');
console.log('Token length:', token?.length);
console.log('Token:', token);

// Tokens típicos tienen 300-500+ caracteres
// Si es muy corto, hay un problema
```

## 📋 Checklist de Debugging

- [ ] Backend Django corriendo en http://localhost:8000
- [ ] Login endpoint funciona: `curl (POST) http://localhost:8000/api/auth/login/`
- [ ] .env existe con VITE_API_URL=http://localhost:8000
- [ ] Vite dev server reiniciado después de cambios
- [ ] No hay errores CORS en browser console
- [ ] Credenciales son correctas (admin/password o lo que creaste)
- [ ] LocalStorage guarda tokens después de login exitoso
- [ ] Auth Context actualiza user state
- [ ] Redirección a /dashboard ocurre después de login

## 🚀 Flujo Correcto de Login

```
1. Usuario escribe credentials y hace click "Iniciar Sesión"
   ↓
2. Login.jsx llama: login('admin', 'password')
   ↓
3. AuthContext.login() llama: authApi.login(username, password)
   ↓
4. authApi.login() hace: axiosInstance.post('/api/auth/login/', {...})
   ↓
5. Vite proxy intercepta /api y envía a http://localhost:8000/api/auth/login/
   ↓
6. Django LoginView recibe request y valida credentials
   ↓
7. Si valido: retorna { access, refresh, user }
   ↓
8. authApi.login() guarda en localStorage y retorna { success: true }
   ↓
9. AuthContext.login() actualiza state: setUser(result.user), setIsAuthenticated(true)
   ↓
10. Login.jsx recibe success:true y hace navigate('/dashboard')
   ↓
11. Dashboard carga con datos del usuario autenticado ✅
```

## 🛠️ Comandos de Debugging Rápido

```bash
# Ver logs en tiempo real del backend
# Terminal 1:
cd c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion
python manage.py runserver 0.0.0.0:8000 --verbosity 2

# Ver qué está haciendo el frontend
# En browser console (F12), ejecuta:
// Obtener todos los logs de API
localStorage.debug = '*'

# Limpiar todo y empezar de nuevo
# En browser console:
localStorage.clear()
location.reload()
```

## 📞 Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| "No active account found" | Credenciales incorrectas | Crear nuevo user o verificar password |
| CORS error | Backend no permite origen | Agregar X-Frame-Options a CORS_ALLOWED_ORIGINS |
| "Failed to fetch" | Proxy no funciona | Reiniciar Vite dev server |
| Token undefined | No se guardó en localStorage | Verificar LoginSerializer en Django |
| Redirect a /login después de login | Auth state no actualizado | Verificar AuthContext.login() |
| "undefined is not an object" | Response format incorrecto | Verificar que LoginView retorna user |

## ✅ Si todo funciona:

```
Deberías ver en browser console:
- API Request: { method: 'POST', url: '/api/auth/login/', hasAuth: false }
- Redirect a http://localhost:5173/dashboard
- Navbar mostrando "Bienvenido, Admin User"
- Sidebar con opciones según role
```

¡Problema resuelto! 🎉

---

**Referencia rápida de archivos:**
- Frontend: `/frontend/src/api/authApi.js`
- Frontend: `/frontend/.env`
- Frontend: `/frontend/vite.config.js`
- Backend: `/usuarios/views.py`
- Backend: `/usuarios/serializers.py`
- Backend: `/config/settings.py` (CORS)

# 🎓 SISTEMA DE GRADUACIÓN - SETUP PROFESIONAL

**Última actualización:** 2026-03-24 | **v1.0 Production Ready**

---

## 📋 Inicio Rápido

### Opción 1: Menú Interactivo (RECOMENDADO)

```powershell
.\start.ps1
```

Elige:
- **[1]** Modo Desarrollo (Frontend local + Backend Docker)
- **[2]** Modo Producción (Todo en Docker)
- **[3]** Validar sistema
- **[4]** Detener todo
- **[5]** Ver documentación

### Opción 2: Ejecutar Directamente

**Desarrollo:**
```powershell
.\1_dev.ps1
# En otra terminal:
cd frontend && npm run dev
```

**Producción:**
```powershell
.\2_prod.ps1
```

**Validar:**
```powershell
.\3_validate.ps1 -Mode both
```

---

## 🏗️ Arquitectura

### Modo 1: Desarrollo
```
Tu Máquina                    Docker
┌──────────────────┐         ┌──────────────┐
│ Frontend React   │         │ PostgreSQL   │
│ (npm run dev)    │◄────────│ (puerto 5432)│
│ localhost:5173   │         └──────────────┘
└──────────────────┘              ▲
       │                          │
       ▼                          ▼
    ┌────────────────────────────────────────┐
    │ Backend Django (Gunicorn)              │
    │ Docker Container (puerto 8000)         │
    └────────────────────────────────────────┘
```

### Modo 2: Producción
```
Tu Navegador
   │
   ▼
┌─────────────────────────────────────┐
│  NGINX (http://localhost:80)        │
│  - Sirve Frontend estático SPA      │
│  - Proxy a Backend (/api, /admin)   │
└─────────────────────────────────────┘
   │               │
   ▼               ▼
┌──────────────┐ ┌──────────────┐
│  Frontend    │ │  Backend     │
│  React SPA   │ │  Django      │
│  (compilado) │ │  Gunicorn    │
└──────────────┘ └──────────────┘
       │               │
       └───────┬───────┘
               ▼
         ┌──────────────┐
         │  PostgreSQL  │
         │  (puerto 5432)
         └──────────────┘
```

---

## 🔍 Características Profesionales

### ✅ Validación Real
- **Healthcheck** de Backend, Frontend, BD
- **Detección** de puertos ocupados
- **Timeouts** apropiados
- **Retry logic** automático

### ✅ Manejo de Errores Robusto
- Validación pre-start
- Mensaje de error claro
- Cleanup automático en caso de fallo
- Logs persistidos a archivos

### ✅ Logs Separados
- Versiones timestamped
- Guardados en `logs/`
- Sistema + Docker logs separados
- Fácil debugging

### ✅ Variables de Entorno Seguras
- `.env.example` completo
- Documentación clara
- Soporta desarrollo y producción
- Aplicación automática

### ✅ Scripts Profesionales
```
start.ps1          ← Menú principal
1_dev.ps1          ← Modo Desarrollo
2_prod.ps1         ← Modo Producción
3_validate.ps1     ← Validación post-start
```

---

## 🌐 URLs de Acceso

### Modo Desarrollo
| Servicio | URL | Puerto |
|----------|-----|--------|
| Frontend | http://localhost:5173 | 5173 |
| Backend API | http://localhost:8000/api | 8000 |
| Admin Django | http://localhost:8000/admin | 8000 |
| PostgreSQL | localhost:5432 | 5432 |

### Modo Producción
| Servicio | URL | Puerto |
|----------|-----|--------|
| Frontend (Nginx) | http://localhost/ | 80 |
| Frontend Direct | http://localhost:5173 | 5173 |
| Backend API | http://localhost:8000/api | 8000 |
| Nginx Proxy | http://localhost:80 | 80 |
| Admin Django | http://localhost:8000/admin | 8000 |

---

## 📊 Estado de Servicios

### Ver Estado
```powershell
docker compose ps
```

### Ver Logs
```powershell
# Backend
docker compose logs -f backend

# Frontend
docker compose logs -f frontend

# Nginx
docker compose logs -f nginx

# Base de datos
docker compose logs -f db
```

### Acceder a Base de Datos
```powershell
docker compose exec db psql -U sistema_user -d sistema_graduacion
```

---

## 🛠️ Verificación y Debugging

### Test Rápido
```powershell
# Validar todos los servicios
.\3_validate.ps1 -Mode both

# Validar solo desarrollo
.\3_validate.ps1 -Mode dev

# Validar solo producción
.\3_validate.ps1 -Mode prod
```

### Logs del Última Validación
```
logs/validation_YYYYMMDD_HHMMSS.log
```

### Test Manual de Backend
```powershell
# Test API
Invoke-WebRequest http://localhost:8000/api/

# Test Admin
Invoke-WebRequest http://localhost:8000/admin/

# Test Token
Invoke-WebRequest -Uri http://localhost:8000/api/token/ -Method POST
```

---

## 🚨 Troubleshooting

### Puerto Ocupado
```powershell
# Ver qué está usando un puerto
netstat -ano | findstr :8000

# Matar proceso específico
taskkill /PID <numero> /F
```

### Backend no responde
```powershell
# Ver logs
docker compose logs -f backend

# Verificar BD está conectada
docker compose logs -f db

# Reiniciar
docker compose restart backend
```

### Frontend no conecta a Backend
```powershell
# Verificar .env.development
cat frontend/.env.development

# Debe ser: VITE_API_URL=http://localhost:8000/api

# Limpiar y reconstruir
cd frontend
npm install
npm run dev
```

### Nginx mostrando error
```powershell
# Ver config
cat nginx/default.conf

# Logs nginx
docker compose logs -f nginx

# Test curl
curl -v http://localhost/

curl -v http://localhost/api/
```

---

## 🔐 Variables de Entorno

### `.env` (Raíz - Requerido)
```bash
# SEGURIDAD
DJANGO_SECRET_KEY=your-random-key-50-chars-min
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
DJANGO_DEBUG=True  # False en producción

# DATABASE
POSTGRES_TAG=15-alpine
POSTGRES_DB=sistema_graduacion
POSTGRES_USER=sistema_user
POSTGRES_PASSWORD=your-secure-password

# MIGRACIONES
RUN_MIGRATIONS=1    # Auto-run al iniciar
RUN_COLLECTSTATIC=1 # Auto-collect static

# PUERTOS (Opcional)
DJANGO_PORT=8000
POSTGRES_PORT=5432
FRONTEND_PORT=5173
NGINX_PORT=80
```

### `frontend/.env.development` (Modo Dev)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

### `frontend/.env.production` (Modo Prod)
```bash
VITE_API_URL=http://backend:8000/api
VITE_API_TIMEOUT=30000
```

---

## 📁 Estructura de Archivos

```
sistema-graduacion/
├── 1_dev.ps1                  ← Script Modo Desarrollo
├── 2_prod.ps1                 ← Script Modo Producción
├── 3_validate.ps1             ← Validación post-start
├── start.ps1                  ← Menú principal
├── .env                        ← Configuración actual
├── .env.example               ← Template de configuración
├── docker-compose.yml         ← Orquestación Docker
├── Dockerfile.backend         ← Imagen Backend
├── Dockerfile.frontend        ← Imagen Frontend
├── entrypoint.sh             ← Script inicio Backend
├── nginx/
│   └── default.conf          ← Config Nginx SPA
├── frontend/
│   ├── .env.development      ← Config dev
│   ├── .env.production       ← Config prod
│   ├── src/
│   ├── public/
│   └── package.json
├── config/
├── logs/                      ← Logs con timestamp
│   ├── backend_*.log
│   ├── system_*.log
│   └── validation_*.log
└── MODOS_EJECUCION.md        ← Documentación completa
```

---

## ✅ Flujo Típico de Desarrollo

### Día 1: Setup
```powershell
# Clonar repo (ya hecho)
# Abrir en VS Code

# Terminal 1: Backend
.\1_dev.ps1

# Esperar "✅ Backend respondiendo"

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Esperar "Local: http://localhost:5173"

# Terminal 3: Validar
.\3_validate.ps1 -Mode dev
```

### Día 2+: Desarrollo Normal
```powershell
# Terminal 1: Backend (si está apagado)
.\1_dev.ps1

# Terminal 2: Frontend (si está apagado)
cd frontend && npm run dev

# Código → Hot-reload automático
# SPA enruta correctamente
# API accesible en 8000
```

### Testing Integración
```powershell
# Terminal 1: Producción
.\2_prod.ps1

# Terminal 2: Validar
.\3_validate.ps1 -Mode prod

# Test: http://localhost / http://localhost:5173
# Todo va por Nginx
```

---

## 🔄 Cambiar de Modo

### Dev → Prod
```powershell
# Terminal Dev: Ctrl+C
# Luego:
.\2_prod.ps1
```

### Prod → Dev
```powershell
docker compose down
.\1_dev.ps1
# Terminal 2:
cd frontend && npm run dev
```

---

## 📝 Logs y Debugging

### Logs Sistema (Timestamped)
```
logs/system_20260324_143022.log
logs/backend_20260324_143022.log
logs/validation_20260324_143022.log
```

### Ver Logs Recientes
```powershell
# Últimos 50 líneas
cat logs/system*.log | tail -50

# Buscar errores
Select-String -Path "logs/*.log" -Pattern "ERROR|error|Error" -List
```

---

## 🚀 Deployment Checklist

- [ ] `.env` con valores reales (DJANGO_SECRET_KEY, passwords)
- [ ] DJANGO_DEBUG=False en producción
- [ ] PostgreSQL password seguro
- [ ] Probado con `.\2_prod.ps1`
- [ ] `.\3_validate.ps1 -Mode prod` pasó
- [ ] Puertos 80, 8000, 5173, 5432 disponibles
- [ ] Docker Desktop corriendo
- [ ] Frontend compilado sin errores
- [ ] Backend migrado correctamente
- [ ] Login funciona
- [ ] Dashboard carga
- [ ] API responde

---

## 📞 Soporte

### Documentación Completa
- `MODOS_EJECUCION.md` - Guía detallada con troubleshooting
- `GUIA_RAPIDA_VISUAL.md` - Paso a paso visual
- `README.md` - Información general

### Recursos
- Django Docs: https://docs.djangoproject.com/
- React Docs: https://react.dev/
- Docker Docs: https://docs.docker.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/

---

## 📊 Comparativa de Modos

| Aspecto | Modo 1 (Dev) | Modo 2 (Prod) |
|--------|-------------|---------------|
| **Frontend** | npm run dev (hot-reload) | Compilado + serve |
| **Backend** | Docker (gunicorn) | Docker (gunicorn) |
| **BD** | Docker (postgres) | Docker (postgres) |
| **Proxy** | Ninguno | Nginx |
| **Velocidad** | ⚡ Rápida (no build) | 📦 Lenta (build) |
| **Mejor para** | Desarrollo | Testing/Producción |
| **URLs** | localhost:5173 | localhost:5173 \| localhost:80 |

---

## 🎯 Resumen

| Necesitas | Comando |
|-----------|---------|
| Comenzar | `.\start.ps1` |
| Dev | `.\1_dev.ps1` |
| Prod | `.\2_prod.ps1` |
| Validar | `.\3_validate.ps1` |
| Detener | `docker compose down` |
| Ver docs | Ver `MODOS_EJECUCION.md` |

---

**Created:** 2026-03-24 | **Version:** 1.0 | **Status:** Production Ready ✅

¡Listo para usar! 🚀

# 🚀 Modos de Ejecución - Sistema de Graduación

## 📋 Resumen Rápido

| Modo | Uso | Comando | URL Frontend | URL Backend |
|------|-----|---------|--------------|-------------|
| **DESARROLLO** | Programar con hot-reload | `./run_modo1_dev.ps1` | http://localhost:5173 | http://localhost:8000 |
| **FULL DOCKER** | Producción/Demo todo contenido | `./run_modo2_prod.ps1` | http://localhost:5173 | http://localhost:80 (Nginx) |

---

## 🔧 MODO 1: DESARROLLO (Local + Docker)

**Ideal para:** Programar, hacer cambios rápidos, debugging.

### Arquitectura
```
TU MÁQUINA                    DOCKER
┌──────────────────┐         ┌──────────────┐
│ Frontend React   │         │ PostgreSQL   │
│ (npm run dev)    │────────▶│ (puerto 5432)│
│ localhost:5173   │         └──────────────┘
│                  │              ▲
└──────────────────┘              │
       │                          │
       ▼                          ▼
┌──────────────────────────────────────────┐
│ Backend Django en Docker                 │
│ (puerto 8000)                            │
└──────────────────────────────────────────┘
```

### Prerequisitos
- ✅ Docker Desktop corriendo
- ✅ Node.js 18+ instalado
- ✅ PowerShell 5.1+ (Windows)

### Pasos de Ejecución

#### **Paso 1: Preparar variables de entorno (Primera vez)**
```powershell
# Copiar archivo de ejemplo si no existe
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env creado desde .env.example"
}
```

#### **Paso 2: Ejecutar el script de Modo 1**
```powershell
# En la raíz del proyecto
.\run_modo1_dev.ps1
```

**Este script hará automáticamente:**
1. ✅ Levanta PostgreSQL en Docker
2. ✅ Levanta Backend (Django) en Docker
3. ✅ Espera a que Backend esté listo
4. ✅ Abre Terminal 2 asignada para Frontend

#### **Paso 3: En otra Terminal, ejecuta el Frontend**
```powershell
cd frontend
npm install  # Solo primera vez
npm run dev
```

**Espera este mensaje:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
```

### 🌐 Acceso en Modo 1
- **Frontend:** http://localhost:5173 ⭐ **AQUÍ PROGRAMAS**
- **Backend API:** http://localhost:8000/api
- **Admin Django:** http://localhost:8000/admin
- **Base de Datos:** localhost:5432 (postgres / tu-password)

### 🛑 Detener Modo 1
```powershell
# Terminal 1: Ctrl + C (detiene Docker)
# Terminal 2: Ctrl + C (detiene npm dev)

# O ejecutar:
docker compose down
```

---

## 🐳 MODO 2: FULL DOCKER (Producción)

**Ideal para:** Producción, testing integral, demostración.

### Arquitectura
```
TU NAVEGADOR
   │
   ▼
┌─────────────────────────────────────┐
│  NGINX (http://localhost:80)        │
│  - Sirve Frontend estático          │
│  - Proxy a Backend                  │
└─────────────────────────────────────┘
   │               │
   ▼               ▼
┌──────────────┐ ┌──────────────┐
│  Frontend    │ │  Backend     │
│  (React)     │ │  (Django)    │
│  :5173       │ │  :8000       │
└──────────────┘ └──────────────┘
       │               │
       └───────┬───────┘
               ▼
         ┌──────────────┐
         │  PostgreSQL  │
         │  :5432       │
         └──────────────┘
```

### Prerequisitos
- ✅ Docker Desktop corriendo
- ✅ Puerto 80 disponible (no usar otro programa)

### Pasos de Ejecución

#### **Paso 1: Preparar variables de entorno (Primera vez)**
```powershell
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env creado desde .env.example"
}
```

#### **Paso 2: Ejecutar script Modo 2**
```powershell
# En la raíz del proyecto
.\run_modo2_prod.ps1
```

**Este script hará automáticamente:**
1. ✅ Detiene todos los contenedores previos
2. ✅ Reconstruye las imágenes (Frontend + Backend)
3. ✅ Levanta todo: DB + Backend + Frontend + Nginx

**Espera estos mensajes:**
```
✅ Sistema listo en:
   - Frontend: http://localhost:5173
   - Nginx (API): http://localhost:80
   - Backend: http://localhost:8000
```

### 🌐 Acceso en Modo 2
- **Frontend vía Nginx:** http://localhost:5173
- **Backend vía Nginx:** http://localhost:80
- **Backend directo:** http://localhost:8000
- **Admin Django:** http://localhost:8000/admin

### 🛑 Detener Modo 2
```powershell
.\stop_sistema.ps1
# O manual:
docker compose down --volumes  # Elimina volúmenes también
```

---

## 🔄 Cambiar entre Modos

### De Modo 1 a Modo 2
```powershell
# Terminal 1 Modo 1: Ctrl + C
docker compose down

# Ejecutar Modo 2:
.\run_modo2_prod.ps1
```

### De Modo 2 a Modo 1
```powershell
# Detener Modo 2:
docker compose down

# Ejecutar Modo 1:
.\run_modo1_dev.ps1
```

---

## 🐛 Troubleshooting

### Puerto 8000 o 5173 ocupado
```powershell
# Encuentra qué está usando el puerto
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Mata el proceso
taskkill /PID <PID> /F
```

### Docker no está corriendo
```powershell
# Reinicia Docker Desktop desde el menú de Windows
# O ejecuta:
docker ps  # Debe mostrar lista de contenedores
```

### Backend no conecta a BD
```powershell
# Verifica que la BD está healthy
docker compose ps db
# Status debe ser "healthy"

# Si no, reconstruye:
docker compose down -v
.\run_modo1_dev.ps1
```

### Frontend no ve Backend
```powershell
# Verifica VITE_API_URL en frontend/.env.development
# Debe ser: VITE_API_URL=http://localhost:8000/api

# Limpia caché:
cd frontend
npm run dev  # Fuerza recarga
```

---

## 📝 Variables de Entorno Importantes

### `.env` (Raíz del proyecto)
```bash
# Django
DJANGO_SECRET_KEY=replace-with-long-random-value
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
POSTGRES_DB=sistema_graduacion
POSTGRES_USER=sistema_user
POSTGRES_PASSWORD=change-this-password
POSTGRES_TAG=15-alpine
```

### `frontend/.env.development` (Modo 1)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

### `frontend/.env.production` (Modo 2)
```bash
VITE_API_URL=http://backend:8000/api
VITE_API_TIMEOUT=30000
```

---

## ✅ Checklist de Primera Ejecución

- [ ] Docker Desktop instalado y corriendo
- [ ] Node.js 18+ instalado: `node --version`
- [ ] `.env` existe en raíz
- [ ] `frontend/.env.development` existe
- [ ] `frontend/.env.production` existe
- [ ] PowerShell ejecuta scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- [ ] Ejecuta `.\run_modo1_dev.ps1` o `.\run_modo2_prod.ps1`

---

## 🎯 Resumen Rapido - Comandos Más Usados

```powershell
# MODO 1 - Desarrollo
.\run_modo1_dev.ps1          # Inicia BD + Backend
cd frontend && npm run dev   # En otra terminal, inicia Frontend

# MODO 2 - Producción Full Docker
.\run_modo2_prod.ps1         # Todo en Docker

# Detener todo
docker compose down

# Ver logs de Backend
docker compose logs -f backend

# Acceder a BD
docker compose exec db psql -U sistema_user -d sistema_graduacion
```

---

**Última actualización:** 2026-03-24

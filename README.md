# 🎓 Sistema de Graduación - UABJB

Aplicación web para gestionar postulantes, postulaciones y documentos para programas de graduación.

**Stack Tecnológico:**
- Backend: Django 4.x + PostgreSQL
- Frontend: React 18 + Vite
- Contenedorización: Docker

---

## ⚡ ¡INICIO RÁPIDO! (¡LO MÁS IMPORTANTE!)

### 🎯 OPCIÓN MÁS FÁCIL - Menú Interactivo

```powershell
# Desde PowerShell en la raíz del proyecto:
.\start.ps1
```

Luego elige:
- **[1]** para Modo Desarrollo 💻
- **[2]** para Modo Full Docker 🐳
- **[3]** para Ver Guía Completa 📖

---

### ✅ O ejecuta directamente:

**Para programar (Frontend con hot-reload):**
```powershell
.\run_modo1_dev.ps1
# En otra terminal: cd frontend && npm run dev
```

**Para producción (Todo en Docker):**
```powershell
.\run_modo2_prod.ps1
```

**Para detener todo:**
```powershell
.\stop_sistema.ps1
```

---

## 📖 Guía Completa de Modos

Ver [**MODOS_EJECUCION.md**](MODOS_EJECUCION.md) para documentación detallada y troubleshooting.

---

## 📋 Modos de Ejecución

### 1️⃣ MODO DESARROLLO (Recomendado para desarrollo local)

Backend y BD en Docker, Frontend con hot-reload local.

**Paso 1: Configurar variables de entorno**

```bash
# En la raíz del proyecto
cp .env.example .env
# Editar .env si es necesario
```

**Paso 2: Levantar BD y Backend en Docker**

```bash
docker compose up db backend
```

Espera a que Backend esté listo:
```
INFO    Starting development server at http://0.0.0.0:8000/
```

**Paso 3: Levantar Frontend en desarrollo (en otra terminal)**

```bash
cd frontend
cp .env.example .env
# Asegurate que VITE_API_URL=http://localhost:8000/api
npm install  # Solo primera vez
npm run dev
```

Frontend disponible en: **http://localhost:5173**

---

### 2️⃣ MODO FULL DOCKER (Para producción/demostración)

Todo en contenedores: DB, Backend, Frontend, Nginx.

**Comando único:**

```bash
# Asegurate de tener .env configurado
docker compose --profile prod up --build
```

**Acceso:**

- Frontend: **http://localhost:5173**
- Backend API: **http://localhost:8000**
- Nginx: **http://localhost:80**

---

## � Configuración de Entorno (Variables)

### Entendiendo los Modos

Vite carga automáticamente archivos `.env` según el modo:

```
npm run dev        → Carga .env.development
npm run build      → Carga .env.production
docker build       → Carga .env.production
```

### Por qué "backend:8000" NO funciona localmente

```
❌ INCORRECTO (navegador local):
VITE_API_URL=http://backend:8000/api
Razón: "backend" es nombre de servicio Docker
       Solo existe dentro de la red Docker interna

✅ CORRECTO (navegador local, con Backend en Docker):
VITE_API_URL=http://localhost:8000/api
Razón: Puerto 8000 está mapeado al host via "ports: 8000:8000"
```

### Configuración por Modo

#### **.env.development** (npm run dev)
```bash
# Backend corre en Docker (:8000)
# Frontend corre localmente en npm dev
# Browser accede a backend via puerto mapeado
VITE_API_URL=http://localhost:8000/api
```

#### **.env.production** (Docker)
```bash
# Todo está en Docker, misma red interna
# Frontend container accede a backend service por nombre DNS
VITE_API_URL=http://backend:8000/api
```

### Cómo Acceder en el Código

```javascript
// En cualquier componente o archivo
const apiUrl = import.meta.env.VITE_API_URL
const timeout = import.meta.env.VITE_API_TIMEOUT

console.log(apiUrl)  // http://localhost:8000/api (dev) o http://backend:8000/api (prod)
```

---


### Variables de Entorno (`.env`)

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
POSTGRES_DB=sistema_graduacion
POSTGRES_USER=sistema_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_TAG=15-alpine
```

### Frontend (`.env` en carpeta frontend/)

```bash
# En desarrollo
VITE_API_URL=http://localhost:8000/api

# En Docker
VITE_API_URL=http://backend:8000/api
```

---

## 📦 Estructura del Proyecto

```
sistema-graduacion/
├── config/                 # Configuración Django
├── auditoria/             # App Django
├── documentos/            # App Django
├── usuarios/              # App Django
├── frontend/              # Aplicación React Vite
│   ├── src/
│   ├── public/
│   └── .env.example
├── nginx/                 # Config Nginx
├── docker-compose.yml     # Orquestación de contenedores
├── Dockerfile.backend     # imagen Backend
├── Dockerfile.frontend    # Imagen Frontend
├── .env.example          # Variables de entorno
└── README.md             # Este archivo
```

---

## 🚀 Comandos Útiles

### Desarrollo

```bash
# Levantar solo DB y Backend
docker compose up db backend

# Frontend en otra terminal
cd frontend && npm run dev

# Ver logs
docker compose logs -f backend

# Detener servicios
docker compose down

# Limpiar volúmenes (¡cuidado! borra BD)
docker compose down -v
```

### Full Docker

```bash
# Construir y levantar
docker compose --profile prod up --build

# En background
docker compose --profile prod up -d --build

# Ver logs
docker compose logs -f frontend

# Detener
docker compose --profile prod down
```

### Migraciones Django

```bash
# Crear migraciones
docker compose exec backend python manage.py makemigrations

# Aplicar migraciones
docker compose exec backend python manage.py migrate

# Crear superusuario
docker compose exec backend python manage.py createsuperuser
```

---

## 🐛 Troubleshooting

### "Port 5432 already in use"

```bash
# Ver qué está usando el puerto
lsof -i :5432

# O cambiar puerto en .env
POSTGRES_PORT=5433:5432
```

### Frontend no conecta a Backend

**La causa más común:** Usar `VITE_API_URL=http://backend:8000/api` en desarrollo local.

**Solución:**
- ✅ Modo desarrollo (npm run dev): Usa `.env.development` → `http://localhost:8000/api`
- ✅ Modo Docker: Usa `.env.production` → `http://backend:8000/api`

**Verificar qué variable se está usando:**
```javascript
// Abierto en DevTools Console:
console.log(import.meta.env.VITE_API_URL)
// Debe mostrar: http://localhost:8000/api (dev) o http://backend:8000/api (prod)
```

**Si aún no funciona:**
```bash
# Limpiar node_modules y reinstalar
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install
npm run dev
```

### Migraciones de BD no aplican

```bash
docker compose up db backend --wait
# Esperar a que backend esté listo, luego:
docker compose exec backend python manage.py migrate
```

### Variables de entorno no cargan en Docker

Asegúrate que:
1. Archivo existe: `frontend/.env.production`
2. Archivo tiene permisos de lectura: `chmod 644 frontend/.env.production`
3. No está gitignoreado: Revisa `.gitignore`

---

## 📚 Documentación Adicional

- [ARCHITECTURE.md](frontend/ARCHITECTURE.md) - Arquitectura Frontend
- [BACKEND_INTEGRATION.md](frontend/BACKEND_INTEGRATION.md) - Integración con Backend
- [SETUP.md](frontend/SETUP.md) - Setup Frontend

---

## ✅ Checklist de Ejecución

### Antes de comprometer código:

- [ ] `npm run build` en frontend (sin errores)
- [ ] Tests pasando
- [ ] Sin console.log o debug en código
- [ ] Variables de entorno no incluidas en git

### Antes de deploy:

- [ ] `docker compose --profile prod up --build` funciona
- [ ] Todas las migraciones aplicadas
- [ ] Superusuario creado
- [ ] Archivos estáticos recolectados

---

## 📞 Soporte

Para reportar problemas, crear un issue en el repositorio con:
- Modo de ejecución (desarrollo/full docker)
- Comandos ejecutados
- Mensajes de error completos
